from random import randint
from threading import Thread

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
    def __init__(self,cpu,latch=None,enable=None):
        super().__init__(cpu,latch,enable)
        self.nROWS = 0
        self.thread = Thread(target=self.print)

    def print(self):
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
        self.thread = Thread(target=self.print)

    def tock(self):
        super().tock()
        if self.latch.istrue():
            try:
                self.thread.start()
            except:
                pass


class DoubleRegister(Register):
    def __init__(self,cpu,bits,latch,enable,latch_hi):
        super().__init__(cpu,bits,latch,enable)
        self.cpu_mask   = (2**cpu.bits)-1
        self.latch_hi   = self.cpu.oflags[latch_hi]


class MAR(DoubleRegister):
    def __init__(self,cpu,bits,latch,latch_hi):
        super().__init__(cpu,bits,latch,None,latch_hi)

    def tock(self):
        if self.latch_hi.istrue():
            lo = self.value & self.cpu_mask
            hi = self.cpu.w & self.cpu_mask
            self.value = (hi<<self.cpu.bits)&lo
        else:
            super().tock()


class PC(DoubleRegister):

    def __init__(self,cpu,bits,latch,enable,latch_hi):
        super().__init__(cpu,bits,latch,enable,latch_hi)

    def tock(self):
        if self.latch_hi.istrue():
            lo = self.value & self.cpu_mask
            hi = self.cpu.w & self.cpu_mask
            self.value = (hi<<self.cpu.bits)&lo
        elif self.latch.istrue():
            if self.enable.istrue():
                self.value = self.cpu.w & self.mask
            else:
                self.value = (self.value + 1) & self.mask
