from time import sleep
from ctl import CtlLine


class CPU(object):
    def __init__(self):
        self.w = 0
        self.oflags = {
            'HLT': CtlLine(0),
            'CLR': CtlLine(1)
        }
    def setram(self,ram):
        self.ram.set(ram)
    def reset(self):
        self.oflags['HLT'].settruth(False)
        self.oflags['CLR'].settruth(True)
    def FlushRam(self,gui=None):
        sleep(1)
        for i in range(256+13):
            if i >= 13 and i <= 268: self.ram.value[i-13] = 0b00000000
            if i >= 12 and i <= 267: self.ram.value[i-12] = 0b11111111
            if i >= 11 and i <= 266: self.ram.value[i-11] = 0b10101010
            if i >= 10 and i <= 265: self.ram.value[i-10] = 0b01010101
            if i >=  9 and i <= 264: self.ram.value[i- 9] = 0b10101010
            if i >=  8 and i <= 263: self.ram.value[i- 8] = 0b01010101
            if i >=  7 and i <= 262: self.ram.value[i- 7] = 0b10101010
            if i >=  6 and i <= 261: self.ram.value[i- 6] = 0b01010101
            if i >=  5 and i <= 260: self.ram.value[i- 5] = 0b11111111
            if i >=  4 and i <= 259: self.ram.value[i- 4] = 0b00100100
            if i >=  3 and i <= 258: self.ram.value[i- 3] = 0b10000001
            if i >=  2 and i <= 257: self.ram.value[i- 2] = 0b01000010
            if i >=  1 and i <= 256: self.ram.value[i- 1] = 0b00100100
            if i >=  0 and i <= 255: self.ram.value[i- 0] = 0b00011000
            if gui is not None:
                gui.clock()

