#!/usr/bin/env python
# -*- coding: utf8 -*-

from generate_zone import Zone, TOTAL_ZONE
from courier import Courier, TOTAL

def __info(step, info):
    print '[STEP] %s: %s' % (step, info)

def initial_courier_pool(zones, couriers):
    start = 0
    orders = 0
    for zone in zones:
        courier = zone.initial_courier_pool(couriers, start)
        print '%s: %d' % (zone._zone, courier)
        start += courier
        # orders += zone.get_order_num()
        print 'Total orders: %d' % zone.get_order_num()

def plan(zones):
    pass

def result(couriers):
    """
    Write results to database
    """
    pass

if __name__ == '__main__':
    import sqlite3

    conn = sqlite3.connect('./Data/data.db')
    
    __info('initial_zones', 'begin')
    couriers = [Courier('D%04d'%i) for i in xrange(1, TOTAL + 1)]
    zones = [Zone(conn, 'A%03d'%i) for i in xrange(1, TOTAL_ZONE + 1)]
    initial_courier_pool(zones, couriers)
    __info('initial_zones', 'done')

    __info('plan', 'begin')
    plan(zones)
    __info('plan', 'done')

    __info('result', 'begin')
    result(couriers)
    __info('result', 'done')
    
    conn.close()

