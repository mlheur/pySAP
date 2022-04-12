from ctl import CtlLine as CtlLine


class CPU(object):
    def __init__(self):
        self.oflags = {
            'HLT': CtlLine(0),
            'CLR': CtlLine(1)
        }
    def setram(self,ram):
        self.ram.set(ram)
    def reset(self):
        self.oflags['HLT'].settruth(False)
        self.oflags['CLR'].settruth(True)