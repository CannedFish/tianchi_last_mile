#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utils

class Action(object):
    def __init__(self, s_point, e_point, s_time, e_time, orders):
        self._s_point = s_point
        self._e_point = e_point
        self._s_time = s_time
        self._e_time = e_time
        self._orders = orders
        self._calc_travel_time()

    def __lt__(self, other):
        return self._e_time <= other._s_time

    def __str__(self):
        return "%s, %s, %s, %s, %d" % (self._s_point, self._e_point, \
                self._s_time, self._e_time, len(self._orders))
    
    def __repr__(self):
        arr = self._courier.recent_arrival()
        fmt = "%s,%s,%s,%s,%d,%s"
        s_point = self.start_point()
        s1 = [fmt % (self._courier._id, s_point, arr, self._s_time, o.num(), o._id) \
                for o in self._orders[:-1]]
        # TODO: calc a ERROR!!
        s2 = map(lambda o,a: fmt % \
                (self._courier._id, o._spot_id, a, a+o.part_time(), -o.num(), o._id), \
                self._orders[:-1], self._t_time)
        s1.extend(s2)
        return "\n".join(s1)

    def _calc_travel_time(self):
        self._t_time = map(lambda x,y: utils.travel_time_p(x.target(), y.target()),\
                self._orders[:-2], self._orders[1:-1])
        self._t_time.insert(0, utils.travel_time_p(self._orders[0].src_addr(),\
                self._orders[0].target()))

    def package(self):
        return reduce(lambda x,y: x+y, [o.num() for o in self._orders])

    def set_courier(self, courier):
        self._courier = courier

    def start_point(self):
        return self._orders[0].src_id()

class Courier(object):
    def __init__(self, c_id):
        self._id = c_id
        # audit=>(c_id, addr_id, a_time, d_time, num, o_id)
        # Use action as the expression of the couriers's state
        self._actions = []
        self._free_time = [0, 840]
        self._last_interval = (0, (0, 840))

    def __eq__(self, other):
        return self._id == other._id

    def __str__(self):
        return "<courier: %s>\n%s" % (self._id, \
                "\n".join([str(a) for a in self._actions]))

    def __repr__(self):
        self._arrival = 0
        path = ""
        for action in self._actions:
            path += "%r\n" % action
            self._arrival = action._e_time
        return path

    def assgin(self, action):
        """
        A seriel of eb_orders
        """
        # print "<%s>courier.assgin: %s, %d" % (self._id, action, action.package())
        for order in action._orders:
            order.assgin()
            # print order._type
        action.set_courier(self)
        self._actions.append(action)
        self._actions.sort()
        self._free_time.extend([action._s_time, action._e_time])
        self._free_time.sort()

    # def extend_o2o_action(self, o2o_action, orders):
        # """
        # Try extend an o2o order action with eb orders
        # """
        # pass

    def recent_arrival(self):
        """
        Return the recent arrival time
        for tracing actions
        """
        return self._arrival

    def free_time(self):
        """
        return the interval of free time
        More than 10 minutes are treated as free
        """
        return filter(lambda x: x[1]!=x[0], \
                map(lambda x,y: (x,y), self._free_time[:-1:2], self._free_time[1::2]))
        
    def get_interval(self):
        """
        return the approprate interval
        Intervals between o2o orders are high priority from last to first
        """
        f_times = self.free_time()
        if len(f_times) == 0:
            return None
        f_times.reverse()
        if f_times[0][1] == 840:
            f_times.append(f_times.pop(0))
        # to avoid dead loop
        idx = (self._last_interval[0]+1) % len(f_times) \
                if f_times[self._last_interval[0]] == self._last_interval[1] \
                else self._last_interval[0]
        self._last_interval = (idx, f_times[idx])
        return f_times[self._last_interval[0]] 

    def two_actions(self, end, start):
        """
        end: end time of first action
        start: start time of second action
        return two actions
        """
        candidate = filter(lambda x: x._e_time==end or x._s_time==start, self._actions)
        if len(candidate) == 2:
            candidate.sort()
            return (candidate[0], candidate[1])
        elif len(candidate) == 1:
            if candidate[0]._e_time == end:
                return (candidate[0], None)
            else:
                return (None, candidate[0])
        else:
            return (None, None)

    def first_action(self):
        return self._actions[0] if len(self._actions)!=0 else None

    def isFree(self, s_time=0, e_time=0):
        """
        time is not in _busy
        """
        if s_time < 0: # or e_time > 840
            return False

        for start, end in self.free_time():
            if s_time == 0 and e_time == 0: 
                return True
            if s_time >= start and e_time <= end:
                return True
        return False

class CourierPool(object):
    def __init__(self, couriers):
        self._couriers = couriers
        self._total = len(couriers)
        self._idx = 0

    def __str__(self):
        return "\n".join([str(c) for c in self._couriers])

    def __repr__(self):
        return "\n".join([repr(c) for c in self._couriers])

    def get(self, s_time=0, e_time=0):
        """
        Every time start from next courier
        """
        i = self._idx
        self._idx = (self._idx+1)%self._total
        while True:
            if self._couriers[i].isFree(s_time, e_time):
                return self._couriers[i]
            i = (i+1)%self._total
            if i == (self._idx-1)%self._total:
                return False

    def add(self, courier):
        if courier in self._couriers:
            return
        self._total += 1
        return self._couriers.append(courier)

    def size(self):
        return self._total

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
