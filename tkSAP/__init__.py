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

REFRESH_RATE = 500 # ms

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

    def mainloop(self):
        self.mgr.root.mainloop()

    def update(self):
        if self.clk.cpu.oflags['HLT'].istrue() and self.clock_thread.running:
            self.clock_stop()
        self.tkCLK.update()
        self.tkCPU.update()

    def clock(self):
        self.update()

    def scheduled_update(self):
        refrate = REFRESH_RATE if self.clock_thread.running else 10 * REFRESH_RATE
        self.update()
        self.mgr.root.after(refrate,self.scheduled_update)

    def update_all(self):
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
        self.tkRAM.update_all()
        self.tkCODE.reset()
        self.mgr.root.title(DEFAULTS['TITLE'])

    def file_quit(self):
        #print(f'Trying to quit')
        if not self.started:
            self.clock_run()
        self.clock_thread.stop(final=True)
        self.clock_thread.join()
        self.mgr.root.quit()
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
