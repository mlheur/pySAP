from random import randint


class Register():

    def __init__(self,cpu,bits,clr,latch=None,enable=None):
        self.cpu        = cpu
        self.bits       = bits
        if clr is not None:
            self.clr    = cpu.control_lines[clr]
        self.mask       = (2**bits) - 1      # ToDo: validate host architecture is more than bits.
        self.value      = randint(0,1+2**bits)
        if latch is not None and latch in self.cpu.control_lines:
            self.latch  = self.cpu.control_lines[latch]
        else:
            self.latch = None
        if enable is not None and enable in self.cpu.control_lines:
            self.enable = self.cpu.control_lines[enable]
        else:
            self.enable = None

    def tick(self):
        if self.clr is not None and self.clr.istrue():
            self.value  = 0
        if self.enable is not None and self.enable.istrue():
            self.cpu.w  = self.value & self.mask

    def tock(self):
        if self.latch is not None and self.latch.istrue():
            self.value  = self.cpu.w & self.mask


class StdRegister(Register):
    def __init__(self,cpu,clr,latch=None,enable=None):
        super().__init__(cpu,cpu.bits,clr,latch,enable)

