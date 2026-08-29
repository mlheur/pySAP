from tkinter import *
from .guiMgr import guiMgr


class guiScrolling(guiMgr):
    def __init__(self, bitlen, rows, cols, title="scrolling_guimgr", border=None, ppb=None, label_width=None, font_label_size=None, font_flag_size=None, colors=None, led=None):
        super().__init__(bitlen, rows, cols, title, border, ppb, label_width, font_label_size, font_flag_size, colors, led)
        # The canvas is currently drawn in the main window frame.
        self.canvas.destroy()

        # we need to create a new subframe,
        self.scrollbar_width = 20
        w = self.width+self.scrollbar_width
        h = min(self.height,768)
        #print("h={},w={}".format(h,w))
        self.subwindow = Frame(self.tkwnd,width=w,height=h)
        self.subwindow.pack(expand=True, fill=BOTH)

        # then move the canvas into the subframe,
        w -= self.scrollbar_width
        h += self.scrollbar_width * 3
        self.canvas = Canvas(self.subwindow, bg = "#000", height = h, width = w, scrollregion=(0,0,self.width,self.height + self.scrollbar_width))

        # then add scrollbars to the subframe,
        self.hbar=Scrollbar(self.canvas,orient=HORIZONTAL)
        self.hbar.pack(side=BOTTOM,fill=X)
        self.hbar.config(command=self.canvas.xview)
        self.vbar=Scrollbar(self.canvas,orient=VERTICAL)
        self.vbar.pack(side=RIGHT,fill=Y)
        self.vbar.config(command=self.canvas.yview)

        # associate reactions to scroll changes
        self.canvas.config(width=w,height=h)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        # and repack it all.
        self.canvas.pack(side=LEFT,expand=True,fill=BOTH)

        self.tkwnd.geometry("{}x{}+0+0".format(w+self.scrollbar_width,h+self.scrollbar_width))
