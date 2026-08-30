from random import randint

class Register():
    def __init__(self,cpu,bits,latch=None,enable=None):
        self.cpu        = cpu
        self.bits       = bits
        self.mask       = (2**bits) - 1      # ToDo: validate host architecture is more than bits.
        self.value      = randint(0,1+2**bits)
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
    nROWS = 0
    def tock(self):
        super().tock()
        if self.latch.istrue():
            if self.nROWS % 25 == 0:
                print(f'')
                print(f'SEQ |    BINARY |  HEX | DEC')
                print(f'===   =========   ====   ===')
                print(f'')
            vBIN = f'{self.value:08b}'
            vBIN = f'{vBIN[0:4]} {vBIN[3:7]}'
            vHEX = f'0x{self.value:02X}'
            vDEC = f'{self.value:03d}'
            vSEQ = f'{self.nROWS:03d}'
            print(f'{vSEQ}   {vBIN}   {vHEX}   {vDEC}')
            self.nROWS += 1


class PC(Register):
    def tock(self):
        if self.latch.istrue():
            if self.enable.istrue(): self.value = self.cpu.w & self.mask
            else: self.value = (self.value + 1) & self.mask


class IR(StdRegister):
    def tick(self):
        if self.cpu.oflags['CLR'].istrue(): self.value = 0
        if self.enable.istrue(): self.cpu.w = ( self.value & self.mask )
