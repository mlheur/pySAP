from register import StdRegister


class ALU(StdRegister):
    def __init__(self,cpu,A,B,enable,sub,shift,carry):
        super().__init__(cpu,enable=enable)
        self.A     = A
        self.B     = B
        self.sub   = self.cpu.oflags[sub]
        self.shift = self.cpu.oflags[shift]
        self.carry = self.cpu.iflags[carry]
        self.update()
    def update(self):
        if self.shift.istrue():
            if self.sub.istrue():
                self.value = ((self.A.value<<1) & self.mask) + (0x01 if self.carry.istrue() else 0)
            else:
                self.value = ((self.A.value>>1) & self.mask) + (0x80 if self.carry.istrue() else 0)
        elif self.sub.istrue():
            self.value = ((self.A.value & self.mask) - (self.B.value & self.mask)) & self.mask
        else:
            self.value = ((self.A.value & self.mask) + (self.B.value & self.mask)) & self.mask
    def tick(self):
        self.update()
        if self.enable.istrue():
            if self.shift.istrue():
                if self.sub.istrue():
                    self.cpu.iflags['CF'].settruth(self.A.value & 0x80 == 0x80)
                else:
                    self.cpu.iflags['CF'].settruth(self.A.value & 0x01 == 0x01)
            elif self.sub.istrue():
                self.cpu.iflags['CF'].settruth((self.B.value & self.mask) > (self.A.value & self.mask))
            else:
                self.cpu.iflags['CF'].settruth(((self.A.value & self.mask) + (self.B.value & self.mask)) > self.mask)
            #print("setting ZF truth to {} on value {}".format(self.value == 0, self.value))
            self.cpu.iflags['ZF'].settruth(self.value == 0)
            self.cpu.w = self.value
    def tock(self):
        if self.shift.istrue():
            self.A.value = self.value & self.mask


