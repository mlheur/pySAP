from register import StdRegister as StdRegister


class RAM(StdRegister):
    def __init__(self,cpu,latch,enable,FirstRAM = []):
        super().__init__(cpu,latch,enable)
        self.value = [0xF]*(2**cpu.addrlen) # default to HLT instruction
        if len(FirstRAM) > 0:
            print("Loading RAM: {}".format(FirstRAM))
            for i,v in enumerate(FirstRAM):
                self.value[i] = v
    def tick(self):
        if self.enable.istrue():
            self.cpu.w = self.value[self.cpu.mar.value] & self.mask
    def tock(self):
        if self.latch.istrue():
            self.value[self.cpu.mar.value] = self.cpu.w & self.mask
            #print("RAM updated: {}".format(self.value))


