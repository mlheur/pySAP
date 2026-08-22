from time import time as time
from time import sleep as sleep


class Clock():
    
    def __init__(self,Hz=0):
        self.Hz         = Hz # 0:manual
        self.freq       = 0
        if self.Hz > 0: self.freq = 1/self.Hz
        self.subscribers = list()
        self.pulse_lock  = False

    def subscribe(self,subscriber):
        self.subscribers.append(subscriber)

    def modify(self,Hz):
        self.freq = 0
        self.Hz = Hz
        if Hz>0: self.freq = 1/Hz

    def pulse(self):
        self.pulse_lock = False

    def _pulse(self):
        self.cpu.clock(self.subscribers)
        self.last_pulse = time()

    def run(self,cpu,ram=None):
        self.cpu = cpu
        if ram is not None:
            cpu.setram(ram)
        self.cpu.reset()
        self.last_pulse = time() - self.freq
        while (not self.cpu.oflags['HLT'].istrue()):
            if self.Hz == 0:
                # Block until either: press enter on the console, or press button on gui
                self.pulse_lock = True
                input("Press [Enter] to pulse the clock.")
                self.pulse_lock = False
            elif self.Hz > 0:
                wait = self.last_pulse + self.freq - time()
                if wait > 0:
                    sleep(wait)
            self._pulse()

