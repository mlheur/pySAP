from time import sleep, time_ns as now
from pynput import keyboard as kbd

NS = 1000000000

class Clock():

    NoTime = 0.0000001

    def __init__(self,cpu=None,Hz=None):
        if Hz is None:
            Hz = 0
        self.cpu         = cpu
        self.last_pulse  = 0
        self.subscribers = list()
        self.performance = {
            'started': 0,
            'current': 0,
            'cycles' : 0,
            'value'  : 0,
        }
        self.modify(Hz)

    def reset_performance(self):
        self.performance['started'] = self.last_pulse
        self.performance['current'] = self.last_pulse
        self.performance['cycles']  = 0

    def update_performance(self):
        self.performance['current'] = self.last_pulse
        if self.performance['cycles'] > 1:
            dT = self.performance['current'] - self.performance['started']
            self.performance['value'] = (NS * self.performance['cycles']) / dT
            #print(f"Average Performance: {self.performance['value']:.2f} Hz, Target: {self.Hz}")
            for subby in self.subscribers:
                if hasattr(subby,"update_performance"):
                    subby.update_performance(self.performance['value'])
            self.reset_performance()

    def subscribe(self,subscriber):
        self.subscribers.append(subscriber)

    def modify(self,Hz):
        self.reset_performance()
        self.Hz           = Hz
        self.freq         = Hz if Hz == 0 else ((1*NS)/Hz)
        self.last_pulse   = max(self.last_pulse, now() - self.freq)

    def pulse(self):
        next_pulse = self.last_pulse + self.freq
        next_pulse -= (NS * Clock.NoTime)
        while (self.Hz != 0) and (self.last_pulse < next_pulse) and (not(self.cpu.oflags['HLT'].istrue())):
            sleep(Clock.NoTime)
            self.last_pulse = now()
        self.cpu.clock(self.subscribers)
        self.performance['cycles'] += 1
        if self.performance['current'] < (self.last_pulse-NS):
            self.update_performance()

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
        self.redraw()
        self.reset_performance()
        while (not self.cpu.oflags['HLT'].istrue()):
            while self.Hz == 0:
                self.redraw()
                # Check if any windows are closed, if yes then quit.
                for subby in self.subscribers:
                    if hasattr(subby,"count_open_windows") and subby.count_open_windows() < 3:
                        return
                sleep(Clock.NoTime)
            self.pulse()
