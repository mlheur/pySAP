from tkinter import Tk, Toplevel, Canvas, Frame, Scrollbar
from tkinter.font import Font

FONT="Tlwg Mono"

PROFILES = {
    "BIG": {
        "LABEL_WIDTH"   :  60,
        "LABEL_PADDING" :   2,
        "BULB_DIAMETER" :  24,
        "BULB_SPACING"  :   2,
        "FONT_SIZE"     :  16,
        "FLAG_SIZE"     :   8,
    },
    "SML": {
        "LABEL_WIDTH"   :  60,
        "LABEL_PADDING" :   0,
        "BULB_DIAMETER" :  12,
        "BULB_SPACING"  :   0,
        "FONT_SIZE"     :   8,
        "FLAG_SIZE"     :   8,
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
        "BG":      "#444",
        "TEXT_BG": "#222",
        "TEXT_FG": "#ffb",
        "FLAG_IN": "#303",
        "FLAG_OV": "#f9f",
    }
}

class WindowMgr(object):
    SCROLLBAR_WIDTH = 12
    def __init__(self,gui):
        self.gui    = gui
        self.tkroot = Tk()
        self.tkroot.withdraw()

        for P in PROFILES:
            if "FONT_SIZE" in PROFILES[P]:
                PROFILES[P]["labelFont"] = Font(
                    family = FONT,
                    size   = PROFILES[P]["FONT_SIZE"],
                    weight = "bold",
                )
            if "FLAG_SIZE" in PROFILES[P]:
                PROFILES[P]["flagFont"] = Font(
                    family = FONT,
                    size   = PROFILES[P]["FLAG_SIZE"],
                    weight = "bold",
                )

    def close(self):
        self.tkwnd.destroy()

    def createWindow(
        self,
        title = "WindowMgr.bitlistcreateWindow()",
    ):
        hWnd = Toplevel(self.tkroot,bg="#000")
        hWnd.title(title)
        return hWnd

    def createScrollingWindow(
        self,
        nBulbs,
        nCells,
        title = "WindowMgr.createScrollingWindow()",
        profile = "SML"
    ):
        _,_,w,h = self.computeDimensions(PROFILES[profile],nBulbs)
        component_height = h
        h *= nCells
        print(f'w={w} h={h}')
        hWnd = WindowMgr.createWindow(self,title)
        hFrame = Frame(
            hWnd,
            width  = w + self.SCROLLBAR_WIDTH,
            height = h + (3 * self.SCROLLBAR_WIDTH),
        )
        hFrame.pack(expand=True,fill="both")

        hScrollCanvas = Canvas(
            hFrame,
            bg                  = "black",
            bd                  = 0,
            highlightcolor      = PROFILES["COLORS"]["BG"],
            highlightbackground = PROFILES["COLORS"]["BG"],
            scrollregion        = (0,0,w,h+self.SCROLLBAR_WIDTH),
        )
        hBar = Scrollbar(
            hScrollCanvas,
            orient  = "horizontal",
            command = hScrollCanvas.xview,
            width   = self.SCROLLBAR_WIDTH,
        )
        vBar = Scrollbar(
            hScrollCanvas,
            orient  = "vertical",
            command = hScrollCanvas.yview,
            width   = self.SCROLLBAR_WIDTH,
        )
        hBar.pack(side="bottom",fill="x")
        vBar.pack(side="right", fill="y")

        hScrollCanvas.configure(
            width          = w,
            height         = h - self.SCROLLBAR_WIDTH,
            xscrollcommand = hBar.set,
            yscrollcommand = vBar.set,
        )
        hScrollCanvas.pack(
            side   = "left",
            expand = True,
            fill   = "both",
        )

        hSubFrame = Frame(
            hScrollCanvas,
            bg     = "black",
            bd     = 0,
            highlightcolor = PROFILES["COLORS"]["BG"],
            highlightbackground = PROFILES["COLORS"]["BG"],
        )
        idInnerFrame = hScrollCanvas.create_window(
            (1,2),
            window = hSubFrame,
            anchor = "nw",
        )
        hWnd.geometry(f'{10+w+self.SCROLLBAR_WIDTH}x{h+self.SCROLLBAR_WIDTH}+0+0')
        self.refreshWindows()
        self.refreshWindows()
        return hSubFrame

    def refreshWindows(self):
        self.tkroot.update()

    def updateComponents(self,components):
        for hBitfield in components:
            curValue = hBitfield.getValue()
            hBitfield.iterVal = curValue
            if hBitfield.guiData["lastValue"] != curValue:
                hBitfield.guiData["lastValue"] = curValue
                hCanvas = hBitfield.guiData['canvas']
                hBulbs  = hBitfield.guiData['bulbs']

                for bitPos,bitVal in enumerate(hBitfield):
                    if bitVal:
                        # hide the OFF bulb
                        hCanvas.itemconfigure(hBulbs[bitPos]["OFF"],state="hidden")
                        # show the ON bulb
                        hCanvas.itemconfigure(hBulbs[bitPos]["ON"],state="normal")
                    else:
                        # hide the ON bulb
                        hCanvas.itemconfigure(hBulbs[bitPos]["ON"],state="hidden")
                        # show the OFF bulb
                        hCanvas.itemconfigure(hBulbs[bitPos]["OFF"],state="normal")

    def computeDimensions(self,sizeProfile,nBulbs):
        bulbs_height = sizeProfile["BULB_DIAMETER"] + ( 2 * sizeProfile["BULB_SPACING"])
        bulbs_width  = bulbs_height * nBulbs
        component_height = bulbs_height
        component_width  = sizeProfile["LABEL_WIDTH"] + bulbs_width
        return bulbs_width,bulbs_height,component_width,component_height

    def placeComponentAt(
        self,
        hWnd,
        hBitfield,
        row,
        col,
        columnspan = 1,
        sticky     = "w",
    ):
        sizeProfile = PROFILES[hBitfield.guiData["profile"]]
        bulbs_width,bulbs_height,component_width,component_height = self.computeDimensions(sizeProfile,hBitfield.wordSize)
        #print(f'bulbs_height={bulbs_height} bulbs_width={bulbs_width}')
        # Create the canvas
        hBitfield.guiData["canvas"] = Canvas(
            hWnd,
            width  = component_width,
            height = component_height,
            bg     = PROFILES["COLORS"]["BG"],
            bd     = 0,
            highlightcolor = PROFILES["COLORS"]["BG"],
            highlightbackground = PROFILES["COLORS"]["BG"],
        )
        # Put the label on the left side of the canvas
        hBitfield.guiData["canvas"].create_rectangle(
            0,
            0,
            sizeProfile["LABEL_WIDTH"],
            component_height,
            fill    = PROFILES["COLORS"]["TEXT_BG"],
        )
        hBitfield.guiData["label"] = hBitfield.guiData["canvas"].create_text(
            sizeProfile["LABEL_WIDTH"] - sizeProfile["LABEL_PADDING"],
            component_height / 2,
            fill    = PROFILES["COLORS"]["TEXT_FG"],
            text    = hBitfield.guiData["title"],
            anchor  = "e",
            font    = sizeProfile["labelFont"]
        )
        # Draw the bitfield on the right side of the canvas
        FarX = component_width
        y1 = sizeProfile["BULB_SPACING"] + 1
        y2 = y1 + sizeProfile["BULB_DIAMETER"] - 1

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

        for bitPos,bitVal in enumerate(hBitfield):
            # For efficiency, draw now both the lit and unlit versionsBULB_SPACING
            # later, just toggle the visibility of it.
            bitBulbs = {
                "ON": None,
                "OFF": None,
            }
            FarX -= bulbs_height
            x1 = FarX + sizeProfile["BULB_SPACING"] + 1
            x2 = x1 + sizeProfile["BULB_DIAMETER"] - 1
            for STATE in bitBulbs:
                if (STATE == "ON" and bitVal) or (STATE == "OFF" and not bitVal):
                    state = "normal"

                else:
                    state = "hidden"
                #print(f'bitPos={bitPos} bitVal={bitVal} x1={x1} x2={x2} y1={y1} y2={y2} FarX={FarX} STATE={STATE} state={state}')
                bitBulbs[STATE] = hBitfield.guiData["canvas"].create_oval(
                    x1,y1,
                    x2,y2,
                    fill    = PROFILES["LED"][hBitfield.guiData["color"]][STATE],
                    outline = PROFILES["LED"][hBitfield.guiData["color"]]["OFF"] if STATE == "ON" else "black",
                    state   = state,
                )
            hBitfield.guiData["bulbs"].append(bitBulbs)
            # If the bitfield is a flag, label the bulb
            if hBitfield.guiData["flags"] is not None:
                hBitfield.guiData["canvas"].create_text(
                    x1+(sizeProfile["BULB_DIAMETER"])/2,
                    y1+(sizeProfile["BULB_DIAMETER"])/2,
                    text  = bulbLabels[bitPos],
                    fill  = bulbInvers[bitPos],
                    font  = sizeProfile["flagFont"]
                )
        hBitfield.guiData["canvas"].grid(row=row,column=col,sticky=sticky,padx=1,pady=1,columnspan=columnspan)
        #print(f'bulbs={hBitfield.guiData["bulbs"]}')
