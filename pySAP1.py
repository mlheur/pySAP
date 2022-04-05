from time import time as time
from time import sleep as sleep
from random import randint as rand


def strflag(F,C="|"):
    if F == 1: return C
    return "-"


class Clock():
    def __init__(self,cpu,Hz=0):
        self.cpu        = cpu
        self.Hz         = Hz # 0:manual
        self.freq       = 0
        if self.Hz > 0: self.freq = 1/self.Hz
        self.last_pulse = time() - self.freq
    def pulse(self):
        self.cpu.clock()
        self.last_pulse = time()
        return self.cpu.flags['HLT'] == 0
    def run(self):
        while (self.cpu.flags['HLT'] == 0):
            if self.Hz == 0:
                input("Press [Enter] to pulse the clock.")
            elif self.Hz > 0:
                wait = self.last_pulse + self.freq - time()
                if wait > 0:
                    sleep(wait)
        print("Final RAM: {}".format(self.cpu.ram.value))


class Register():
    def __init__(self,cpu,bits):
        self.cpu = cpu
        self.mask = (2**bits) - 1
        self.value = rand(0,self.mask) & self.mask
        self.latch = 0
        self.enable = 0
    def tick(self):
        if self.cpu.flags['CLR'] == 1:
            self.value = 0
        if self.enable == 1:
            self.cpu.w = self.value & self.mask
    def tock(self):
        if self.latch == 1:
            self.value = self.cpu.w & self.mask
    def __str__(self):
        L=strflag(self.latch,"l")
        E=strflag(self.enable,"e")
        V='{self.value:02X}'.format(self=self)
        return '{}{}{}'.format(L,E,V)


class StdRegister(Register):
    def __init__(self,cpu):
        super().__init__(cpu,cpu.bits)


class AReg(StdRegister):
    pass


class BReg(StdRegister):
    pass


class OUT(StdRegister):
    def __str__(self):
        L=strflag(self.latch,"l")
        V='{self.value:02X}'.format(self=self)
        return '{}{}'.format(L,V)


class PC(Register):
    def tock(self):
        if self.latch == 1:
            if self.enable == 1:
                self.value = self.cpu.w & self.mask
            else:
                self.value += 1
                if self.value > (self.mask):
                    self.value = 0


class IR(StdRegister):
    def tick(self):
        if self.cpu.flags['CLR'] == 1:
            self.value = 0
        if self.enable == 1:
            self.cpu.w = self.value & 0xF


class MAR(Register):
    def __str__(self):
        L=strflag(self.latch,"l")
        E=strflag(self.enable,"e")
        V='{self.value:01X}'.format(self=self)
        return '{}{}-{}'.format(L,E,V)


class RAM(StdRegister):
    def __init__(self,cpu,FirstRAM = []):
        super().__init__(cpu)
        self.value = [0]*(2**cpu.addrlen)
        if len(FirstRAM) > 0:
            print("Loading RAM: {}".format(FirstRAM))
            for i,v in enumerate(FirstRAM):
                self.value[i] = v
    def tick(self):
        if self.enable == 1:
            self.cpu.w = self.value[self.cpu.mar.value] & self.mask
    def tock(self):
        if self.latch == 1:
            self.value[self.cpu.mar.value] = self.cpu.w & self.mask
    def __str__(self):
        L=strflag(self.latch,"l")
        E=strflag(self.enable,"e")
        return '{}{}'.format(L,E)


class ALU(StdRegister):
    def __init__(self,cpu):
        super().__init__(cpu)
        self.value = self.mask & (self.cpu.a.value + self.cpu.b.value)
        self.sub = 0
    def update(self):
        if self.sub == 1:
            self.value = (self.cpu.a.value - self.cpu.b.value)
        else:
            self.value = (self.cpu.a.value + self.cpu.b.value)
        self.value &= self.mask
    def tick(self):
        self.update()
        if self.enable == 1:
            self.cpu.w = self.value
    def tock(self):
        self.update()
    def __str__(self):
        return '{}{}'.format(super().__str__(),strflag(self.sub,"s"))


