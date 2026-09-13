from tkinter import Label, PhotoImage
from .constants import DEFAULTS, PROFILES

from threading import Thread


class tkRAM(object):
    def __init__(self,frame,clk):
        self.frame = frame
        self.clk   = clk
        self.clk.subscribe(self)
        self.addrspace = 2**self.clk.cpu.addrlen
        w = DEFAULTS['RAM_COLUMNS'] * self.clk.cpu.bits
        h = int(self.addrspace / DEFAULTS['RAM_COLUMNS'])
        #print(f'w={w},h={h}')
        #self.canvas = Canvas(
        #    self.frame,
        #    bg                 = '#000',
        #    bd                 = 0,
        #    highlightthickness = 0,
        #    width              = w,
        #    height             = h,
        #)
        self.next_clock = None
        self.masks = [None] * self.clk.cpu.bits
        for bitpos in range(self.clk.cpu.bits):
            self.masks[bitpos] = 1 << bitpos
        hdr = f'P6\n{w} {h}\n255\n'.encode()
        pxl = bytearray(PROFILES["RAM"][False] * self.addrspace * self.clk.cpu.bits)
        self.bitmap = PhotoImage(data=hdr+pxl)
        self.canvas = Label(frame,image=self.bitmap)
        self.update_all()
        self.canvas.pack()

    def update_all(self):
        pxl = bytearray(PROFILES["RAM"][False] * self.addrspace * self.clk.cpu.bits)
        for addr in range(self.addrspace):

    def update_byte(self,addr=None):
        if addr is None:
            addr = self.next_clock
            self.next_clock = None
        to      = (self.clk.cpu.bits * addr,1)
        byte    = self.clk.cpu.ram.value[addr]
        pxl     = bytearray()
        for bitpos in range(self.clk.cpu.bits-1,-1,-1):
            pxl.extend(PROFILES["RAM"][(byte & self.masks[bitpos]) > 0])
        self.bitmap.put(
            data = f'P6\n{self.clk.cpu.bits} 1\n255\n'.encode()+pxl,
            to   = to
        )

    def clock(self):
        if self.next_clock is not None:
            Thread(target=self.update_byte).run()
        else:
            self.next_clock = self.clk.cpu.mar.value
