#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

R = 6378137
T = math.pi / 180

def distance(p1, p2):
    d_lat = (p1[0] - p2[0]) / 2
    d_lng = (p1[1] - p2[1]) / 2
    return 2 * R * math.asin(math.sqrt((math.sin(T*d_lat))**2 \
        + math.cos(T*p1[0]) \
        * math.cos(T*p2[0]) \
        * (math.sin(T*d_lng))**2))

def dur_time(x):
    return 3 * math.sqrt(x) + 5

if __name__ == "__main__":
    print "Test distance (121.511363, 31.273124) and (121.445216,31.120448): %f" \
            % distance((121.511363, 31.273124), (121.445216,31.120448))
    print "Test dur_time 9: %f" % dur_time(9)

# vim: set sw=4 ts=4 softtabstop=4
