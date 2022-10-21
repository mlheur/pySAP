from tkinter import *

class guimgr():
    BORDER      = 5
    PPB         = 20
    LABEL_WIDTH = 80
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

    def __init__(self,bitlen,rows,cols,title = "guimgr"):
        self.bitlen = bitlen
        self.rows = rows
        self.cols = cols
        self.tkwnd = Tk()
        self.tkwnd.title(title)
        self.width = ((self.cols+1)*self.BORDER) + (self.cols * self.get_col_width())
        self.height = ((self.rows+1)*self.BORDER) + (self.rows * self.get_row_height())
        self.canvas = Canvas(self.tkwnd, bg = "#000000", height = self.height, width = self.width)

    def draw_bitfield(self, bf):
        coords = self.get_bitfield_coords(bf)
        print("name={}:coords={}".format(bf.name,coords))
        self.canvas.create_rectangle(coords, fill=self.LED["BG"])
        return coords

    def draw_bit(self,bf,bitpos):
        x1 = bf.coords[0] + ( self.BORDER + ( (bf.bitlen-1-bitpos) * ( self.PPB + self.BORDER ) ) )
        x2 = x1 + self.PPB
        y1 = bf.coords[1] + self.BORDER
        y2 = y1 + self.PPB
        return(self.canvas.create_oval(x1, y1, x2, y2, fill = self.LED[bf.color]["OFF"]))

    def update_bit(self,bf,bitID,bitval):
        fill = self.LED[bf.color]["ON"]
        if bitval == 0:
            fill = self.LED[bf.color]["OFF"]
        self.canvas.itemconfigure(bitID,fill=fill)

    def get_row_height(self):
        return (2 * self.BORDER) + self.PPB
    
    def get_col_width(self,bitlen=None):
        if bitlen is None:
            bitlen = self.bitlen
        return (self.LABEL_WIDTH + self.BORDER) + ((bitlen+1) * self.BORDER) + (bitlen * self.PPB)
    
    def get_row_y1(self,row):
        yoff = self.BORDER
        while(row > 0):
            yoff += (3 * self.BORDER) + self.PPB
            row -= 1
        return yoff
    
    def get_col_x1(self,col):
        xoff = self.BORDER
        while(col > 0):
            #xoff += (3+self.bitlen * self.BORDER) + ( self.bitlen * self.PPB )
            xoff += (2 * self.BORDER) + ((self.bitlen) * (self.PPB + self.BORDER)) + (self.LABEL_WIDTH + self.BORDER)
            col -= 1
        return (xoff)

    def get_label_coords(self,row,col):
        x1 = self.get_col_x1(col)
        x2 = x1 + self.LABEL_WIDTH
        y1 = self.get_row_y1(row)
        y2 = y1 + self.get_row_height()
        return x1,y1,x2,y2

    def get_bitfield_coords(self,bf):
        x1 = self.get_col_x1(bf.col) + self.LABEL_WIDTH + self.BORDER
        if bf.justify == "right" and bf.bitlen != self.bitlen:
            x1 += ((self.bitlen - bf.bitlen) * (self.BORDER + self.PPB))
        x2 = x1 + self.get_col_width(bf.bitlen) - (self.LABEL_WIDTH + self.BORDER)
        y1 = self.get_row_y1(bf.row)
        y2 = y1 + self.get_row_height()
        return x1,y1,x2,y2
    
    def redraw(self):
        self.tkwnd.update_idletasks()
        self.tkwnd.update()

    def wait_for_close(self):
        self.tkwnd.mainloop()

    def pack(self):
        self.canvas.pack()