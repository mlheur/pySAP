from tkinter import *

class gui_layout():
    PIXELS_BORDER = 5
    PIXELS_PER_BIT = 10
    GRID = {
        "row_y_offset": {
            0: 5,
            1: 30,
            2: 55,
            3: 80,
            4: 105,
            5: 130
        },
        "col_x_offset": {
            0: 5,
            1: 135
        }
    }

class gui_register():
    COLOR_ON = "#30FF30"
    COLOR_OFF = "#306030"
    COLOR_BG = "#101010"
    def __init__(self,reg,row,col,canvas,name):
        self.reg = reg
        self.row = row
        self.col = col
        self.canvas = canvas
        self.name = name

        self.bits = list()
        self.topleft_x = gui_layout.GRID["col_x_offset"][col]
        self.topleft_y = gui_layout.GRID["row_y_offset"][row]
        self.width = ( self.reg.bits * gui_layout.PIXELS_PER_BIT ) + ( ( self.reg.bits + 1 ) * gui_layout.PIXELS_BORDER )
        self.height = (2*gui_layout.PIXELS_BORDER)+gui_layout.PIXELS_PER_BIT
        self.bgID = self.canvas.create_rectangle(self.topleft_x,self.topleft_y,self.topleft_x+self.width,self.topleft_y+self.height,fill=self.COLOR_BG)
        for bitpos in range(self.reg.bits):
            x1 = self.topleft_x + gui_layout.PIXELS_BORDER + ( (self.reg.bits-1-bitpos) * ( gui_layout.PIXELS_PER_BIT + gui_layout.PIXELS_BORDER ) )
            x2 = x1 + gui_layout.PIXELS_PER_BIT
            y1 = self.topleft_y + gui_layout.PIXELS_BORDER
            y2 = y1 + gui_layout.PIXELS_PER_BIT
            coord = x1, y1, x2, y2
            self.bits.append(self.canvas.create_oval(coord,fill=self.COLOR_OFF))
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

class guiSAP1():
    def __init__(self,cpu):
        self.cpu = cpu

        self.main_wnd = Tk()
        self.canvas = Canvas(self.main_wnd, bg = "#000000", height = 130, width = 265)

        self.components = list()
        self.components.append(gui_register(self.cpu.pc,  0, 1, self.canvas, "PC"))
        self.components.append(gui_register(self.cpu.mar, 1, 0, self.canvas, "MAR"))
        self.components.append(gui_register(self.cpu.a,   1, 1, self.canvas, "A"))
        self.components.append(gui_register(self.cpu.ram, 2, 0, self.canvas, "RAM"))
        self.components.append(gui_register(self.cpu.alu, 2, 1, self.canvas, "ALU"))
        self.components.append(gui_register(self.cpu.ir,  3, 0, self.canvas, "IR"))
        self.components.append(gui_register(self.cpu.b,   3, 1, self.canvas, "B"))
        self.components.append(gui_register(self.cpu.out, 4, 1, self.canvas, "OUT"))

        self.canvas.pack()

    def clock(self):
        for comp in self.components:
            comp.redraw()
        self.main_wnd.update_idletasks()
        self.main_wnd.update()




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
    g = guiSAP1(cpu)
    clk.subscribe(g)
    clk.run(cpu)
    g.main_wnd.mainloop()
