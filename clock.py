from time import time as time
from time import sleep as sleep


class Clock():
    
    def __init__(self,Hz=0):
        self.Hz         = Hz # 0:manual
        self.freq       = 0
        if self.Hz > 0: self.freq = 1/self.Hz
        self.subscribers = list()

    def subscribe(self,subscriber):
        self.subscribers.append(subscriber)

    def run(self,cpu,ram=None):
        if ram is not None:
            cpu.setram(ram)
        cpu.reset()
        last_pulse = time() - self.freq
        while (not cpu.oflags['HLT'].istrue()):
            if self.Hz == 0:
                input("Press [Enter] to pulse the clock.")
            elif self.Hz > 0:
                wait = last_pulse + self.freq - time()
                if wait > 0:
                    sleep(wait)
            cpu.clock()
            for subscriber in self.subscribers:
                subscriber.clock()
            last_pulse = time()
