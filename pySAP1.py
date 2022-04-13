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
from rom import SAP1rom as ROM
from cpu import CPU as CPU


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
        self.ctlseq.clock()


if __name__ == "__main__":
    rom = ROM()
    fib = []
    fib.append(rom.assemble('LDI',0x1))
    fib.append(rom.assemble('STA',0xE))
    fib.append(rom.assemble('LDI',0x0))
    fib.append(rom.assemble('STA',0xF))
    fib.append(rom.assemble('OUT'))
    fib.append(rom.assemble('LDA',0xE))
    fib.append(rom.assemble('ADD',0xF))
    fib.append(rom.assemble('STA',0xE))
    fib.append(rom.assemble('OUT'))
    fib.append(rom.assemble('STA',0xF))
    fib.append(rom.assemble('ADD',0xE))
    fib.append(rom.assemble('JC', 0xD))
    fib.append(rom.assemble('JMP',0x3))
    fib.append(rom.assemble('HLT'))
    cpu = pySAP1(rom,fib)
    clk = Clock(100)
    clk.run(cpu)

