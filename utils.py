#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math, re

R = 6378137
T = math.pi / 180

# point=>(lng, lat)
def distance(p1, p2):
    """
    p1: source point's (lng, lat)
    p2: target point's (lng, lat)
    return distance between these two points
    """
    d_lng = (p1[0] - p2[0]) / 2
    d_lat = (p1[1] - p2[1]) / 2
    return 2 * R * math.asin(math.sqrt((math.sin(T*d_lat))**2 \
        + math.cos(T*p1[1]) \
        * math.cos(T*p2[1]) \
        * (math.sin(T*d_lng))**2))

def order_by_distance(center, points):
    """
    center=>(id, lng, lat)
    points=>[(id1, lng1, lat1), (id2, lng2, lat2), ...]
    return ordered points(ascending order)
    """
    pass

# Minutes
def part_time(x):
    return int(round(3 * math.sqrt(x) + 5))

V = 15 * 1000 / 60 # meters per minutes
# Minutes
def travel_time(dis):
    return int(round(dis/V))

def travel_time_p(p1, p2):
    return travel_time(distance(p1, p2))

# e.g. '8:30' => 30, '18:30' => 630
def time2minutes(timestr):
    ret = re.split(':', timestr)
    return (int(ret[0]) - 8) * 60 + int(ret[1])

# latest delivery time of online orders
LAST = time2minutes('22:00')

if __name__ == "__main__":
    print "Test distance (121.511363, 31.273124) and (121.445216,31.120448): %f" \
            % distance((121.511363, 31.273124), (121.445216,31.120448))
    print "Test part_time 61:", part_time(61)
    print "Travel time:", travel_time(93849.3948)
    print "Time string to minutes: %d" % time2minutes('8:30')
    print "Time string to minutes: %d" % time2minutes('18:30')
    print "LAST:", LAST
    print "Travel time point:", travel_time_p((121.48203,31.26577),(121.489265,31.26754))

# vim: set sw=4 ts=4 softtabstop=4
