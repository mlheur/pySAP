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
from rom import ROM as ROM
from cpu import CPU as CPU


class SAP1rom(ROM):
    NOP = 0x043E3
    def __init__(self):
        self.ASM = {
            'LDA': 0x0,
            'ADD': 0x1,
            'SUB': 0x2,
            'STA': 0x3,
            'RST': 0x4,
            'NOP': 0x5,
            'JMP': 0x6,
            'LDI': 0x7,
            'JC':  0x8,
            'JZ':  0x9,
            'JNZ': 0xA,



            'OUT': 0xE,
            'HLT': 0xF
        }
        self.iflags = {
            'CARRY':      CtlLine(0),
            'ZERO':       CtlLine(1)
        }
        self.oflags = {
            'Lo':         CtlLine(0,inv=1),  # Latch OUT
            'Lb':         CtlLine(1,inv=1),  # Latch B
            'Eu':         CtlLine(2),        # Enable ALU
            'Su':         CtlLine(3),        # Subtract
            'Ea':         CtlLine(4),        # Enable A
            'La':         CtlLine(5,inv=1),  # Latch A
            'Ei':         CtlLine(6,inv=1),  # Enable IR
            'Li':         CtlLine(7,inv=1),  # Latch IR
            'CE':         CtlLine(8,inv=1),  # Chip Enable RAM
            'Lm':         CtlLine(9,inv=1),  # Latch MAR
            'Ep':         CtlLine(10),       # Enable PC
            'Cp':         CtlLine(11),       # Clock PC
            'Lr':         CtlLine(12),       # Latch RAM
            'Eb':         CtlLine(13),       # Enable B
            'CLR':        CtlLine(14,inv=1), # CLR
            'HLT':        CtlLine(15),       # HLT
            'Rt':         CtlLine(16)        # Reset T counter, on last microinstruction to avoid fixed-length checking and not use a whole NOP at the end of everything.
        }
        self.mask = (2**len(self.oflags))-1
        self.ctl = [
            self.mkctl(),                                                                       # 0x00 NOP : NOP
            self.mkctl(['Ep','Lm']),self.mkctl(['Cp','CE','Li']),                               # 0x01 T1,T2 : PC->MAR, IncPC and RAM->IR
            self.mkctl(['Ei','Lm']),self.mkctl(['CE','La','Rt']),                               # 0x03 LDA : IR->MAR, RAM->A, NOP
            self.mkctl(['Ei','Lm']),self.mkctl(['CE','Lb']),self.mkctl(['Eu','La','Rt']),       # 0x05 ADD : IR->MAR, RAM->B, ALU->A
            self.mkctl(['Ei','Lm']),self.mkctl(['CE','Lb']),self.mkctl(['Eu','Su','La','Rt']),  # 0x08 SUB : IR->MAR, RAM->B, ALU->A w/ SUB
            self.mkctl(['Ea','Lo','Rt']),                                                       # 0x0B OUT : A->OUT, NOP
            self.mkctl(['HLT']),                                                                # 0x0C HLT : NOP w/ HLT
            self.mkctl(['Ei','Lm']),self.mkctl(['Ea','Lr','Rt']),                               # 0x0D STA : IR->MAR, A->RAM, NOP
            self.mkctl(['CLR']),                                                                # 0x0F RST : NOP w/ CLR
            self.mkctl(['Ei','Cp','Ep','Rt']),                                                  # 0x10 JMP : IR->PC, NOP
            self.mkctl(['Ei','La','Rt'])                                                        # 0x11 LDI : IR->A, NOP
        ]
        self.addr = {}
        self.addinstr('LDA',0x03)
        self.addinstr('ADD',0x05)
        self.addinstr('SUB',0x08)
        self.addinstr('STA',0x0D)
        self.addinstr('RST',0x0F)
        self.addinstr('NOP',0x00)
        self.addinstr('JMP',0x10)
        self.addinstr('LDI',0x11)
        self.addinstr('OUT',0x0B)
        self.addinstr('HLT',0x0C)
        self.addinstr('JC', [0x00,0x10,0x00,0x10])
        self.addinstr('JZ', [0x00,0x00,0x10,0x10])
        self.addinstr('JNZ',[0x10,0x10,0x00,0x00])


class pySAP1(CPU):
    def __init__(self,rom,FirstRAM,bits=8,addrlen=4):
        super().__init__()
        self.bits       = bits
        self.addrlen    = addrlen
        self.iflags     = dict(rom.iflags)
        self.oflags     = dict(rom.oflags)
        self.a          = StdRegister(self,'La','Ea')
        self.b          = StdRegister(self,'Lb','Eb')
        self.out        = OUT(self,'Lo')
        self.ir         = IR(self,'Li','Ei')
        self.pc         = PC(self,addrlen,'Cp','Ep')
        self.mar        = Register(self,addrlen,'Lm')
        self.ram        = RAM(self,'Lr','CE',FirstRAM)       
        self.ctlseq     = CtlSeq(self,dict(rom.addr),list(rom.ctl),'Rt')
        self.alu        = ALU(self,self.a,self.b,'Eu','Su')
        self.components = [self.a,self.b,self.alu,self.out,self.pc,self.ir,self.mar,self.ram]
    def clock(self):
        self.ctlseq.clock(self.components)


if __name__ == "__main__":

    rom = SAP1rom()
    fib = []
    fib.append(rom.assemble('LDI',0x1)) # 0
    fib.append(rom.assemble('STA',0xE)) # 1
    fib.append(rom.assemble('LDI',0x0)) # 2
    fib.append(rom.assemble('STA',0xF)) # 3
    fib.append(rom.assemble('OUT'))     # 4
    fib.append(rom.assemble('LDA',0xE)) # 5
    fib.append(rom.assemble('ADD',0xF)) # 6
    fib.append(rom.assemble('STA',0xE)) # 7
    fib.append(rom.assemble('OUT'))     # 8
    fib.append(rom.assemble('LDA',0xF)) # 9
    fib.append(rom.assemble('ADD',0xE)) # A
    fib.append(rom.assemble('JC', 0xD)) # B
    fib.append(rom.assemble('JMP',0x3)) # C
    fib.append(rom.assemble('HLT'))     # D
    #  Var 1                            # E
    #  Var 2                            # F


    count = []
    count.append(rom.assemble("LDA",0x4))
    count.append(rom.assemble("SUB",0x5))
    count.append(rom.assemble("OUT"))
    count.append(rom.assemble("HLT"))
    count.append(0x5)
    count.append(0x4)



    cpu = pySAP1(rom,fib)
    clk = Clock(100)

    from gui import guiSAP1 as GUI
    gui = GUI(cpu,clk)

    clk.run(cpu)
    gui.wait_for_close()

