

from ctl import CtlLine as CtlLine


class ROM(object):
    NOP = 0
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
        

class SAP1rom(ROM):
    NOP = 0x043E3
    def __init__(self):
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
            'HLT':        CtlLine(15)        # HLT
        }
        self.mask = (2**len(self.oflags))-1

        self.ctl = [
            self.mkctl(),                                                                  # 0x00 NOP : NOP
            self.mkctl(['Ep','Lm']),self.mkctl(['Cp','CE','Li']),                          # 0x01 T1,T2 : PC->MAR, IncPC and RAM->IR
            self.mkctl(['Ei','Lm']),self.mkctl(['CE','La']),self.NOP,                      # 0x03 LDA : IR->MAR, RAM->A, NOP
            self.mkctl(['Ei','Lm']),self.mkctl(['CE','Lb']),self.mkctl(['Eu','La']),       # 0x06 ADD : IR->MAR, RAM->B, ALU->A
            self.mkctl(['Ei','Lm']),self.mkctl(['CE','Lb']),self.mkctl(['Eu','Su','La']),  # 0x09 SUB : IR->MAR, RAM->B, ALU->A w/ SUB
            self.mkctl(['Ea','Lo']),self.NOP,                                              # 0x0C OUT : A->OUT, NOP
            self.mkctl(['HLT']),                                                           # 0x0E HLT : NOP w/ HLT
            self.mkctl(['Ei','Lm']),self.mkctl(['Ea','Lr']),self.NOP,                      # 0x0F STA : IR->MAR, A->RAM, NOP
            self.mkctl(['CLR']),                                                           # 0x12 RST : NOP w/ CLR
            self.mkctl(['Ei','Cp','Ep']),self.NOP,                                         # 0x13 JMP : IR->PC, NOP
            self.mkctl(['Ei','La']),self.NOP                                               # 0x15 LDI : IR->A, NOP
        ]


        self.iflags = {
            'CARRY':      CtlLine(0),
            'ZERO':       CtlLine(1)
        }

        # ISAv3 - now with conditional flags
        self.addr = [
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
        # copy the base addr ROM across all conditions
        for condition in range(1,4):
            self.addr.append([])
            for v in self.addr[0]:
                self.addr[condition].append(v)
        # override the base when conditions warrant
        # ToDo: generalize this.
        self.addr[0b01][0x8] = 0x13 # JC  0x8 Addr | do JMP when Carry condition is on
        self.addr[0b11][0x8] = 0x13 # JC  0x8 Addr | do JMP when Carry condition is on
        self.addr[0b10][0x9] = 0x13 # JZ  0x9 Addr | do JMP when Zero condition is on
        self.addr[0b11][0x9] = 0x13 # JZ  0x9 Addr | do JMP when Zero condition is on
        self.addr[0b10][0xA] = 0x00 # JNZ 0xA Addr | do NOP when Zero condition is on
        self.addr[0b11][0xA] = 0x00 # JNZ 0xA Addr | do NOP when Zero condition is on


if __name__ == "__main__":
    rom = SAP1rom()
    for i,word in enumerate(rom.ctl):
        print("addr=[{i:04x}] word=[{v:020b} {v:04x} {v:06d}]".format(i=i,v=word))
