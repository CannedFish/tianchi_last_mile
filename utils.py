#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math, re

R = 6378137
T = math.pi / 180

def distance(p1, p2):
    d_lat = (p1[0] - p2[0]) / 2
    d_lng = (p1[1] - p2[1]) / 2
    return 2 * R * math.asin(math.sqrt((math.sin(T*d_lat))**2 \
        + math.cos(T*p1[0]) \
        * math.cos(T*p2[0]) \
        * (math.sin(T*d_lng))**2))

def part_time(x):
    return 3 * math.sqrt(x) + 5

V = 15 * 1000 / 60 # meters per minutes
def travel_time(dis):
    return round(dis/V)

# e.g. '8:30' => 30, '18:30' => 630
def time2minutes(timestr):
    ret = re.split(':', timestr)
    return (int(ret[0]) - 8) * 60 + int(ret[1])

if __name__ == "__main__":
    print "Test distance (121.511363, 31.273124) and (121.445216,31.120448): %f" \
            % distance((121.511363, 31.273124), (121.445216,31.120448))
    print "Test part_time 9: %f" % part_time(9)
    print "Travel time: %d" % travel_time(93849.3948)
    print "Time string to minutes: %d" % time2minutes('8:30')
    print "Time string to minutes: %d" % time2minutes('18:30')

# vim: set sw=4 ts=4 softtabstop=4
