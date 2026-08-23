from time import time
from time import sleep
from pynput import keyboard as kbd


class Clock():

    NoTime = 0.000001

    def __init__(self,Hz=0):
        self.Hz         = Hz # 0:manual
        self.freq       = 0
        if self.Hz > 0: self.freq = 1/self.Hz
        self.subscribers = list()
        self.pulse_lock  = False

        self.has_enter = False
        def keyhandler(key):
            if (self.has_enter == False or self.Hz == 0) and f'{key}' == "Key.enter":
                self.has_enter = True
        kbd.Listener(on_press=keyhandler).start()

    def subscribe(self,subscriber):
        self.subscribers.append(subscriber)

    def modify(self,Hz):
        oHz = self.Hz
        oFreq = self.freq
        self.freq = 0
        self.Hz = Hz
        self.freq = Hz if Hz == 0 else 1/Hz
        self.last_pulse = time() - self.freq

    def pulse(self):
        time_delta = time() - self.last_pulse
        while (self.Hz != 0) and (time_delta < self.freq) and (not(self.cpu.oflags['HLT'].istrue())):
            sleep(Clock.NoTime)
            time_delta = time() - self.last_pulse
        self.cpu.clock(self.subscribers)
        self.last_pulse = time()
        if self.Hz == 0:
            print("Press [Enter] to pulse the clock.")

    def run(self,cpu,ram=None):
        self.cpu = cpu
        if ram is not None:
            cpu.setram(ram)
        self.cpu.reset()
        self.last_pulse = time() - self.freq
        if self.Hz == 0:
            print("Press [Enter] to pulse the clock.")
        while (not self.cpu.oflags['HLT'].istrue()):
            if self.Hz == 0:
                for subby in self.subscribers:
                    if hasattr(subby,'redraw'):
                        subby.redraw()
                if self.has_enter:
                    self.has_enter = False
                    self.pulse()
                sleep(Clock.NoTime)
            else:
                self.pulse()

