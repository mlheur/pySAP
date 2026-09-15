from logger import LOGGER, TRACE, INFO


class CtlLine():
    POS_COUNTER = 0
    def __init__(self,pos=None,value=0,inv=0):
        if pos is None:
            pos = CtlLine.POS_COUNTER
            CtlLine.POS_COUNTER += 1
        elif pos >= 0:
            CtlLine.POS_COUNTER = pos+1
        self.pos        = pos
        self.mask       = 1 << self.pos
        self.value      = value
        self.inv        = inv
    def update(self,word):
        self.value      = (word & self.mask) >> self.pos
        #print("CtlLine.update({:016b}); mask={self.mask:016b} value={self.value} inv={self.inv} truth={t}".format(word,self=self,t=self.istrue()))
    def settruth(self,truth):
        self.value = int(truth != self.inv)
    def istrue(self):
        return not self.value == self.inv


class CtlSeq():
    def __init__(self,cpu,arom,crom,ResetT,hlt,clr,invalid_opcode):
        self.cpu            = cpu
        self.AROM           = arom
        self.CROM           = crom
        self.Tstep          = 1
        self.micro          = self.CROM[0]
        self.ResetT         = cpu.oflags[ResetT]
        self.hlt            = cpu.oflags[hlt]
        self.clr            = cpu.oflags[clr]
        self.invalid_opcode = cpu.iflags[invalid_opcode]

    def __str__(self):
        return '{}'.format(self.Tstep)

    def get_flags(self,flagset):
        result = 0
        for f in flagset:
            result |= flagset[f].value << flagset[f].pos
        return result

    def iflags(self):
        return self.get_flags(self.cpu.iflags)

    def oflags(self):
        return self.get_flags(self.cpu.oflags)

    def decode(self):
        do_clear = self.clr.istrue()
        if do_clear:
            self.micro = self.CROM[2] & ~(self.clr.mask)
        else:
            if self.Tstep <= 0x2:
                self.micro = self.CROM[self.Tstep]
            else:
                conditions = self.iflags()
                try:
                    microaddr = (self.AROM[conditions][self.cpu.ir.value]) + (self.Tstep-3)
                    self.micro = self.CROM[microaddr]
                except KeyError:
                    print(f'Invalid opcode: 0x{self.cpu.ir.value:02X} at address 0x{self.cpu.pc.value-1:02X}')
                    #input("Press [Enter] to continue")
                    for F in self.cpu.oflags:
                        self.cpu.oflags[F].settruth(False)
                    self.ResetT.settruth(True)
                    self.hlt.settruth(True)
                    self.clr.settruth(True)
                    self.invalid_opcode.settruth(True)
                    return
        for F in self.cpu.oflags:
            self.cpu.oflags[F].update(self.micro)
        return do_clear

    def clock(self,components,subscribers):
        LOGGER.log(TRACE,f'++CtlSeq:clock()')
        # Parse the subinstruction
        do_clear = self.decode()
        LOGGER.log(2,f'micro after decode:     {self.micro:b}')

        # enable to bus
        for component in components:
            component.tick()

        if do_clear:
            self.clr.value = self.clr.inv
            self.ResetT.value = self.ResetT.inv

        # Update GUI
        for subby in subscribers:
            if hasattr(subby,"clock"):
                subby.clock()

        if self.hlt.istrue():
            return

        # latch from bus
        for component in components:
            component.tock()

        # update iflags if relevant set/clr oflag is set.
        for CMD in "SC": # Set or Clr
            for FLG in "CZ": # Carry or Zero
                oCTL = f'{CMD}{FLG}'
                iCTL = f'{FLG}F'
                if self.cpu.oflags[oCTL].istrue():
                    self.cpu.iflags[iCTL].settruth(CMD == "S")

#        #print("A={:08x} B={:08x} OUT={:08x} IR={:08x} PC={:08x} MAR={:08x} ALU={:08x}".format(
#            self.cpu.a.value,
#            self.cpu.b.value,
#            self.cpu.out.value,
#            self.cpu.ir.value,
#            self.cpu.pc.value,
#            self.cpu.mar.value,
#            self.cpu.alu.value
#        ))

        # Increment the RingCounter
        if do_clear:
            for f in self.cpu.oflags:
                self.cpu.oflags[f].value = self.cpu.oflags[f].inv
            self.Tstep = 1
        elif self.micro == self.CROM[0]:
            self.Tstep = 1
        elif self.ResetT.istrue():
            self.Tstep = 1
        else:
            self.Tstep += 1
        LOGGER.log(TRACE,f'--CtlSeq:clock(): Normal exit')
