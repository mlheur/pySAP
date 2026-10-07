from pySocket import pySocket
from pyRegister import pyRegister

class pyCPU(object):

    def __init__(
            self,
            bits   : int,
            socket : pySocket = None,
        ):
        self.bits      : int        = bits
        self.mask      : int        = (2**self.bits)-1
        self.registers : pyRegister = {}
        self.socket    : pySocket   = socket

    def tick(self):
        for register in self.registers.values():
            register.tick()

    def tock(self):
        for register in self.registers.values():
            register.tock()

    def __str__(self):
        return f'CPU(bits={self.bits},mask=0x{self.mask:X},registers={self.registers},busses={self.busses})'
