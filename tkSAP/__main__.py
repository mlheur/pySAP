from tkSAP import tkSAP

if __name__ == "__main__":
    UI = tkSAP()
    UI.file_open("./code/checkerboard.sap")
    UI.clock_run()
    UI.mainloop()