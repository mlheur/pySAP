from tkinter import Tk, Toplevel, Canvas, Frame, Scrollbar
from tkinter.font import Font

FONT="Tlwg Mono"
WMGR_X=24
WMGR_Y=60

PROFILES = {
    "BIG": {
        "LABEL_WIDTH"   :  48,
        "LABEL_PADDING" :   2,
        "BULB_DIAMETER" :  24,
        "BULB_SPACING"  :   1,
        "PADDING"       :   1,
        "FONT_SIZE"     :  16,
        "FLAG_SIZE"     :   8,
    },
    "SML": {
        "LABEL_WIDTH"   :  40,
        "LABEL_PADDING" :   1,
        "BULB_DIAMETER" :   8,
        "BULB_SPACING"  :   0,
        "PADDING"       :   0,
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
        "BG":      "#555",
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
        self._dimCache = dict()

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

    def getWmgrX(self):
        return WMGR_X

    def getWmgrY(self):
        return WMGR_Y

    def quit(self):
        self.tkwnd.destroy()

    def getDimension(self,profile,nBulbs):
        if profile in self._dimCache and nBulbs in self._dimCache[profile]:
            return self._dimCache[profile][nBulbs]
        if profile not in self._dimCache:
            self._dimCache[profile] = dict()

        thisProfile = PROFILES[profile]

        outer_diameter_bulbs = thisProfile["BULB_DIAMETER"] + ( 2 * thisProfile["BULB_SPACING"] )
        width_of_all_bulbs = nBulbs * outer_diameter_bulbs
        dim = {
            "width": {
                "bulbs"    : width_of_all_bulbs,
                "label"    : thisProfile["LABEL_WIDTH"],
                "component": thisProfile["LABEL_WIDTH"] + width_of_all_bulbs + ( 2 * thisProfile["PADDING"] ),
            },
            "height": {
                "bulbs"    : outer_diameter_bulbs,
                "label"    : outer_diameter_bulbs,
                "component": outer_diameter_bulbs + ( 2 * thisProfile["PADDING"] ),
            },
        }
        self._dimCache[profile][nBulbs] = dict(dim)
        return self._dimCache[profile][nBulbs]

    def createWindow(
        self,
        title = "WindowMgr.bitlistcreateWindow()",
    ):
        hWnd = Toplevel(self.tkroot,bg=PROFILES["COLORS"]["BG"])
        hWnd.title(title)
        return hWnd

    def createScrollingWindow(
        self,
        nBulbs,
        nCells,
        title   = "WindowMgr.createScrollingWindow()",
        profile = "SML"
    ):
        component_dimensions = self.getDimension(profile,nBulbs)
        total_height         = nCells * (2+component_dimensions["height"]["component"])
        window_dimensions = {
            "width": {
                "subwindow" : component_dimensions["width"]["component"],
                "clientarea": component_dimensions["width"]["component"] + self.SCROLLBAR_WIDTH,
                "dressings" : 2,
            },
            "height": {
                "subwindow" : total_height,
                "clientarea": total_height + self.SCROLLBAR_WIDTH,
                "dressings" : 0,
            },
        }

        hWnd = WindowMgr.createWindow(self,title)
        _w = window_dimensions["width"]["dressings"]  + window_dimensions["width"]["clientarea"]
        _h = window_dimensions["height"]["dressings"] + window_dimensions["height"]["clientarea"]
        #print(f'hwnd.geometry({_w}x{_h}+0+0)')
        hWnd.geometry(f'{_w}x{_h}+0+0')

        _w = window_dimensions["width"]["clientarea"]
        _h = window_dimensions["height"]["clientarea"]
        #print(f'hScrollCanvas({_w}x{_h}+0+0)')
        hScrollCanvas = Canvas(
            hWnd,
            width              = _w,
            height             = _h,
            bg                 = "#080",
            scrollregion       = (0,0,_w,_h),
            bd                 = 0,
            highlightthickness = 0,
        )
        hBar = Scrollbar(
            hWnd,
            orient  = "horizontal",
            command = hScrollCanvas.xview,
            width   = self.SCROLLBAR_WIDTH,
        )
        hBar.pack(side="bottom",fill="x")
        vBar = Scrollbar(
            hWnd,
            orient  = "vertical",
            command = hScrollCanvas.yview,
            width   = self.SCROLLBAR_WIDTH,
        )
        vBar.pack(side="right", fill="y")

        _w = window_dimensions["width"]["clientarea"]
        _h = window_dimensions["height"]["clientarea"]
        #print(f'hScrollCanvas.configure({_w}x{_h}+0+0)')
        hScrollCanvas.configure(
            xscrollcommand = hBar.set,
            yscrollcommand = vBar.set,
            width          = _w,
            height         = _h,
        )
        hSubFrame = Frame(
            hScrollCanvas,
        )
        idInnerFrame = hScrollCanvas.create_window(
            (0,0),
            window = hSubFrame,
            anchor = "nw",
        )
        hSubFrame.bind(
            "<Configure>",
            lambda e: hScrollCanvas.configure(scrollregion=hScrollCanvas.bbox("all"))
        )
        hScrollCanvas.pack()
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
                        #hCanvas.itemconfigure(hBulbs[bitPos]["OFF"],state="hidden")
                        # show the ON bulb
                        hCanvas.itemconfigure(hBulbs[bitPos]["ON"],state="normal")
                    else:
                        # hide the ON bulb
                        hCanvas.itemconfigure(hBulbs[bitPos]["ON"],state="hidden")
                        # show the OFF bulb
                        #hCanvas.itemconfigure(hBulbs[bitPos]["OFF"],state="normal")

    def placeComponentAt(
        self,
        hWnd,
        hBitfield,
        row,
        col,
        columnspan = 1,
        sticky     = "w",
        padx       = 1,
        pady       = 1,
    ):
        sizeProfile = PROFILES[hBitfield.guiData["profile"]]
        component_dimensions = self.getDimension(hBitfield.guiData["profile"],hBitfield.wordSize)
        #print(f'bulbs_height={bulbs_height} bulbs_width={bulbs_width}')
        # Create the canvas
        hBitfield.guiData["canvas"] = Canvas(
            hWnd,
            width              = component_dimensions["width"]["component"],
            height             = component_dimensions["height"]["component"],
            bg                 = PROFILES["COLORS"]["BG"],
            bd                 = 0,
            highlightthickness = 0,
        )
        # Put the label on the left side of the canvas
        hBitfield.guiData["canvas"].create_rectangle(
            0,0,
            sizeProfile["LABEL_WIDTH"]-1,
            component_dimensions["height"]["label"]-1,
            fill               = PROFILES["COLORS"]["TEXT_BG"],
            outline            = PROFILES["COLORS"]["TEXT_BG"],
        )
        hBitfield.guiData["label"] = hBitfield.guiData["canvas"].create_text(
            sizeProfile["LABEL_WIDTH"] - sizeProfile["LABEL_PADDING"],
            component_dimensions["height"]["label"] / 2,
            fill    = PROFILES["COLORS"]["TEXT_FG"],
            text    = hBitfield.guiData["title"],
            anchor  = "e",
            font    = sizeProfile["label_font"]
        )

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
        FarX = component_dimensions["width"]["component"]
        y1 = sizeProfile["BULB_SPACING"]
        y2 = y1 + sizeProfile["BULB_DIAMETER"] - 2
        for bitPos,bitVal in enumerate(hBitfield):
            # For efficiency, draw now both the lit and unlit versionsBULB_SPACING
            # later, just toggle the visibility of it.
            bitBulbs = {
                "OFF": None,
                "ON": None,
            }
            FarX -= component_dimensions["height"]["bulbs"]
            x1 = FarX + sizeProfile["BULB_SPACING"]
            x2 = x1 + sizeProfile["BULB_DIAMETER"] - 2
            for STATE in bitBulbs:
                #print(f'bitPos={bitPos} bitVal={bitVal} x1={x1} x2={x2} y1={y1} y2={y2} FarX={FarX} STATE={STATE} state={state}')
                bitBulbs[STATE] = hBitfield.guiData["canvas"].create_oval(
                    x1,y1,
                    x2+1,y2+1,
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
        hBitfield.guiData["canvas"].grid(row=row,column=col,sticky=sticky,padx=padx,pady=pady,ipadx=0,ipady=0,columnspan=columnspan)
        #print(f'bulbs={hBitfield.guiData["bulbs"]}')
