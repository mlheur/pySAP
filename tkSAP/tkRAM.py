from tkinter import Label, PhotoImage
from .constants import DEFAULTS, PROFILES


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
        self.hdr = f'P6\n{w} {h}\n15\n'.encode()
        self.pxl = bytearray(PROFILES["RAM"][False] * self.addrspace * self.clk.cpu.bits)
        self.bitmap = PhotoImage(data=self.hdr+self.pxl)
        self.canvas = Label(frame,image=self.bitmap)
        self.update_all()
        self.canvas.pack()

    def update_all(self):
        self.pxl = bytearray(PROFILES["RAM"][False] * self.addrspace * self.clk.cpu.bits)
        for addr in range(self.addrspace):
            self.update_byte(addr,with_update=False)
        self.bitmap.configure(
            data = self.hdr + self.pxl,
        )

    def update_byte(self,addr,with_update=True):
        pxladdr = self.clk.cpu.bits * addr
        byte = self.clk.cpu.ram.value[addr]
        for bitpos in range(self.clk.cpu.bits-1,-1,-1):
            #print(f'  bitpos={bitpos} bitmask={self.masks[bitpos]:08b}')
            is_lit = (byte & self.masks[bitpos]) > 0
            for rgb in [0,1,2]:
                self.pxl[rgb+(3*pxladdr)] = PROFILES["RAM"][is_lit][rgb]
            pxladdr += 1
        if with_update:
            self.bitmap.configure(
                data = self.hdr + self.pxl,
            )

    def clock(self):
        if self.next_clock is not None:
            self.update_byte(self.next_clock)
            self.next_clock = None
        else:
            self.next_clock = self.clk.cpu.mar.value
