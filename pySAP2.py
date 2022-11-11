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

class SAP2rom(ROM):
    # Hard coding which control lines are on or off during NOP operation.
    # The value is tightly coupled with self.oflags sequencing.

    def __init__(self):
        # The iflags are control bits set by other components, and used in the
        # instruction decoder to take different actions depending on these conditions.
        self.iflags = {
            'CF':      CtlLine(0),
            'ZF':      CtlLine(1)
        }
        # The oflags are the control lines set by the instruction decoder for enabling
        # various latches and operations on the next clock clock cyckle.
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
            'Rt':         CtlLine(16),       # Reset T counter, on last microinstruction to avoid fixed-length checking and not use a whole NOP at the end of everything.
            'Sh':         CtlLine(17)        # ALU Shift Left; [Sh+Su] = ALU Shift Right.
        }
        # We build the bitwise mask for the output flags at runtime since the length of oflags is arbitrary.
        self.mask = (2**len(self.oflags))-1
        
        # initialize the final ROM address space
        self.addr = dict()

        # Generate the control word that's all 'false' regardless if high or low means true
        self.NOP = 0
        for f in self.oflags:
            self.NOP = self.NOP | (self.oflags[f].inv << self.oflags[f].pos)

        # Building the self.ctl control word array is how we're teaching the instruction decoder which oflags to set for each microinstruction.
        # Any flag not listed on the mkctl call is set to false (high or low depending on inv=0|1), the ones listed will be set to true.
        self.ctl = [
            self.mkctl(['Rt']),                # 0x00 NOP : Next

            self.mkctl(['Ep','Lm']),           # 0x01 T1 : PC->MAR,
            self.mkctl(['Cp','CE','Li']),      # 0x02 T2 : IncPC RAM->IR  

            self.mkctl(['HLT']),               # 0x03 HLT : HLT

            self.mkctl(['Ep','Lm']),           # 0x04 JMP : PC->MAR
            self.mkctl(['Cp','Ep','CE','Rt']), # 0x05     : RAM->PC Next

            self.mkctl(['Ep','Lm']),           # 0x06 LDI : PC->MAR
            self.mkctl(['Cp','CE','La','Rt']), # 0x07     : IncPC RAM->A Next

            self.mkctl(['Ep','Lm']),           # 0x08 ADD : PC->MAR
            self.mkctl(['Cp','CE','Lm']),      # 0x09     : IncPC RAM->MAR
            self.mkctl(['CE','Lb']),           # 0x0A     : RAM->B
            self.mkctl(['Eu','La','Rt']),      # 0x0B     : ALU->A Next

            self.mkctl(['CLR']),               # 0x0C RST : CLR

            self.mkctl(['Ea','Lo','Rt']),      # 0x0D OUT : A->OUT Next

            self.mkctl(['Ep','Lm']),           # 0x0E LDA : PC->MAR
            self.mkctl(['Cp','CE','Lm']),      # 0x0F     : IncPC RAM->MAR
            self.mkctl(['CE','La','Rt']),      # 0x10     : RAM->A Next

            # For conditional branching, when _NOT_ taking the branch
            # we need the PC to skip the branch address before letting
            # the CPU read the next instruction.
            self.mkctl(['Cp','Rt']),           # 0x11 *** : IncPC Next

            self.mkctl(['Ep','Lm']),           # 0x12 SUB : PC->MAR
            self.mkctl(['Cp','CE','Lm']),      # 0x13     : IncPC RAM->MAR
            self.mkctl(['CE','Lb']),           # 0x14     : RAM->B
            self.mkctl(['Su','Eu','La','Rt']), # 0x15     : Sub ALU->A Next

            self.mkctl(['Ep','Lm']),           # 0x16 STA : PC->MAR
            self.mkctl(['Cp','CE','Lm']),      # 0x17     : IncPC RAM->MAR
            self.mkctl(['Lr','Ea','Rt']),      # 0x18     : RAM->A Next

            None
        ]
        
        # This array assigns binary mnemonics for each string of ASM code. 
        self.ASM = {
            'NOP': 0x0,
            'HLT': 0x1,
            'JMP': 0x2,
            'JC':  0x3,
            'JZ':  0x4,
            'JNZ': 0x5,
            'LDI': 0x6,
            'ADD': 0x7,
            'RST': 0x8,
            'OUT': 0x9,
            'LDA': 0xA,
            'SUB': 0xB,
            'STA': 0xC
        }

        # Lastly we teach the instruction decoder which micronstruction is the entry point when the clock hits T3.
        # The decoder knows all instructions share the same T1,T2 to fetch the actual instruction from RAM.
        self.addinstr('NOP',0x00)
        self.addinstr('HLT',0x03)
        self.addinstr('JMP',0x04)
        # More complex instructions, e.g. conditional branching, will enter
        # at different microinstructions depending on flag value, so all
        # possible outcomes are listed in the addinstr parameters.
        self.addinstr('JC', [0x11,0x04,0x11,0x04])
        self.addinstr('JZ', [0x11,0x11,0x04,0x04])
        self.addinstr('JNZ',[0x04,0x04,0x11,0x11])
        self.addinstr('LDI',0x06)
        self.addinstr('ADD',0x08)
        self.addinstr('RST',0x0C)
        self.addinstr('OUT',0x0D)
        self.addinstr('LDA',0x0E)
        self.addinstr('SUB',0x12)
        self.addinstr('STA',0x16)

