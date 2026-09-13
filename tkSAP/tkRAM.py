from tkinter import Label, PhotoImage
from .constants import DEFAULTS, PROFILES


class tkRAM(object):
    def __init__(self,frame,clk):
        self.frame = frame
        self.clk   = clk
        self.clk.subscribe(self)
        self.addrspace = 2**self.clk.cpu.addrlen
        self.w = DEFAULTS['RAM_COLUMNS'] * self.clk.cpu.bits
        self.h = int(self.addrspace / DEFAULTS['RAM_COLUMNS'])
        self.next_clock = None
        self.masks = [None] * self.clk.cpu.bits
        for bitpos in range(self.clk.cpu.bits):
            self.masks[bitpos] = 1 << bitpos
        self.hdr = f'P6\n{self.w} {self.h}\n{PROFILES["RAM"]["BPP"]}\n'.encode()
        data = bytearray()
        for addr in range(self.addrspace * self.clk.cpu.bits):
            data.extend(PROFILES["RAM"][False])
        self.bitmap = PhotoImage(data=self.hdr+data)
        self.canvas = Label(frame,image=self.bitmap)
        #self.update_all()
        self.canvas.pack()

    def get_byte_pixeldata(self,addr):
        byte = self.clk.cpu.ram.value[addr]
        data = bytearray()
        for bitpos in range(self.clk.cpu.bits-1,-1,-1):
            data.extend(PROFILES["RAM"][(byte & self.masks[bitpos]) > 0])
        return data

    def get_byte_rgbdata(self,addr):
        byte = self.clk.cpu.ram.value[addr]
        data = []
        for bitpos in range(self.clk.cpu.bits-1,-1,-1):
            [r,g,b] = PROFILES["RAM"][(byte & self.masks[bitpos]) > 0]
            data.append(f'#{r:X}{g:X}{b:X}')
        return [data]

    def update_all(self):
        data = bytearray()
        for addr in range(self.addrspace):
            data.extend(self.get_byte_pixeldata(addr))
        self.bitmap.configure(
            data = self.hdr + data,
        )

    def update_byte(self,addr):
        pxladdr = (addr * self.clk.cpu.bits)
        #pxldata = self.get_byte_pixeldata(addr)
        data    = self.get_byte_rgbdata(addr)
        x = pxladdr % self.w
        y = int(pxladdr / self.w)
        #print(f'update_byte:\n  addr={addr}\n  pxladdr={pxladdr}\n  data={data}\n  x={x} y={y}')
        self.bitmap.put(
            data   = data,
            to     = (x,y),
        )

    def clock(self):
        if self.next_clock is not None:
            self.update_byte(self.next_clock)
            self.next_clock = None
        else:
            if self.clk.cpu.oflags['Lr'].istrue():
                self.next_clock = self.clk.cpu.mar.value
