from .constants import PROFILES, DEFAULTS
from tkinter import Scrollbar, Listbox
from tkinter.font import Font


class tkCODE(object):
    def __init__(self,frame,clk):
        self.frame  = frame
        self.clk    = clk
        self.scrl   = Scrollbar(self.frame,orient="vertical")
        self.scrl.pack(side="right",fill="y")
        self.code_font = Font(
            family = DEFAULTS['FONT'], # already resolved by tkMGR
            size   = PROFILES['CODE']['SIZE'],
            weight = "bold",
        )
        self.listboxes = {
            'ASM' : Listbox(
                self.frame,
                yscrollcommand     = self.sync_listboxes,
                width              = PROFILES['CODE']['WIDTH'],
                bg                 = PROFILES['CODE']['BG'],
                bd                 = 0,
                highlightthickness = 0,
                font               = self.code_font,
            ),
            'SRC' : Listbox(
                self.frame,
                yscrollcommand     = self.sync_listboxes,
                width              = PROFILES['CODE']['WIDTH'],
                bg                 = PROFILES['CODE']['BG'],
                bd                 = 0,
                highlightthickness = 0,
                font               = self.code_font,
            ),
        }
        self.scrl.config(command=self.sync_scrollbar)
        for box in self.listboxes:
            self.listboxes[box].pack(
                side="left",
                fill="y",
                expand=True,
            )

    def sync_scrollbar(self,*args):
        #print(f'scrollbar=[{args}]')
        for box in self.listboxes:
            self.listboxes[box].yview(*args)

    def sync_listboxes(self,*args):
        #print(f'listbox=[{args}]')
        self.scrl.set(*args)
        for box in self.listboxes:
            self.listboxes[box].yview('moveto',args[0])

    def reset(self):
        for box in self.listboxes:
            self.listboxes[box].delete(0,"end")

    def toggle_source_assembled(self,arg,*args,**argv):
        old_assembled_state = self.canvas.itemcget(self.assembled,"state")
        old_sourced_state   = self.canvas.itemcget(self.sourced,  "state")
        #print(f'toggle: a={old_assembled_state} s={old_sourced_state}')
        self.canvas.itemconfigure(self.assembled,state=old_sourced_state)
        self.canvas.itemconfigure(self.sourced,state=old_assembled_state)

    def loadfile(self,fname):
        self.reset()

        code = {
            'ASM' : self.clk.cpu.isa.assemble_file(fname,as_string=True),
            'SRC' : self.clk.cpu.isa.assemble_file(fname,as_source=True),
        }

        lengths = dict()
        for box in code:
            lengths[box] = 0
            for i,line in enumerate(code[box].split('\n')):
                if line != "":
                    self.listboxes[box].insert(i,line)
                    lengths[box] += 1
        maxlen = 0
        for box in code:
            if maxlen < lengths[box]:
                maxlen = lengths[box]
        for box in code:
            if lengths[box] < maxlen:
                for i in range(lengths[box],maxlen):
                    self.listboxes[box].insert(i,"")