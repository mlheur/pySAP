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
        self.ctlseq     = CtlSeq(self,list(rom.addr),list(rom.ctl),'Rt')
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
    
    cpu = pySAP1(ROM(),Fib)
    clk = Clock(100)
    clk.run(cpu)

    clk.run(cpu,Count)
    Count[8] = 0
    cpu.setram(Count)
    Clock(-1).run(cpu)
