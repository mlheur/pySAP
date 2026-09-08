from .guiBitfield import guiBitfield
from .WindowMgr import RAM_COLUMNS
from .WindowMgr import SCROLLBAR_WIDTH
from tkinter import Canvas, Scrollbar, Frame

class guiRAM(object):
    def __init__(self,cpu,mgr):
        self.cpu  = cpu
        self.mgr  = mgr
        self.hWnd = self.mgr.newWindow("RAM")
        # Create the scrolling subwindow structures
        self.scrolling_canvas = Canvas(self.hWnd)
        self.vertical_scroll = Scrollbar(
            self.hWnd,
            orient  = "vertical",
            command = self.scrolling_canvas.yview,
            width   = SCROLLBAR_WIDTH,
        )
        self.vertical_scroll.pack(
            side   = "right",
            fill   = "y",
        )
        self.horizontal_scroll = Scrollbar(
            self.hWnd,
            orient  = "horizontal",
            command = self.scrolling_canvas.xview,
            width   = SCROLLBAR_WIDTH,
        )
        self.horizontal_scroll.pack(
            side   = "bottom",
            fill   = "x",
        )
        self.hFrame = Frame(self.scrolling_canvas)
        self.hFrame.bind(
            "<Configure>",
            lambda e: self.scrolling_canvas.configure(
                scrollregion = self.scrolling_canvas.bbox("all")
            )
        )
        self.scrolling_canvas.create_window(
            (0,0),
            window = self.hFrame,
            anchor = "nw",
        )
        self.scrolling_canvas.configure(
            xscrollcommand = self.horizontal_scroll.set,
            yscrollcommand = self.vertical_scroll.set,
        )
        self.scrolling_canvas.pack(
            side   = "left",
            fill   = "both",
            expand = True,
        )
        # Allocate a list that will hold pointers to the memory cell GUI objects.
        self.cells = list("-"*2**self.cpu.addrlen)
        #print(f'preallocated n={len(self.cells)} memory cells')
        # For each memory cell, create its graphical components and put them in the client area.
        for addr in range(len(self.cells)):
            memCell = guiBitfield(
                wordSize     = self.cpu.ram.bits,
                color        = "RED",
                title        = f'0x{addr:04X}',
                profile      = "SML",
                addr         = addr,
                getAddrValue = lambda addr : self.cpu.ram.value[addr],
            )
            col = 2 * (addr % RAM_COLUMNS)
            fn = self.mgr.addLabelledBitfieldToWindow if col == 0 else self.mgr.addUnlabelledBitfieldToWindow
            fn(
                self.hFrame,
                memCell,
                row       = int(addr / RAM_COLUMNS),
                col       = col,
                sticky    = "e",
            )
            self.cells[addr] = memCell
        self.updateAllCells()

    def updateAllCells(self):
        self.mgr.updateComponents(self.cells)
