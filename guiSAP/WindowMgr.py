from tkinter import Tk, Canvas, Toplevel
from tkinter.font import Font

FONT="Tlwg Mono"
WMGR_X=24
WMGR_Y=60
SCROLLBAR_WIDTH = 12
RAM_COLUMNS = 8

PROFILES = {
    "BIG": {
        "LABEL_WIDTH"   :  72,
        "LABEL_PADDING" :   2,
        "BULB_DIAMETER" :  48,
        "BULB_SPACING"  :   1,
        "PADDING"       :   1,
        "FONT_SIZE"     :  22,
        "FLAG_SIZE"     :   8,
        "SPACER"        :   8,
    },
    "SML": {
        "LABEL_WIDTH"   :  40,
        "LABEL_PADDING" :   1,
        "BULB_DIAMETER" :   4,
        "BULB_SPACING"  :   0,
        "PADDING"       :   0,
        "FONT_SIZE"     :   6,
        "FLAG_SIZE"     :   6,
        "SPACER"        :   4,
    },
    "LED": {
        "RED":     {"ON":"#F22", "OFF":"#622"},
        "GREEN":   {"ON":"#2F2", "OFF":"#262"},
        "BLUE":    {"ON":"#22F", "OFF":"#226"},
        "YELLOW":  {"ON":"#FF2", "OFF":"#662"},
        "MAGENTA": {"ON":"#F2F", "OFF":"#626"},
        "CYAN":    {"ON":"#2FF", "OFF":"#266"},
        "WHITE":   {"ON":"#FFF", "OFF":"#666"},
    },
    "COLORS": {
        "BG":      "#555",
        "TEXT_BG": "#222",
        "TEXT_FG": "#ffb",
        "FLAG_IN": "#303",
        "FLAG_OV": "#f9f",
    }
}

