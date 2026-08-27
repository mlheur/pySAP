from register import StdRegister
from random import randint


class RAM(StdRegister):

    def __init__(self,cpu,latch,enable):
        super().__init__(cpu,latch,enable)
        self.value = []
        for addr in range(2**cpu.bits):
            self.value.append(randint(0,0x100))
            #self.value.append(addr)

    def set(self,newram):
        if newram is None or len(newram) == 0:
            return
        for i,v in enumerate(newram):
            self.value[i] = v

    def tick(self):
        if self.enable.istrue():
            self.cpu.w = self.value[self.cpu.mar.value] & self.mask

    def tock(self):
        if self.latch.istrue():
            self.value[self.cpu.mar.value] = self.cpu.w & self.mask
            #print("RAM updated: {}".format(self.value))
