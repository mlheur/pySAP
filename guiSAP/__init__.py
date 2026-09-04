from .WindowMgr import WindowMgr
from .guiBitfield import guiBitfield
from .guiClockCtl import guiClockCtl
from .guiRAM import guiRAM
from .guiCPU import guiCPU
from time import sleep
from tkinter import TclError


class guiSAP(object):
    def __init__(self,cpu,clk):
        clk.subscribe(self)
        self.cpu = cpu
        self.clk = clk
        self.mgr = WindowMgr(self)
        self.windows = dict()
        # Create a RAM window
        self.windows["ram"] = guiRAM(self.cpu,self.mgr)
        self.mgr.refreshWindows()
        xoff = 0
        yoff = 0
        _w = self.windows["ram"].hWnd.winfo_width()
        _h = self.windows["ram"].hWnd.winfo_height()
        self.windows["ram"].hWnd.geometry(f'{_w}x{_h}+{xoff}+{yoff}')
        # Create a CPU window
        self.windows["cpu"] = guiCPU(self.cpu,self.mgr)
        self.mgr.refreshWindows()
        # Reposition the CPU window adjacent to the RAM window
        xoff = self.windows["ram"].hWnd.winfo_width() + self.mgr.getWmgrX()
        _w = self.windows["cpu"].hWnd.winfo_width()
        _h = self.windows["cpu"].hWnd.winfo_height()
        self.windows["cpu"].hWnd.geometry(f'{_w}x{_h}+{xoff}+0')
        self.mgr.refreshWindows()
        # Create a clock-controller window
        self.windows["clk"] = guiClockCtl(
            self.cpu,
            self.mgr,
            self.clk,
        )
        self.mgr.refreshWindows()
        # Reposition the clock-controller window
        yoff = self.windows["cpu"].hWnd.winfo_height() + self.mgr.getWmgrY()
        _w = self.windows["clk"].hWnd.winfo_width()
        _h = self.windows["clk"].hWnd.winfo_height()
        self.windows["clk"].hWnd.geometry(f'{_w}x{_h}+{xoff}+{yoff}')
        self.mgr.refreshWindows()
        self._previous_latch = None
        # Update the bulbs' on/off state
        self.clock()

    def redraw(self):
        self.mgr.refreshWindows()

    def clock(self):
        self.mgr.updateComponents(self.windows["cpu"].components)
        if self._previous_latch is not None:
            addr = self._previous_latch
            self._previous_latch = None
            self.mgr.updateComponents([self.windows["ram"].cells[addr]])
        elif self.cpu.oflags['Lr'].istrue():
            addr = self.cpu.mar.value
            self._previous_latch = addr
        self.mgr.refreshWindows()

    def count_open_windows(self):
        n = 0
        try:
            for wnd in self.windows:
                if self.windows[wnd].hWnd.winfo_ismapped():
                    n += 1
        except TclError as TE:
            return 0
        return n

    def wait_for_close(self):
        while self.count_open_windows() >= 3:
            self.mgr.refreshWindows()
            sleep(0.01)
        self.mgr.quit()