class CtlSeq():
    def __init__(self,cpu,AROM,CROM):
        self.cpu     = cpu
        self.AROM    = AROM
        self.CROM    = CROM
        self.Tstep   = 1
        self.micro   = 0x43E3
    def __str__(self):
        return '{}'.format(self.Tstep)
    def decode(self):
        if self.cpu.flags['CLR']:
            self.micro = 0x43E3
        else:
            if self.Tstep <= 0x2:
                self.micro = self.CROM[self.Tstep-1]
            else:
                instr = (self.cpu.ir.value & 0xF0) >> self.cpu.addrlen
                self.micro = self.CROM[self.AROM[instr]+(self.Tstep-3)]
        #print("MICRO: Bin={v:012b} Hex={v:03X} Dec={v:05d}".format(v=micro))
        self.cpu.flags['HLT'] =   (self.micro & 0x8000) >> 15
        self.cpu.flags['CLR'] =   (self.micro & 0x4000) >> 14
        self.cpu.b.enable     =   (self.micro & 0x2000) >> 13
        self.cpu.ram.latch    =   (self.micro & 0x1000) >> 12
        self.cpu.pc.latch     =   (self.micro &  0x800) >> 11
        self.cpu.pc.enable    =   (self.micro &  0x400) >> 10
        self.cpu.mar.latch    = ~((self.micro &  0x200) >>  9) & 1 
        self.cpu.ram.enable   = ~((self.micro &  0x100) >>  8) & 1
        self.cpu.ir.latch     = ~((self.micro &   0x80) >>  7) & 1
        self.cpu.ir.enable    = ~((self.micro &   0x40) >>  6) & 1
        self.cpu.a.latch      = ~((self.micro &   0x20) >>  5) & 1
        self.cpu.a.enable     =   (self.micro &   0x10) >>  4
        self.cpu.alu.sub      =   (self.micro &    0x8) >>  3
        self.cpu.alu.enable   =   (self.micro &    0x4) >>  2
        self.cpu.b.latch      = ~((self.micro &    0x2) >>  1) & 1
        self.cpu.out.latch    = ~((self.micro &    0x1)      ) & 1
    def clock(self):
        # Parse the subinstruction
        self.decode()
        print("{}".format(self.cpu))
        if self.cpu.flags['HLT'] == 1:
            return
        # enable to bus
        for component in [self.cpu.a,self.cpu.b,self.cpu.alu,self.cpu.out,self.cpu.pc,self.cpu.ir,self.cpu.mar,self.cpu.ram]:
            component.tick()
        # latch from bus
        for component in [self.cpu.a,self.cpu.b,self.cpu.alu,self.cpu.out,self.cpu.pc,self.cpu.ir,self.cpu.mar,self.cpu.ram]:
            component.tock()
        # Increment the RingCounter
        if self.cpu.flags['CLR'] != 0:
            self.cpu.flags['CLR'] = 0
            self.Tstep = 1
        elif self.micro == 0x03E3:
            self.Tstep = 1
        else:
            self.Tstep += 1
            if self.Tstep > 5:
                self.Tstep = 1


class pySAP1():
    def __init__(self,AROM,CROM,FirstRAM,bits=8,addrlen=4):
        self.bits      = bits
        self.addrlen   = addrlen
        self.a         = AReg(self)
        self.b         = BReg(self)
        self.out       = OUT(self)
        self.ir        = IR(self)
        self.pc        = PC(self,addrlen)
        self.mar       = MAR(self,addrlen)
        self.ram       = RAM(self, FirstRAM)       
        self.ctlseq    = CtlSeq(self,AROM,CROM)
        self.alu       = ALU(self)
        self.flags     = { 'CLR':1, 'HLT':0 }
    def clock(self):
        self.ctlseq.clock()
    def __str__(self):
        return '''{}{} o:{self.out} T:{self.ctlseq} alu:{self.alu} a:{self.a} b:{self.b} pc:{self.pc} mar:{self.mar} ram:{self.ram} ir:{self.ir}'''.format(strflag(self.flags['CLR'],"c"),strflag(self.flags['HLT'],"h"),self=self)       


if __name__ == "__main__":
    # ISAv2
    AddrROM = [
        0x02,    #   LDA 0x0 Addr
        0x05,    #   ADD 0x1 Addr
        0x08,    #   SUB 0x2 Addr
        0x0E,    #   STA 0x3 Addr
        0x11,    #   RST 0x4*
        0x12,    #   NOP 0x5*
        0x13,    #   JMP 0x6 Value
        0x15,    #   LDI 0x7 Value
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0x0B,    #   OUT 0xE*
        0x0D     #   HLT 0xF*
    ]
    CtlROM = [
        0b0000010111100011,0b0000101001100011,
        0x01A3,0x02C3,0x03E3,
        0x01A3,0x02E1,0x03C7,
        0x01A3,0x02E1,0x03CF,
        0x03F2,0x03E3,
        0x83E3,
        0x01A3,0x13F3,0x03E3,
        0x43E3,
        0x03E3,
        0x0FA3,0x03E3,
        0x0383,0x03E3
    ]
    MyProgram = [
        0x09, 0x1A, 0x1B, 0x2C, 0xE0, 0x78, 0x3E, 0x6E,
        0x55, 0x01, 0x02, 0x03, 0x04, 0x55, 0xFF, 0xF0
    ]

    Clock(pySAP1(AddrROM,CtlROM,MyProgram),-1).run()
