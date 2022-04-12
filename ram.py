from register import StdRegister as StdRegister


class RAM(StdRegister):

    def __init__(self,cpu,latch,enable,FirstRAM = []):
        super().__init__(cpu,latch,enable)
        self.value = [0xF]*(2**cpu.addrlen) # default to HLT instruction
        self.set(FirstRAM)

    def set(self,newram):
        if len(newram) > 0:
            print("Loading RAM: {}".format(newram))
            self.value = []
            for v in newram:
                self.value.append(v)
                
    def tick(self):
        if self.enable.istrue():
            self.cpu.w = self.value[self.cpu.mar.value] & self.mask

    def tock(self):
        if self.latch.istrue():
            self.value[self.cpu.mar.value] = self.cpu.w & self.mask
            #print("RAM updated: {}".format(self.value))
