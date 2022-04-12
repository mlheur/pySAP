from clock import Clock as Clock
from register import Register as Register
from register import StdRegister as StdRegister
from register import OUT as OUT
from register import PC as PC
from register import IR as IR
from ram import RAM as RAM
from alu import ALU as ALU
from ctl import CtlLine as CtlLine
from ctl import CtlSeq as CtlSeq


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


if __name__ == "__main__":
    Fib = [
        0x71,0x3E,0x70,0x3F,0xE5,0x0E,0x1F,0x3E,
        0xE5,0x0F,0x1E,0x8D,0x63,0xF5,0x55,0x55
    ]
    Count = [
        0x08,0xE5,0x29,0xE5,0xA2,0x6F,0x55,0x55,
        0x09,0x01,0x55,0x55,0x55,0x55,0x55,0xF5
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
            0x13,    #   JNZ 0xA Addr | do JMP when all conditions are off
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
    AddrROM[0b01][0x8] = 0x13 # JC  0x8 Addr | do JMP when Carry condition is on
    AddrROM[0b11][0x8] = 0x13 # JC  0x8 Addr | do JMP when Carry condition is on
    AddrROM[0b10][0x9] = 0x13 # JZ  0x9 Addr | do JMP when Zero condition is on
    AddrROM[0b11][0x9] = 0x13 # JZ  0x9 Addr | do JMP when Zero condition is on
    AddrROM[0b10][0xA] = 0x00 # JNZ 0xA Addr | do NOP when Zero condition is on
    AddrROM[0b11][0xA] = 0x00 # JNZ 0xA Addr | do NOP when Zero condition is on

    CtlROM = [
        0x043E3,                                  # 0x00 NOP : NOP
        0b00100010111100011,0b00100101001100011,  # 0x01 T1,T2 : PC->MAR, IncPC and RAM->IR
        0x041A3,0x042C3,0x043E3,                  # 0x03 LDA : IR->MAR, RAM->A, NOP
        0x041A3,0x042E1,0x143C7,                  # 0x06 ADD : IR->MAR, RAM->B, ALU->A
        0x041A3,0x042E1,0x143CF,                  # 0x09 SUB : IR->MAR, RAM->B, ALU->A w/ SUB
        0x043F2,0x043E3,                          # 0x0C OUT : A->OUT, NOP
        0x0C3E3,                                  # 0x0E HLT : NOP w/ HLT
        0x041A3,0x053F3,0x043E3,                  # 0x0F STA : IR->MAR, A->RAM, NOP
        0x003E3,                                  # 0x12 RST : NOP w/ CLR
        0x04FA3,0x043E3,                          # 0x13 JMP : IR->PC, NOP
        0x04383,0x043E3                           # 0x15 LDI : IR->A, NOP
    ]


    Clock(pySAP1(AddrROM,CtlROM,Count),200).run()
    Clock(pySAP1(AddrROM,CtlROM,Fib),200).run()
    Count[8] = 0
    Clock(pySAP1(AddrROM,CtlROM,Count),-1).run()
