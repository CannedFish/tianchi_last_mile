#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utils
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

    def type(self):
        return self._type

    def part_time(self):
        return utils.part_time(self.num())

    def src_id(self):
        return self._id

    def src_addr(self):
        return self._target

class EBOrder(Order):
    def __init__(self, order, site):
        super(EBOrder, self).__init__(order)
        self._type = 'eb'
        self._site_id = site[0]
        self._site_addr = site[1]
        self._spot_id = order[1]
        self._package_num = order[2]
        self._target = (order[3], order[4])

    def __str__(self):
        return "<\nID: %s\nSpot: %s\nPackage: %s\n>" \
                % (self._id, self._target, self._package_num)

    def src_id(self):
        return self._site_id

    def src_addr(self):
        return self._site_addr

class O2OOrder(Order):
    def __init__(self, order):
        super(O2OOrder, self).__init__(order)
        self._type = 'o2o'
        self._spot_id = order[1]
        self._shop_id = order[2]
        self._pickup_time = order[3]
        self._delivery_time = order[4]
        self._package_num = order[5]
        self._time_spent = order[6]
        self._shop_addr = order[7]
        self._target = order[8]

    def __str__(self):
        return "<\nID: %s\nShop: %s\nSpot: %s\nPickup: %s\nDelivery: %s\nPackage: %s\n>" \
                % (self._id, self._shop_addr, self._target, \
                self._pickup_time, self._delivery_time, self._package_num)

    def src_id(self):
        return self._shop_id

    def src_addr(self):
        return self._shop_addr

    def shop(self):
        return self._shop_addr

class PickupOrder(Order):
    def __init__(self, order):
        super(PickupOrder, self).__init__(order)
        self._type = 'pickup'
        self._target = order[1]
        self._target_type = order[2] # site | shop
        self._package_num = 0

    def __str__(self):
        return "<PickupOrder>Target:%s,TargetType:%s." % (self._target, self._target_type)

class Orders(object):
    def __init__(self, orders):
        self._orders = orders

    def __len__(self):
        return len(self._orders)

    def __str__(self):
        return "\n".join([str(order) for order in self._orders])

    def assgined(self):
        return filter(lambda x: x.isAssgined(), self._orders)

    def remain(self):
        return filter(lambda x: not x.isAssgined(), self._orders)

