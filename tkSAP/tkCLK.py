from tkinter import Canvas, Spinbox, Button, StringVar
from .constants import PROFILES, DEFAULTS

BLOCK_SIZE = 150
BORDER_SIZE = 15
TEXT_PAD_FACTOR = 1.5


class tkCLK(object):
    def __init__(self,frame,clk):
        self.frame               = frame
        self.clk                 = clk
        self.target_hz_stringvar = StringVar()
        self.target_hz_stringvar.set(DEFAULTS['Hz'])
        self.clk.modify(int(self.target_hz_stringvar.get()))
        self.canvas              = Canvas(
            self.frame,
            bg                 = "#000",
            bd                 = 0,
            highlightthickness = 0,
            height             = BLOCK_SIZE,
            width              = BLOCK_SIZE * 2,
        )
        self.frame.rowconfigure(0, weight = 1)
        self.frame.columnconfigure(0, weight = 1)
        self.canvas.grid(row=0,column=0)
        # Draw the faux panels
        xoff = BLOCK_SIZE
        yoff = 0
        xy1 = BORDER_SIZE
        xy2 = BLOCK_SIZE - BORDER_SIZE
        #print(f'xoff={xoff} yoff={yoff} xy1={xy1} xy2={xy2} xoff+xy1={xoff+xy1} yoff+xy1={yoff+xy1} xoff+xy2={xoff+xy2} yoff+xy2={yoff+xy2}')
        self.canvas.create_rectangle(
            xoff+xy1,yoff+xy1,xoff+xy2,yoff+xy2,
            fill    = PROFILES["COLORS"]["BG"],
            outline = PROFILES["COLORS"]["BG"],
        )
        xoff = 0
        yoff = 0
        xy1 = BORDER_SIZE
        xy2 = BLOCK_SIZE - BORDER_SIZE
        #print(f'xoff={xoff} yoff={yoff} xy1={xy1} xy2={xy2} xoff+xy1={xoff+xy1} yoff+xy1={yoff+xy1} xoff+xy2={xoff+xy2} yoff+xy2={yoff+xy2}')
        self.canvas.create_rectangle(
            xoff+xy1,yoff+xy1,xoff+xy2,yoff+xy2,
            fill    = PROFILES["COLORS"]["BG"],
            outline = PROFILES["COLORS"]["BG"],
        )
        # Draw the label
        label_height = 10
        self.canvas.create_text(
            xoff + BLOCK_SIZE/2,
            label_height + int(TEXT_PAD_FACTOR*BORDER_SIZE),
            text = "TGT HZ",
            font = PROFILES["BIG"]["label_font"],
            fill = PROFILES["COLORS"]["TEXT_FG"],
        )
        # Draw the value
        self.hz_value = self.canvas.create_text(
            xoff + BLOCK_SIZE/2,
            BLOCK_SIZE - label_height - int(TEXT_PAD_FACTOR*BORDER_SIZE),
            text = "0 HZ",
            font = PROFILES["BIG"]["label_font"],
            fill = PROFILES["COLORS"]["TEXT_FG"],
        )
        # Use a spinbox for the setpoint
        ## it requires a stringvar for Tk reasons
        ## Constrain the options to 1,2,5,10,20,50,100,...
        spinvals = [0]
        stops = [1,2,5]
        for exp in range(4):
            for stop in stops:
                n = stop * (10**exp)
                spinvals.append(str(n))
        ## finally create the spinbox
        self.hz_spinner = Spinbox(
            self.frame,
            values = spinvals,
            width=4,
            relief="sunken",
            repeatdelay=500,
            repeatinterval=100,
            font=PROFILES["BIG"]["label_font"],
            fg="blue",
            bg="lightgrey",
            command=self.modify_clk,
            textvariable=self.target_hz_stringvar,
            state="normal", cursor="hand2", bd=3, justify="center", wrap=True
        )
        self.target_hz_stringvar.set(str(self.clk.Hz))
        self.hz_spinner.place(x=BLOCK_SIZE*1/2,y=BLOCK_SIZE/2,in_=self.canvas,anchor="center")
        # Create the button in memory, unplaced.
        self.btn_pulse = Button(
            self.frame,
            text="Manual\nClock\nTrigger",
            command=self.clk.pulse,
            width=4,
            height=3,
            activebackground="lightgrey",
            relief="raised",
        )
        self.btn_pulse.place(x=BLOCK_SIZE*3/2,y=BLOCK_SIZE/2,in_=self.canvas,anchor="center")
        self.canvas.pack()

    def update_btn_pulse(self):
        self.btn_pulse.configure(state = "active" if (self.clk.Hz==0) else "disabled" )

    def modify_clk(self):
        self.clk.modify(int(self.target_hz_stringvar.get()))
        self.update_btn_pulse()

    def update(self):
        Hz = self.clk.perf_data['history'][self.clk.perf_data['histptr']]
        Hz = 0 if Hz is None else Hz
        if Hz   > 99.94:
            Hz  = f'{Hz:.0f}'
        elif Hz >  9.994:
            Hz  = f'{Hz:.1f}'
        else:
            Hz  = f'{Hz:.2f}'
        self.canvas.itemconfigure(self.hz_value, text=f"{Hz}")
        self.target_hz_stringvar.set(str(self.clk.Hz))
        self.update_btn_pulse()