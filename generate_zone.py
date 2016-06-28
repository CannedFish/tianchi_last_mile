#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import utils

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

if __name__ == '__main__':
    import sqlite3, sys
    if len(sys.argv) < 2:
        print "Usage: generate_zone.py [spot|shop|all]"
        sys.exit(1)

    conn = sqlite3.connect('./Data/data.db')
    do_generate(conn, sys.argv[1])
    conn.close()

# vim: set sw=4 ts=4 softtabstop=4
