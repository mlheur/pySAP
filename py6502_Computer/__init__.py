from .cpu import py6502
from pySocket import pySocket, buildPinoutFromDefinition, buildPinoutFromPinCollection
from pySocket.control_line import ControlLine
from pyRAM import pyRAM

FLAGS = 'CZIDB_VN'

PINOUT_6502 = [
    {'GND':{}},
    {'RDY':{'pin_id': 2}},
    {'Ph1':{'pin_id': 3}},
    {'IRQ':{'pin_id': 4,'inverted':True}},
    {'_'  :None},
    {'NMI':{'pin_id': 6,'inverted':True}},
    {'SYN':{'pin_id': 7}},
    {'Vcc':{}},
    {'A00':{'pin_id': 9}},
    {'A01':{'pin_id':10}},
    {'A02':{'pin_id':11}},
    {'A03':{'pin_id':12}},
    {'A04':{'pin_id':13}},
    {'A05':{'pin_id':14}},
    {'A06':{'pin_id':15}},
    {'A07':{'pin_id':16}},
    {'A08':{'pin_id':17}},
    {'A09':{'pin_id':18}},
    {'A10':{'pin_id':19}},
    {'A11':{'pin_id':20}},
    {'GND':{}},
    {'A12':{'pin_id':22}},
    {'A13':{'pin_id':23}},
    {'A14':{'pin_id':24}},
    {'A15':{'pin_id':25}},
    {'D07':{'pin_id':26}},
    {'D06':{'pin_id':27}},
    {'D05':{'pin_id':28}},
    {'D04':{'pin_id':29}},
    {'D03':{'pin_id':30}},
    {'D02':{'pin_id':31}},
    {'D01':{'pin_id':32}},
    {'D00':{'pin_id':33}},
    {'RW' :{'pin_id':34}},
    {'_'  :None},
    {'_'  :None},
    {'Ph0':{'pin_id':37}},
    {'SO' :{'pin_id':38,'inverted':True}},
    {'Ph2':{'pin_id':39}},
    {'RES':{'pin_id':40,'inverted':True}},
]

###
# The 'Computer' is essentially the motherboard, with traces, sockets,
# and some few logic gates.
class py6502_Computer(object):

    def __init__(self,Hz):
        self.sockets = {}
        self.sockets['6502'] = pySocket(buildPinoutFromDefinition(PINOUT_6502)),
        self.sockets['6502'].makeBus(
            name        = 'ADDR',
            pin_id_list = [9,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25],
        )
        self.sockets['6502'].makeBus(
            name        = 'DATA',
            pin_id_list = [33,32,31,30,29,28,27,26],
        )

        CE = ControlLine(position=0,inverted=True)
        CS = ControlLine(inverted=True)
        self.sockets['RAM'] = pySocket([CE,CS])
        for bus_name in ['DATA','ADDR']:
            self.sockets['RAM'].attachToBus(self.sockets['6502'].getBus(bus_name),bus_name)

        self.sockets['6502'].addChip(py6502(self.sockets['6502']))
        self.sockets['RAM'].addChip(pyRAM(self.sockets['RAM']))

        # Allow a UI to subscribe to view the computer's state after it changes.
        self.viewers = []
        self.reset()

    def addViewer(self,viewer):
        self.subscribers.append(viewer)

    def updateViewers(self):
        for viewer in self.viewers:
            if hasattr(viewer,"clock"):
                viewer.clock()

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
