
class SAP1rom(object):
    def __init__(self):
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

        self.ctl = [
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

