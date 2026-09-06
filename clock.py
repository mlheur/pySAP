from time import sleep, time_ns as now

NS                     = 1000000000
TIME_FRACTION          = 1000


class Clock():

    def __init__(self,cpu=None,Hz=None):
        self.cpu          = cpu
        self.Hz           = 0 if Hz is None else Hz
        self.subscribers  = list()
        self.NoTime       = 0
        self.next_pulse   = None
        self.perf_data    = None

    def modify(self,Hz):
        self.Hz                   = Hz
        self.period               = Hz if Hz == 0 else int((1*NS)/Hz)
        self.NoTime               = int(self.period / TIME_FRACTION)
        _now                      = now()
        self.perf_data            = dict()
        self.next_pulse           = _now + self.period
        #print(f'Set next_pulse={self.next_pulse}')
        self.perf_data['started'] = _now
        self.perf_data['cycles']  = 0

    def subscribe(self,subscriber):
        self.subscribers.append(subscriber)

    def pulse(self):
        # Gate ourselves until it's almost time to clock.
        _now = now()
        #print(f'Entering gate at {_now} period={self.period} NoTime={self.NoTime} next_pulse={self.next_pulse}')
        while (not(self.cpu.oflags['HLT'].istrue())) and (self.Hz != 0) and (_now < self.next_pulse):
            sleep(self.NoTime/NS)
            _now = now()
        # Released from the gate, set the next goalpost.
        #print(f'Released from gate at {_now} period={self.period} NoTime={self.NoTime} next_pulse={self.next_pulse}')
        self.next_pulse += self.period
        #print(f'Advanced next_pulse={self.next_pulse}')
        # do the thing.
        self.cpu.clock(self.subscribers)
        self.perf_data['cycles'] += 1
        if (_now - self.perf_data['started'] > NS) :
            perfset = (self.perf_data['started'],_now,self.perf_data['cycles'])
            self.perf_data['started'] = _now
            self.perf_data['cycles']  = 0
            _Hz = perfset[2] / ((perfset[1] - perfset[0]) / NS)
            for subby in self.subscribers:
                if hasattr(subby,"update_performance"):
                    subby.update_performance(_Hz)

    def redraw(self):
        for subby in self.subscribers:
            if hasattr(subby,'redraw'):
                subby.redraw()

    def run(self,cpu=None,ram=None,Hz=None):
        if cpu is not None:
            self.cpu = cpu
        if ram is not None:
            self.cpu.setram(ram)
        self.cpu.reset()
        self.redraw()
        if Hz is not None:
            self.modify(Hz)
        else:
            self.modify(self.Hz)
        while (not self.cpu.oflags['HLT'].istrue()):
            while self.Hz == 0:
                self.redraw()
                # Check if any windows are closed, if yes then quit.
                for subby in self.subscribers:
                    if hasattr(subby,"count_open_windows") and subby.count_open_windows() < 3:
                        return
                sleep(self.NoTime/NS)
            self.pulse()
        #print(self.perf_history)