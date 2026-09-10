DEFAULTS = {
    'Hz'   : 50,
    'EXT'  : '.sap',
    'DIR'  : './code/',
    'FONT' : 'Courier',
}

PROFILES = {
    "BIG": {
        "LABEL_WIDTH"   :  72,
        "LABEL_PADDING" :   1,
        "BULB_DIAMETER" :  24,
        "BULB_SPACING"  :   2,
        "PADDING"       :   1,
        "FONT_SIZE"     :  22,
        "FLAG_SIZE"     :   8,
        "SPACER"        :   8,
    },
    "SML": {
        "LABEL_WIDTH"   :  35,
        "LABEL_PADDING" :   1,
        "BULB_DIAMETER" :   8,
        "BULB_SPACING"  :   0,
        "PADDING"       :   0,
        "FONT_SIZE"     :   6,
        "FLAG_SIZE"     :   0,
        "SPACER"        :   1,
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
