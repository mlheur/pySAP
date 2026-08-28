from time import perf_counter, process_time
from time import sleep
from pynput import keyboard as kbd


class Clock():

    NoTime = 0.00001

    def __init__(self,cpu=None,Hz=None):
        if Hz is None:
            Hz = 0
        self.cpu         = cpu
        self.last_pulse  = 0
        self.subscribers = list()
        self.reset_performance()
        self.modify(Hz)
        # Spawn a thread that listens for keyboard events to have non-blocking
        # I/O waiting for manual clock pulse from either the console or the GUI.
        self.has_enter = False
        def keyhandler(key):
            if (self.has_enter == False or self.Hz == 0) and f'{key}' == "Key.enter":
                self.has_enter = True
        kbd.Listener(on_press=keyhandler).start()

    def reset_performance(self):
        self.performance = {
            'started': self.last_pulse,
            'current': self.last_pulse,
            'cycles':  0,
        }

    def print_performance(self):
        self.performance['current'] = self.last_pulse
        if self.performance['cycles'] > 1:
            dT = self.performance['current'] - self.performance['started']
            aHz = self.performance['cycles'] / dT
            print(f'Average Performance: {aHz:.2f} Hz, Target: {self.Hz}')

    def subscribe(self,subscriber):
        self.subscribers.append(subscriber)

    def modify(self,Hz):
        self.print_performance()
        self.reset_performance()
        self.Hz         = Hz
        self.freq       = Hz if Hz == 0 else 1/Hz
        self.last_pulse = max(self.last_pulse, perf_counter() - self.freq)

    def pulse(self):
        time_delta = perf_counter() - self.last_pulse
        while (self.Hz != 0) and (time_delta < self.freq) and (not(self.cpu.oflags['HLT'].istrue())):
            sleep(Clock.NoTime)
            time_delta = perf_counter() - self.last_pulse
        self.last_pulse = perf_counter()
        self.cpu.clock(self.subscribers)
        self.performance['cycles'] += 1
        if self.performance['current'] < (self.last_pulse-4) and self.Hz > 0:
            self.print_performance()
            self.reset_performance()
        if self.Hz == 0:
            print("Press [Enter] to pulse the clock.")

    def redraw(self):
        for subby in self.subscribers:
            if hasattr(subby,'redraw'):
                subby.redraw()

    def run(self,cpu=None,ram=None,Hz=None):
        self.reset_performance()
        if cpu is not None:
            self.cpu = cpu
        if Hz is not None:
            self.modify(Hz)
        if ram is not None:
            self.cpu.setram(ram)
        self.cpu.reset()
        self.redraw()
        if self.Hz == 0:
            print("Press [Enter] to pulse the clock.")
        self.reset_performance()
        while (not self.cpu.oflags['HLT'].istrue()):
            if self.Hz == 0:
                self.redraw()
                if self.has_enter:
                    self.has_enter = False
                    self.pulse()
                sleep(Clock.NoTime)
            else:
                self.pulse()
        self.print_performance()
