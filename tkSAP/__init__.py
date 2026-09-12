from pySAP import SAPisa, pySAP
from clock import Clock

from .constants import DEFAULTS
from .clock_thread import clock_thread
from .tkMGR import tkMGR
from .tkCLK import tkCLK
from .tkCPU import tkCPU
from .tkRAM import tkRAM
from .tkCODE import tkCODE

from tkinter.filedialog import askopenfilename

REFRESH_RATE = 20 # ms

MENU = {
    '_File': {
        '_Open and assemble source file to start of RAM...' : 'file_open',
        '_Wipe RAM'                                         : 'file_wiperam',
        '_Reset CPU'                                        : 'file_reset',
        '---'                                               : None,
        '_Quit'                                             : 'file_quit',
    },
    '_Clock' : {
        '_Run'                                              : 'clock_run',
        '_Stop'                                             : 'clock_stop',
    },
}


class tkSAP(object):
    def __init__(self):
        # A main window will have some subframes / panels.
        self.mgr = tkMGR(DEFAULTS['TITLE'])
        self.mgr.build_menu(self,MENU)
        # The system needs a clock, it needs a CPU, which needs an ISA.
        self.clk = Clock(cpu=pySAP(isa=SAPisa(),addrlen=12))
        self.clk.subscribe(self)
        self.code = None
        self.cpu_state = dict()
        self.capture_cpu_bits()
        self.capture_cpu_state()
        # Run said clock in its own thread.
        self.clock_thread = clock_thread(self.clk)
        self.started = False
        self.panes = self.mgr.build_panes()
        # Finally, populate the individual frames: clock,
        self.tkCLK = tkCLK(
            self.panes['CLK'],
            self.clk,
            self,
        )
        #, CPU
        self.tkCPU = tkCPU(
            self.panes['CPU'],
            self.clk,
            self,
        )
        #, and RAM.
        self.tkRAM = tkRAM(
            self.panes['RAM'],
            self.clk,
        )
        self.tkCODE = tkCODE (
            self.panes['CODE'],
            self.clk,
        )
        self.mgr.root.after(REFRESH_RATE,self.scheduled_update)
        self.file_open(DEFAULTS['PROGRAM'])

    def capture_cpu_bits(self):
        for reg in self.clk.cpu.components:
            self.cpu_state[reg]         = dict()
            self.cpu_state[reg]['bits'] = self.clk.cpu.components[reg].bits
        for reg in ['FLG','CTL','STP','BUS',]:
            self.cpu_state[reg] = dict()
        self.cpu_state['FLG']['bits'] = len(self.clk.cpu.iflags)
        self.cpu_state['CTL']['bits'] = len(self.clk.cpu.oflags)
        self.cpu_state['STP']['bits'] = 4
        self.cpu_state['BUS']['bits'] = self.clk.cpu.bits

    def capture_cpu_state(self):
        for reg in self.clk.cpu.components:
            if reg == "RAM":
                self.cpu_state[reg]['value'] = self.clk.cpu.components["RAM"].value[self.clk.cpu.components["MAR"].value]
            else:
                self.cpu_state[reg]['value'] = self.clk.cpu.components[reg].value
        self.cpu_state['FLG']['value'] = self.clk.cpu.ctlseq.iflags()
        self.cpu_state['CTL']['value'] = self.clk.cpu.ctlseq.oflags()
        self.cpu_state['STP']['value'] = self.clk.cpu.ctlseq.Tstep
        self.cpu_state['BUS']['value'] = self.clk.cpu.w

    def mainloop(self):
        self.mgr.root.mainloop()

    def update(self):
        if self.clk.cpu.oflags['HLT'].istrue() and self.clock_thread.running:
            self.clock_stop()
        self.tkCLK.update()
        self.tkCPU.update()

    def clock(self):
        self.capture_cpu_state()

    def scheduled_update(self):
        refrate = REFRESH_RATE if self.clock_thread.running else 10 * REFRESH_RATE
        self.update()
        self.mgr.root.after(refrate,self.scheduled_update)

    def update_all(self):
        self.capture_cpu_state
        self.tkCLK.update()
        self.tkCPU.update()
        self.tkRAM.update_all()

    def file_open(self,fname=None):
        if fname is None:
            fname = askopenfilename(
                defaultextension = DEFAULTS['EXT'],
                initialdir       = DEFAULTS['DIR'],
            )
        self.file_reset()
        self.clk.cpu.setram(self.clk.cpu.isa.assemble_file(fname))
        self.mgr.root.title(f'{DEFAULTS["TITLE"]}: {fname}')
        self.tkCODE.loadfile(fname)
        self.update_all()

    def file_reset(self):
        self.clock_stop()
        self.clk.cpu.w = 0
        for f in self.clk.cpu.oflags:
            self.clk.cpu.oflags[f].value = 0
        #self.clk.pulse()
        self.update_all()

    def file_wiperam(self):
        for i in range(len(self.clk.cpu.ram.value)):
            self.clk.cpu.ram.value[i] = 0
        self.tkCODE.reset()
        self.mgr.root.title(DEFAULTS['TITLE'])
        self.update_all()

    def file_quit(self):
        #print(f'Trying to quit')
        self.mgr.root.quit()
        if self.started:
            self.clock_thread.stop(final=True)
            self.clock_thread.join()
        from sys import exit
        exit(0)

    def clock_run(self):
        self.clk.pulse()
        if not self.started:
            self.started = True
            self.clock_thread.start()
        self.clock_thread.resume()

    def clock_stop(self):
        self.clock_thread.stop()
