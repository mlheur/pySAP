from clock import Clock
from cpu import CPU
from cpu.register import StdRegister, DoubleRegister

FLAGS = "CZIDB_VN"

CONTROLS = {
    'HLT':{'inverted':True, 'assert_on_reset': True},
    'CLR':{'inverted':False,'assert_on_reset': True},
    'Rt' :{'inverted':False},
    'Lph':{'inverted':True},
    'Lpl':{'inverted':True},
    'Eph':{'inverted':False},
    'Epl':{'inverted':False},
    'Lmh':{'inverted':True},
    'Lml':{'inverted':True},
    'Emh':{'inverted':False},
    'Eml':{'inverted':False},
    'Cp' :{'inverted':True},
    'Cm' :{'inverted':True},
    'La' :{'inverted':True},
    'Ea' :{'inverted':False},
    'Cc' :{'inverted':True},
    'Cd' :{'inverted':True},
    'Ci' :{'inverted':True},
    'Sc' :{'inverted':False},
    'Sd' :{'inverted':False},
    'Si' :{'inverted':False},
}

INSTRUCTIONS = [
    {
        'nmemonic'           : "NOP",
        'machine_code'       : 0x00,
        'micro_instructions' : [ ['Rt'] ],
    },
    {
        'nmemonic'           : "PC_MAR",
        'micro_instructions' : [ ['Epl','Eph','Lml','Lmh','Cp'],  ['CE','Li']],
    },
    {
        'nmemonic'           : "HLT",
        'machine_code'       : 0xFF,
        'micro_instructions' : [ ['HLT'] ],
    },
    {
        'nmemonic'           : "RST",
        'machine_code'       : 0xFF,
        'micro_instructions' : [ ['CLR'] ],
    },
    {
        'nmemonic'           : "SEC",
        'machine_code'       : 0x38,
        'micro_instructions' : [ ['Sc','Rt'] ],
    },
    {
        'nmemonic'           : "SED",
        'machine_code'       : 0xF8,
        'micro_instructions' : [ ['Sd','Rt'] ],
    },
    {
        'nmemonic'           : "SEI",
        'machine_code'       : 0x78,
        'micro_instructions' : [ ['Si','Rt'] ],
    },
    {
        'nmemonic'           : "CLC",
        'machine_code'       : 0x18,
        'micro_instructions' : [ ['Cc','Rt'] ],
    },
    {
        'nmemonic'           : "CLD",
        'machine_code'       : 0xD8,
        'micro_instructions' : [ ['Cd','Rt'] ],
    },
    {
        'nmemonic'           : "CLI",
        'machine_code'       : 0x58,
        'micro_instructions' : [ ['Ci','Rt'] ],
    },
]

#ADC
#AND
#ASL
#BCC
#BCS
#BEQ
#BIT
#BMI
#BNE
#BPL
#BRK
#BVC
#BVS
#CLC
#CLD
#CLI
#CLV
#CMP
#CPX
#CPY
#DEC
#DEX
#DEY
#EOR
#INC
#INX
#INY
#JMP
#JSR
#LDA
#LDX
#LDY
#LSR
#NOP
#ORA
#PHA
#PHP
#PLA
#PLP
#ROL
#ROR
#RTI
#RTS
#SBC
#SEC
#SED
#SEI
#STA
#STX
#STY
#TAX
#TAY
#TSX
#TXA
#TXS
#TYA

class py6502(CPU):

    def __init__(self):
        super().__init__(bits=8,address_space=16)

        for i in range(len(FLAGS)):
            self.addFlag(
                name     = FLAGS[i],
                position = i,
                inverted = False
            )

        for ctl in CONTROLS:
            self.addControlLine(
                name            = ctl,
                inverted        = CONTROLS[ctl]['inverted'],
                assert_on_reset = CONTROLS[ctl]['assert_on_reset'] if 'assert_on_reset' in CONTROLS[ctl] else False,
            )

        micro_address = 0
        saved_addresses = dict()
        for instr_definition in INSTRUCTIONS:
            for i,control_sequence in enumerate(instr_definition['micro_instructions']):
                micro_address = self.sequencer.createMicroInstruction(control_sequence)
                if i == 0:
                    self.addAssemblyInstruction(instr_definition['nmemonic'],micro_address)
                    saved_addresses[instr_definition['nmemonic']] = micro_address




        self.addComponent(
            name      = "PC",
            component = DoubleRegister(self,'CLR','Lpl','Epl','Lph','Eph'),
        )
        
        self.addComponent(
            name      = "MAR",
            component = DoubleRegister(self,'CLR','Lml','Eml','Lmh','Emh'),
        )

        self.addComponent(
            name      = "A",
            component = StdRegister(self,'CLR','La','Ea'),
        )