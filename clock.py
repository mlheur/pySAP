from time import time as time
from time import sleep as sleep
from pynput import keyboard as kbd

class Clock():
    
    def __init__(self,Hz=0):
        self.Hz         = Hz # 0:manual
        self.freq       = 0
        if self.Hz > 0: self.freq = 1/self.Hz
        self.subscribers = list()
        self.pulse_lock  = False

        self.has_enter = False
        def keyhandler(key):
            if self.Hz == 0 and f'{key}' == "Key.enter":
                self.has_enter = True
        kbd.Listener(on_press=keyhandler).start()

    def subscribe(self,subscriber):
        self.subscribers.append(subscriber)

    def modify(self,Hz):
        self.freq = 0
        self.Hz = Hz
        if Hz>0: self.freq = 1/Hz

    def pulse(self):
        time_delta = time() - self.last_pulse
        if self.Hz > 0 and (time_delta < self.last_pulse + self.freq):
            sleep(time_delta)
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
                sleep(0.01)
            else:
                self.pulse()

