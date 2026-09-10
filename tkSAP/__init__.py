from pySAP import SAPisa, pySAP
from clock import Clock

from .constants import DEFAULTS
from .clock_thread import clock_thread
from .tkMGR import tkMGR
from .tkCLK import tkCLK
from .tkCPU import tkCPU
from .tkRAM import tkRAM

from tkinter.filedialog import askopenfilename

REFRESH_RATE = 2 # ms

MENU = {
    '_File': {
        '_Open and assemble source file to start of RAM...' : 'file_open',
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
        self.mgr = tkMGR("tkSAP")
        self.mgr.build_menu(self,MENU)
        # The system needs a clock, it needs a CPU, which needs an ISA.
        self.clk = Clock(cpu=pySAP(isa=SAPisa()))
        #self.clk.subscribe(self)
        self.code = None
        # Run said clock in its own thread.
        self.clock_thread = clock_thread(self.clk)
        self.started = False
        self.panes = self.mgr.build_panes()
        # Finally, populate the individual frames: clock,
        self.tkCLK = tkCLK(
            self.panes['CLK'],
            self.clk,
        )
        #, CPU
        self.tkCPU = tkCPU(
            self.panes['CPU'],
            self.clk.cpu,
        )
        #, and RAM.
        self.tkRAM = tkRAM(
            self.panes['RAM'],
            self.clk,
        )
        self.mgr.root.after(REFRESH_RATE,self.scheduled_update)
        self.mgr.root.mainloop()

    def update(self):
        if self.clk.cpu.oflags['HLT'].istrue():
            return
        self.tkCLK.update()
        self.tkCPU.update()
        self.tkRAM.update()

    def scheduled_update(self):
        self.update()
        self.mgr.root.after(REFRESH_RATE,self.scheduled_update)

#    def clock(self):
#        self.update()

    def file_open(self):
        self.clk.cpu.setram(
            self.clk.cpu.isa.assemble_file(
                askopenfilename(
                    defaultextension = DEFAULTS['EXT'],
                    initialdir       = DEFAULTS['DIR'],
                )
            )
        )

    def file_reset(self):
        self.clk.cpu = pySAP(isa=SAPisa(),code=self.code)

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
        if not self.started:
            self.started = True
            self.clock_thread.start()
        else:
            self.clock_thread.resume()

    def clock_stop(self):
        self.clock_thread.stop()
