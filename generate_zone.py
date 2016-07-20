#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import math
import utils
from courier import TOTAL, Courier, CourierPool

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
c_total = TOTAL
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
        cu.execute("select order_id, spot_id, num \
                from eb_order where site_id=='%s' \
                order by num" % self._zone)
        return cu.fetchall()

    def _initial_o2o_orders_start(self):
        cu = self._conn.cursor()
        ret = []
        for order in cu.execute("select t1.* from o2o_order as t1 \
                join shop as t2 on t1.shop_id==t2.shop_id \
                where zone=='%s' \
                order by pickup_time" % self._zone):
            ret.append((order[0], order[1], order[2], \
                    utils.time2minutes(order[3]), \
                    utils.time2minutes(order[4]), \
                    order[5]))
        return ret

    def _initial_o2o_orders_end(self):
        cu = self._conn.cursor()
        ret = []
        for order in cu.execute("select t1.* from o2o_order as t1 \
                join spot as t2 on t1.spot_id==t2.spot_id \
                where zone=='%s' \
                order by delivery_time" % self._zone):
            ret.append((order[0], order[1], order[2], \
                    utils.time2minutes(order[3]), \
                    utils.time2minutes(order[4]), \
                    order[5]))
        return ret
    
    def get_order_num(self):
        return len(self._eb_orders) + len(self._o2o_orders_start)

    def initial_courier_pool(self, couriers, start):
        """
        Based on the total number of order to be send
        and o2o orders whose spot is in this zone, whereas
        the shop is not.
        """
        # global c_total
        num = int(math.floor(self.get_order_num()*TOTAL/TOTAL_ORDER))
        num = 1 if num == 0 else num
        # ret = CourierPool([Courier('D%04d' % (c_total-i)) for i in xrange(num)])
        self._courier_pool = CourierPool(couriers[start:start+num])
        return num
        # print ret
        # c_total -= num
        # return ret

    def add_courier(self, courier):
        self._courier_pool.add(courier)

    def do_execute(self):
        """
        Execute the delivery plan
        """
        pass

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
