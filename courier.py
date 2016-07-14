#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Courier(object):
    def __init__(self, c_id):
        self._id = c_id
        self._orders = []
        self._audit = []
        # audit=>(c_id, addr_id, a_time, d_time, num, o_id)

    def __eq__(self, other):
        return self._id == other._id

    def __str__(self):
        return "<courier: %s>" % self._id

    def pickup_order(self):
        pass

    def delivery_order(self):
        pass

class CourierPool(object):
    def __init__(self, couriers):
        self._idle_couriers = couriers
        self._busy_couriers = []

    def get(self):
        courier = self._idle_couriers.pop()
        self._busy_couriers.append(courier)
        return courier

    def free(self, courier):
        self._busy_couriers.remove(courier)
        self._idle_couriers.append(courier)

if __name__ == '__main__':
    cs = []
    for i in xrange(10):
        cs.append(Courier(i))
    cp = CourierPool(cs)
    c = cp.get()
    print c
    c2 = cp.get()
    print c2
    cp.free(c)
    cp.free(c2)

# vim: set sw=4 ts=4 softtabstop=4
