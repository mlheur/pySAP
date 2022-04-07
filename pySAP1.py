from time import time as time
from time import sleep as sleep
from random import randint as rand


def strflag(F,C="|"):
    if F: return C
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
    def run(self):
        while (not self.cpu.oflags['HLT'].istrue()):
            if self.Hz == 0:
                input("Press [Enter] to pulse the clock.")
            elif self.Hz > 0:
                wait = self.last_pulse + self.freq - time()
                if wait > 0:
                    sleep(wait)
            self.pulse()
        print("Final RAM: {}".format(self.cpu.ram.value))


class Register():
    def __init__(self,cpu,bits,latch=None,enable=None):
        self.cpu        = cpu
        self.mask       = (2**bits) - 1      # ToDo: validate host architecture is more than bits.
        self.value      = rand(0,self.mask)
        if latch is not None: self.latch  = self.cpu.oflags[latch]
        else: self.latch = None
        if enable is not None: self.enable = self.cpu.oflags[enable]
        else: self.enable = None
    def tick(self):
        if self.cpu.oflags['CLR'].istrue(): self.value  = 0
        if self.enable is not None and self.enable.istrue(): self.cpu.w  = self.value & self.mask
    def tock(self):
        if self.latch is not None and self.latch.istrue():
            self.value  = self.cpu.w & self.mask
    def __str__(self):
        if self.latch is not None: L=strflag(self.latch.istrue(),"l")
        else: L=""
        if self.enable is not None: E=strflag(self.enable.istrue(),"e")
        else: E=""
        V='{self.value:02X}'.format(self=self)
        return '{L}{E}{V:02X}'.format(L=L,E=E,V=self.value)


class StdRegister(Register):
    def __init__(self,cpu,latch=None,enable=None):
        super().__init__(cpu,cpu.bits,latch,enable)


class OUT(StdRegister):
    def tock(self):
        super().tock()
        if self.latch.istrue():
            print("OUT: {v:02X} {v:03d} {v:08b}".format(v=self.value))


class PC(Register):
    def tock(self):
        if self.latch.istrue():
            if self.enable.istrue(): self.value = self.cpu.w & self.mask
            else: self.value = (self.value + 1) & self.mask


class IR(StdRegister):
    def tick(self):
        if self.cpu.oflags['CLR'].istrue(): self.value = 0
        if self.enable.istrue(): self.cpu.w = self.value & 0xF


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
    def __str__(self):
        L=strflag(self.latch.istrue(),"l")
        E=strflag(self.enable.istrue(),"e")
        return '{}{}'.format(L,E)


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
            self.cpu.iflags['CARRY'].settruth(self.B.value > self.A.value)
        else:
            self.value = ((self.A.value & self.mask) + (self.B.value & self.mask))
            self.cpu.iflags['CARRY'].settruth(self.value > self.mask)
        self.cpu.iflags['ZERO'].settruth(self.value == 0)
    def tick(self):
        self.update()
        if self.enable.istrue():
            self.cpu.w = self.value
    def tock(self):
        self.update()
    def __str__(self):
        return '{}{}'.format(super().__str__(),strflag(self.sub.istrue(),"s"))


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
    def __init__(self,cpu,AROM,CROM):
        self.cpu     = cpu
        self.AROM    = AROM
        self.CROM    = CROM
        self.Tstep   = 1
        self.micro   = self.CROM[0]
    def __str__(self):
        return '{}'.format(self.Tstep)
    def iflags(self):
        result = 0
        for f in self.cpu.iflags:
            result |= (self.cpu.iflags[f].mask & self.cpu.iflags[f].value)
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
            if self.Tstep > 5:
                self.Tstep = 1

