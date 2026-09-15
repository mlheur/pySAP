#!/usr/bin/env ./venv/bin/python3

from logger import LOGGER, TRACE, INFO

from clock import Clock
from register import StdRegister
from register import OUT
from register import DoubleRegister
from ram import RAM
from alu import ALU
from ctl import CtlLine
from ctl import CtlSeq
from instruction_set import instruction_set as ISA
from cpu import CPU

WORD_SIZE =  8
ADDR_LEN  = 16


class SAPisa(ISA):

    def __init__(self,word_size=WORD_SIZE):
        LOGGER.log(TRACE,f"++SAPisa:__init__(word_size={word_size})")
        super().__init__(
            word_size = word_size
        )
        # The iflags are control bits set by other components, and used in the
        # instruction decoder to take different actions depending on these conditions.
        self.iflags = {
            'CF':  CtlLine(),
            'ZF':  CtlLine(),
            'Op':  CtlLine(),
        }
        # The oflags are the control lines set by the instruction decoder for enabling
        # various latches and operations on the next clock cycle.
        self.oflags = {
            'CLR': CtlLine(pos=0,inv=1), # CLR
            'Rt':  CtlLine(),            # Reset T counter, on last microinstruction to avoid fixed-length checking and not use a whole NOP at the end of everything.
            'Lo':  CtlLine(inv=1),       # Latch OUT
            'Et':  CtlLine(),            # Enable TMP
            'Lt':  CtlLine(inv=1),       # Latch TMP
            'Eu':  CtlLine(),            # Enable ALU
            'Su':  CtlLine(),            # Subtract
            'Sh':  CtlLine(),            # ALU Shift Left; [Sh+Su] = ALU Shift Right.
            'Ea':  CtlLine(),            # Enable A
            'La':  CtlLine(inv=1),       # Latch A
            'Eb':  CtlLine(),            # Enable B
            'Lb':  CtlLine(inv=1),       # Latch B
            'Ec':  CtlLine(),            # Enable C
            'Lc':  CtlLine(inv=1),       # Latch C
            'Ei':  CtlLine(),            # Enable IR
            'Li':  CtlLine(inv=1),       # Latch IR
            'CE':  CtlLine(),            # Chip Enable RAM
            'Lr':  CtlLine(inv=1),       # Latch RAM
            'CC':  CtlLine(inv=1),       # Clear the Carry Flag
            'SC':  CtlLine(inv=0),       # Set the Carry Flag
            'CZ':  CtlLine(inv=1),       # Clear the Zero Flag
            'SZ':  CtlLine(inv=0),       # Set the Zero Flag
            'Cm':  CtlLine(inv=1),       # Clock the MAR
            'Cp':  CtlLine(inv=1),       # Clock PC
            'Eml': CtlLine(),            # Enable MAR lo
            'Emh': CtlLine(),            # Enable MAR hi
            'Epl': CtlLine(),            # Enable PC
            'Eph': CtlLine(),            # Put the bus in the hi-byte of the PC
            'Lml': CtlLine(inv=1),       # Latch MAR lo
            'Lmh': CtlLine(inv=1),       # Latch MAR hi
            'Lpl': CtlLine(inv=1),       # Enable PC
            'Lph': CtlLine(inv=1),       # Put the bus in the hi-byte of the PC
            'HLT': CtlLine(),            # HLT
        }
        # We build the bitwise mask for the output flags at runtime since the length of oflags is arbitrary.
        self.mask = (2**len(self.oflags))-1
        # initialize the final instruction decoder's address space
        self.addr = dict()
        # Generate the control word that's all 'false' regardless if high or low means true
        self.NOP = 0
        for f in self.oflags:
            self.NOP = self.NOP | (self.oflags[f].inv << self.oflags[f].pos)
        LOGGER.log(2,f'Built NOP as 0x{self.NOP:X} {self.NOP:b}')
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
        self.ctl = []

        ctl_PC_to_MAR = self.mkctl(['Epl','Eph','Lml','Lmh','Cp']) # This control word is used in most memory-access instructions, build it once.
        LOGGER.log(2,f'Built PC-MAR 0x{ctl_PC_to_MAR:X} {ctl_PC_to_MAR:b}')

        self.addinstr('NOP',len(self.ctl))
        self.ctl.extend([self.mkctl(['Rt'])])

        self.ctl.extend([
            ctl_PC_to_MAR,           # 0x01 T1 : PC->MAR, IncPC,
            self.mkctl(['CE','Li']), # 0x02 T2 : RAM->IR
        ])

        self.addinstr('HLT',len(self.ctl))
        self.ctl.extend([self.mkctl(['HLT'])])

        self.addinstr('RST',len(self.ctl))
        self.ctl.extend([self.mkctl(['CLR'])])

        self.addinstr('CCF',len(self.ctl))
        self.ctl.extend([self.mkctl(['CC','Rt'])])

        self.addinstr('SCF',len(self.ctl))
        self.ctl.extend([self.mkctl(['SC','Rt'])])

        self.addinstr('CZF',len(self.ctl))
        self.ctl.extend([self.mkctl(['CZ','Rt'])])

        self.addinstr('SZF',len(self.ctl))
        self.ctl.extend([self.mkctl(['SZ','Rt'])])

        self.addinstr('SHL',len(self.ctl))
        self.ctl.extend([self.mkctl(['Sh','Eu','Rt'])])

        self.addinstr('SHR',len(self.ctl))
        self.ctl.extend([self.mkctl(['Sh','Eu','Su','Rt'])])

        self.addinstr('OUT',len(self.ctl))
        self.ctl.extend([self.mkctl(['Ea','Lo','Rt'])])

        self.addinstr('LDI',len(self.ctl))
        self.ctl.extend([
            ctl_PC_to_MAR,                # LDI : PC->MAR, IncPC,
            self.mkctl(['CE','La','Rt']), #     : RAM->A Next
        ])

        _JMP_adr = len(self.ctl)
        self.addinstr('JMP',_JMP_adr,is_mri=True)
        self.ctl.extend([
            ctl_PC_to_MAR,                 # JMP : PC->MAR, IncPC,
            self.mkctl(['CE','Lph','Cm']), #     : RAM->PC-HI, IncMAR
            self.mkctl(['CE','Lpl','Rt']), #     : RAM->PC-LO, Next
        ])

        _NOJ_adr = len(self.ctl)
        self.addinstr('JC', [_NOJ_adr,_JMP_adr,_NOJ_adr,_JMP_adr], is_mri=True)
        self.addinstr('JNC',[_JMP_adr,_NOJ_adr,_JMP_adr,_NOJ_adr], is_mri=True)
        self.addinstr('JZ', [_NOJ_adr,_NOJ_adr,_JMP_adr,_JMP_adr], is_mri=True)
        self.addinstr('JNZ',[_JMP_adr,_JMP_adr,_NOJ_adr,_NOJ_adr], is_mri=True)
        self.ctl.extend([
            # For conditional branching, when _NOT_ taking the branch
            # we need the PC to skip the branch address before letting
            # the CPU read the next instruction.
            self.mkctl(['Cp']),                # not JMP : IncPC
            self.mkctl(['Cp','Rt']),           #         : IncPC, Next
        ])

        self.addinstr('ADD',len(self.ctl),is_mri=True)
        self.ctl.extend([
            ctl_PC_to_MAR,                     # ADD : PC->MAR, IncPC,
            self.mkctl(['CE','Lt','Cm']),      #     : RAM->TMP IncMAR
            self.mkctl(['CE','Lml','Cp']),     #     : RAM->MAR-LO IncPC
            self.mkctl(['Et','Lmh']),          #     : TMP->MAR-HI
            self.mkctl(['CE','Lt']),           #     : RAM->TMP
            self.mkctl(['Eu','La','Rt']),      #     : ALU->A Next
        ])

        self.addinstr('SUB',len(self.ctl),is_mri=True)
        self.ctl.extend([
            ctl_PC_to_MAR,                     # SUB : PC->MAR, IncPC,
            self.mkctl(['CE','Lt','Cm']),      #     : RAM->TMP IncMAR
            self.mkctl(['CE','Lml','Cp']),     #     : RAM->MAR-LO IncPC
            self.mkctl(['Et','Lmh']),          #     : TMP->MAR-HI
            self.mkctl(['CE','Lt']),           #     : RAM->TMP
            self.mkctl(['Su','Eu','La','Rt']), #     : Sub ALU->A Next
        ])

        self.addinstr('LDA',len(self.ctl),is_mri=True)
        self.ctl.extend([
            ctl_PC_to_MAR,                     # LDA : PC->MAR, IncPC,
            self.mkctl(['CE','Lt','Cm']),      #     : RAM->TMP IncMAR
            self.mkctl(['CE','Lml','Cp']),     #     : RAM->MAR-LO IncPC
            self.mkctl(['Et','Lmh']),          #     : TMP->MAR-HI
            self.mkctl(['CE','La','Rt']),      #     : RAM->A Next
        ])

        self.addinstr('STA',len(self.ctl),is_mri=True)
        self.ctl.extend([
            ctl_PC_to_MAR,                     # STA : PC->MAR, IncPC,
            self.mkctl(['CE','Lt','Cm']),      #     : RAM->TMP IncMAR
            self.mkctl(['CE','Lml','Cp']),     #     : RAM->MAR-LO IncPC
            self.mkctl(['Et','Lmh']),          #     : TMP->MAR-HI
            self.mkctl(['Ea','Lr','Rt']),      #     : A->RAM Next
        ])

        self.addinstr('STM',len(self.ctl),is_mri=True)
        self.ctl.extend([
            ctl_PC_to_MAR,                     # STM : PC->MAR, IncPC,
            self.mkctl(['CE','Lt','Cm']),      #     : RAM->TMP IncMAR
            self.mkctl(['CE','Lml','Cp']),     #     : RAM->MAR-LO IncPC
            self.mkctl(['Et','Lmh']),          #     : TMP->MAR-HI
            self.mkctl(['CE','Lt','Cm']),      #     : RAM->TMP IncMAR
            self.mkctl(['CE','Lml']),          #     : RAM->MAR-LO
            self.mkctl(['Et','Lmh']),          #     : TMP->MAR-HI
            self.mkctl(['Ea','Lr','Rt']),      #     : A->RAM Next
        ])

        self.addinstr('LDM',len(self.ctl),is_mri=True)
        self.ctl.extend([
            ctl_PC_to_MAR,                     # LDM : PC->MAR, IncPC,
            self.mkctl(['CE','Lt','Cm']),      #     : RAM->TMP IncMAR
            self.mkctl(['CE','Lml','Cp']),     #     : RAM->MAR-LO IncPC
            self.mkctl(['Et','Lmh']),          #     : TMP->MAR-HI
            self.mkctl(['CE','Lt','Cm']),      #     : RAM->TMP IncMAR
            self.mkctl(['CE','Lml']),          #     : RAM->MAR-LO
            self.mkctl(['Et','Lmh']),          #     : TMP->MAR-HI
            self.mkctl(['CE','La','Rt']),      #     : RAM->A Next
        ])
        LOGGER.log(TRACE,f"--SAPisa:__init__(): Normal Exit")

