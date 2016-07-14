#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utils

def initial_o2o_dis(conn):
    cu = conn.cursor()
    time_spents = []
    for order_id, shop_lng, shop_lat, spot_lng, spot_lat \
        in cu.execute("select t1.order_id, t2.lng, t2.lat, t3.lng, t3.lat \
        from o2o_order as t1 \
        join shop as t2 on t1.shop_id==t2.shop_id \
        join spot as t3 on t1.spot_id==t3.spot_id"):
        t = utils.travel_time(utils.distance((shop_lng, shop_lat), (spot_lng, spot_lat)))
        time_spents.append((int(t), order_id)) 
    cu.executemany("update o2o_order set time_spent=? where order_id=?", time_spents)
    conn.commit()
    print "Done"

def do_initialize(conn, action):
    if action == 'o2o_dis':
        initial_o2o_dis(conn)

if __name__ == "__main__":
    import sys, sqlite3
    if len(sys.argv) < 2:
        print "Usage: ./initailization.py [o2o_dis]"
        sys.exit(1)

    conn = sqlite3.connect('./Data/data.db')
    do_initialize(conn, sys.argv[1])
    conn.close()

# vim: set sw=4 ts=4 softtabstop=4
