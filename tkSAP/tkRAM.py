from .tkBitfield import tkBitfield
from tkinter import Canvas
from .constants import DEFAULTS

class tkRAM(object):
    def __init__(self,frame,clk):
        self.frame = frame
        self.clk   = clk
        self.clk.subscribe(self)
        self.addrspace = 2**self.clk.cpu.addrlen
        self.canvas = Canvas(self.frame,bg='#000',bd=0,highlightthickness=0)
        x = 0
        y = 0
        w = 0
        h = 0
        self.cells = [None] * self.addrspace
        for addr in range(self.addrspace):
            self.cells[addr] = tkBitfield(
                addr         = addr,
                getAddrValue = lambda addr : self.clk.cpu.ram.value[addr],
                wordSize     = self.clk.cpu.bits,
                color        = 'RED',
                title        = f'0x{addr:04X}',
                canvas       = self.canvas,
                x            = x,
                y            = y,
                show_label   = x == 0,
                profile      = 'SML',
            )
            x += self.cells[addr].coords['w']
            if y == 0:
                w += self.cells[addr].coords['w']
            if x >= DEFAULTS['RAM_COLUMNS'] * self.cells[addr].coords['w']:
                x = 0
                y += self.cells[addr].coords['h']
                if x == 0:
                    h += self.cells[addr].coords['h']
        self.update_all()
        self.canvas.pack()
        self.canvas.config(
            width  = w,
            height = h,
        )
        self.next_update = None

    def update_all(self):
        for cell in self.cells:
            cell.update()

    def clock(self):
        #print(f'Clocked tkRAM')
        if self.next_update is not None:
            #print(f'Redrawing RAM, addr={self.next_update}')
            self.cells[self.next_update].update()
            self.next_update = None
        elif self.clk.cpu.oflags['Lr'].istrue():
            self.next_update = self.clk.cpu.mar.value
            #print(f'Written to RAM, addr={self.next_update}')