class pySAP1():
    def __init__(self,AROM,CROM,FirstRAM,bits=8,addrlen=4):
        self.bits       = bits
        self.addrlen    = addrlen
        self.iflags = {
            'CARRY':      CtlLine(0),
            'ZERO':       CtlLine(1)
        }
        self.oflags = {
            'Lo':         CtlLine(0,inv=1),
            'Lb':         CtlLine(1,inv=1),
            'Eu':         CtlLine(2),
            'Su':         CtlLine(3),
            'Ea':         CtlLine(4),
            'La':         CtlLine(5,inv=1),
            'Ei':         CtlLine(6,inv=1),
            'Li':         CtlLine(7,inv=1),
            'CE':         CtlLine(8,inv=1),
            'Lm':         CtlLine(9,inv=1),
            'Ep':         CtlLine(10),
            'Cp':         CtlLine(11),
            'Lr':         CtlLine(12),
            'Eb':         CtlLine(13),
            'CLR':        CtlLine(14,inv=1),
            'HLT':        CtlLine(15)
        }
        self.a          = StdRegister(self,'La','Ea')
        self.b          = StdRegister(self,'Lb','Eb')
        self.out        = OUT(self,'Lo')
        self.ir         = IR(self,'Li','Ei')
        self.pc         = PC(self,addrlen,'Cp','Ep')
        self.mar        = Register(self,addrlen,'Lm')
        self.ram        = RAM(self,'Lr','CE',FirstRAM)       
        self.ctlseq     = CtlSeq(self,AROM,CROM)
        self.alu        = ALU(self,self.a,self.b,'Eu','Su')
        self.components = [self.a,self.b,self.alu,self.out,self.pc,self.ir,self.mar,self.ram]
    def clock(self):
        self.ctlseq.clock()
    def __str__(self):
        return '''{}{} o:{self.out} T:{self.ctlseq} alu:{self.alu} a:{self.a} b:{self.b} pc:{self.pc} mar:{self.mar} ram:{self.ram} ir:{self.ir}'''.format(strflag(self.oflags['CLR'].istrue(),"c"),strflag(self.oflags['HLT'].istrue(),"h"),self=self)       


if __name__ == "__main__":
    Fib = [
        0x71,0x3E,0x70,0x3F,0xE5,0x0E,0x1F,0x3E,
        0xE5,0x0F,0x1E,0x8D,0x63,0xF5,0x55,0x55
    ]
    
    # ISAv3 - now with conditional flags
    AddrROM = [
        [ # conditions == 0b00
            0x03,    #   LDA 0x0 Addr
            0x06,    #   ADD 0x1 Addr
            0x09,    #   SUB 0x2 Addr
            0x0F,    #   STA 0x3 Addr
            0x12,    #   RST 0x4*
            0x00,    #   NOP 0x5*
            0x13,    #   JMP 0x6 Addr
            0x15,    #   LDI 0x7 Value
            0x00,    #   JC  0x8 Addr | do NOP when all conditions are off
            0x00,    #   JZ  0x9 Addr | do NOP when all conditions are off
            0xFF,
            0xFF,
            0xFF,
            0xFF,
            0x0C,    #   OUT 0xE*
            0x0E     #   HLT 0xF*
        ]
    ]
    # copy the base AddrROM across all conditions
    for CONDS in range(1,4):
        AddrROM.append([])
        for v in AddrROM[0]:
            AddrROM[CONDS].append(v)
    # override the base when conditions warrant
    # ToDo: generalize this.
    AddrROM[0b01][0x8] = 0x13 # JC 0x8 Addr | do JMP when Carry condition is on
    AddrROM[0b11][0x8] = 0x13 # JC 0x8 Addr | do JMP when Carry condition is on
    AddrROM[0b10][0x9] = 0x13 # JZ 0x9 Addr | do JMP when Zero condition is on
    AddrROM[0b11][0x9] = 0x13 # JZ 0x9 Addr | do JMP when Zero condition is on

    CtlROM = [
        0x43E3,                                # 0x00 NOP : NOP
        0b0100010111100011,0b0100101001100011, # 0x01 T1,T2 : PC->MAR, IncPC and RAM->IR
        0x41A3,0x42C3,0x43E3,                  # 0x03 LDA : IR->MAR, RAM->A, NOP
        0x41A3,0x42E1,0x43C7,                  # 0x06 ADD : IR->MAR, RAM->B, ALU->A
        0x41A3,0x42E1,0x43CF,                  # 0x09 SUB : IR->MAR, RAM->B, ALU->A w/ SUB
        0x43F2,0x43E3,                         # 0x0C OUT : A->OUT, NOP
        0xC3E3,                                # 0x0E HLT : NOP w/ HLT
        0x41A3,0x53F3,0x43E3,                  # 0x0F STA : IR->MAR, A->RAM, NOP
        0x03E3,                                # 0x12 RST : NOP w/ CLR
        0x4FA3,0x43E3,                         # 0x13 JMP : IR->PC, NOP
        0x4383,0x43E3                          # 0x15 LDI : IR->A, NOP
    ]


    Clock(pySAP1(AddrROM,CtlROM,Fib),200).run()
