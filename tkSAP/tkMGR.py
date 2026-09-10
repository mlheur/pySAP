from tkinter import Tk, Menu, PanedWindow, Frame, BOTH, LEFT, BOTTOM, RIGHT, TOP, HORIZONTAL, VERTICAL
from tkinter.font import Font

from .constants import PROFILES, DEFAULTS


class tkMGR(object):
    def __init__(self,title):
        self.root = Tk()
        self.root.title(title)
        # Resize to fullscreen
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        x = 0
        y = 0
        g = f'{w}x{h}+{x}+{y}'
        self.root.geometry(g)
        # Generate the fonts that will be used in the UI
        for P in PROFILES:
            if "FONT_SIZE" in PROFILES[P]:
                PROFILES[P]["label_font"] = Font(
                    family = DEFAULTS['FONT'],
                    size   = PROFILES[P]["FONT_SIZE"],
                    weight = "bold",
                )
            if "FLAG_SIZE" in PROFILES[P]:
                PROFILES[P]["flag_font"] = Font(
                    family = DEFAULTS['FONT'],
                    size   = PROFILES[P]["FLAG_SIZE"],
                    weight = "bold",
                )
        # Pre-compute some dimensions
        for profile in PROFILES:
            if "BULB_DIAMETER" in PROFILES[profile]:
                PROFILES[profile]["OUTER_DIAMETER"] = PROFILES[profile]["BULB_DIAMETER"] + ( 2 * PROFILES[profile]["BULB_SPACING"])

    def build_menu(self,handler,menuitems):
        menu = Menu(self.root)
        for submenu in menuitems:
            sub = Menu(menu, tearoff=0)
            for item in menuitems[submenu]:
                if item == "---":
                    sub.add_separator()
                else:
                    callback = getattr(handler,menuitems[submenu][item])
                    if '_' in item:
                        under = item.index('_')
                        label = item[:under] + item[under+1:]
                        sub.add_command(label=label,command=callback, underline=under)
                    else:
                        sub.add_command(label=item,command=callback)
            if '_' in submenu:
                under = submenu.index('_')
                label = submenu[:under] + submenu[under+1:]
                menu.add_cascade(menu=sub,label=label,underline=under)
            else:
                menu.add_cascade(menu=sub,label=submenu)
            sub=None # GC
        self.root.config(menu=menu)
        self.root.protocol("WM_DELETE_WINDOW", getattr(handler,"file_quit"))

    def build_panes(self):
        panes = dict()
        # Create the outermost frame that's got a horizontal divider
        panes['OUTER'] = PanedWindow(orient=VERTICAL)
        # Create the inner frame on the upper half that's got a vertical divider
        panes['INNER'] = PanedWindow(panes['OUTER'], orient=HORIZONTAL)
        panes['INNER'].pack(side=TOP)
        panes['OUTER'].add(panes['INNER'])
        # Create the RAM frame on the lower half of the outer frame
        panes['RAM'] = Frame(self.root,bg='blue')
        panes['RAM'].pack(side=BOTTOM)
        panes['OUTER'].add(panes['RAM'])
        # Create the clock and CPU that wil go on the left and right halves of the lower frame.
        panes['CLK'] = Frame(panes['INNER'],bg='red')
        panes['CLK'].pack(side=RIGHT)
        panes['INNER'].add(panes['CLK'])
        panes['CPU'] = Frame(panes['INNER'],bg='green')
        panes['CPU'].pack(side=LEFT)
        panes['INNER'].add(panes['CPU'])
        panes['OUTER'].pack(fill=BOTH,expand=True)
        return panes
