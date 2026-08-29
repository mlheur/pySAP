from tkinter import *
from .guiMgr import guiMgr
from .guiScrolling import guiScrolling
from .guiClock import guiClock

from time import sleep


# Generic class for handling any kind of bitfield.
# This should be subclassed by a component that has
# some kind of binary value to display.
class _bitfield(object):
    def __init__(self, gm, name, row, col, color, justify = "left"):
        self.gm = gm
        self.name = name
        self.row = row
        self.col = col
        self.color = color
        if self.bitlen is None: self.bitlen = self.gm.bitlen
        self.justify = justify
        self.coords = self.gm.draw_bitfield(self)
        self.bits = list()
        for bitpos in range(self.bitlen):
            self.bits.append(self.gm.draw_bit(self,bitpos))
        self.oldValue = None

    def redraw(self,value):
        if self.oldValue is not None and self.oldValue == value:
            return
        self.oldValue = value
        for bitpos,bitID in enumerate(self.bits):
            bitval = 0b1 & (value >> bitpos)
            self.gm.update_bit(self,bitID,bitval)

# Display which T step the controller/sequencer is on.
class _tstep(_bitfield):
    def __init__(self, gm, ctlseq, name = "T", row = 0, col = 0, color = "BLUE", justify = "left"):
        self.ctlseq = ctlseq
        self.bitlen = 4
        super().__init__(gm, name, row, col, color, justify = justify)
    def redraw(self):
        return super().redraw(self.ctlseq.Tstep)

# Display any standard register (aka CPU word) value.
class _register(_bitfield):
    def __init__(self, gm, reg, name, row, col, color = "GREEN", justify = "left"):
        self.reg = reg
        self.bitlen = reg.bits
        super().__init__(gm, name, row, col, color, justify = justify)
        self.redraw()
    def redraw(self):
        return super().redraw(self.reg.value)

# Display any standard register (aka CPU word) value.
class _bus(_bitfield):
    def __init__(self, gm, cpu, name, row, col, color = "RED", justify = "left"):
        self.cpu = cpu
        self.bitlen = self.cpu.bits
        super().__init__(gm, name, row, col, color, justify = justify)
        self.redraw()
    def redraw(self):
        return super().redraw(self.cpu.w)

# RAM is a special kind of array of registers, and we
# display one value based on the pointer in the Memory Address Register (MAR)
class _ram_register(_bitfield):
    def __init__(self, gm, cpu, name = "RAM", row = 0, col = 0, color = "RED", justify = "left", address = None):
        self.cpu = cpu
        self.bitlen = cpu.bits
        self.address = address
        super().__init__(gm, name, row, col, color, justify = justify)
        self.redraw()
    def redraw(self):
        addr = self.cpu.ir.value if self.address is None else self.address
        return super().redraw(self.cpu.ram.value[addr])

# Flags are different than registers because it's a list of bits rather than a word.
class _flags(_bitfield):
    def __init__(self, gm, flags, name, row, col, color = "CYAN", justify = "left"):
        self.flags = flags
        self.bitlen = len(self.flags)
        super().__init__(gm, name, row, col, color, justify = justify)
        for fname in self.flags.keys():
            label = fname
            label_color = "#303"
            if self.flags[fname].inv == 1:
                # label = "-{}-".format(fname)
                label_color = "#f9f"
            gm.draw_bit_label(self, self.flags[fname].pos, label, label_color)
    def redraw(self):
        result = 0
        for fname in (self.flags.keys()):
            #print("fname=[{}] value=[{}] pos=[{}]".format(fname,self.flags[fname].value,self.flags[fname].pos))
            result |= ( self.flags[fname].value << self.flags[fname].pos )
        #print("resulting value=[{}]".format(result))
        return super().redraw(result)


# The collection of gui components specific to pySAP1 cpu type.
class guiSAP(object):
    def __init__(self,cpu,clk):
        self.cpu = cpu
        clk.subscribe(self) # Ask the clock to notify us on each pulse.
        self.gm = guiMgr(bitlen = self.cpu.bits, rows = 5, cols = 3, title = "SAP CPU: Registers, Flags and Control Lines")

        self.components = list()
        self.components.append(_tstep(   self.gm, self.cpu.ctlseq, name = "T",    row = 0, col = 0, justify = "left"))
        self.components.append(_register(self.gm, self.cpu.mar,    name = "MAR",  row = 1, col = 0, justify = "right"))
        self.components.append(_ram_register(self.gm, self.cpu,                   row = 2, col = 0))
        self.components.append(_register(self.gm, self.cpu.ir,     name = "IR",   row = 3, col = 0))
        self.components.append(_flags(   self.gm, self.cpu.iflags, name = "FLG",  row = 4, col = 0, justify = "left"))
        self.components.append(_register(self.gm, self.cpu.pc,     name = "PC",   row = 0, col = 2, justify = "right"))
        self.components.append(_register(self.gm, self.cpu.a,      name = "A",    row = 1, col = 2))
        self.components.append(_register(self.gm, self.cpu.alu,    name = "ALU",  row = 2, col = 2, color = "YELLOW"))
        self.components.append(_register(self.gm, self.cpu.b,      name = "B",    row = 3, col = 2))
        self.components.append(_register(self.gm, self.cpu.out,    name = "OUT",  row = 3, col = 1, color = "WHITE"))
        self.components.append(_flags(   self.gm, self.cpu.oflags, name = "CTL",  row = 4, col = 2, color = "MAGENTA", justify = "right"))
        self.components.append(_bus(     self.gm, self.cpu,        name = "BUS",  row = 1, col = 1))
        self.gm.pack()

        self.rgm = guiScrolling( bitlen = self.cpu.bits, cols = 1, rows = 2**self.cpu.addrlen, title = "RAM",
        border = 1, ppb = 16, label_width = 120, font_label_size = 12 )
        for addr in range(2**self.cpu.addrlen):
            self.components.append(_ram_register(self.rgm, self.cpu, row = addr, col = 0, address=addr, name = "0x{:02X}".format(addr)))
        self.rgm.pack()

        self.rgm.refreshwnd()
        self.gm.tkwnd.geometry(f'{self.gm.tkwnd.winfo_width()}x{self.gm.tkwnd.winfo_height()}+{10+self.rgm.tkwnd.winfo_width()}+0')
        self.gm.refreshwnd()
        self.clk_ctl = guiClock(
            clk,
            self.gm,
            self.rgm.tkwnd.winfo_width(),
            self.gm.tkwnd.winfo_height()
        )

    # Redraw the bitfields after each clock cycle, must be subscribed to the clock.
    def clock(self):
        for comp in self.components:
            comp.redraw()
        if self.cpu.oflags['Lr'].istrue():
            self.rgm.refreshwnd()
        self.gm.refreshwnd()
        self.clk_ctl.refreshwnd()

    # Tk nuance.
    def wait_for_close(self):
        bGM = 1
        bRGM = 1
        bCLK = 1
        while bGM + bRGM + bCLK >= 3:
            try:
                bGM = self.gm.tkwnd.winfo_ismapped()
                bRGM = self.rgm.tkwnd.winfo_ismapped()
                bCLK = self.clk_ctl.tkwnd.winfo_ismapped()
                sleep(0.01)
                self.gm.tkwnd.update()
                self.rgm.tkwnd.update()
                self.clk_ctl.tkwnd.update()
            except:
                break
        self.gm.tkwnd.quit()
        self.rgm.tkwnd.quit()
        self.clk_ctl.tkwnd.quit()
