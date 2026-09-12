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
        # Draw the current Input Flags beside the ring counter
        tkFlags = tkBitfield(
            getValue  = getInputFlags,
            wordSize  = len(self.clk.cpu.iflags),
            color     = "CYAN",
            title     = "FLG",
            flags     = self.clk.cpu.iflags,
            canvas    = self.canvas,
            x         = x + tkTstep.coords['w'],
            y         = y,
        )
        self.components.append(tkFlags)
        y += tkTstep.coords['h']
        # Draw the current RAM value
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
        y += tkRAM.coords['h']
        # Draw the Memory Address Register
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
        y += tkMAR.coords['h']
        # Draw the current Instruction Register value
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
        y += tkIR.coords['h']
        # Draw the current OUT1 value
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
        # COLUMN 2
        #####
        x += tkRAM.coords['w']
        y = 0
        # Draw the current Bus value
        y = tkRAM.coords['y']
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
        y += tkBUS.coords['h']
        #####
        # COLUMN 3
        #####
        x += tkBUS.coords['w']
        y = 0
        # Draw the current Program Counter valuewinfo screenheight
        tkPC = tkBitfield(
            getValue  = lambda : self.clk.cpu.pc.value,
            wordSize  = self.clk.cpu.pc.bits,
            color     = "GREEN",
            title     = "PC",
            canvas    = self.canvas,
            x         = x+tkBUS.coords['w'],
            y         = y,
            justify   = "right",
        )
        self.components.append(tkPC)
        y += tkPC.coords['h']
        # Draw the current A register value
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
        y += tkA.coords['h']
        # Draw the current A register value
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
        y += tkALU.coords['h']
        # Draw the current B register value
        tkTMP = tkBitfield(
            getValue  = lambda : self.clk.cpu.tmp.value,
            wordSize  = self.clk.cpu.tmp.bits,
            color     = "GREEN",
            title     = "TMP",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkTMP)
        y += tkTMP.coords['h']
        # Draw the current B register value
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
        y += tkB.coords['h']
        # Draw the current C register value
        tkC = tkBitfield(
            getValue  = lambda : self.clk.cpu.c.value,
            wordSize  = self.clk.cpu.c.bits,
            color     = "GREEN",
            title     = "C",
            canvas    = self.canvas,
            x         = x,
            y         = y,
        )
        self.components.append(tkC)
        y += tkC.coords['h']
        # Draw the current Output Control Lines
        tkCtls = tkBitfield(
            getValue  = getOutputFlags,
            wordSize  = len(self.clk.cpu.oflags),
            color     = "MAGENTA",
            title     = "CTL",
            flags     = self.clk.cpu.oflags,
            canvas    = self.canvas,
            x         = x + tkPC.coords['w'],
            y         = y,
            justify    = "right",
        )
        self.components.append(tkCtls)
        self.canvas.pack()
        self.canvas.config(
            width  = 3 * tkALU.coords['w'],
            height = 7 * tkALU.coords['h'],
        )

    def update(self):
        for c in self.components:
            c.update()
