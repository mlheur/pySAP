from register import StdRegister
from random import randint


class RAM(StdRegister):

    def __init__(self,cpu,latch,enable,FirstRAM):
        super().__init__(cpu,latch,enable)
        self.value = []
        for addr in range(0,1+2**cpu.bits):
            self.value.append(randint(0,0x100))
        self.set(FirstRAM)

    def set(self,newram):
        if newram is not None and len(newram) > 0:
            for i,v in enumerate(newram):
                self.value[i] = v

    def tick(self):
        if self.enable.istrue():
            self.cpu.w = self.value[self.cpu.mar.value] & self.mask

    def tock(self):
        if self.latch.istrue():
            self.value[self.cpu.mar.value] = self.cpu.w & self.mask
            #print("RAM updated: {}".format(self.value))
