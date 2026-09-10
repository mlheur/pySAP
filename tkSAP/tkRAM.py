from .tkBitfield import tkBitfield
from tkinter import Canvas
from .constants import DEFAULTS

class tkRAM(object):
    def __init__(self,frame,clk):
        self.frame = frame
        self.clk   = clk
        self.clk.subscribe(self)
        self.addrspace = 2**self.clk.cpu.addrlen
        self.canvas = Canvas(self.frame,bd=0,highlightthickness=0)
        x = 0
        y = 0
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
            if x >= DEFAULTS['RAM_COLUMNS'] * self.cells[addr].coords['w']:
                x = 0
                y += self.cells[addr].coords['h']
        self.update_all()
        self.canvas.pack()
        self.canvas.config(
            width  = DEFAULTS['RAM_COLUMNS'] * self.cells[0].coords['w'],
            height = (self.addrspace / DEFAULTS['RAM_COLUMNS']) * self.cells[0].coords['w'],
        )

    def update_all(self):
        for cell in self.cells:
            cell.update()

    def clock(self):
        if self.clk.cpu.oflags['Lr'].istrue():
            self.cells[self.clk.cpu.mar.value].update()
