from .guiBitfield import guiBitfield


class guiRAM(object):
    def __init__(self,cpu,mgr):
        self.cpu  = cpu
        self.mgr  = mgr
        self.hWnd = self.mgr.createScrollingWindow(
            self.cpu.ram.bits,
            2**self.cpu.mar.bits,
            title = "RAM",
        )
        self.cells = list("-"*2**self.cpu.mar.bits)
        for addr in range(2**self.cpu.mar.bits):
            memCell = guiBitfield(
                wordSize     = self.cpu.ram.bits,
                color        = "RED",
                title        = f'0x{addr:04X}',
                profile      = "SML",
                addr         = addr,
                getAddrValue = lambda addr : self.cpu.ram.value[addr],
            )
            self.mgr.placeComponentAt(
                self.hWnd,
                memCell,
                row       = int(addr / self.mgr.RAM_COLUMNS),
                col       = 2 * (addr % self.mgr.RAM_COLUMNS),
                sticky    = "e",
                padx      = 0,
                pady      = 0,
            )
            self.cells[addr] = memCell
        self.updateAllCells()

    def updateAllCells(self):
        self.mgr.updateComponents(self.cells)
