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
    def assemble(self,instr,data=0xF):
        if instr in self.ASM:
            return (self.ASM[instr] << 4) | data


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

if __name__ == "__main__":
    rom = SAP1rom()
    for i,word in enumerate(rom.ctl):
        print("addr=[{i:02x}] word=[{v:020b} {v:05x} {v:08d}]".format(i=i,v=word))
    print("rom.addr = [{}]".format(rom.addr))
