#!/usr/bin/env python
# -*- coding: utf-8 -*-

TOTAL = 1000

class Courier(object):
    def __init__(self, c_id):
        self._id = c_id
        self._orders = []
        self._audit = []
        self._work_util = 0
        # audit=>(c_id, addr_id, a_time, d_time, num, o_id)

    def __eq__(self, other):
        return self._id == other._id

    def __str__(self):
        return "<courier: %s>" % self._id

    def pickup_order(self):
        pass

    def delivery_order(self):
        pass

    def isFree(self, time):
        """
        free=>time >= _work_util
        busy=>time < _work_util
        """
        return time >= self._work_util

    def _best_path(self):
        pass

    def next(self):
        """
        return next order to delivery
        """
        pass

class CourierPool(object):
    def __init__(self, couriers):
        self._couriers = couriers

    def get(self, time):
        for courier in self._couriers:
            if courier.isFree(time):
                return courier
        return False

    def add(self, courier):
        if courier in self._couriers:
            return
        return self._couriers.append(courier)

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
