#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import matplotlib.pyplot as plt

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
    plt.plot(sites[0], sites[1], 'ro', spots[0], spots[1], 'bs', shops[0], shops[1], 'g^')
    plt.show()

def show_es_order(conn):
    pass

def show_o2o_order(conn):
    pass

def show_all(conn):
    pass

def show(conn, plottype):
    if plottype == 'point':
        show_point(conn)
    elif plottype == 'es_order':
        show_es_order(conn)
    elif plottype == 'o2o_order':
        show_o2o_order(conn)
    else:
        show_all(conn)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print "Usage: virualize.py [point|es_order|o2o_order|all]"
        sys.exit(1)

    conn = sqlite3.connect('./Data/data.db')
    show(conn, sys.argv[1])
    conn.close()

# vim: set ts=4 sw=4 softtabstop=4