class WindowMgr(object):
    def __init__(self,gui):
        self.gui    = gui
        # Establish the one Tk framework that will be used for all windows.
        # Do it only once so that many Toplevel windows can share some resources,
        # i.e. fonts.
        self.tkroot = Tk()
        self.tkroot.withdraw()
        # Generate the fonts that will be used in the UI
        for P in PROFILES:
            if "FONT_SIZE" in PROFILES[P]:
                PROFILES[P]["label_font"] = Font(
                    family = FONT,
                    size   = PROFILES[P]["FONT_SIZE"],
                    weight = "bold",
                )
            if "FLAG_SIZE" in PROFILES[P]:
                PROFILES[P]["flag_font"] = Font(
                    family = FONT,
                    size   = PROFILES[P]["FLAG_SIZE"],
                    weight = "bold",
                )
        # Pre-compute some dimensions
        for profile in PROFILES:
            if "BULB_DIAMETER" in PROFILES[profile]:
                PROFILES[profile]["OUTER_DIAMETER"] = PROFILES[profile]["BULB_DIAMETER"] + ( 2 * PROFILES[profile]["BULB_SPACING"])

    def newWindow(self,title):
        hWnd = Toplevel(self.tkroot,bg="black")
        hWnd.title(title)
        return hWnd

    def getWmgrX(self):
        return WMGR_X

    def getWmgrY(self):
        return WMGR_Y

    def quit(self):
        self.tkwnd.destroy()

    def refreshWindows(self):
        self.tkroot.update()

    def updateComponents(self,components):
        for hBitfield in components:
            curValue = hBitfield.get()
            if hBitfield.guiData["lastValue"] != curValue:
                hBitfield.guiData["lastValue"] = curValue
                hCanvas = hBitfield.guiData['canvas']
                hBulbs  = hBitfield.guiData['bulbs']
                for bitPos,bitVal in enumerate(hBitfield):
                    state = "normal" if bitVal else "hidden"
                    hCanvas.itemconfigure(hBulbs[bitPos]["ON"],state=state)

    def addUnlabelledBitfieldToWindow(
        self,
        hWnd,
        hBitfield,
        row,
        col,
        columnspan = 1,
        sticky     = "e",
    ):
        sizeProfile = PROFILES[hBitfield.guiData["profile"]]
        fullWidth = sizeProfile["SPACER"] + sizeProfile["LABEL_PADDING"] + ( hBitfield.wordSize * sizeProfile["OUTER_DIAMETER"] )
        # Create the canvas where the bulbs and labels will be added.
        hBitfield.guiData["canvas"] = Canvas(
            hWnd,
            width              = fullWidth,
            height             = sizeProfile["OUTER_DIAMETER"],
            bg                 = PROFILES["COLORS"]["BG"],
            bd                 = 0,
            highlightthickness = 0,
        )
        # Draw the bitfield on the right side of the canvas
        ## Least-significant-bulb starts at a large value of X, X decreases down to zero as significance increases.
        FarX = fullWidth
        # The Y coordinates will be the same for all bulbs.
        y1 = sizeProfile["BULB_SPACING"]
        y2 = y1 + sizeProfile["BULB_DIAMETER"] - 1
        for bitPos in range(hBitfield.wordSize):
            # For efficiency, draw now both the lit and unlit versionsBULB_SPACING
            # later, just toggle the visibility of it.
            bitBulbs = {
                "OFF": None,
                "ON": None,
            }
            # Backtrack the X value for the next-significant-bulb.
            FarX -= sizeProfile["OUTER_DIAMETER"]
            # Calculate the exact X coordinates for this bulb.
            x1 = FarX + sizeProfile["BULB_SPACING"]
            x2 = x1 + sizeProfile["BULB_DIAMETER"] - 1
            # Finally draw each unlit and lit bulb.
            for STATE in bitBulbs:
                #print(f'bitPos={bitPos} bitVal={bitVal} x1={x1} x2={x2} y1={y1} y2={y2} FarX={FarX} STATE={STATE} state={state}')
                bitBulbs[STATE] = hBitfield.guiData["canvas"].create_oval(
                    x1,y1,
                    x2,y2,
                    fill    = PROFILES["LED"][hBitfield.guiData["color"]][STATE],
                    outline = PROFILES["LED"][hBitfield.guiData["color"]]["OFF"] if STATE == "ON" else "black",
                    state   = "normal",
                )
            hBitfield.guiData["bulbs"].append(bitBulbs)
            # If the bitfield is a flag, label the bulb
            if hBitfield.guiData["flags"] is not None:
                hBitfield.guiData["canvas"].create_text(
                    -1+x1+(sizeProfile["BULB_DIAMETER"])/2,
                    -1+y1+(sizeProfile["BULB_DIAMETER"])/2,
                    font  = sizeProfile["flag_font"]
                )
        hBitfield.guiData["canvas"].grid(
            row        = row,
            column     = col,
            sticky     = sticky,
            padx       = sizeProfile["PADDING"],
            pady       = sizeProfile["PADDING"],
            ipadx      = 0,
            ipady      = 0,
            columnspan = columnspan
        )

    def addLabelledBitfieldToWindow(
        self,
        hWnd,
        hBitfield,
        row,
        col,
        columnspan = 1,
        sticky     = "e",
    ):
        sizeProfile = PROFILES[hBitfield.guiData["profile"]]
        fullWidth = sizeProfile["LABEL_WIDTH"] + sizeProfile["LABEL_PADDING"] + ( hBitfield.wordSize * sizeProfile["OUTER_DIAMETER"] )
        # Create the canvas where the bulbs and labels will be added.
        hBitfield.guiData["canvas"] = Canvas(
            hWnd,
            width              = fullWidth,
            height             = sizeProfile["OUTER_DIAMETER"],
            bg                 = PROFILES["COLORS"]["BG"],
            bd                 = 0,
            highlightthickness = 0,
        )
        # Put the label on the left side of the canvas
        ## First draw a rectangular background
        hBitfield.guiData["canvas"].create_rectangle(
            0,0,
            sizeProfile["LABEL_WIDTH"],
            sizeProfile["OUTER_DIAMETER"],
            fill               = PROFILES["COLORS"]["TEXT_BG"],
            outline            = PROFILES["COLORS"]["TEXT_BG"],
        )
        ## Then add the text, right justified aka east-anchored.
        hBitfield.guiData["label"] = hBitfield.guiData["canvas"].create_text(
            sizeProfile["LABEL_WIDTH"] - sizeProfile["LABEL_PADDING"],
            sizeProfile["OUTER_DIAMETER"] / 2,
            fill    = PROFILES["COLORS"]["TEXT_FG"],
            text    = hBitfield.guiData["title"],
            anchor  = "e",
            font    = sizeProfile["label_font"]
        )
        # Before drawing the bulbs, some kinds of bulbs need labels.
        ## The kind of label depends on the kind of bulb, figure that out in advance.
        bulbLabels = dict()
        bulbInvers = dict()
        if hBitfield.guiData["flags"] is not None:
            for flag in hBitfield.guiData["flags"]:
                hFlag = hBitfield.guiData["flags"][flag]
                bulbLabels[hFlag.pos] = flag
                if hFlag.inv == 0:
                    bulbInvers[hFlag.pos] = PROFILES["COLORS"]["FLAG_IN"]
                else:
                    bulbInvers[hFlag.pos] = PROFILES["COLORS"]["FLAG_OV"]
        # Draw the bitfield on the right side of the canvas
        ## Least-significant-bulb starts at a large value of X, X decreases down to zero as significance increases.
        FarX = fullWidth - 1
        # The Y coordinates will be the same for all bulbs.
        y1 = sizeProfile["BULB_SPACING"]
        y2 = y1 + sizeProfile["BULB_DIAMETER"] - 1
        for bitPos in range(hBitfield.wordSize):
            # For efficiency, draw now both the lit and unlit versionsBULB_SPACING
            # later, just toggle the visibility of it.
            bitBulbs = {
                "OFF": None,
                "ON": None,
            }
            # Backtrack the X value for the next-significant-bulb.
            FarX -= sizeProfile["OUTER_DIAMETER"]
            # Calculate the exact X coordinates for this bulb.
            x1 = FarX + sizeProfile["BULB_SPACING"]
            x2 = x1 + sizeProfile["BULB_DIAMETER"] - 1
            # Finally draw each unlit and lit bulb.
            for STATE in bitBulbs:
                #print(f'bitPos={bitPos} bitVal={bitVal} x1={x1} x2={x2} y1={y1} y2={y2} FarX={FarX} STATE={STATE} state={state}')
                bitBulbs[STATE] = hBitfield.guiData["canvas"].create_oval(
                    x1,y1,
                    x2,y2,
                    fill    = PROFILES["LED"][hBitfield.guiData["color"]][STATE],
                    outline = PROFILES["LED"][hBitfield.guiData["color"]]["OFF"] if STATE == "ON" else "black",
                    state   = "normal",
                )
            hBitfield.guiData["bulbs"].append(bitBulbs)
            # If the bitfield is a flag, label the bulb
            if hBitfield.guiData["flags"] is not None:
                hBitfield.guiData["canvas"].create_text(
                    x1+(sizeProfile["BULB_DIAMETER"])/2,
                    y1+(sizeProfile["BULB_DIAMETER"])/2,
                    text  = bulbLabels[bitPos],
                    fill  = bulbInvers[bitPos],
                    font  = sizeProfile["flag_font"]
                )
        hBitfield.guiData["canvas"].grid(
            row        = row,
            column     = col,
            sticky     = sticky,
            padx       = sizeProfile["PADDING"],
            pady       = sizeProfile["PADDING"],
            ipadx      = 0,
            ipady      = 0,
            columnspan = columnspan
        )
