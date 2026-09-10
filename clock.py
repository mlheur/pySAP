from time import sleep, time_ns as now

NS                 = 1000000000
THENTH_NS          = NS / 10
NOTIME_FRACTION    = 1000
PERF_HIST_LENGTH   = 10
PERF_HIST_TIME     = 0.1 * NS

class Clock():

    def __init__(self,cpu=None,Hz=None):
        self.cpu           = cpu
        self.Hz            = 0 if Hz is None else Hz
        self.subscribers   = list()
        self.NoTime        = 0
        self.next_pulse    = None
        self.perf_data     = None
        self.modify(self.Hz)

    def modify(self,Hz):
        if self.perf_data is not None:
            print(self.perf_data['history'])
        self.Hz                   = Hz
        self.period               = Hz if Hz == 0 else int((1*NS)/Hz)
        self.NoTime               = int((self.period / NOTIME_FRACTION) / NS)
        _now                      = now()
        self.perf_data            = dict()
        self.next_pulse           = _now + self.period
        #print(f'Set next_pulse={self.next_pulse}')
        self.perf_data['started'] = _now
        self.perf_data['cycles']  = 0
        self.perf_data['history'] = [None] * PERF_HIST_LENGTH
        # histptr will start at PERF_HIST_LENGTH - 1 so that histptr can be,
        # incremented before assignment, so that histptr is always pointing
        # to the most-recently-added entry.  UI updates will read the value
        # at histptr, which will always be valid.
        self.perf_data['histptr'] = PERF_HIST_LENGTH - 1

    def subscribe(self,subscriber):
        self.subscribers.append(subscriber)

    def pulse(self):
        # Gate ourselves until it's almost time to clock.
        _now = now()
        #print(f'Entering gate at {_now} period={self.period} NoTime={self.NoTime} next_pulse={self.next_pulse}')
        while (not(self.cpu.oflags['HLT'].istrue())) and (self.Hz != 0) and (_now < self.next_pulse):
            sleep(self.NoTime)
            _now = now()
        # Released from the gate, set the next goalpost.
        #print(f'Released from gate at {_now} period={self.period} NoTime={self.NoTime} next_pulse={self.next_pulse}')
        self.next_pulse += self.period
        #print(f'Advanced next_pulse={self.next_pulse}')
        # do the thing.
        self.cpu.clock(self.subscribers)
        self.perf_data['cycles'] += 1
        if (_now > self.perf_data['started'] + PERF_HIST_TIME):
            perfset = (self.perf_data['started'],_now,self.perf_data['cycles'])
            self.perf_data['started'] = _now
            self.perf_data['cycles']  = 0
            self.perf_data['histptr'] += 1
            self.perf_data['histptr'] %= PERF_HIST_LENGTH
            self.perf_data['history'][self.perf_data['histptr']] = perfset[2] / ((perfset[1] - perfset[0]) / NS)

    def run(self,cpu=None,ram=None,Hz=None):
        if cpu is not None:
            self.cpu = cpu
        if ram is not None:
            self.cpu.setram(ram)
        self.cpu.reset()
        if Hz is not None:
            self.modify(Hz)
        else:
            self.modify(self.Hz)
        while (not self.cpu.oflags['HLT'].istrue()):
            while self.Hz == 0:
                sleep(self.NoTime/NS)
            self.pulse()
        print(self.perf_data['history'])