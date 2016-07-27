#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import math
import utils
from courier import TOTAL, Courier, CourierPool, Action
from orders import EBOrder, O2OOrder, Orders

def do_mark_spots(conn):
    cu = conn.cursor()
    cu.execute("select site_id, spot_id from eb_order")
    pairs = cu.fetchall()
    cu.executemany("update spot set zone=? where spot_id=?", pairs)
    conn.commit()

def do_classify_shops(conn):
    cu = conn.cursor()
    X = []
    y = []
    for lng, lat, zone in cu.execute("select lng, lat, zone from spot"):
        X.append((lng, lat))
        y.append(zone)
    neigh = KNeighborsClassifier(n_neighbors=5, metric='pyfunc', func=utils.distance)
    neigh.fit(np.array(X), np.array(y))

    zones = []
    for shop_id, lng, lat in cu.execute("select shop_id, lng, lat from shop"):
        # print (shop_id, neigh.predict([[lng, lat]])[0])
        zones.append((neigh.predict([[lng, lat]])[0], shop_id))
    cu.executemany("update shop set zone=? where shop_id=?", zones)
    conn.commit()

def do_generate(conn, action):
    if action == 'spot' or action == 'all':
        do_mark_spots(conn)
    if action == 'shop' or action == 'all':
        do_classify_shops(conn)

# eb + o2o
TOTAL_ORDER = 12487
TOTAL_ZONE = 124

class Zone(object):
    def __init__(self, conn, zone):
        self._conn = conn
        self._zone = zone
        self._eb_orders = self._initial_eb_orders()
        self._o2o_orders_start = self._initial_o2o_orders_start()
        self._o2o_orders_end = self._initial_o2o_orders_end()
        self._courier_pool = []

    def _initial_eb_orders(self):
        cu = self._conn.cursor()
        orders = [EBOrder(order) for order in cu.execute(\
                    "select order_id, spot_id, num \
                    from eb_order where site_id=='%s' \
                    order by num" % self._zone)]
        return Orders(orders)

    def _initial_o2o_orders_start(self):
        cu = self._conn.cursor()
        orders = [O2OOrder((order[0], order[1], order[2], \
                    utils.time2minutes(order[3]), \
                    utils.time2minutes(order[4]), \
                    order[5], order[6])) for order in cu.execute(\
                    "select t1.* from o2o_order as t1 \
                    join shop as t2 on t1.shop_id==t2.shop_id \
                    where zone=='%s' \
                    order by pickup_time" % self._zone)]
        return Orders(orders)
        
    def _initial_o2o_orders_end(self):
        cu = self._conn.cursor()
        orders = [O2OOrder((order[0], order[1], order[2], \
                    utils.time2minutes(order[3]), \
                    utils.time2minutes(order[4]), \
                    order[5], order[6])) for order in cu.execute(\
                    "select t1.* from o2o_order as t1 \
                    join spot as t2 on t1.spot_id==t2.spot_id \
                    where zone=='%s' \
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
    def plan_by_DP(orders, start):
        """
        orders: list of orders
        start: lng and lat of start point
        return ordered orders
        """
        d = [float('inf') for i in xrange(141)] # initialize the state
        d[0] = 0
        locate = start
        for i in xrange(140):
            p_num = i + 1
            tmp = filter(lambda x: x.num() == p_num, orders)
            if len(tmp) == 0: # and cannot be aggregated by small orders
                continue
            # TODO: calc distance decompose
            d[p_num]
        return orders

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
            planned_orders = Zone.plan_by_DP(orders)
            # TODO: generate an eb order action based on dp
            courier.assgin()

    def __str__(self):
        return "eb_orders: %d\n%s\no2o_orders: %d\n%s\n" \
                % (len(self._eb_orders), self._eb_orders\
                , len(self._o2o_orders_start), self._o2o_orders_start)

if __name__ == '__main__':
    import sqlite3, sys
    if len(sys.argv) < 2:
        print "Usage: generate_zone.py [spot|shop|all]"
        sys.exit(1)

    conn = sqlite3.connect('./Data/data.db')
    # do_generate(conn, sys.argv[1])
    zone1 = Zone(conn, 'A001')
    print zone1
    conn.close()

# vim: set sw=4 ts=4 softtabstop=4
