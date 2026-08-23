from time import time
from time import sleep
from pynput import keyboard as kbd


class Clock():

    NoTime = 0.000001

    def __init__(self,cpu=None,Hz=0):
        self.cpu         = cpu
        self.last_pulse  = 0
        self.subscribers = list()
        self.modify(Hz)
        # Spawn a thread that listens for keyboard events to have non-blocking
        # I/O waiting for manual clock pulse from either the console or the GUI.
        self.has_enter = False
        def keyhandler(key):
            if (self.has_enter == False or self.Hz == 0) and f'{key}' == "Key.enter":
                self.has_enter = True
        kbd.Listener(on_press=keyhandler).start()

    def subscribe(self,subscriber):
        self.subscribers.append(subscriber)

    def modify(self,Hz):
        self.Hz         = Hz
        self.freq       = Hz if Hz == 0 else 1/Hz
        self.last_pulse = max(self.last_pulse, time() - self.freq)

    def pulse(self):
        time_delta = time() - self.last_pulse
        while (self.Hz != 0) and (time_delta < self.freq) and (not(self.cpu.oflags['HLT'].istrue())):
            sleep(Clock.NoTime)
            time_delta = time() - self.last_pulse
        self.last_pulse = time()
        self.cpu.clock(self.subscribers)
        if self.Hz == 0:
            print("Press [Enter] to pulse the clock.")

    def redraw(self):
        for subby in self.subscribers:
            if hasattr(subby,'redraw'):
                subby.redraw()

    def run(self,cpu=None,ram=None,Hz=None):
        if cpu is not None:
            self.cpu = cpu
        if Hz is not None:
            self.modify(Hz)
        if ram is not None:
            self.cpu.setram(ram)
        self.cpu.reset()
        self.last_pulse = time() - self.freq
        self.redraw()
        if self.Hz == 0:
            print("Press [Enter] to pulse the clock.")
        while (not self.cpu.oflags['HLT'].istrue()):
            if self.Hz == 0:
                self.redraw()
                if self.has_enter:
                    self.has_enter = False
                    self.pulse()
                sleep(Clock.NoTime)
            else:
                self.pulse()
