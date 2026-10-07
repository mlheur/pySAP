from random import randint
from pySocket.control_line import ControlLine

class pyRegister(object):

    def __init__(
            self,
            bits : int,
            ce   : ControlLine,
            cs   : ControlLine,
        ):
        self.bits  : int         = bits
        self.mask  : int         = 2**self.bits
        self.value : int         = randint(0,self.mask)
        self.ce    : ControlLine = ce
        self.cs    : ControlLine = cs
