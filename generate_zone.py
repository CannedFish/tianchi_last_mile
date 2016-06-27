#!/usr/bin/env python
# -*- coding: utf-8 -*-

def do_mark_spots(conn):
    cu = conn.cursor()
    cu.execute("select site_id, spot_id from eb_order")
    pairs = cu.fetchall()
    cu.executemany("update spot set zone=? where spot_id=?", pairs)
    conn.commit()

def do_classify_shops(conn):
    pass

def do_generate(conn):
    do_mark_spots(conn)
    do_classify_shops(conn)

if __name__ == '__main__':
    import sqlite3

    conn = sqlite3.connect('./Data/data.db')
    do_generate(conn)
    conn.close()

# vim: set sw=4 ts=4 softtabstop=4
