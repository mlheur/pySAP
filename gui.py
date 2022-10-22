from tkinter import *
from guimgr import guimgr as guimgr

# Generic class for handling any kind of bitfield.
# This should be subclassed by a component that has
# some kind of binary value to display.
class gui_bitfield(object):
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

    def redraw(self,value):
        for bitpos,bitID in enumerate(self.bits):
            bitval = 0b1 & (value >> bitpos)
            self.gm.update_bit(self,bitID,bitval)

# Display which T step the controller/sequencer is on.
class gui_tstep(gui_bitfield):
    def __init__(self, gm, ctlseq, name = "T", row = 0, col = 0, color = "BLUE", justify = "left"):
        self.ctlseq = ctlseq
        self.bitlen = 4
        super().__init__(gm, name, row, col, color, justify = justify)
    def redraw(self):
        return super().redraw(self.ctlseq.Tstep)

# Display any standard register (aka CPU word) value.
class gui_register(gui_bitfield):
    def __init__(self, gm, reg, name, row, col, color = "GREEN", justify = "left"):
        self.reg = reg
        self.bitlen = reg.bits
        super().__init__(gm, name, row, col, color, justify = justify)
        self.redraw()
    def redraw(self):
        return super().redraw(self.reg.value)

# RAM is a special kind of array of registers, and we
# display one value based on the pointer in the Memory Address Register (MAR)
class gui_ram(gui_bitfield):
    def __init__(self, gm, cpu, name, row, col, color = "RED", justify = "left"):
        self.cpu = cpu
        self.bitlen = cpu.bits
        super().__init__(gm, name, row, col, color, justify = justify)
    def redraw(self):
        return super().redraw(self.cpu.ram.value[self.cpu.mar.value])

# Flags are different than registers because it's a list of bits rather than a word.
class gui_flags(gui_bitfield):
    def __init__(self, gm, flags, name, row, col, color = "CYAN", justify = "left"):
        self.flags = flags
        self.bitlen = len(self.flags)
        super().__init__(gm, name, row, col, color, justify = justify)
        for fname in self.flags.keys():
            gm.draw_bit_label(self, self.flags[fname].pos, fname)
    def redraw(self):
        result = 0
        for fname in (self.flags.keys()):
            #print("fname=[{}] value=[{}] pos=[{}]".format(fname,self.flags[fname].value,self.flags[fname].pos))
            result |= ( self.flags[fname].value << self.flags[fname].pos )
        #print("resulting value=[{}]".format(result))
        return super().redraw(result)


# The collection of gui components specific to pySAP1 cpu type.
class guiSAP1(object):
    def __init__(self,cpu,clk):
        self.cpu = cpu
        clk.subscribe(self) # Ask the clock to notify us on each pulse.
        self.gm = guimgr(bitlen = self.cpu.bits, rows = 6, cols = 2, title = "SAP1")

        self.components = list()
        self.components.append(gui_tstep(   self.gm, self.cpu.ctlseq,               row = 0, col = 0, justify = "left"))
        self.components.append(gui_register(self.gm, self.cpu.mar,    name = "MAR", row = 1, col = 0, justify = "right"))
        self.components.append(gui_ram(     self.gm, self.cpu,        name = "RAM", row = 2, col = 0))
        self.components.append(gui_register(self.gm, self.cpu.ir,     name = "IR",  row = 3, col = 0))
        self.components.append(gui_flags(   self.gm, self.cpu.iflags, name = "FLG", row = 4, col = 0, justify = "right"))
        self.components.append(gui_register(self.gm, self.cpu.pc,     name = "PC",  row = 0, col = 1, justify = "right"))
        self.components.append(gui_register(self.gm, self.cpu.a,      name = "A",   row = 1, col = 1))
        self.components.append(gui_register(self.gm, self.cpu.alu,    name = "ALU", row = 2, col = 1, color = "YELLOW"))
        self.components.append(gui_register(self.gm, self.cpu.b,      name = "B",   row = 3, col = 1))
        self.components.append(gui_register(self.gm, self.cpu.out,    name = "OUT", row = 4, col = 1, color = "WHITE"))
        self.components.append(gui_flags(   self.gm, self.cpu.oflags, name = "CTL", row = 5, col = 1, color = "MAGENTA", justify = "right"))
        self.gm.pack()

    # Redraw the bitfields after each clock cycle, must be subscribed to the clock.
    def clock(self):
        for comp in self.components:
            comp.redraw()
        self.gm.redraw()

    # Tk nuance.
    def wait_for_close(self):
        self.gm.wait_for_close()