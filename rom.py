from ctl import CtlLine as CtlLine


class ROM(object):
    NOP = 0
    def mkctl(self,flags=[]):
        word = self.NOP
        for f in flags:
            if f not in self.oflags:
                print("unknown control flag: [{}]".format(f))
                continue
            if self.oflags[f].inv == 1:
                word &= ~self.oflags[f].mask
            else:
                word |= self.oflags[f].mask
        return word
    def addinstr(self,instr,micro):
        if type(micro) is list:
            for condition,value in enumerate(micro):
                if not condition in self.addr:
                    self.addr[condition] = dict()
                self.addr[condition][self.ASM[instr]] = value
        elif type(micro) is int:
            for condition in range(2**len(self.iflags)):
                if not condition in self.addr:
                    self.addr[condition] = dict()
                self.addr[condition][self.ASM[instr]] = micro
    def assemble(self,instr,data=0xF):
        if instr in self.ASM:
            return (self.ASM[instr] << 4) | data
