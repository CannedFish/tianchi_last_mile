#!/usr/bin/env python
# -*- coding: utf-8 -*-

# eb + o2o
TOTAL_ORDER = 12487

class Order(object):
    def __init__(self, order):
        """
        order = (id, ...)
        """
        self._order = order
        self._id = order[0]
        self._assign = False

    def __eq__(self, other):
        return self._id == other._id

    def assgin(self):
        self._assign = True

    def unassgin(self):
        self._assign = False

    def isAssgined(self):
        return self._assign

    def num(self):
        return self._package_num

    def target(self):
        """
        return (lng, lat) of the target
        """
        return self._target

class EBOrder(Order):
    def __init__(self, order):
        super(EBOrder, self).__init__(order)
        self._spot = order[1]
        self._package_num = order[2]
        self._target = (order[3], order[4])

    # TODO: some methods

class O2OOrder(Order):
    def __init__(self, order):
        super(O2OOrder, self).__init__(order)
        self._spot = order[1]
        self._shop = order[2]
        self._pickup_time = order[3]
        self._delivery_time = order[4]
        self._package_num = order[5]
        self._time_spent = order[6]
        self._shop_addr = order[7]
        self._target = order[8]

    # TODO: some methods
    def shop(self):
        return self._shop_addr()

class Orders(object):
    def __init__(self, orders):
        self._orders = orders

    def __len__(self):
        return len(self._orders)

    def assgined(self):
        return filter(lambda x: x.isAssgined(), self._orders)

    def remain(self):
        return filter(lambda x: not x.isAssgined(), self._orders)

