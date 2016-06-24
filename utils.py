#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

R = 6378137
T = math.pi / 180

def distance(p1, p2):
    d_lat = (p1[0] - p2[0]) / 2
    d_lng = (p1[1] - p2[1]) / 2
    return 2 * R * math.asin((math.sin(T*d_lat))**2 \
        + math.cos(T*p1[0]) \
        * math.cos(T*p2[0]) \
        * (math.sin(T*d_lng))**2)

# vim: set sw=4 ts=4 softtabstop=4
