from register import StdRegister as StdRegister


class ALU(StdRegister):
    def __init__(self,cpu,A,B,enable,sub):
        super().__init__(cpu,enable=enable)
        self.A   = A
        self.B   = B
        self.sub = self.cpu.oflags[sub]
        self.update()
    def update(self):
        if self.sub.istrue():
            self.value = ((self.A.value & self.mask) - (self.B.value & self.mask))
        else:
            self.value = ((self.A.value & self.mask) + (self.B.value & self.mask))
    def tick(self):
        self.update()
        if self.enable.istrue():
            if self.sub.istrue():
                self.cpu.iflags['CARRY'].settruth(self.B.value > self.A.value)
            else:
                self.cpu.iflags['CARRY'].settruth(self.value > self.mask)
            self.cpu.iflags['ZERO'].settruth(self.value == 0)
            self.cpu.w = self.value
    def tock(self):
        self.update()


