#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import utils
from courier import TOTAL, Courier, CourierPool, Action
from orders import EBOrder, O2OOrder, PickupOrder, Orders, TOTAL_ORDER

TOTAL_ZONE = 124

class Zone(object):
    def __init__(self, conn, zone, center):
        self._conn = conn
        self._zone = zone
        self._center = center
        self._eb_orders = self._initial_eb_orders()
        self._o2o_orders_start = self._initial_o2o_orders_start()
        self._o2o_orders_end = self._initial_o2o_orders_end()

    def _initial_eb_orders(self):
        cu = self._conn.cursor()
        orders = [EBOrder(order, (self._zone, self._center)) for order in cu.execute(\
                    "select order_id, t1.spot_id, t1.num, t2.lng, t2.lat \
                    from eb_order as t1 \
                    join spot as t2 on t1.spot_id==t2.spot_id \
                    where site_id=='%s' \
                    order by num" % self._zone)]
        return Orders(orders)

    def _initial_o2o_orders_start(self):
        cu = self._conn.cursor()
        orders = [O2OOrder((order[0], order[1], order[2], \
                    utils.time2minutes(order[3]), \
                    utils.time2minutes(order[4]), \
                    order[5], order[6], \
                    (order[7], order[8]), \
                    (order[9], order[10]))) for order in cu.execute(\
                    "select t1.*, t2.lng, t2.lat, t3.lng, t3.lat \
                    from o2o_order as t1 \
                    join shop as t2 on t1.shop_id==t2.shop_id \
                    join spot as t3 on t1.spot_id==t3.spot_id \
                    where t2.zone=='%s' \
                    order by pickup_time" % self._zone)]
        return Orders(orders)
        
    def _initial_o2o_orders_end(self):
        cu = self._conn.cursor()
        orders = [O2OOrder((order[0], order[1], order[2], \
                    utils.time2minutes(order[3]), \
                    utils.time2minutes(order[4]), \
                    order[5], order[6], \
                    (order[7], order[8]), \
                    (order[9], order[10]))) for order in cu.execute(\
                    "select t1.*, t2.lng, t2.lat, t3.lng, t3.lat \
                    from o2o_order as t1 \
                    join shop as t2 on t1.shop_id==t2.shop_id \
                    join spot as t3 on t1.spot_id==t3.spot_id \
                    where t3.zone=='%s' \
                    order by delivery_time" % self._zone)]
        return Orders(orders)
    
    def get_order_num(self):
        return len(self._eb_orders) + len(self._o2o_orders_start)

    def initial_courier_pool(self, couriers, start):
        """
        Based on the total number of order to be send
        and o2o orders whose spot is in this zone, whereas
        the shop is not.
        """
        num = int(math.floor(self.get_order_num()*TOTAL/TOTAL_ORDER))
        num = max(1, num-2)
        self._courier_pool = CourierPool(couriers[start:start+num])
        return num

    def add_courier(self, courier):
        self._courier_pool.add(courier)

    def is_center(self, point):
        """
        point: (lng, lat) for a point
        return True or False
        """
        return self._center==point

    @staticmethod
    def plan_by_DP(orders, site, start, end, limit, start_with_site, end_with_site, pack=0):
        """
        orders: list of orders
        site: lng and lat of site
        start: lng and lat of start point
        end: lng and lat of end point
        limit: the limit of time used
        start_with_site: True or False for starting from site or not
        end_with_site: True or False for stopping at site or not
        pack: the number of packages already have
        return ordered orders
        """
        def _in(l, e):
            """
            l: list
            e: element to test
            return False if e is in l
            """
            try:
                l.index(e)
            except Exception:
                return False
            return True

        def _time_spent(order, last, end):
            """
            order: order object
            last: object in d
            return time spent(this order's plus last's)
            """
            # avoid loop back!!
            if _in(last['path'], order):
                return float('inf')
            last_order = last['path'][-1]
            # last order to new order
            dis1 = utils.distance(last_order.target(), order.target())
            t_spent1 = utils.travel_time(dis1) + order.part_time()
            # new order to end
            dis2 = utils.distance(order.target(), end)
            t_spent2 = utils.travel_time(dis2)
            # last order to end
            dis3 = utils.distance(last_order.target(), end)
            t_spent3 = utils.travel_time(dis3)
            # total time spent
            return last['cost'] - t_spent3 + t_spent1 + t_spent2

        empty_order = EBOrder(('Empty', 'fake_spot', 0, start[0], start[1]), ('site_id', (0,0)))
        site_pickup_order = PickupOrder(('Center', site, 'site'))
        d = [{'path':[empty_order], 'cost': float('inf')} \
                for i in xrange(141-pack)] if start_with_site \
                else [{'path':[empty_order, site_pickup_order], \
                'cost': float('inf')} for i in xrange(141-pack)]
        d[0]['cost'] = 0 if start_with_site else \
                utils.travel_time(utils.distance(start, site))
        # locate = start
        for i in xrange(140-pack):
            p_num = i + 1
            tmp = filter(lambda x: x.num() <= p_num, orders)
            if len(tmp) == 0:
                continue
            # calc d[p_num] = min{d[a] + t(order)}
            # a < p_num, order belongs to tmp
            next_order = min(map(lambda x: \
                    (_time_spent(x, d[p_num-x.num()], end), x), \
                    tmp), key=lambda x: x[0])
            d[p_num]['cost'] = next_order[0]
            d[p_num]['path'] = [o for o in d[p_num-next_order[1].num()]['path']]
            d[p_num]['path'].append(next_order[1])
            # print 'd[%d]: %s' % (p_num, d[p_num])
        # return orders[1:] to exclude the empty order
        for plan in d[::-1]:
            if plan['cost'] != float('inf') and plan['cost'] <= limit:
                end_type = 'site' if end_with_site else 'shop'
                plan['path'].append(PickupOrder(('fake_order', end, end_type)))
                return plan['path'][1:], plan['cost']
        return [], float('inf')

    @staticmethod
    def plan_by_TSP(orders, start, s_time):
        """
        orders: orders to be plan
        start: (lng, lat) for start point
        destination for picking up orders
        return (plan, end_point, min_cost)
        """
        def cost(p, k):
            """
            p: source o2o order
            k: target o2o order
            """
            return utils.travel_time(utils.distance(p.target(), k.target())) \
                    + utils.part_time(k.num())

        # TODO: how to get the path
        def TSP(p, V):
            """
            p: the fake o2o order of starting point
            V: the collection of o2o orders to be chosen
            return the min cost and path
            """
            if len(V)==0:
                return 0, []
            c_min = float('inf')
            path = None
            for v in V:
                next_c, path_n = TSP(v, filter(lambda x: x!=v, V))
                c = cost(p, v) + next_c
                if c < c_min:
                    c_min = c
                    path_n.append(v)
                    path = path_n
            return c_min, path

        start_order = O2OOrder(('Fake_O', 'Spot_id', 'Shop_id', s_time, \
                s_time, 0, 0, start, start))
        cost, path = TSP(start_order, orders)

        return path[len(path)-1::-1], path[0].target(), cost

    def do_plan(self):
        """
        Execute the delivery plan
        """
        print "planning %s..." % self._zone

        # o2o_orders' plan, new a o2o action, and extend it with eb orders
        o2os = self._o2o_orders_start.remain()
        pickup_time = list(set([(o.shop(), o._pickup_time) for o in o2os]))
        pickup_time.sort(key=lambda x: x[1], reverse=True)
        pickup_order = PickupOrder(('Pickup', self._center, 'site'))
        for t in pickup_time:
            o2o = filter(lambda x: (x.shop(), x._pickup_time)==t, o2os)
            if len(o2o) > 1:
                plan, end, cost = Zone.plan_by_TSP(o2o, t[0], t[1])
            else:
                plan = o2o
                end = o2o[0].target()
                cost = utils.travel_time(utils.distance(o2o[0].shop(), \
                        o2o[0].target())) + o2o[0].part_time()
            # print plan, end, (t[1], t[1]+cost), utils.travel_time(\
                    # utils.distance(end, self._center))
            # find the next location, site or shop
            no_courier = 0
            while True:
                courier = self._courier_pool.get(t[1], t[1]+cost)
                no_courier += 1
                if not courier or no_courier == self._courier_pool.size():
                    print "No courier can match up"
                    # no_courier = True
                    break
                n_action = courier.first_action()
                # the first o2o order
                if not n_action:
                    end2site = utils.travel_time(utils.distance(end, self._center))
                    plan.append(pickup_order)
                    e_time = t[1]+cost+end2site
                    courier.assgin(Action(t[0], self._center, t[1], e_time, plan))
                    break
                # Not the first o2o order
                end2n_shop = utils.travel_time(utils.distance(end, n_action._s_point))
                if t[1]+cost+end2n_shop > n_action._s_time:
                    continue
                end2site = utils.travel_time(utils.distance(end, self._center))
                site2n_shop = utils.travel_time(utils.distance(self._center, n_action._s_point))
                # if end->site->shop <= t(n_shop)-t(end) then shop else site
                if t[1]+cost+end2site+site2n_shop <= n_action._s_time:
                    plan.append(pickup_order)
                    e_point = self._center
                    e_time = t[1]+cost+end2site
                else:
                    shop_pickup_order = PickupOrder(('Pickup', n_action._s_point, 'shop'))
                    plan.append(shop_pickup_order)
                    e_point = n_action._s_point
                    e_time = t[1]+cost+end2n_shop
                courier.assgin(Action(t[0], e_point, t[1], e_time, plan))
                break
        print "O2O assigned"

        no_free = 0
        # es_orders' plan
        while True:
            orders = self._eb_orders.remain()
            if len(orders) == 0:
                print "EB assgined"
                break
            courier = self._courier_pool.get()
            if not courier or self._courier_pool.size() == no_free:
                print "%s has no courier free" % self._zone
                break
            interval = courier.get_interval()
            if interval:
            # for start, end in courier.free_time():
                start, end = interval
                # print "Round: %d--%d" % (start, end)
                action_before, action_next = courier.two_actions(start, end)
                s_point = self._center if not action_before else action_before._e_point
                if not self.is_center(s_point):
                    continue
                e_point = self._center if not action_next else action_next._s_point
                planned_orders, real_cost = Zone.plan_by_DP(orders, self._center, s_point, \
                        e_point, end-start, self.is_center(s_point), self.is_center(e_point))
                no_free = no_free+1 if real_cost == 0 else 0
                if len(planned_orders) == 0:
                    continue
                # print 'planned: %s, cost: %d' % (planned_orders, real_cost)
                # generate an eb order action based on dp
                if end == 840:
                    courier.assgin(Action(s_point, e_point, start, start+real_cost, planned_orders))
                else:
                    courier.assgin(Action(s_point, e_point, end-real_cost, end, planned_orders))
        
        with file("./Data/result.rc", "a") as f:
            f.write("<%s>\n%r\n" % (self._zone, self._courier_pool))
        # print self._courier_pool

        return len(self._eb_orders.remain()) + len(self._o2o_orders_start.remain())

    def __str__(self):
        return "eb_orders: %d\n%s\no2o_orders: %d\n%s\n" \
                % (len(self._eb_orders), self._eb_orders\
                , len(self._o2o_orders_start), self._o2o_orders_start)

if __name__ == '__main__':
    import sqlite3, sys

    conn = sqlite3.connect('./Data/data.db')
    # TODO: Bugs
    zone1 = Zone(conn, 'A001', (121.486181, 31.270203))
    # zone1 = Zone(conn, 'A099', (121.799314, 31.033621))
    couriers = [Courier('D%04d'%i) for i in xrange(1, TOTAL + 1)]
    last = zone1.initial_courier_pool(couriers, 0)
    # print zone1
    while True:
        if zone1.do_plan() == 0:
            break
        zone1.add_courier(couriers[last])
        last += 1
    conn.close()
