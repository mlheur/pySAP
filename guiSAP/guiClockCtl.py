from tkinter import Canvas, StringVar, Spinbox, Button
from .WindowMgr import PROFILES


BLOCK_SIZE  = 100
BORDER_SIZE = 10

class guiClockCtl(object):
    def __init__(self,cpu,clk,hWnd):
        clk.subscribe(self)
        self.clk  = clk
        self.cpu  = cpu
        self.hWnd = hWnd
        # Reset the window to match its contents
        self.hWnd.geometry(f'{2*BLOCK_SIZE}x{BLOCK_SIZE}+0+0')
        # Left Half: The Hz selector and display
        self.ticker = Canvas(
            hWnd,
            width              = BLOCK_SIZE,
            height             = BLOCK_SIZE,
            bg                 = "#000",
            bd                 = 0,
            highlightthickness = 0,
        )
        self.ticker.grid(row=0,column=0)
        # Draw the faux panel
        xoff = 0
        yoff = 0
        xy1 = BORDER_SIZE
        xy2 = BLOCK_SIZE - BORDER_SIZE
        #print(f'xoff={xoff} yoff={yoff} xy1={xy1} xy2={xy2} xoff+xy1={xoff+xy1} yoff+xy1={yoff+xy1} xoff+xy2={xoff+xy2} yoff+xy2={yoff+xy2}')
        self.ticker.create_rectangle(
            xoff+xy1,yoff+xy1,xoff+xy2,yoff+xy2,
            fill    = PROFILES["COLORS"]["BG"],
            outline = PROFILES["COLORS"]["BG"],
        )
        # Draw the label
        label_height = 10
        self.ticker.create_text(
            xoff + BLOCK_SIZE/2,
            label_height + BORDER_SIZE,
            text = "TGT HZ",
            font = PROFILES["BIG"]["label_font"],
            fill = PROFILES["COLORS"]["TEXT_FG"],
        )
        # Draw the value
        self.hz_value = self.ticker.create_text(
            xoff + BLOCK_SIZE/2,
            BLOCK_SIZE - label_height - BORDER_SIZE,
            text = "0 HZ",
            font = PROFILES["BIG"]["label_font"],
            fill = PROFILES["COLORS"]["TEXT_FG"],
        )
        # Use a spinbox for the setpoint
        ## it requires a stringvar for Tk reasons
        self.hz_tracker = StringVar(self.hWnd)
        ## Constrain the options to 1,2,5,10,20,50,100,...
        spinvals = [0]
        stops = [1,2,5]
        for exp in range(4):
            for stop in stops:
                n = stop * (10**exp)
                spinvals.append(str(n))
        ## finally create the spinbox
        self.hz_spinner = Spinbox(
            self.hWnd,
            values = spinvals,
            width=4,
            relief="sunken",
            repeatdelay=500,
            repeatinterval=100,
            font=PROFILES["BIG"]["label_font"],
            fg="blue",
            bg="lightgrey",
            command=self.modify_clk,
            textvariable=self.hz_tracker,
            state="normal", cursor="hand2", bd=3, justify="center", wrap=True
        )
        self.hz_tracker.set(str(self.clk.Hz))
        self.hz_spinner.place(x=50,y=50,in_=self.ticker,anchor="center")
        # Right Half: The manual clock pulsing button
        self.pulser = Canvas(
            hWnd,
            width              = BLOCK_SIZE,
            height             = BLOCK_SIZE,
            bg                 = "#000",
            bd                 = 0,
            highlightthickness = 0,
        )
        self.pulser.grid(row=0,column=1)
        # border
        #print(f'xoff={xoff} yoff={yoff} xy1={xy1} xy2={xy2} xoff+xy1={xoff+xy1} yoff+xy1={yoff+xy1} xoff+xy2={xoff+xy2} yoff+xy2={yoff+xy2}')
        self.pulser.create_rectangle(
            xoff+xy1,yoff+xy1,xoff+xy2,yoff+xy2,
            fill    = PROFILES["COLORS"]["BG"],
            outline = PROFILES["COLORS"]["BG"],
        )
        # Create the button in memory, unplaced.
        self.btn_pulse = Button(
            self.hWnd,
            text="Manual\nClock\nTrigger",
            command=self.pulse_clk,
            width=4,
            height=3,
            activebackground="lightgrey",
            relief="raised",
        )
        self.btn_pulse.place(x=50,y=50,in_=self.pulser,anchor="center")

    def modify_clk(self):
        self.clk.modify(int(self.hz_tracker.get()))
        self.update_btn_pulse()

    def pulse_clk(self):
        #print("pulse the clock from GUI")
        self.clk.manual_pulse = True

    def update_performance(self,Hz):
        if Hz   > 99.95:
            Hz  = f'{Hz:.0f}'
        elif Hz >  9.995:
            Hz  = f'{Hz:.1f}'
        else:
            Hz  = f'{Hz:.0f}'
        self.ticker.itemconfigure(self.hz_value, text=f"{Hz}")
        self.hz_tracker.set(str(self.clk.Hz))
        self.update_btn_pulse()

    def update_btn_pulse(self):
        self.btn_pulse.configure(state = "active" if (self.clk.Hz==0) else "disabled" )
