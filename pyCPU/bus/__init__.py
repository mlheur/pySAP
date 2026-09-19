from random import randint
from pyCPU import ControlLine


class Bus(object):

    def __init__(self,width:int):
        self.bits  = width
        self.mask  = (2**self.bits) - 1
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
            self.action['latch'] = lambda : latch.isTrue
        if enable is not None:
            self.action['enable'] = lambda : enable.isTrue

    def getWidth(self):
        return self.bus.bits

    def actionIsTrue(self,action:str):
        return self.action[action] is not None and self.action[action]()

    def busRead(self):
        return self.bus.read()

    def busWrite(self):
        return self.bus.write()


class BusUser(object):

    def __init__(self):
        self.connections = {}

    def tick(self):
        for conn in self.connections:
            if conn.actionIsTrue(conn,'enable'):
                conn.busWrite(self.value & self.cpu.mask)

    def tock(self):
        for conn in self.connections:
            if conn.actionIsTrue(conn,'latch'):
                self.value = conn.busRead() & self.cpu.mask

    def addBusConnection(
            self,
            bus_name   : str,
            connection : "BusConnection",
        ):
        self.connections[bus_name] = connection

