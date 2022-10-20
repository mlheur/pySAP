from tkinter import *

class guimgr():
    BORDER      = 5
    PPB         = 15
    LED = {
        "RED":     {"ON":"#F33", "OFF":"#633"},
        "GREEN":   {"ON":"#3F3", "OFF":"#363"},
        "BLUE":    {"ON":"#33F", "OFF":"#336"},
        "YELLOW":  {"ON":"#FF3", "OFF":"#663"},
        "MAGENTA": {"ON":"#F3F", "OFF":"#636"},
        "CYAN":    {"ON":"#3FF", "OFF":"#366"},
        "WHITE":   {"ON":"#FFF", "OFF":"#666"},
        "BG": "#222"
    }

    def __init__(self,maxbits,rows,cols):
        self.maxbits = maxbits
        self.rows = rows
        self.cols = cols
        self.BORDER = guimgr.BORDER
        self.PPB = guimgr.PPB

    def get_row_height(self):
        return (2 * self.BORDER) + self.PPB
    
    def get_col_width(self,bits=None):
        if bits is None:
            bits = self.maxbits
        return ((bits+1) * self.BORDER) + (bits * self.PPB)
    
    def get_row_yoffset(self,row):
        return ((row+1) * self.BORDER) + (row * self.get_row_height())
    
    def get_col_xoffset(self,col):
        return ((col+1) * self.BORDER) + (col * self.get_col_width())
    
    def get_coords(self,row,col):
        x1 = self.get_col_xoffset(col)
        x2 = x1 + self.get_col_width()
        y1 = self.get_row_yoffset(row)
        y2 = y1 + self.get_row_height()
        return x1,y1,x2,y2
    
    def get_canvas_size(self):
        width = ((self.cols+1)*self.BORDER) + (self.cols * self.get_col_width())
        height = ((self.rows+1)*self.BORDER) + (self.rows * self.get_row_height())
        return height,width
  
class gui_bitfield():
    def __init__(self,row,col,canvas,name,glm,bitlen):
        self.row = row
        self.col = col
        self.canvas = canvas
        self.name = name
        self.gm = glm
        self.coords = self.gm.get_coords(row,col)
        self.bgID = self.canvas.create_rectangle(self.coords,fill=guimgr.LED["BG"])
        self.bits = list()
        for bitpos in range(bitlen):
            x1 = self.coords[0] + self.gm.BORDER + ( (bitlen-1-bitpos) * ( self.gm.PPB + self.gm.BORDER ) )
            x2 = x1 + self.gm.PPB
            y1 = self.coords[1] + self.gm.BORDER
            y2 = y1 + self.gm.PPB
            self.bits.append(self.canvas.create_oval(x1, y1, x2, y2, fill = guimgr.LED[self.COLOR]["OFF"]))

    def redraw(self,value):
        for bitpos,bitID in enumerate(self.bits):
            bitval = 0b1 & (value >> bitpos)
            fill = guimgr.LED[self.COLOR]["ON"]
            if bitval == 0:
                fill = guimgr.LED[self.COLOR]["OFF"]
            self.canvas.itemconfigure(bitID,fill=fill)

class gui_register(gui_bitfield):
    COLOR = "GREEN"
    def __init__(self,reg,row,col,canvas,name,glm):
        self.reg = reg
        super().__init__(row, col, canvas, name, glm, self.reg.bits)
        self.redraw()
    def redraw(self):
        return super().redraw(self.reg.value)

class gui_tstep(gui_bitfield):
    COLOR = "BLUE"
    def __init__(self, ctlseq, row, col, canvas, name, glm):
        self.ctlseq = ctlseq
        super().__init__(row, col, canvas, name, glm, 5)
    def redraw(self):
        return super().redraw(self.ctlseq.Tstep)

class gui_ram(gui_bitfield):
    COLOR = "RED"
    def __init__(self, cpu, row, col, canvas, name, glm):
        self.cpu = cpu
        super().__init__(row, col, canvas, name, glm, self.cpu.ram.bits)
    def redraw(self):
        return super().redraw(self.cpu.ram.value[self.cpu.mar.value])

class guiSAP1():
    def __init__(self,cpu,clk):
        self.cpu = cpu
        clk.subscribe(self)
        self.gm = guimgr(self.cpu.bits,5,2)

        self.main_wnd = Tk()
        self.main_wnd.title("SAP1")
        height,width = self.gm.get_canvas_size()
        self.canvas = Canvas(self.main_wnd, bg = "#000000", height = height, width = width)

        self.components = list()
        self.components.append(gui_register(self.cpu.pc,  0, 1, self.canvas, "PC",  self.gm))
        self.components.append(gui_register(self.cpu.mar, 1, 0, self.canvas, "MAR", self.gm))
        self.components.append(gui_register(self.cpu.a,   1, 1, self.canvas, "A",   self.gm))
        self.components.append(     gui_ram(self.cpu,     2, 0, self.canvas, "RAM", self.gm))
        self.components.append(gui_register(self.cpu.alu, 2, 1, self.canvas, "ALU", self.gm))
        self.components.append(gui_register(self.cpu.ir,  3, 0, self.canvas, "IR",  self.gm))
        self.components.append(gui_register(self.cpu.b,   3, 1, self.canvas, "B",   self.gm))
        self.components.append(gui_register(self.cpu.out, 4, 1, self.canvas, "OUT", self.gm))
        self.components.append(gui_tstep(self.cpu.ctlseq, 0, 0, self.canvas, "T",   self.gm))
        self.components[0].COLOR = "MAGENTA"
        self.components[1].COLOR = "CYAN"
        self.components[4].COLOR = "YELLOW"
        self.components[7].COLOR = "WHITE"

        self.canvas.pack()

    def clock(self):
        for comp in self.components:
            comp.redraw()
        self.main_wnd.update_idletasks()
        self.main_wnd.update()
    
    def wait_for_close(self):
        self.main_wnd.mainloop()




if __name__ == "__main__":
    from pySAP1 import SAP1rom as ROM
    rom = ROM()
    fib = []
    fib.append(rom.assemble('LDI',0x1)) # 0
    fib.append(rom.assemble('STA',0xE)) # 1
    fib.append(rom.assemble('LDI',0x0)) # 2
    fib.append(rom.assemble('STA',0xF)) # 3
    fib.append(rom.assemble('OUT'))     # 4
    fib.append(rom.assemble('LDA',0xE)) # 5
    fib.append(rom.assemble('ADD',0xF)) # 6
    fib.append(rom.assemble('STA',0xE)) # 7
    fib.append(rom.assemble('OUT'))     # 8
    fib.append(rom.assemble('LDA',0xF)) # 9
    fib.append(rom.assemble('ADD',0xE)) # A
    fib.append(rom.assemble('JC', 0xD)) # B
    fib.append(rom.assemble('JMP',0x3)) # C
    fib.append(rom.assemble('HLT'))     # D
    #  Var 1                            # E
    #  Var 2                            # F
    from pySAP1 import pySAP1 as CPU
    cpu = CPU(rom,fib)
    from clock import Clock as Clock
    clk = Clock(10)
    g = guiSAP1(cpu,clk)
    clk.run(cpu)
    g.main_wnd.mainloop()
