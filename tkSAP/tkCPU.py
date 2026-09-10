from .tkBitfield import tkBitfield
from tkinter import Canvas


class tkCPU(object):
    def __init__(self,frame,clk):
        self.frame      = frame
        self.canvas     = Canvas(self.frame,bg='#000',bd=0,highlightthickness=0)
        self.clk        = clk
        self.components = list()
        # Lambda functions to be called in by bitfield drawing routines
        def getFlags(flagset):
            result = 0
            for f in flagset:
                result |= flagset[f].value << flagset[f].pos
            return result
        def getInputFlags():
            return getFlags(self.clk.cpu.iflags)
        def getOutputFlags():
            return getFlags(self.clk.cpu.oflags)
        ###
        # COLUMN 1
        ###
        # Draw the Tstep from the Ring Counter
        x = 0
        y = 0
        tkTstep = tkBitfield(
            getValue  = lambda : self.clk.cpu.ctlseq.Tstep,
            wordSize  = 4,
            color     = "BLUE",
            title     = "T",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkTstep)
        # Draw the Memory Address Register
        y += tkTstep.coords['h']
        tkMAR = tkBitfield(
            getValue  = lambda : self.clk.cpu.mar.value,
            wordSize  = self.clk.cpu.mar.bits,
            color     = "GREEN",
            title     = "MAR",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkMAR)
        # Draw the current RAM value
        y += tkMAR.coords['h']
        tkRAM = tkBitfield(
            getValue  = lambda : self.clk.cpu.ram.value[self.clk.cpu.mar.value],
            wordSize  = self.clk.cpu.ram.bits,
            color     = "RED",
            title     = "RAM",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkRAM)
        # Draw the current Instruction Register value
        y += tkRAM.coords['h']
        tkIR = tkBitfield(
            getValue  = lambda : self.clk.cpu.ir.value,
            wordSize  = self.clk.cpu.ir.bits,
            color     = "GREEN",
            title     = "IR",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkIR)
        # Draw the current Input Flags
        y += tkIR.coords['h']
        tkFlags = tkBitfield(
            getValue  = getInputFlags,
            wordSize  = len(self.clk.cpu.iflags),
            color     = "CYAN",
            title     = "FLG",
            flags     = self.clk.cpu.iflags,
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkFlags)
        #####
        # COLUMN 2
        #####
        x += tkMAR.coords['w']
        # Draw the current Bus value
        y = 0
        y = tkMAR.coords['y']
        tkBUS = tkBitfield(
            getValue  = lambda : self.clk.cpu.w,
            wordSize  = 8,
            color     = "RED",
            title     = "BUS",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkBUS)
        # Draw the current OUT1 value
        y = tkIR.coords['y']
        tkOUT = tkBitfield(
            getValue  = lambda : self.clk.cpu.out.value,
            wordSize  = self.clk.cpu.out.bits,
            color     = "WHITE",
            title     = "OUT",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkOUT)
        #####
        # COLUMN 3
        #####
        x += tkBUS.coords['w']
        # Draw the current Program Counter valuewinfo screenheight
        y = 0
        tkPC = tkBitfield(
            getValue  = lambda : self.clk.cpu.pc.value,
            wordSize  = self.clk.cpu.pc.bits,
            color     = "GREEN",
            title     = "PC",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkPC)
        # Draw the current A register value
        y += tkPC.coords['h']
        tkA = tkBitfield(
            getValue  = lambda : self.clk.cpu.a.value,
            wordSize  = self.clk.cpu.a.bits,
            color     = "GREEN",
            title     = "A",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkA)
        # Draw the current A register value
        y += tkA.coords['h']
        tkALU = tkBitfield(
            getValue  = lambda : self.clk.cpu.alu.value,
            wordSize  = self.clk.cpu.alu.bits,
            color     = "YELLOW",
            title     = "ALU",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkALU)
        # Draw the current B register value
        y += tkALU.coords['h']
        tkB = tkBitfield(
            getValue  = lambda : self.clk.cpu.b.value,
            wordSize  = self.clk.cpu.b.bits,
            color     = "GREEN",
            title     = "B",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkB)
        # Draw the current Output Control Lines
        y += tkB.coords['h']
        tkCtls = tkBitfield(
            getValue  = getOutputFlags,
            wordSize  = len(self.clk.cpu.oflags),
            color     = "MAGENTA",
            title     = "CTL",
            flags     = self.clk.cpu.oflags,
            canvas    = self.canvas,
            x         = x + tkB.coords['w'],
            y         = y,
            justify    = "right",
        )
        self.components.append(tkCtls)
        self.canvas.pack()
        self.canvas.config(
            width  = 3 * tkALU.coords['w'],
            height = 5 * tkALU.coords['h'],
        )

    def update(self):
        for c in self.components:
            c.update()