class CtlLine():
    def __init__(self,pos,value=0,inv=0):
        self.pos        = pos
        self.mask       = 1 << self.pos
        self.value      = value
        self.inv        = inv
    def update(self,word):
        self.value      = (word & self.mask) >> self.pos
        #print("CtlLine.update({:016b}); mask={self.mask:016b} value={self.value} inv={self.inv} truth={t}".format(word,self=self,t=self.istrue()))
    def settruth(self,truth):
        if self.inv == 0: self.value = int(truth)
        else: self.value = int(not truth)
    def istrue(self):
        return not self.value == self.inv


class CtlSeq():
    def __init__(self,cpu,arom,crom,Tlimit=5):
        self.cpu     = cpu
        self.AROM    = arom
        self.CROM    = crom
        self.Tstep   = 1
        self.micro   = self.CROM[0]
        self.Tlimit  = Tlimit
    def __str__(self):
        return '{}'.format(self.Tstep)
    def iflags(self):
        result = 0
        for f in self.cpu.iflags:
            result |= ((self.cpu.iflags[f].mask & (self.cpu.iflags[f].value) << self.cpu.iflags[f].pos))
        return result
    def decode(self):
        if self.cpu.oflags['CLR'].istrue():
            self.micro = self.CROM[0] & ~(self.cpu.oflags['CLR'].mask)
        else:
            if self.Tstep <= 0x2:
                self.micro = self.CROM[self.Tstep]
            else:
                instr = (self.cpu.ir.value & 0xF0) >> self.cpu.addrlen
                self.micro = self.CROM[self.AROM[self.iflags()][instr]+(self.Tstep-3)]
        for F in self.cpu.oflags:
            self.cpu.oflags[F].update(self.micro)
    def clock(self):
        # Parse the subinstruction
        self.decode()
        #print("T:{} MICRO: Bin={v:016b} Hex={v:04X} Dec={v:05d}".format(self.Tstep,v=self.micro))
        #print("{}".format(self.cpu))
        if self.cpu.oflags['HLT'].istrue():
            return
        # enable to bus
        for component in self.cpu.components:
            component.tick()
        # latch from bus
        for component in self.cpu.components:
            component.tock()
        # Increment the RingCounter
        if self.cpu.oflags['CLR'].istrue():
            self.cpu.oflags['CLR'].settruth(False)
            self.Tstep = 1
        elif self.micro == self.CROM[0]:
            self.Tstep = 1
        else:
            self.Tstep += 1
            if self.Tstep > self.Tlimit:
                self.Tstep = 1

