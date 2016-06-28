#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3, random
import matplotlib.pyplot as plt
import numpy as np

def _get_points(conn):
    cu = conn.cursor()
    ret = []
    for table in ['site', 'spot', 'shop']:
        lng = []
        lat = []
        for point in cu.execute("select lng, lat from %s" % table):
            lng.append(point[0])
            lat.append(point[1])
        ret.append((lng, lat))
    return ret[0], ret[1], ret[2]

def show_point(conn):
    sites, spots, shops = _get_points(conn)
    print len(sites[0]), len(spots[0]), len(shops[0])
    plt.plot(spots[0], spots[1], 'bs', label='spot')
    plt.plot(sites[0], sites[1], 'ro', label='site', ms=12)
    plt.plot(shops[0], shops[1], 'g^', label='shop', ms=12)
    plt.legend()
    plt.show()

def _get_orders(conn, table1, table2):
    cu = conn.cursor()
    lines = []
    for order in cu.execute("select t2.lng, t2.lat, t3.lng, t3.lat \
        from %s as t1 \
        join %s as t2 on t1.%s_id==t2.%s_id \
        join spot as t3 on t1.spot_id==t3.spot_id" \
        % (table1, table2, table2, table2)):
        lines.append(((order[0], order[2]), (order[1], order[3])))
    return lines

def show_eb_order(conn):
    sites, spots, shops = _get_points(conn)
    orders = _get_orders(conn, 'eb_order', 'site')
    plt.plot(spots[0], spots[1], 'bs', label='spot')
    for order in orders:
        plt.plot(order[0], order[1], 'k-')
    plt.plot(sites[0], sites[1], 'ro', label='site', ms=12)
    plt.legend()
    plt.show()

def show_o2o_order(conn):
    sites, spots, shops = _get_points(conn)
    orders = _get_orders(conn, 'o2o_order', 'shop')
    plt.plot(spots[0], spots[1], 'bs', label='spot')
    for order in orders:
        plt.plot(order[0], order[1], 'y-')
    plt.plot(shops[0], shops[1], 'g^', label='shop', ms=12)
    plt.legend()
    plt.show()

def show_class(conn):
    cu = conn.cursor()
    cu.execute("select * from site")
    sites = cu.fetchall()
    for site_id, lng, lat in sites:
        # color = 0xff
        color = random.randint(1, 0xffffff)
        cc = '#%06x' % color
        for table, size, marker in [('spot', 6, 'o'), ('shop', 12, '^')]: 
            cu.execute("select lng, lat from %s where zone=='%s'" % (table, site_id))
            arr = np.array(cu.fetchall())
            if len(arr) == 0:
                continue
            plt.plot(arr[:, 0], arr[:, 1], c=cc, ms=size, marker=marker, ls='None')
        plt.plot([lng], [lat], c=cc, ms=20, marker='*')
        # color += 0x20000
    plt.show()

def show_all(conn):
    pass

def show(conn, plottype):
    if plottype == 'point':
        show_point(conn)
    elif plottype == 'eb_order':
        show_eb_order(conn)
    elif plottype == 'o2o_order':
        show_o2o_order(conn)
    elif plottype == 'class':
        show_class(conn)
    else:
        show_all(conn)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print "Usage: virualize.py [point|eb_order|o2o_order|all|class]"
        sys.exit(1)

    conn = sqlite3.connect('./Data/data.db')
    show(conn, sys.argv[1])
    conn.close()

# vim: set ts=4 sw=4 softtabstop=4
