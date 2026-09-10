from .tkBitfield import tkBitfield
from tkinter import Canvas


class tkCPU(object):
    def __init__(self,frame,cpu):
        self.frame      = frame
        self.canvas     = Canvas(self.frame,bd=0,highlightthickness=0)
        self.cpu        = cpu
        self.components = list()
        # Lambda functions to be called in by bitfield drawing routines
        def getFlags(flagset):
            result = 0
            for f in flagset:
                result |= flagset[f].value << flagset[f].pos
            return result
        def getInputFlags():
            return getFlags(self.cpu.iflags)
        def getOutputFlags():
            return getFlags(self.cpu.oflags)
        ###
        # COLUMN 1
        ###
        # Draw the Tstep from the Ring Counter
        x = 0
        y = 0
        tkTstep = tkBitfield(
            getValue  = lambda : self.cpu.ctlseq.Tstep,
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
            getValue  = lambda : self.cpu.mar.value,
            wordSize  = self.cpu.mar.bits,
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
            getValue  = lambda : self.cpu.ram.value[self.cpu.mar.value],
            wordSize  = self.cpu.ram.bits,
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
            getValue  = lambda : self.cpu.ir.value,
            wordSize  = self.cpu.ir.bits,
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
            wordSize  = len(self.cpu.iflags),
            color     = "CYAN",
            title     = "FLG",
            flags     = self.cpu.iflags,
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
            getValue  = lambda : self.cpu.w,
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
            getValue  = lambda : self.cpu.out.value,
            wordSize  = self.cpu.out.bits,
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
            getValue  = lambda : self.cpu.pc.value,
            wordSize  = self.cpu.pc.bits,
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
            getValue  = lambda : self.cpu.a.value,
            wordSize  = self.cpu.a.bits,
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
            getValue  = lambda : self.cpu.alu.value,
            wordSize  = self.cpu.alu.bits,
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
            getValue  = lambda : self.cpu.b.value,
            wordSize  = self.cpu.b.bits,
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
            wordSize  = len(self.cpu.oflags),
            color     = "MAGENTA",
            title     = "CTL",
            flags     = self.cpu.oflags,
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