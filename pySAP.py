from clock import Clock
from register import Register
from register import StdRegister
from register import OUT
from register import PC
from register import IR
from ram import RAM
from alu import ALU
from ctl import CtlLine
from ctl import CtlSeq
from instruction_set import instruction_set as ISA
from cpu import CPU


class SAPisa(ISA):

    def __init__(self):
        # The iflags are control bits set by other components, and used in the
        # instruction decoder to take different actions depending on these conditions.
        self.iflags = {
            'CF':      CtlLine(0),
            'ZF':      CtlLine(1)
        }
        # The oflags are the control lines set by the instruction decoder for enabling
        # various latches and operations on the next clock cycle.
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
            'Sh':         CtlLine(17),       # ALU Shift Left; [Sh+Su] = ALU Shift Right.
            'CC':         CtlLine(18),       # Clear the Carry Flag
            'SC':         CtlLine(19,inv=1), # Set the Carry Flag
            'CZ':         CtlLine(20),       # Clear the Zero Flag
            'SZ':         CtlLine(21,inv=1), # Set the Zero Flag
        }
        # We build the bitwise mask for the output flags at runtime since the length of oflags is arbitrary.
        self.mask = (2**len(self.oflags))-1

        # initialize the final ROM address space
        self.addr = dict()

        # Generate the control word that's all 'false' regardless if high or low means true
        self.NOP = 0
        for f in self.oflags:
            self.NOP = self.NOP | (self.oflags[f].inv << self.oflags[f].pos)

        # This array assigns binary mnemonics for each string of ASM code.
        self.ASM = {
            'NOP': 0x00,
            'HLT': 0x01,
            'JMP': 0x02,
            'JC':  0x03,
            'JNC': 0x04,
            'JZ':  0x05,
            'JNZ': 0x06,
            'LDI': 0x07,
            'ADD': 0x08,
            'RST': 0x09,
            'OUT': 0x0A,
            'LDA': 0x0B,
            'SUB': 0x0C,
            'STA': 0x0D,
            'SHL': 0x0E,
            'SHR': 0X0F,
            'CCF': 0X10,
            'SCF': 0X11,
            'CZF': 0X12,
            'SZF': 0X13,
            'STM': 0x14,
            'LDM': 0x15,
        }

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
            self.mkctl(['Ea','Lr','Rt']),      # 0x18     : A->RAM Next

            self.mkctl(['Sh','Eu','Rt']),      # 0x19 SHL : A->shift->ALU->A Next
            self.mkctl(['Sh','Eu','Su','Rt']), # 0x1A SHR : A->shift->ALU->A Next

            self.mkctl(['CC','Rt']),           # 0x1B CCF
            self.mkctl(['SC','Rt']),           # 0x1C SCF
            self.mkctl(['CZ','Rt']),           # 0x1D CZF
            self.mkctl(['SZ','Rt']),           # 0x1E SZF

            self.mkctl(['Ep','Lm']),           # 0x1F STM : PC->MAR
            self.mkctl(['Cp','CE','Lm']),      # 0x20     : IncPC RAM->MAR
            self.mkctl(['CE','Lm']),           # 0x21     : RAM->MAR
            self.mkctl(['Ea','Lr','Rt']),      # 0x22     : A->RAM Next

            self.mkctl(['Ep','Lm']),           # 0x23 LDM : PC->MAR
            self.mkctl(['Cp','CE','Lm']),      # 0x24     : IncPC RAM->MAR
            self.mkctl(['CE','Lm']),           # 0x25     : RAM->MAR
            self.mkctl(['CE','La','Rt']),      # 0x26     : RAM->A Next

            None
        ]

        # Lastly we teach the instruction decoder which micronstruction is the entry point when the clock hits T3.
        # The decoder knows all instructions share the same T1,T2 to fetch the actual instruction from RAM.
        self.addinstr('NOP',0x00)
        self.addinstr('HLT',0x03)
        self.addinstr('JMP',0x04)
        # More complex instructions, e.g. conditional branching, will enter
        # at different microinstructions depending on flag value, so all
        # possible outcomes are listed in the addinstr parameters.
        self.addinstr('JC', [0x11,0x04,0x11,0x04])
        self.addinstr('JNC',[0x04,0x11,0x04,0x11])
        self.addinstr('JZ', [0x11,0x11,0x04,0x04])
        self.addinstr('JNZ',[0x04,0x04,0x11,0x11])
        self.addinstr('LDI',0x06)
        self.addinstr('ADD',0x08)
        self.addinstr('RST',0x0C)
        self.addinstr('OUT',0x0D)
        self.addinstr('LDA',0x0E)
        self.addinstr('SUB',0x12)
        self.addinstr('STA',0x16)
        self.addinstr('SHR',0x19)
        self.addinstr('SHL',0x1A)
        self.addinstr('CCF',0x1B)
        self.addinstr('SCF',0x1C)
        self.addinstr('CZF',0x1D)
        self.addinstr('SZF',0x1E)
        self.addinstr('STM',0x1F)
        self.addinstr('LDM',0x23)

# The CPU itself is a simple collection of components.  It's the clock and
# controller/sequencer that do all the work, with help from the ROM.
class pySAP(CPU):
    def __init__(self,isa=None,bits=8,addrlen=8):
        super().__init__()
        self.isa        = isa
        self.bits       = bits
        self.addrlen    = addrlen
        self.iflags     = dict(isa.iflags)
        self.oflags     = dict(isa.oflags)
        self.a          = StdRegister(self,'La','Ea')
        self.b          = StdRegister(self,'Lb','Eb')
        self.out        = OUT(self,'Lo')
        self.ir         = IR(self,'Li','Ei')
        self.pc         = PC(self,addrlen,'Cp','Ep')
        self.mar        = Register(self,addrlen,'Lm')
        self.ram        = RAM(self,'Lr','CE')
        self.ctlseq     = CtlSeq(self,dict(isa.addr),list(isa.ctl),'Rt')
        self.alu        = ALU(self,self.a,self.b,'Eu','Su','Sh','CF')
        self.components = [self.a,self.b,self.alu,self.out,self.pc,self.ir,self.mar,self.ram]
    def clock(self,subscribers):
        self.ctlseq.clock(self.components,subscribers)


if __name__ == "__main__":

    from sys import argv
    assemble_only = False
    filename = None
    Hz = None
    WipeRam = False
    DollarZero = argv.pop(0)
    while len(argv) > 0:
        arg = argv.pop(0)
        if arg[0] == "-":
            if arg[1] == "f":
                filename = argv.pop(0)
                #print(f'filename {filename}')
                continue
            elif arg[1] == "a":
                #print("Assemble Only")
                assemble_only = True
                continue
            elif arg == "-Hz":
                Hz=int(argv.pop(0))
                continue
            elif arg[1] == "w":
                WipeRam = True
                continue
        raise RuntimeError(f'unable to handle the arg {arg}, remaining argv {argv}')
    argv.append(DollarZero)

    isa = SAPisa()
    if assemble_only:
        if filename is not None:
            isa.assemble_file(filename,verbose=True)
        else:
            raise RuntimeError("assembly needs a source file [-f ./code/source.sap]")
        from sys import exit
        exit(0)

    sap = pySAP(isa=isa)
    if WipeRam:
        sap.WipeRam()
    clk = Clock(cpu=sap,Hz=Hz)

    from guiSAP import guiSAP as GUI
    gui = GUI(sap,clk)

    if filename is None:
        filename = "./code/cylon.sap"
        if Hz is None:
            clk.modify(5000)
    clk.run(ram=isa.assemble_file(filename))
    gui.wait_for_close()
