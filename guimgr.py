from tkinter import *
from tkinter.font import *

class guimgr(object):
    BORDER          = 4
    PPB             = 36
    LABEL_WIDTH     = 70
    FONT_LABEL_SIZE = 24
    FONT_FLAG_SIZE  = 10
    LABEL_HEIGHT = ((2*BORDER)+PPB)
    LED = {
        "RED":     {"ON":"#F22", "OFF":"#622"},
        "GREEN":   {"ON":"#2F2", "OFF":"#262"},
        "BLUE":    {"ON":"#22F", "OFF":"#226"},
        "YELLOW":  {"ON":"#FF2", "OFF":"#662"},
        "MAGENTA": {"ON":"#F2F", "OFF":"#626"},
        "CYAN":    {"ON":"#2FF", "OFF":"#266"},
        "WHITE":   {"ON":"#FFF", "OFF":"#666"}
    }
    COLORS = {
        "BG":      "#444",
        "TEXT_BG": "#222",
        "TEXT_FG": "#ffb"
    }

    def __init__(self,bitlen,rows,cols,title = "guimgr"):
        self.bitlen = bitlen
        self.rows = rows
        self.cols = cols
        self.tkwnd = Tk()
        self.tkwnd.title(title)
        self.width = ((self.cols+1)*self.BORDER) + (self.cols * self.get_col_width())
        self.height = ((self.rows+1)*self.BORDER) + (self.rows * self.get_row_height())
        self.canvas = Canvas(self.tkwnd, bg = "#000", height = self.height, width = self.width)
        self.label_font = Font(family='Courier', size = self.FONT_LABEL_SIZE, weight = 'bold')
        self.flag_font = Font(family='Courier', size = self.FONT_FLAG_SIZE, weight = 'bold')

    def draw_bitfield(self, bf):
        coords = self.get_bitfield_coords(bf)
        #print("name={}:coords={}".format(bf.name,coords))
        self.canvas.create_rectangle(coords, fill=self.COLORS["BG"])
        text_width = self.label_font.measure(bf.name)
        x1 = coords[0] - self.BORDER - self.LABEL_WIDTH
        x2 = x1 + self.LABEL_WIDTH
        y1 = coords[1]
        y2 = coords[3]
        self.canvas.create_rectangle(x1,y1,x2,y2, fill=self.COLORS["TEXT_BG"])
        x1 = coords[0] - (2*self.BORDER) - text_width
        y1 = coords[1] + (self.LABEL_HEIGHT / 2)
        self.canvas.create_text(x1, y1, text = bf.name, fill = self.COLORS["TEXT_FG"], anchor = "w", justify = 'right', font = self.label_font)
        return coords

    def draw_bit(self,bf,bitpos):
        x1 = bf.coords[0] + ( self.BORDER + ( (bf.bitlen-1-bitpos) * ( self.PPB + self.BORDER ) ) )
        x2 = x1 + self.PPB
        y1 = bf.coords[1] + self.BORDER
        y2 = y1 + self.PPB
        return(self.canvas.create_oval(x1, y1, x2, y2, fill = self.LED[bf.color]["OFF"]))

    def draw_bit_label(self,bf,bitpos,bitname,color):
        coords = self.get_bitfield_coords(bf)
        x1 = coords[0] + ( self.BORDER + ( (bf.bitlen-1-bitpos) * ( self.PPB + self.BORDER ) ) ) + (self.PPB/2)
        y1 = coords[1] + self.BORDER + (self.PPB/2) - 2
        self.canvas.create_text(x1, y1, text = bitname, fill = color, font = self.flag_font)

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
            xoff += (2 * self.BORDER) + ((self.bitlen) * (self.PPB + self.BORDER)) + (self.LABEL_WIDTH + self.BORDER)
            col -= 1
        return (xoff)

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