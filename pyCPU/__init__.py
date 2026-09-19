from .control_line import ControlLine
from .bus import Bus, BusConnection, BusUser
from .register import Register


class CPU(object):

    def __init__(
            self,
            bits : int,
        ):
        self.bits      = bits
        self.mask      = (2**self.bits)-1
        self.registers = {}
        self.busses    = {}

    def createBus(
            self,
            bus_name  : str,
            bus_width : int = None
        ):
        if bus_width is None:
            bus_width = self.bits
        self.busses[bus_name] = Bus(bus_width)

    def createRegister(
            self,
            register_name : str,
            bus_name      : str,
        ):
        if bus_name not in self.busses:
            raise ValueError(f'bus_name={bus_name} not in self.busses')
        reg = Register(self)
        reg.addBusConnection(
            bus_name,
            BusConnection(
                self.busses[bus_name],
                ControlLine(inverted=True),
                ControlLine(inverted=False),
            )
        )
        self.registers[register_name] = reg
         
    def tick(self):
        for register in self.registers:
            register.tick()

    def tock(self):
        for register in self.registers:
            register.tock()

    def __str__(self):
        return f'CPU(bits={self.bits},mask=0x{self.mask:X},registers={self.registers},busses={self.busses})'
