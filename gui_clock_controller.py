import tkinter as tk


class gui_clock_controller(object):
    def __init__(self,clk,gm):
        self.clk = clk
        # Main window
        self.tkwnd = tk.Tk()
        self.tkwnd.title("Clock Controller")
        self.canvas = tk.Canvas(
            self.tkwnd,
            bg      = "#000",
            height  = 100,
            width   = 200,
        )
        # Hz display and spinbox
        self.canvas.create_rectangle(
            10,10,90,90,
            fill    = gm.COLORS["TEXT_BG"]
        )
        self.canvas.create_text(
            50,30,
            text    = "Hz",
            fill    = gm.COLORS['TEXT_FG'],
            font    = gm.label_font
        )
        self.hz_tracker = tk.StringVar(self.tkwnd)
        self.hz_tracker.set(str(self.clk.Hz))
        self.hz_spinner = tk.Spinbox(
            self.tkwnd,
            from_=0,
            to=1000,
            width=4,
            relief="sunken",
            repeatdelay=500,
            repeatinterval=100,
            font=gm.flag_font,
            fg="blue",
            bg="lightgrey",
            command=self.modify_clk,
            textvariable=self.hz_tracker
        )
        self.hz_spinner.config(state="normal", cursor="hand2", bd=3, justify="center", wrap=True)
        self.hz_spinner.place(x=20,y=50)
        # The manual clock pulser
        self.canvas.create_rectangle(
            110,10,190,90,
            fill    = gm.COLORS["TEXT_BG"]
        )
        self.btn_pulse = tk.Button(
            self.tkwnd,
            text="Manual\nClock\nTrigger",
            command=self.pulse_clk,
            anchor="w"
        )
        self.btn_pulse.configure(
            width=4,
            height=3,
            activebackground="lightgrey",
            relief="raised",
        )
        self.update_btn_pulse()
        self.canvas.create_window(
            150,50,
            window=self.btn_pulse
        )
        # Finally update window
        self.canvas.pack()

    def update_btn_pulse(self):
        self.btn_pulse.configure(state = "active" if (self.clk.Hz==0) else "disabled" )

    def modify_clk(self):
        self.clk.modify(int(self.hz_tracker.get()))
        self.update_btn_pulse()

    def pulse_clk(self):
        #print("pulse the clock from GUI")
        self.clk.pulse()

    def redraw(self):
        self.tkwnd.update_idletasks()
        self.tkwnd.update()

    def wait_for_close(self):
        self.tkwnd.mainloop()
