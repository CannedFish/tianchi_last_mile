#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Courier(object):
    def __init__(self, c_id):
        self._id = c_id
        self._orders = [] # a 2d list
        self._audit = []
        self._busy = [] # (start, end)
        self._stay_at = (0, 0) # stay at where now
        # audit=>(c_id, addr_id, a_time, d_time, num, o_id)
        # TODO: How to express the couriers's state

    def __eq__(self, other):
        return self._id == other._id

    def __str__(self):
        return "<courier: %s>" % self._id

    def pickup_order(self, order):
        # add an order && modify assgin property of this order
        map(lambda x: x.assgin(), order)
        self._orders.append(order)
        # TODO: calc time used and modify stay position

    def delivery_order(self, start, end):
        # remove an order && recode the time used
        pass

    def isFree(self, time=0):
        """
        time is not in _busy
        """
        if time == 0:
            return True
        if time < 0: # or time > 840
            return False

        for t in self._busy:
            if time >= t[0] and time <= t[1]:
                return False
        return True

    # def _best_path(self, remain_orders):
        # pass

    # def next(self):
        # """
        # return next order to delivery
        # """
        # pass

class CourierPool(object):
    def __init__(self, couriers):
        self._couriers = couriers

    def get(self, time=0):
        for courier in self._couriers:
            if courier.isFree(time):
                return courier
        return False

    def add(self, courier):
        if courier in self._couriers:
            return
        return self._couriers.append(courier)

TOTAL = 1000
# TOTAL_COURIERS = [Courier('D%04d'%i) for i in xrange(TOTAL)]

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
