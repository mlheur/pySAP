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
    def __init__(self,cpu,bits,clock,latch_lo,latch_hi,enable_lo,enable_hi):
        super().__init__(cpu,bits,latch_lo,enable_lo)
        self.cpu_mask   = (2**cpu.bits)-1
        self.latch_hi   = self.cpu.oflags[latch_hi]
        self.enable_hi  = self.cpu.oflags[enable_hi]
        self.increment  = self.cpu.oflags[clock]

    def get_truth(self):
        tt = dict()
        tt['clock'] = self.increment.istrue()
        tt['en_hi'] = self.enable_hi.istrue()
        tt['en_lo'] = self.enable.istrue()
        tt['la_hi'] = self.latch_hi.istrue()
        tt['la_lo'] = self.latch.istrue()
        return tt

    def tick(self):
        if self.cpu.oflags['CLR'].istrue():
            self.value = 0
        tt = self.get_truth()
        if tt['en_lo'] and tt['en_hi']:
            self.cpu.w = self.value & self.mask
        elif tt['en_lo']:
            self.cpu.w = self.value & self.cpu_mask
        elif tt['en_hi']:
            self.cpu.w = (self.value>>self.cpu.bits) & self.cpu_mask

    def tock(self):
        tt = self.get_truth()
        if tt['clock']:
            self.value += 1
            self.value %= self.mask
        elif tt['la_lo'] and tt['la_hi']:
            self.value = self.cpu.w & self.mask
        elif tt['la_lo']:
            hi = (self.value >> self.cpu.bits) & self.cpu_mask
            lo = self.cpu.w & self.cpu_mask
            self.value = ((hi<<self.cpu.bits) + (lo)) & self.mask
        elif tt['la_hi']:
            hi = self.cpu.w & self.cpu_mask
            lo = self.value & self.cpu_mask
            self.value = ((hi<<self.cpu.bits) + (lo)) & self.mask
