from .WindowMgr import WindowMgr
from .guiBitfield import guiBitfield

class guiSAP(object):
    def __init__(self,cpu,clk):
        clk.subscribe(self)
        self.cpu = cpu
        self.clk = clk
        self.mgr = WindowMgr(self)

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

        self.windows = {
            'CPU': self.mgr.createWindow(
                title = "CPU: Registers, Flags and Control Lines",
            ),
            'RAM': self.mgr.createScrollingWindow(
                self.cpu.ram.bits,
                2**self.cpu.mar.bits,
                title = "RAM",
            ),
            #'CLK': self.mgr.createWindow(
                #title = "Clock",
            #),
        }

        self.components = []

        for addr in range(2**self.cpu.mar.bits):
            memCell = guiBitfield(
                getValue  = lambda : self.cpu.ram.value[addr],
                wordSize  = self.cpu.ram.bits,
                color     = "RED",
                title     = f'0x{addr:04X}',
                profile   = "SML",
            )
            self.mgr.placeComponentAt(
                self.windows['RAM'],
                memCell,
                row       = addr,
                col       = 0,
                sticky    = "e",
            )
        # Resize and position the RAM window on the left of the screen
        self.mgr.refreshWindows()

        ###
        # COLUMN 1
        ###

        # Draw the Tstep from the Ring Counter
        guiTstep = guiBitfield(
            getValue  = lambda : self.cpu.ctlseq.Tstep,
            wordSize  = 4,
            color     = "BLUE",
            title     = "T",
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiTstep,
            row        = 0,
            col        = 0,
            columnspan = 2,
            sticky     = "e"
        )
        self.components.append(guiTstep)

        # Draw the Memory Address Register
        guiMAR = guiBitfield(
            getValue  = lambda : self.cpu.mar.value,
            wordSize  = self.cpu.mar.bits,
            color     = "GREEN",
            title     = "MAR"
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiMAR,
            row        = 1,
            col        = 0,
            columnspan = 2,
        )
        self.components.append(guiMAR)

        # Draw the current RAM value
        guiRAM = guiBitfield(
            getValue  = lambda : self.cpu.ram.value[self.cpu.mar.value],
            wordSize  = self.cpu.ram.bits,
            color     = "RED",
            title     = "RAM",
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiRAM,
            row        = 2,
            col        = 0,
            columnspan = 2,
        )
        self.components.append(guiRAM)

        # Draw the current Instruction Register value
        guiIR = guiBitfield(
            getValue  = lambda : self.cpu.ir.value,
            wordSize  = self.cpu.ir.bits,
            color     = "GREEN",
            title     = "IR"
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiIR,
            row        = 3,
            col        = 0,
            columnspan = 2,
        )
        self.components.append(guiIR)

        # Draw the current Input Flags
        guiFlags = guiBitfield(
            getValue  = getInputFlags,
            wordSize  = len(self.cpu.iflags),
            color     = "CYAN",
            title     = "FLG",
            flags     = self.cpu.iflags,
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiFlags,
            row        = 4,
            col        = 0,
            columnspan = 1,
        )
        self.components.append(guiFlags)

        #####
        # COLUMN 2
        #####

        # Draw the current Bus value
        guiBUS = guiBitfield(
            getValue  = lambda : self.cpu.w,
            wordSize  = 8,
            color     = "RED",
            title     = "BUS"
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiBUS,
            row        = 1,
            col        = 2,
            columnspan = 2,
        )
        self.components.append(guiBUS)

        # Draw the current OUT1 value
        guiOUT = guiBitfield(
            getValue  = lambda : self.cpu.out.value,
            wordSize  = self.cpu.out.bits,
            color     = "WHITE",
            title     = "OUT"
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiOUT,
            row        = 3,
            col        = 2,
            columnspan = 2,
        )
        self.components.append(guiOUT)

        #####
        # COLUMN 3
        #####

        # Draw the current Program Counter valuewinfo screenheight
        guiPC = guiBitfield(
            getValue  = lambda : self.cpu.pc.value,
            wordSize  = self.cpu.pc.bits,
            color     = "GREEN",
            title     = "PC"
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiPC,
            row        = 0,
            col        = 4,
            columnspan = 2,
        )
        self.components.append(guiPC)

        # Draw the current A register value
        guiA = guiBitfield(
            getValue  = lambda : self.cpu.a.value,
            wordSize  = self.cpu.a.bits,
            color     = "GREEN",
            title     = "A"
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiA,
            row        = 1,
            col        = 4,
            columnspan = 2,
        )
        self.components.append(guiA)

        # Draw the current A register value
        guiALU = guiBitfield(
            getValue  = lambda : self.cpu.alu.value,
            wordSize  = self.cpu.alu.bits,
            color     = "YELLOW",
            title     = "ALU"
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiALU,
            row        = 2,
            col        = 4,
            columnspan = 2,
        )
        self.components.append(guiALU)

        # Draw the current B register value
        guiB = guiBitfield(
            getValue  = lambda : self.cpu.b.value,
            wordSize  = self.cpu.b.bits,
            color     = "GREEN",
            title     = "B",
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiB,
            row        = 3,
            col        = 4,
            columnspan = 2,
        )
        self.components.append(guiB)

        # Draw the current Output Control Lines
        guiCtls = guiBitfield(
            getValue  = getOutputFlags,
            wordSize  = len(self.cpu.oflags),
            color     = "MAGENTA",
            title     = "CTL",
            flags     = self.cpu.oflags,
        )
        self.mgr.placeComponentAt(
            self.windows['CPU'],
            guiCtls,
            row        = 4,
            col        = 1,
            columnspan = 5,
            sticky     = "E",
        )
        self.components.append(guiCtls)

        self.mgr.refreshWindows()

    def redraw(self):
        self.mgr.refreshWindows()

    def clock(self):
        self.mgr.updateComponents(self.components)
        self.mgr.refreshWindows()

    def wait_for_close(self):
        self.mgr.refreshWindows()
        self.mgr.mainloop()
        self.mgr.close()
