from .constants import PROFILES, DEFAULTS
from tkinter import Canvas


class tkCODE(object):
    def __init__(self,frame,clk):
        self.frame  = frame
        self.clk    = clk
        self.canvas = None

    def reset(self):
        if self.canvas is not None:
            self.canvas.destroy()
        self.canvas = Canvas(self.frame)
        self.canvas.pack()

    def toggle_source_assembled(self,arg,*args,**argv):
        old_assembled_state = self.canvas.itemcget(self.assembled,"state")
        old_sourced_state   = self.canvas.itemcget(self.sourced,  "state")
        #print(f'toggle: a={old_assembled_state} s={old_sourced_state}')
        self.canvas.itemconfigure(self.assembled,state=old_sourced_state)
        self.canvas.itemconfigure(self.sourced,state=old_assembled_state)

    def loadfile(self,fname):
        self.reset()
        w = 0
        h = 0

        multiline_assembly = self.clk.cpu.isa.assemble_file(fname,as_string=True)
        #print(multiline_assembly)
        self.assembled = self.canvas.create_text(
            0,0,
            text    = multiline_assembly,
            font    = PROFILES["BIG"]["label_font"],
            fill    = '#000',
            justify = "left",
            anchor  = "nw",
        )
        coords = self.canvas.bbox(self.assembled)
        w = max(w,coords[2])
        h = max(w,coords[3])

        multiline_source = self.clk.cpu.isa.assemble_file(fname,as_source=True)
        #print(multiline_source)
        self.sourced = self.canvas.create_text(
            0,0,
            text    = multiline_source,
            font    = PROFILES["BIG"]["label_font"],
            fill    = '#000',
            justify = "left",
            anchor  = "nw",
        )
        coords = self.canvas.bbox(self.sourced)
        w = max(w,coords[2])
        h = max(w,coords[3])

        self.canvas.configure(
            width  = w + DEFAULTS['SOURCE_X'],
            height = h + DEFAULTS['SOURCE_Y'],
        )

        self.canvas.itemconfigure(self.assembled,state="hidden")
        self.canvas.itemconfigure(self.sourced,state="normal")

        self.canvas.bind(
            "<Button-1>",
            self.toggle_source_assembled,
        )



