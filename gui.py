from tkinter import *

class gui_layout_manager():
    BORDER     = 5
    PPB        = 10

    def __init__(self,maxbits,rows,cols):
        self.maxbits = maxbits
        self.rows = rows
        self.cols = cols
        self.BORDER = gui_layout_manager.BORDER
        self.PPB = gui_layout_manager.PPB

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
  

class gui_register():
    COLOR_ON = "#30FF30"
    COLOR_OFF = "#306030"
    COLOR_BG = "#202020"
    def __init__(self,reg,row,col,canvas,name,glm):
        self.reg = reg
        self.row = row
        self.col = col
        self.canvas = canvas
        self.name = name
        self.glm = glm
        self.coords = self.glm.get_coords(row,col)
        self.bgID = self.canvas.create_rectangle(self.coords,fill=self.COLOR_BG)

        self.bits = list()
        for bitpos in range(self.reg.bits):
            x1 = self.coords[0] + self.glm.BORDER + ( (self.reg.bits-1-bitpos) * ( self.glm.PPB + self.glm.BORDER ) )
            x2 = x1 + self.glm.PPB
            y1 = self.coords[1] + self.glm.BORDER
            y2 = y1 + self.glm.PPB
            self.bits.append(self.canvas.create_oval(x1, y1, x2, y2, fill=self.COLOR_OFF))
        self.redraw()

    def redraw(self):
        for bitpos,bitID in enumerate(self.bits):
            value = self.reg.value
            if self.name == "RAM":
                value = self.reg.value[self.reg.cpu.mar.value]
#           print("NAME=[{}]: bitpos={}, bitID={}".format(self.name,bitpos,bitID))
            bitval = 0b1 & (value >> bitpos)
            fill = self.COLOR_ON
            if bitval == 0:
                fill = self.COLOR_OFF
            self.canvas.itemconfigure(bitID,fill=fill)

class gui_tstep(gui_register):
    def __init__(self, ctlseq, row, col, canvas, name, glm):
        self.COLOR_ON = "#3030FF"
        self.COLOR_OFF = "#303060"
        self.COLOR_BG = "#202020"
        super().__init__(reg, row, col, canvas, name, glm)


class guiSAP1():
    def __init__(self,cpu,clk):
        self.cpu = cpu
        clk.subscribe(self)
        self.glm = gui_layout_manager(self.cpu.bits,5,2)

        self.main_wnd = Tk()
        self.main_wnd.title("SAP1")
        height,width = self.glm.get_canvas_size()
        self.canvas = Canvas(self.main_wnd, bg = "#000000", height = height, width = width)

        self.components = list()
        self.components.append(gui_register(self.cpu.pc,  0, 1, self.canvas, "PC",  self.glm))
        self.components.append(gui_register(self.cpu.mar, 1, 0, self.canvas, "MAR", self.glm))
        self.components.append(gui_register(self.cpu.a,   1, 1, self.canvas, "A",   self.glm))
        self.components.append(gui_register(self.cpu.ram, 2, 0, self.canvas, "RAM", self.glm))
        self.components.append(gui_register(self.cpu.alu, 2, 1, self.canvas, "ALU", self.glm))
        self.components.append(gui_register(self.cpu.ir,  3, 0, self.canvas, "IR",  self.glm))
        self.components.append(gui_register(self.cpu.b,   3, 1, self.canvas, "B",   self.glm))
        self.components.append(gui_register(self.cpu.out, 4, 1, self.canvas, "OUT", self.glm))

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
