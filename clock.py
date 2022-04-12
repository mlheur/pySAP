from time import time as time
from time import sleep as sleep


class Clock():
    def __init__(self,cpu,Hz=0):
        self.cpu        = cpu
        self.Hz         = Hz # 0:manual
        self.freq       = 0
        if self.Hz > 0: self.freq = 1/self.Hz
        self.last_pulse = time() - self.freq
    def pulse(self):
        self.cpu.clock()
        self.last_pulse = time()
    def run(self):
        while (not self.cpu.oflags['HLT'].istrue()):
            if self.Hz == 0:
                input("Press [Enter] to pulse the clock.")
            elif self.Hz > 0:
                wait = self.last_pulse + self.freq - time()
                if wait > 0:
                    sleep(wait)
            self.pulse()
        print("Final RAM: {}".format(self.cpu.ram.value))