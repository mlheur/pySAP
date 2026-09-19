from pyCPU import CPU, Bus, BusConnection
from pyCPU.control_line import ControlLine

from pyRAM import pyRAM
from pyClock import pyClock

FLAGS = 'CZIDB_VN'

EXTERNAL_CONTROLS = {
    'RW' :{'inverted':False},
    'SO' :{'inverted':False},
    'SYN':{'inverted':False},
    'RDY':{'inverted':False},
    'RES':{'inverted':True},
    'IRQ':{'inverted':True},
    'NMI':{'inverted':True},
    'Ph0':{'inverted':False},
    'Ph1':{'inverted':False},
    'Ph2':{'inverted':False},
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
        'DL' :True,
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

    def __init__(self,external_control_lines):
        super().__init__(bits=8)
        self.external_control_lines = external_control_lines
        self.external_control_tracker = {}
        for name in self.external_control_lines:
            self.external_control_tracker[name] = 0

        self.createBus('DATA')
        self.createBus('ADH')
        self.createBus('ADL')
        self.busses['ADDR'] = AddressBusCombined(
            adh = self.busses['ADH'],
            adl = self.busses['ADL'],
        )

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

    def _updateControlLine(self,control_name,direction):
        self.external_control_tracker[control_name] += direction
        self.external_control_lines[control_name].setTruth(self.external_control_tracker[control_name]>0)

    def assertControlLine(self,control_name):
        self._updateControlLine(control_name,1)

    def releaseControlLine(self,control_name):
        self._updateControlLine(control_name,-1)


class py6502_Computer(object):

    def __init__(self,Hz):
        self.external_control_lines = {}
        for control in EXTERNAL_CONTROLS:
            self.external_control_lines[control] = ControlLine(
                inverted = EXTERNAL_CONTROLS[control]['inverted']
            )
        self.chips = {}
        self.chips["6502"] = py6502(self.external_control_lines)
        self.chips["RAM"] = pyRAM(
            addr_bus            = self.chips["6502"].busses["ADDR"],
            data_bus            = self.chips["6502"].busses["DATA"],
            phase1_control_line = self.external_control_lines['Ph1'],
            phase2_control_line = self.external_control_lines['Ph2'],
            rw_control_line     = self.external_control_lines['RW'],
        )
        self.chips['CLOCK'] = pyClock(cpu=self,Hz=Hz)
        self.state = "tick"
        self.viewers = []

    def addViewer(self,viewer):
        self.subscribers.append(viewer)

    def clock(self):
        if self.state == "tick":
            self.chips['6502'].assertControlLine('Ph0')
            self.chips['6502'].tick()
            self.chips['RAM'].tick()
            self.state = "tock"
        elif self.state == "tock":
            self.chips['6502'].releaseControlLine('Ph0')
            self.chips['6502'].tock()
            self.chips['RAM'].tock()
            self.state = "tick"
        for viewer in self.viewers:
            if hasattr(viewer,"clock"):
                viewer.clock()
