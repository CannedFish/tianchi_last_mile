#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

import utils

def _valid_site_spot(conn):
    cu = conn.cursor()
    for spot in cu.execute("select spot_id from spot"):
        cu2 = conn.cursor()
        cu2.execute("select site_id from eb_order where spot_id=='%s'" % spot)
        sites = cu2.fetchall()
        if len(sites) > 1:
            print "%s: %s" % (spot[0], sites)
    print "Done"

def _valid_dis_time_o2o(conn):
    cu = conn.cursor()
    for order_id, time_spent \
        in cu.execute("select order_id, time_spent \
        from o2o_order"):
        if time_spent > 90:
            print "%3d minutes need, not enough: %s!!" % (time_spent, order_id)
    print "Done"

def valid(conn, todo):
    if todo == 'site_spot':
        _valid_site_spot(conn)
    elif todo == 'o2o_dis_time':
        _valid_dis_time_o2o(conn)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print "Usage: some_valid.py [site_spot|o2o_dis_time]"
        sys.exit(1)

    conn = sqlite3.connect("./Data/data.db")
    valid(conn, sys.argv[1])
    conn.close()

# vim: set sw=4 ts=4 softtabstop=4
