from .WindowMgr import WindowMgr
from .guiBitfield import guiBitfield
from .guiClockCtl import guiClockCtl
from .guiRAM import guiRAM
from .guiCPU import guiCPU


class guiSAP(object):
    def __init__(self,cpu,clk):
        clk.subscribe(self)
        self.cpu = cpu
        self.clk = clk
        self.mgr = WindowMgr(self)
        # Create a RAM window
        self.ram_window = guiRAM(self.cpu,self.mgr)
        self.mgr.refreshWindows()
        # Create a CPU window
        self.cpu_window = guiCPU(self.cpu,self.mgr)
        self.mgr.refreshWindows()
        # Reposition the CPU window adjacent to the RAM window
        xoff = self.ram_window.hWnd.winfo_width() + self.mgr.getWmgrX()
        _w = self.cpu_window.hWnd.winfo_width()
        _h = self.cpu_window.hWnd.winfo_height()
        self.cpu_window.hWnd.geometry(f'{_w}x{_h}+{xoff}+0')
        self.mgr.refreshWindows()
        yoff = self.cpu_window.hWnd.winfo_height() + self.mgr.getWmgrY()
        # Create a clock-controller window
        self.clock_ctl = guiClockCtl(
            self.cpu,
            self.mgr,
            self.clk,
        )
        self.mgr.refreshWindows()
        # Reposition the clock-controller window
        _w = self.clock_ctl.hWnd.winfo_width()
        _h = self.clock_ctl.hWnd.winfo_height()
        self.clock_ctl.hWnd.geometry(f'{_w}x{_h}+{xoff}+{yoff}')
        self.mgr.refreshWindows()
        self._previous_latch = None
        # Update the bulbs' on/off state
        self.clock()

    def redraw(self):
        self.mgr.refreshWindows()

    def clock(self):
        self.mgr.updateComponents(self.cpu_window.components)
        if self._previous_latch is not None:
            addr = self._previous_latch
            self._previous_latch = None
            self.mgr.updateComponents([self.ram_window.cells[addr]])
        elif self.cpu.oflags['Lr'].istrue():
            addr = self.cpu.mar.value
            self._previous_latch = addr
        self.mgr.refreshWindows()

    def wait_for_close(self):
        self.mgr.refreshWindows()
        self.mgr.tkroot.mainloop()
        self.mgr.quit()
