from tkSAP import tkSAP

if __name__ == "__main__":
    ui = tkSAP()
    ui.file_open("./code/fib.sap")
    ui.clk.modify(2)
    ui.clock_run()
    ui.mainloop()
