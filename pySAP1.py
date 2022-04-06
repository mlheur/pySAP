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
            self.pulse()
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
    def tock(self):
        super().tock()
        if self.latch == 1:
            print("OUT: {v:02X} {v:03d} {v:08b}".format(v=self.value))


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
            #print("RAM updated: {}".format(self.value))
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
            self.cpu.conditions['CARRY']['VALUE'] = int(self.cpu.b.value > self.cpu.a.value)
        else:
            self.value = (self.cpu.a.value + self.cpu.b.value)
            self.cpu.conditions['CARRY']['VALUE'] = int(self.value > self.mask)
        self.cpu.conditions['ZERO']['VALUE'] = int(self.value == 0)
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
        self.micro   = self.CROM[0]
        self.masks   = {
            'CLR':{'POS':14,'BITS':0x4000},
            'HLT':{'POS':15,'BITS':0x8000}
        }
    def __str__(self):
        return '{}'.format(self.Tstep)
    def getConditions(self):
        result = 0
        for condition in self.cpu.conditions.keys():
            result |= (self.cpu.conditions[condition]['BITS'] & self.cpu.conditions[condition]['VALUE'])
        return result
    def decode(self):
        if self.cpu.flags['CLR']:
            self.micro = self.CROM[0] | self.masks['CLR']['BITS']
        else:
            if self.Tstep <= 0x2:
                self.micro = self.CROM[self.Tstep]
            else:
                instr = (self.cpu.ir.value & 0xF0) >> self.cpu.addrlen
                self.micro = self.CROM[self.AROM[self.getConditions()][instr]+(self.Tstep-3)]
        for F in self.masks.keys():
            self.cpu.flags[F] =   (self.micro & self.masks[F]['BITS']) >> self.masks[F]['POS']
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
        #print("T:{} MICRO: Bin={v:016b} Hex={v:04X} Dec={v:05d}".format(self.Tstep,v=self.micro))
        #print("{}".format(self.cpu))
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
        self.a          = AReg(self)
        self.b          = BReg(self)
        self.out        = OUT(self)
        self.ir         = IR(self)
        self.pc         = PC(self,addrlen)
        self.mar        = MAR(self,addrlen)
        self.ram        = RAM(self, FirstRAM)       
        self.ctlseq     = CtlSeq(self,AROM,CROM)
        self.alu        = ALU(self)
        self.flags      = { 'CLR':1, 'HLT':0 }
        self.conditions = {
            'CARRY':{'POS':0, 'BITS':0b01, 'VALUE':0},
            'ZERO': {'POS':1, 'BITS':0b10, 'VALUE':0}
        }
    def clock(self):
        self.ctlseq.clock()
    def __str__(self):
        return '''{}{} o:{self.out} T:{self.ctlseq} alu:{self.alu} a:{self.a} b:{self.b} pc:{self.pc} mar:{self.mar} ram:{self.ram} ir:{self.ir}'''.format(strflag(self.flags['CLR'],"c"),strflag(self.flags['HLT'],"h"),self=self)       


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
        0x03E3,                                # 0x00 NOP : NOP
        0b0000010111100011,0b0000101001100011, # 0x01 T1,T2 : PC->MAR, IncPC and RAM->IR
        0x01A3,0x02C3,0x03E3,                  # 0x03 LDA : IR->MAR, RAM->A, NOP
        0x01A3,0x02E1,0x03C7,                  # 0x06 ADD : IR->MAR, RAM->B, ALU->A
        0x01A3,0x02E1,0x03CF,                  # 0x09 SUB : IR->MAR, RAM->B, ALU->A w/ SUB
        0x03F2,0x03E3,                         # 0x0C OUT : A->OUT, NOP
        0x83E3,                                # 0x0E HLT : NOP w/ HLT
        0x01A3,0x13F3,0x03E3,                  # 0x0F STA : IR->MAR, A->RAM, NOP
        0x43E3,                                # 0x12 RST : NOP w/ CLR
        0x0FA3,0x03E3,                         # 0x13 JMP : IR->PC, NOP
        0x0383,0x03E3                          # 0x15 LDI : IR->A, NOP
    ]


    Clock(pySAP1(AddrROM,CtlROM,Fib),-1).run()