# The CPU itself is a simple collection of components.  It's the clock and
# controller/sequencer that do all the work, with help from the ROM.
class pySAP(CPU):
    def __init__(self,isa=None,bits=WORD_SIZE,addrlen=ADDR_LEN,code=None,ipl=None):
        LOGGER.log(TRACE,f"++pySAP:__init__(bits={bits},addrlen={addrlen},code={code},ipl={ipl})")
        super().__init__()
        self.isa        = isa
        if ipl is not None:
            code = self.isa.assemble_file(ipl)
        self.bits       = bits
        self.addrlen    = addrlen
        self.iflags     = dict(isa.iflags)
        self.oflags     = dict(isa.oflags)
        self.tmp        = StdRegister(self,'CLR','Lt','Et')
        self.a          = StdRegister(self,'CLR','La','Ea')
        self.b          = StdRegister(self,'CLR','Lb','Eb')
        self.c          = StdRegister(self,'CLR','Lc','Ec')
        self.out        = OUT(self,'CLR','Lo')
        self.ir         = StdRegister(self,'CLR','Li','Ei')
        self.pc         = DoubleRegister(self,addrlen,'CLR','Cp','Lpl','Lph','Epl','Eph')
        self.mar        = DoubleRegister(self,addrlen,'CLR','Cm','Lml','Lmh','Eml','Emh')
        self.ram        = RAM(self,'Lr','CE',code)
        self.ctlseq     = CtlSeq(self,dict(isa.addr),list(isa.ctl),'Rt','HLT','CLR','Op')
        self.alu        = ALU(self,self.a,self.tmp,'Eu','Su','Sh','CF')
        self.components = {
            'A'   : self.a,
            'B'   : self.b,
            'C'   : self.c,
            'TMP' : self.tmp,
            'ALU' : self.alu,
            'OUT' : self.out,
            'PC'  : self.pc,
            'IR'  : self.ir,
            'MAR' : self.mar,
            'RAM' : self.ram,
        }
        LOGGER.log(TRACE,f"--pySAP:__init__(): Normal Exit")

    def clock(self,subscribers):
        self.ctlseq.clock(self.components.values(),subscribers)