# The CPU itself is a simple collection of components.  It's the clock and
# controller/sequencer that do all the work, with help from the ROM.
class pySAP2(CPU):
    def __init__(self,rom,FirstRAM,bits=8,addrlen=8):
        super().__init__()
        self.rom        = rom
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
        self.alu        = ALU(self,self.a,self.b,'Eu','Su','Sh')
        self.components = [self.a,self.b,self.alu,self.out,self.pc,self.ir,self.mar,self.ram]
    def clock(self,subscribers):
        self.ctlseq.clock(self.components,subscribers)


if __name__ == "__main__":

    rom = SAP2rom()

    countup = []
    # Code
    DataAddr = 0x8
    countup.extend(rom.assemble("LDI",0x20))
    countup.extend(rom.assemble("SUB",DataAddr))
    countup.extend(rom.assemble("OUT"))
    countup.extend(rom.assemble("JNZ",0x2))
    countup.extend(rom.assemble("HLT"))
    # Data
    countup.append(0x01)

    cpu = pySAP2(rom,countup)
    clk = Clock(10)

    from gui import guiSAP2 as GUI
    gui = GUI(cpu,clk)

    DataAddr = 0x19
    fib = []
    fib.extend(rom.assemble('LDI',0x1))        # 00,01
    fib.extend(rom.assemble('STA',DataAddr))   # 02,03
    fib.extend(rom.assemble('LDI',0x0))        # 04,05
    fib.extend(rom.assemble('STA',DataAddr+1)) # 06,07
    fib.extend(rom.assemble('OUT'))            # 08
    fib.extend(rom.assemble('LDA',DataAddr))   # 09,0a
    fib.extend(rom.assemble('ADD',DataAddr+1)) # 0b,0c
    fib.extend(rom.assemble('STA',DataAddr))   # 0d,0e
    fib.extend(rom.assemble('OUT'))            # 0f
    fib.extend(rom.assemble('LDA',DataAddr+1)) # 10,11
    fib.extend(rom.assemble('ADD',DataAddr))   # 12,13
    fib.extend(rom.assemble('JC', 0x18))       # 14,15
    fib.extend(rom.assemble('JMP',0x06))       # 16,17
    fib.extend(rom.assemble('HLT'))            # 18
    #  Var 1                                   # 19
    #  Var 2                                   # 1A

    #from time import sleep as sleep
    #print("ROM microinstructions dump")
    #print("{}".format(rom))
    #print("countup listing")
    #print("{}".format(countup))
    #print("running countup program")
    clk.run(cpu,fib)
    gui.wait_for_close()

