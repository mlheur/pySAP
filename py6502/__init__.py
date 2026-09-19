from pyCPU.control_line import ControlLine
from pyRAM import pyRAM
from pyClock import pyClock
from .cpu import py6502
from pyCPU.bus import Bus

FLAGS = 'CZIDB_VN'

EXTERNAL_CONTROLS = {
    'RW' :{'inverted':False},
    'SO' :{'inverted':False},
    'SYN':{'inverted':False},
    'RDY':{'inverted':False},
    'RES':{'inverted':True},
    'IRQ':{'inverted':True},
    'NMI':{'inverted':True},
    'CP0':{'inverted':False},
    'CP1':{'inverted':False},
    'CP2':{'inverted':False},
}

EXTERNAL_BUSSES = {
    'ADDR' : 16,
    'DATA' :  8,
}

###
# The 'Computer' is essentially the motherboard, with traces sockets,
# and some few logic gates.
class py6502_Computer(object):

    def __init__(self,Hz):
        # Instatiate all the single-pin Control Lines
        self.external_control_lines : dict[str:ControlLine] = {}
        for control in EXTERNAL_CONTROLS:
            self.external_control_lines[control] = ControlLine(
                inverted = EXTERNAL_CONTROLS[control]['inverted']
            )
        # Instantiate all the multi-pin Busses
        self.busses = {}
        for bus_name in EXTERNAL_BUSSES:
            self.busses[bus_name] = Bus(width=EXTERNAL_BUSSES[bus_name])
        # Add chips in the sockets
        self.chips : dict[str:object] = {}
        self.chips['CLOCK'] = pyClock(cpu=self,Hz=Hz)
        self.chips["6502"]  = py6502(self.external_control_lines)
        self.chips["RAM"]   = pyRAM(
            addr_bus            = self.chips["6502"].busses["ADDR"],
            data_bus            = self.chips["6502"].busses["DATA"],
            phase1_control_line = self.external_control_lines['Ph1'],
            phase2_control_line = self.external_control_lines['Ph2'],
            rw_control_line     = self.external_control_lines['RW'],
        )
        # Allow a UI to subscribe to view the computer's state after it changes.
        self.viewers = []
        self.reset()

    def addViewer(self,viewer):
        self.subscribers.append(viewer)

    def reset(self):
        self.state : str = "tick"
        self.updateViewers()

    def _runOnChips(self,function):
        for chip in self.chips:
            fn_ptr = getattr(self.chips[chip],function)
            if fn_ptr is not None:
                fn_ptr()

    def clock(self):
        if self.state == "tick":
            self.chips['6502'].assertControlLine('Ph0')
            self._runOnChips(function=self.state)
            self.state = "tock"
        elif self.state == "tock":
            self.chips['6502'].releaseControlLine('Ph0')
            self._runOnChips(function=self.state)
            self.state = "tick"
        self.updateViewers()

    def updateViewers(self):
        for viewer in self.viewers:
            if hasattr(viewer,"clock"):
                viewer.clock()
