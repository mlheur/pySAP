from ctl import CtlLine as CtlLine

# The ROM class is where the microinstructions are figured out
# for the instruction decoder.  This implementation of SAP CPU
# is using a lookup table, for each instruction, for each t-step
# in those instructions, what is the bitwise representation of
# the various control lines that have to be pulled high and low
# to set the various Enable and Latch lines on the components.

class ROM(object):
    NOP = 0
    # mkctl generates control words that are bitwise representations
    # for the control lines, stored in CPU.oflags.
    def mkctl(self,flags=[]):
        word = self.NOP
        for f in flags:
            if f not in self.oflags:
                print("unknown control flag: [{}]".format(f))
                continue
            if self.oflags[f].inv == 1:
                word &= ~self.oflags[f].mask
            else:
                word |= self.oflags[f].mask
        return word
    # At runtime we can create a new assembly instruction
    # for the ROM, providing the microinstructions associated
    # with the assembly instruction.
    def addinstr(self,instr,micro):
        if type(micro) is list:
            for condition,value in enumerate(micro):
                if not condition in self.addr:
                    self.addr[condition] = dict()
                self.addr[condition][self.ASM[instr]] = value
        elif type(micro) is int:
            for condition in range(2**len(self.iflags)):
                if not condition in self.addr:
                    self.addr[condition] = dict()
                self.addr[condition][self.ASM[instr]] = micro
    # At runtime, we can assemble a new program into machine code,
    # usually those will get stored back into RAM for later execution.
    def assemble(self,instr,data=0xF):
        if instr in self.ASM:
            return (self.ASM[instr] << 4) | data
