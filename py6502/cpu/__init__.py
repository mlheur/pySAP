from pyCPU import CPU, Bus, BusConnection
from pyCPU.control_line import ControlLine


# True:=RW; False=RO; None=WO.
INTERNAL_BUS_ATTACHMENTS = {
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
        'DL' :True,
        'DBO':True,
    },
    'ADH' : {
        'ALU':None,
        'PCH':True,
        'DL' :None,
    },
    'ADL' : {
        'ALU':None,
        'PCL':True,
        'DL' :None,
    },
}


class AddressBusCombined(Bus):

    def __init__(self,adh,adl):
        super().__init__(adh.bits+adl.bits)

    def read(self):
        return self.adl.read() & (self.adh.read() << self.adl.bits)

    def write(self):
        pass


class py6502(CPU):

    def __init__(
            self,
            external_control_lines : dict[str:ControlLine]
        ):
        super().__init__(bits=8)
        self.external_control_lines = external_control_lines
        self.external_control_tracker = {}
        for name in self.external_control_lines:
            self.external_control_tracker[name] = 0

        self.createBus('ADH')
        self.createBus('ADL')
        self.busses['ADDR'] = AddressBusCombined(
            adh = self.busses['ADH'],
            adl = self.busses['ADL'],
        )
        self.createBus('DATA')

        bus_name = 'DATA'
        for register_name in INTERNAL_BUS_ATTACHMENTS[bus_name]:
            self.createRegister(
                register_name = register_name,
                bus_name      = bus_name,
            )

        for bus_name in INTERNAL_BUS_ATTACHMENTS:
            if bus_name == 'DATA':
                continue
            for register_name in INTERNAL_BUS_ATTACHMENTS[bus_name]:
                action = INTERNAL_BUS_ATTACHMENTS[bus_name][register_name]
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

    def _updateControlLine(self,control_name,direction):
        self.external_control_tracker[control_name] += direction
        self.external_control_lines[control_name].setTruth(self.external_control_tracker[control_name]>0)

    def assertControlLine(self,control_name):
        self._updateControlLine(control_name,1)

    def releaseControlLine(self,control_name):
        self._updateControlLine(control_name,-1)


