


class Register():
    def __init__(self,cpu,bits,latch=None,enable=None):
        self.cpu        = cpu
        self.mask       = (2**bits) - 1      # ToDo: validate host architecture is more than bits.
        self.value      = 0
        if latch is not None and latch in self.cpu.oflags:
            self.latch  = self.cpu.oflags[latch]
        else:
            self.latch = None
        if enable is not None and enable in self.cpu.oflags:
            self.enable = self.cpu.oflags[enable]
        else:
            self.enable = None
    def tick(self):
        if self.cpu.oflags['CLR'].istrue():
            self.value  = 0
        if self.enable is not None and self.enable.istrue():
            self.cpu.w  = self.value & self.mask
    def tock(self):
        if self.latch is not None and self.latch.istrue():
            self.value  = self.cpu.w & self.mask


class StdRegister(Register):
    def __init__(self,cpu,latch=None,enable=None):
        super().__init__(cpu,cpu.bits,latch,enable)


class OUT(StdRegister):
    def tock(self):
        super().tock()
        if self.latch.istrue():
            print("OUT: {v:02X} {v:03d} {v:08b}".format(v=self.value))


class PC(Register):
    def tock(self):
        if self.latch.istrue():
            if self.enable.istrue(): self.value = self.cpu.w & self.mask
            else: self.value = (self.value + 1) & self.mask


class IR(StdRegister):
    def tick(self):
        if self.cpu.oflags['CLR'].istrue(): self.value = 0
        if self.enable.istrue(): self.cpu.w = self.value & 0xF


