#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import utils
from courier import TOTAL, Courier, CourierPool, Action
from orders import EBOrder, O2OOrder, Orders, TOTAL_ORDER

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
        orders = [EBOrder(order) for order in cu.execute(\
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
                    # "select t1.* from o2o_order as t1 \
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
        num = 1 if num == 0 else num
        self._courier_pool = CourierPool(couriers[start:start+num])
        return num

    def add_courier(self, courier):
        self._courier_pool.add(courier)

    @staticmethod
    def plan_by_DP(orders, start, end, limit):
        """
        orders: list of orders
        start: lng and lat of start point
        end: lng and lat of end point
        limit: the limit of time used
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
            t_spent1 = utils.travel_time(dis1) + utils.part_time(order.num())
            # new order to end
            dis2 = utils.distance(order.target(), end)
            t_spent2 = utils.travel_time(dis2)
            # last order to end
            dis3 = utils.distance(last_order.target(), end)
            t_spent3 = utils.travel_time(dis3)
            # total time spent
            return last['cost'] - t_spent3 + t_spent1 + t_spent2

        empty_order = EBOrder(('Empty', 'fake_spot', 0, start[0], start[1]))
        d = [{'path':[empty_order], 'cost': float('inf')} \
                for i in xrange(141)] # initialize the state
        d[0]['cost'] = 0
        locate = start
        for i in xrange(140):
            p_num = i + 1
            tmp = filter(lambda x: x.num() <= p_num, orders)
            if len(tmp) == 0: # and cannot be aggregated by small orders
                continue
            # calc d[p_num] = min{d[a] + t(order)}
            # a < p_num, order belongs to tmp
            next_order = min(map(lambda x: \
                    (_time_spent(x, d[p_num-x.num()], end), x), \
                    tmp), key=lambda x: x[0])
            d[p_num]['cost'] = next_order[0]
            d[p_num]['path'] = [o for o in d[p_num-next_order[1].num()]['path']]
            d[p_num]['path'].append(next_order[1])
            print 'd[%d]: %s' % (p_num, d[p_num])
        # return orders[1:] to exclude the empty order
        for plan in d[::-1]:
            if plan['cost'] != float('inf') and plan['cost'] <= limit:
                return plan['path'][1:], plan['cost']
        return []

    def do_plan(self):
        """
        Execute the delivery plan
        """
        print "planning %s..." % self._zone
        # TODO: o2o_orders' plan, new a o2o action, and extend it with eb orders
        # es_orders' plan
        while True:
            orders = self._eb_orders.remain()
            if len(orders) == 0:
                break
            courier = self._courier_pool.get()
            if not courier:
                print "%s has no courier free" % self._zone
                break
            for start, end in courier.free_time():
                print "Round: %d--%d" % (start, end)
                if start == end:
                    if start == 840:
                        break
                    continue
                action_before, action_next = courier.two_actions(start, end)
                s_point = self._center if not action_before else action_before._e_point
                e_point = self._center if not action_next else action_next._s_point
                planned_orders, real_cost = Zone.plan_by_DP(orders, s_point, e_point, end-start)
                print 'planned: %s, cost, %d' % (planned_orders, real_cost)
                # TODO: calc real time used
                # generate an eb order action based on dp
                courier.assgin(Action(s_point, e_point, start, start + real_cost, planned_orders))

    def __str__(self):
        return "eb_orders: %d\n%s\no2o_orders: %d\n%s\n" \
                % (len(self._eb_orders), self._eb_orders\
                , len(self._o2o_orders_start), self._o2o_orders_start)

if __name__ == '__main__':
    import sqlite3, sys

    conn = sqlite3.connect('./Data/data.db')
    zone1 = Zone(conn, 'A001', (121.486181, 31.270203))
    couriers = [Courier('D%04d'%i) for i in xrange(1, TOTAL + 1)]
    zone1.initial_courier_pool(couriers, 0)
    print zone1
    zone1.do_plan()
    conn.close()
