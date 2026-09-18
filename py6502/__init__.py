from pyCPU import CPU, BusConnection
from pyCPU.control_line import ControlLine

FLAGS = 'CZIDB_VN'

EXTERNAL_CONTROLS = {
    'RW' :{'inverted':False},
    'SO' :{'inverted':False},
    'SYN':{'inverted':False},
    'RDY':{'inverted':False},
    'RES':{'inverted':True},
    'IRQ':{'inverted':True},
    'NMI':{'inverted':True},
}

# True:=RW; False=RO; None=WO.
REGISTER_BUS_ATTACHMENTS = {
    'DATA' : {
        'ALU':True,
        'A'  :True,
        'S'  :True,
        'X'  :True,
        'Y'  :True,
        'P'  :True,
        'I'  :False,
        'PCH':False,
        'PCL':False,
        'IDL':True,
        'DBB':True,
    },
    'ADH' : {
        'ALU':None,
        'PCH':True,
        'IDL':None,
    },
    'ADL' : {
        'ALU':None,
        'PCL':True,
        'IDL':None,
    },
}


class py6502(CPU):

    def __init__(self):
        super().__init__(bits=8)

        self.createBus('A_ALU')

        self.createBus('DATA')
        self.createBus('ADH')
        self.createBus('ADL')

        bus_name = 'DATA'
        for register_name in REGISTER_BUS_ATTACHMENTS[bus_name]:
            self.createRegister(
                register_name = register_name,
                bus_name      = bus_name,
            )

        for bus_name in REGISTER_BUS_ATTACHMENTS:
            if bus_name == 'DATA':
                continue
            for register_name in REGISTER_BUS_ATTACHMENTS[bus_name]:
                action = REGISTER_BUS_ATTACHMENTS[bus_name][register_name]
                use_latch = True
                use_enable = True
                if action is None:
                    use_enable = False
                elif not action:
                    use_latch = False
                self.registers[register_name].addBusConnection(
                    bus_name,
                    BusConnection(
                        self.busses[bus_name],
                        ControlLine(inverted=True)  if use_latch  else None,
                        ControlLine(inverted=False) if use_enable else None,
                    )
                )
