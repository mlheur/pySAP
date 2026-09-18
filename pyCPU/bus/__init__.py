from random import randint
from pyCPU import ControlLine


class Bus(object):

    def __init__(self,width:int):
        self.mask  = (2**width) - 1
        self.value = randint(0,self.mask)

    def read(self):
        return self.value & self.mask

    def write(self,value):
        self.value = value & self.mask


class BusConnection(object):

    def __init__(
            self,
            bus    : Bus,
            latch  : ControlLine,
            enable : ControlLine,
        ):
        self.bus    = bus
        self.action = {}
        if latch is not None:
            self.action['latch'] = lambda : latch.isTrue()
        if enable is not None:
            self.action['enable'] = lambda : enable.isTrue()

