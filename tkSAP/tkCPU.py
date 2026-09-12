from .tkBitfield import tkBitfield
from tkinter import Canvas


class tkCPU(object):
    def __init__(self,frame,clk,ui):
        self.ui         = ui
        self.frame      = frame
        self.canvas     = Canvas(self.frame,bg='#000',bd=0,highlightthickness=0)
        self.clk        = clk
        self.components = list()

        coords = dict()
        # Calculator functions for bifield postions relative to another bitfield.
        def absolute(x,y):
            relcoord = dict()
            relcoord['x'] = x
            relcoord['y'] = y
            relcoord['j'] = "left"
            return relcoord
        def below(relative):
            relcoord = dict()
            relcoord['x'] = coords[relative]['x']
            relcoord['y'] = coords[relative]['y'] + coords[relative]['h']
            relcoord['j'] = "left"
            return relcoord
        def below_right(relative):
            relcoord = dict()
            relcoord['x'] = coords[relative]['x'] + coords[relative]['w']
            relcoord['y'] = coords[relative]['y'] + coords[relative]['h']
            relcoord['j'] = "right"
            return relcoord
        def rightof(relative):
            relcoord = dict()
            relcoord['x'] = coords[relative]['x'] + coords[relative]['w']
            relcoord['y'] = coords[relative]['y']
            relcoord['j'] = "left"
            return relcoord

        coords['MAR'] = self.draw_StdRegister(absolute(0,0),'MAR')
        coords['RAM'] = self.draw_RAM(below('MAR'))
        coords['IR']  = self.draw_StdRegister(below('RAM'),'IR')
        coords['STP'] = self.draw_STP(below('IR'))
        coords['FLG'] = self.draw_FLG(rightof('STP'))

        coords['BUS'] = self.draw_BUS(rightof('RAM'))
        coords['OUT'] = self.draw_StdRegister(below('BUS'),'OUT',color="WHITE")

        coords['TMP'] = self.draw_StdRegister(rightof('BUS'),'TMP')
        coords['ALU'] = self.draw_StdRegister(below('TMP'),'ALU',color="YELLOW")
        coords['A']   = self.draw_StdRegister(below('ALU'),'A')
        coords['B']   = self.draw_StdRegister(below('A'),'B')
        coords['C']   = self.draw_StdRegister(below('B'),'C')
        coords['CTL'] = self.draw_CTL(below_right('C'))

        coords['PC']  = self.draw_StdRegister(
            {
                'x':coords['TMP']['x'] + coords['TMP']['w'],
                'y':0,
                'j':"right",
            },
            'PC',
        )

        self.canvas.config(
            width  = 3 * coords['A']['w'],
            height = 7 * coords['A']['h'],
        )
        self.canvas.pack()

    def draw_bitfield(self,color,title,relcoord,flags=None):
        x = relcoord['x']
        y = relcoord['y']
        j = relcoord['j']
        bitfield = tkBitfield(
            getValue  = lambda : self.ui.cpu_state[title]['value'],
            wordSize  = self.ui.cpu_state[title]['bits'],
            color     = color,
            title     = title,
            canvas    = self.canvas,
            x         = x,
            y         = y,
            justify   = j,
            flags     = flags,
        )
        self.components.append(bitfield)
        return bitfield.coords

    def draw_StdRegister(self,relcoord,title,color="GREEN"):
        return self.draw_bitfield(
            color     = color,
            title     = title,
            relcoord  = relcoord,
        )

    def draw_RAM(self,relcoord):
        return self.draw_bitfield(
            color     = "RED",
            title     = "RAM",
            relcoord  = relcoord,
        )

    def draw_BUS(self,relcoord):
        return self.draw_bitfield(
            color     = "RED",
            title     = "BUS",
            relcoord  = relcoord,
        )

    def draw_CTL(self,relcoord):
        return self.draw_bitfield(
            color     = "MAGENTA",
            title     = "CTL",
            flags     = self.clk.cpu.oflags,
            relcoord  = relcoord,
        )

    def draw_STP(self,relcoord):
        return self.draw_bitfield(
            color     = "BLUE",
            title     = "STP",
            relcoord  = relcoord,
        )

    def draw_FLG(self,relcoord):
        return self.draw_bitfield(
            color     = "CYAN",
            title     = "FLG",
            flags     = self.clk.cpu.iflags,
            relcoord  = relcoord,
        )

    def update(self):
        for c in self.components:
            c.update()