if __name__ == "__main__":
    # Handle arguments and default values
    from sys import argv
    DollarZero = argv.pop(0)
    RUNTIME = dict()
    while len(argv) > 0:
        arg = argv.pop(0)
        if arg[0] == "-":
            if arg[1] == "f":
                RUNTIME['SOURCE'] = argv.pop(0)
                #print(f'filename {filename}')
                continue
            elif arg[1] == "a":
                RUNTIME['PRINT_ASM'] = True
                #print("Assemble Only")
                continue
            elif arg == "-Hz":
                RUNTIME['Hz'] = int(argv.pop(0))
                continue
        raise RuntimeError(f'unable to handle the arg {arg}, remaining argv {argv}')
    argv.append(DollarZero)
    # Instantiate the instruction decoder, it's necessary for assembling the initial program.
    if 'PRINT_ASM' in RUNTIME and RUNTIME['PRINT_ASM']:
        if 'SOURCE' not in RUNTIME or RUNTIME['SOURCE'] is None:
            raise RuntimeError(f"assembly needs a source file [{DollarZero} -a -f ./code/source.sap]")
        SAPisa().assemble_file(RUNTIME['SOURCE'],verbose=True)
        from sys import exit
        exit(0)
    Clock(
        Hz  = RUNTIME['Hz'],
        cpu = pySAP(
            isa = SAPisa(),
            ipl = RUNTIME['SOURCE'],
        ),
    ).run()
