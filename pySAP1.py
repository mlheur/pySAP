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
        self.last_pulse = time()
        #print("{}".format(self.cpu))
    def pulse(self):
        self.cpu.ctlseq.tick()
        if self.cpu.ctlseq.HLT == 1:
            print("Final RAM: {}".format(self.cpu.ram.value))
            return False
        self.cpu.ctlseq.tock()
        self.last_pulse = time()
        return True
    def run(self):
        if self.Hz == 0:
            input("Press [Enter] to pulse the clock.")
        elif self.Hz > 0:
            freq = 1/self.Hz
            while (time() < (self.last_pulse + freq)):
                sleep(freq)
        return self.pulse()


class Register():
    def __init__(self,cpu,bits):
        self.cpu = cpu
        self.mask = (2**bits) - 1
        self.value = rand(0,self.mask) & self.mask
        self.latch = 0
        self.enable = 0
    def tick(self):
        if self.cpu.ctlseq.CLR == 1:
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
    pass


class PC(Register):
    def tock(self):
        if self.latch == 1:
            self.value += 1
            if self.value > (self.mask):
                self.value = 0


class IR(StdRegister):
    def tick(self):
        if self.cpu.ctlseq.CLR == 1:
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
        self.CLR     = 1 # Clear Flag for PC and IR on boot
        self.HLT     = 0 # Halt the clock
        self.Tstep   = 1
    def __str__(self):
        return '{}{}{}'.format(strflag(self.CLR,"c"),strflag(self.HLT,"h"),self.Tstep)
    def decode(self):
        if self.CLR:
            micro = 0x3E3
        else:
            if self.Tstep <= 0x3:
                micro = self.CROM[self.Tstep-1]
            else:
                instr = (self.cpu.ir.value & 0xF0) >> 4
                if instr == 0xF:    # HLT
                    self.HLT = 1
                micro = self.CROM[self.AROM[instr]+(self.Tstep-4)]
        #print("MICRO: Bin={v:012b} Hex={v:03X} Dec={v:05d}".format(v=micro))
        self.cpu.pc.latch   =   (micro & 0x800) >> 11
        self.cpu.pc.enable  =   (micro & 0x400) >> 10
        self.cpu.mar.latch  = ~((micro & 0x200) >>  9) & 1
        self.cpu.ram.enable = ~((micro & 0x100) >>  8) & 1
        self.cpu.ir.latch   = ~((micro & 0x080) >>  7) & 1
        self.cpu.ir.enable  = ~((micro & 0x040) >>  6) & 1
        self.cpu.a.latch    = ~((micro & 0x020) >>  5) & 1
        self.cpu.a.enable   =   (micro & 0x010) >>  4
        self.cpu.alu.sub    =   (micro & 0x008) >>  3
        self.cpu.alu.enable =   (micro & 0x004) >>  2
        self.cpu.b.latch    = ~((micro & 0x002) >>  1) & 1
        self.cpu.out.latch  = ~((micro & 0x001)      ) & 1
        if micro == 0x3E3:
            self.Tstep = 0
        return 0
    def tick(self):
        # Parse the subinstruction
        self.decode()
        print("{}".format(self.cpu))
        # enable to bus
        self.cpu.a.tick()
        self.cpu.b.tick()
        self.cpu.alu.tick()
        self.cpu.out.tick()
        self.cpu.pc.tick()
        self.cpu.ir.tick()
        self.cpu.mar.tick()
        self.cpu.ram.tick()
    def tock(self):
        # latch from bus
        self.cpu.a.tock()
        self.cpu.b.tock()
        self.cpu.alu.tock()
        self.cpu.out.tock()
        self.cpu.pc.tock()
        self.cpu.ir.tock()
        self.cpu.mar.tock()
        self.cpu.ram.tock()
        # Increment the RingCounter
        if self.CLR != 0:
            self.CLR = 0
            self.Tstep = 1
        else:
            self.Tstep += 1
            if self.Tstep > 6:
                self.Tstep = 1


class pySAP1():
    def __init__(self,AROM,CROM,FirstRAM,bits=8,addrlen=4,instrlen=4):
        self.bits      = bits
        self.addrlen   = addrlen
        self.instrlen  = instrlen
        self.a         = AReg(self)
        self.b         = BReg(self)
        self.out       = OUT(self)
        self.ir        = IR(self)
        self.pc        = PC(self,addrlen)
        self.mar       = MAR(self,addrlen)
        self.ram       = RAM(self, FirstRAM)       
        self.ctlseq    = CtlSeq(self,AROM,CROM)
        self.alu       = ALU(self)
    def __str__(self):
        return '''o:{self.out} cs:{self.ctlseq} alu:{self.alu} a:{self.a} b:{self.b} pc:{self.pc} mar:{self.mar} ram:{self.ram} ir:{self.ir}'''.format(self=self)       


if __name__ == "__main__":
    # ISAv1
    #   LDA 0x0
    #   ADD 0x1
    #   SUB 0x2
    #   OUT 0xE
    #   HLT 0xF
    
    AddrROM = [
        0x03,
        0x06,
        0x09,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0xFF,
        0x0C,
        0x0E
    ]
    CtlROM = [
        0b010111100011,
        0b101111100011,
        0b001001100011,
        0x1A3,0x2C3,0x3E3,
        0x1A3,0x2E1,0x3C7,
        0x1A3,0x2E1,0x3CF,
        0x3F2,0x3E3,
        0x3E3
    ]
    PaulMalvinoSAP1 = [
        0x09, 0x1A, 0x1B, 0x2C, 0xE0, 0xF0,
        0xFF, 0xFF, 0xFF,
        0x01, 0x02, 0x03, 0x04,
        0xFF, 0xFF, 0xFF
    ]
    cpu    = pySAP1(AddrROM,CtlROM,PaulMalvinoSAP1)
    clock  = Clock(cpu,-1)
    while( clock.run() ): pass
