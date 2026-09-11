DEFAULTS = {
    'Hz'          : 50,
    'EXT'         : '.sap',
    'DIR'         : './code/',
    'FONT'        : 'Oxygen Mono',
    'RAM_COLUMNS' : 16,
}

PROFILES = {
    "CLK": {
        "BLOCK_SIZE"      : 150,
        "BORDER_SIZE"     :  15,
        "TEXT_PAD_FACTOR" :   1.5,
    },
    "BIG": {
        "LABEL_WIDTH"     :  40,
        "LABEL_PADDING"   :   1,
        "BULB_DIAMETER"   :  20,
        "BULB_SPACING"    :   1,
        "PADDING"         :   0,
        "FONT_SIZE"       :  16,
        "FLAG_SIZE"       :   6,
        "SPACER"          :   8,
    },
    "SML": {
        "LABEL_WIDTH"     :  30,
        "LABEL_PADDING"   :   0,
        "BULB_DIAMETER"   :   6,
        "BULB_SPACING"    :   0,
        "PADDING"         :   0,
        "FONT_SIZE"       :   6,
        "FLAG_SIZE"       :   0,
        "SPACER"          :   1,
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
