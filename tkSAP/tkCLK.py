from tkinter import Canvas, Spinbox, Button, StringVar
from .constants import PROFILES, DEFAULTS


class tkCLK(object):
    def __init__(self,frame,clk,ui):
        self.ui                  = ui
        self.frame               = frame
        self.clk                 = clk
        self.target_hz_stringvar = StringVar()
        self.canvas              = Canvas(
            self.frame,
            bg                 = "#000",
            bd                 = 0,
            highlightthickness = 0,
        )
        self.target_hz_stringvar.set(DEFAULTS['Hz'])
        self.clk.modify(int(self.target_hz_stringvar.get()))
        # Start drawing
        x = 0
        y = 0
        w = 0
        h = 0
        # Draw the Hz setter/tracker
        self.draw_Hz(x,y)
        w += PROFILES['CLK']['BLOCK_SIZE']
        h += PROFILES['CLK']['BLOCK_SIZE']
        # Draw the button for manually pulsing the clock
        x += PROFILES['CLK']['BLOCK_SIZE']
        self.draw_btn_pulse(x,y)
        w += PROFILES['CLK']['BLOCK_SIZE']
        # Draw the button for starting/stopping the clock
        x += PROFILES['CLK']['BLOCK_SIZE']
        self.draw_btn_runstop(x,y)
        w += PROFILES['CLK']['BLOCK_SIZE']
        # Finalize the drawing
        self.canvas.configure(
            height = h,
            width  = w,
        )
        self.canvas.pack()

    def draw_backplate(self,x,y):
        x1 = x + PROFILES['CLK']['BORDER_SIZE']
        y1 = y + PROFILES['CLK']['BORDER_SIZE']
        x2 = x + PROFILES['CLK']['BLOCK_SIZE'] - PROFILES['CLK']['BORDER_SIZE']
        y2 = y + PROFILES['CLK']['BLOCK_SIZE'] - PROFILES['CLK']['BORDER_SIZE']
        self.canvas.create_rectangle(
            x1,y1,x2,y2,
            fill               = PROFILES["COLORS"]["BG"],
            outline            = PROFILES["COLORS"]["BG"],
            width              = 0,
        )
        #print(f'draw_backplate(x={x},y={y}) x1={x1},y1={y1},x2={x2},y2={y2}')

    def draw_Hz(self,x,y):
        self.draw_backplate(x,y)
        # Draw the label
        label_height = 10
        self.canvas.create_text(
            x + PROFILES['CLK']['BLOCK_SIZE']/2,
            y + label_height + int(PROFILES['CLK']['TEXT_PAD_FACTOR']*PROFILES['CLK']['BORDER_SIZE']),
            text = "TGT HZ",
            font = PROFILES["BIG"]["label_font"],
            fill = PROFILES["COLORS"]["TEXT_FG"],
        )
        # Draw the value
        self.hz_value = self.canvas.create_text(
            x + PROFILES['CLK']['BLOCK_SIZE']/2,
            y + PROFILES['CLK']['BLOCK_SIZE'] - label_height - int(PROFILES['CLK']['TEXT_PAD_FACTOR']*PROFILES['CLK']['BORDER_SIZE']),
            text = "0000 HZ",
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
        self.hz_spinner.place(x=x+(PROFILES['CLK']['BLOCK_SIZE']/2),y=y+PROFILES['CLK']['BLOCK_SIZE']/2,in_=self.canvas,anchor="center")

    def draw_btn_pulse(self,x,y):
        self.draw_backplate(x,y)
        self.btn_pulse = Button(
            self.frame,
            text="Manual\nClock\nTrigger",
            command=self.clk.pulse,
            width=4,
            height=3,
            activebackground="lightgrey",
            relief="raised",
        )
        self.btn_pulse.place(
            x      = x + PROFILES['CLK']['BLOCK_SIZE']/2,
            y      = y + PROFILES['CLK']['BLOCK_SIZE']/2,
            in_    = self.canvas,
            anchor = "center",
        )

    def draw_btn_runstop(self,x,y):
        self.draw_backplate(x,y)
        self.btn_run = Button(
            self.frame,
            text="Run",
            command=self.ui.clock_run,
            width=4,
            height=1,
            activebackground="lightgrey",
            relief="raised",
        )
        self.btn_stop = Button(
            self.frame,
            text="Stop",
            command=self.ui.clock_stop,
            width=4,
            height=1,
            activebackground="lightgrey",
            relief="raised",
        )
        self.btn_run.place(
            x      = x + PROFILES['CLK']['BLOCK_SIZE']/2,
            y      = y + PROFILES['CLK']['BLOCK_SIZE']*.35,
            in_    = self.canvas,
            anchor = "center",
        )
        self.btn_stop.place(
            x      = x + PROFILES['CLK']['BLOCK_SIZE']/2,
            y      = y + PROFILES['CLK']['BLOCK_SIZE']*.65,
            in_    = self.canvas,
            anchor = "center",
        )
        self.update_btn_runstop()

    def update_btn_runstop(self):
        stop = self.ui.clock_thread.running
        run  = not stop
        if run:
            runstate  = "normal"
            stopstate = "disabled"
        else:
            runstate  = "disabled"
            stopstate = "normal"
        self.btn_run.configure(state=runstate)
        self.btn_stop.configure(state=stopstate)

    def update_btn_pulse(self):
        self.btn_pulse.configure(state = "active" if (self.clk.Hz==0) else "disabled" )

    def modify_clk(self):
        self.clk.modify(int(self.target_hz_stringvar.get()))
        self.update()

    def update(self):
        Hz = self.clk.perf_data['history'][self.clk.perf_data['histptr']]
        Hz = 0 if Hz is None else Hz
        if Hz > 999.4:
            Hz  = f'{Hz:03.0f}'
        elif Hz   > 99.94:
            Hz  = f'{Hz:03.0f}.'
        elif Hz >  9.994:
            Hz  = f'{Hz:04.1f}'
        elif Hz > 0.0:
            Hz  = f'{Hz:04.2f}'
        else:
            Hz  = '0000'
        self.canvas.itemconfigure(self.hz_value, text=f"{Hz}")
        self.target_hz_stringvar.set(str(self.clk.Hz))
        self.update_btn_pulse()
        self.update_btn_runstop()
