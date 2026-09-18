from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyCPU import CPU, BusConnection

from random import randint


class Register(object):

    def __init__(
            self,
            cpu        : "CPU",
        ):
        self.cpu         = cpu
        self.connections = {}
        self.value       = randint(0,self.cpu.mask)

    def _actionIsTrue(self,conn,action:str):
        return conn.action[action] is not None and conn.action[action].isTrue()

    def tick(self):
        for conn in self.connections:
            if self._actionIsTrue(conn,'enable'):
                conn.bus.write(self.value & self.cpu.mask)

    def tock(self):
        for conn in self.connections:
            if self._actionIsTrue(conn,'latch'):
                self.value = conn.bus.read() & self.cpu.mask

    def addBusConnection(
            self,
            bus_name   : str,
            connection : "BusConnection",
        ):
        self.connections[bus_name] = connection

    def __str__(self):
        return f'0x0{self.value:{self.cpu.bits}X}'