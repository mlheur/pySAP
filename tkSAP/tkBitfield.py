from .constants import PROFILES


class tkBitfield(object):
    def __init__(
        self,
        wordSize     = None,
        color        = None,
        title        = None,
        x            = None,
        y            = None,
        getValue     = None,
        getAddrValue = None,
        addr         = None,
        profile      = "BIG",
        flags        = None,
        show_label   = True,
        canvas       = None,
        justify      = "left",
    ):
        self.canvas        = canvas
        self.color         = color
        self.title         = title
        self.profile       = PROFILES[profile]
        self.flags         = flags
        self.wordSize      = wordSize
        self.getValue      = getValue
        self.getAddrValue  = getAddrValue
        self.addr          = addr
        self.iterPtr       = None
        self.iterVal       = None
        self.justify       = justify
        self.last_value    = None
        self.last_sequence = [True] * self.wordSize
        # Assert the parameters are sufficient
        if (self.addr is None and self.getValue is None) or (self.addr is not None and self.getAddrValue is None):
            raise RuntimeError('FATAL: tkBitfield constructor requires either [addr and getAddrValue] or [getValue]')
        if self.justify != "left" and self.justify != "right":
            raise RuntimeError('FATAL: justify must be one of "left" or "right"')
        # Preallocate arrays
        self.bulbs        = {
            True  : [] * self.wordSize,
            False : [] * self.wordSize,
        }
        ###
        # Determine overall dimensions, this bitfield widget is drawn from right-to-left;
        # and then placed on the canvas based on justify value.
        ###
        # Allocate some space for tha label or spacer
        lbl_width   = self.profile['LABEL_WIDTH'] if show_label else self.profile['SPACER']
        # Allocate some padding around the backplates, bulbs for sure, label if shown.
        qty_padding = 4 if show_label else 2
        # The width is [pad+label+pad]+[pad+bulbs+pad] or [spacer][pad+bulbs+pad]
        w = (qty_padding*self.profile['LABEL_PADDING']) + lbl_width + (self.wordSize * self.profile['OUTER_DIAMETER'])
        h = (self.profile['OUTER_DIAMETER']) + (2*self.profile['LABEL_PADDING'])
        # The final coordinates are chosen ...
        self.coords       = {'x':x,'y':y,'w':w,'h':h}
        # ... except when right-justified we have to translate the left-most pixel leftward according to the final width
        if self.justify == "right":
            self.coords['x'] -= w
        # The widget size and position is fixed, all remaining components are relative to self.coords
        y1 = self.coords['y'] + self.profile['LABEL_PADDING']
        y2 = self.coords['y'] + self.coords['h'] - self.profile['LABEL_PADDING']
        if show_label:
            # Create a backplate for the label
            x1 = self.coords['x'] + self.profile['LABEL_PADDING']
            x2 = x1               + self.profile['LABEL_WIDTH']
            x3 = x2 - 1
            y3 = self.coords['y'] + self.profile['LABEL_PADDING'] + (0.5 * self.profile['OUTER_DIAMETER'])
            self.canvas.create_rectangle(
                x1,y1,x2,y2,
                fill    = PROFILES["COLORS"]["TEXT_BG"],
                width   = 0,
            )
            # Draw the label text
            self.canvas.create_text(
                x3,y3,
                anchor  = 'e',
                font    = self.profile['label_font'],
                text    = self.title,
                fill    = PROFILES["COLORS"]["TEXT_FG"],
            )
        # Create a backplate for the bulbs.
        x1 = self.coords['x'] + (3 * self.profile['LABEL_PADDING']) + lbl_width
        x2 = self.coords['x'] + self.coords['w'] - self.profile['LABEL_PADDING']
        # y1 and y2 remain the same as for the label backplate
        self.canvas.create_rectangle(
            x1,y1,x2,y2,
            fill    = PROFILES["COLORS"]["BG"],
            width   = 0,
        )
        # Finally create each bulb,
        # they all share the same y coordinates
        y1 = self.coords['y'] + self.profile['LABEL_PADDING'] + self.profile['BULB_SPACING']
        y2 = y1 + self.profile['BULB_DIAMETER']
        FarX = self.coords['x'] + self.coords['w'] - self.profile['LABEL_PADDING']
        if self.flags is not None:
            flag_labels = [None] * self.wordSize
            flag_colors = [None] * self.wordSize
            for title in self.flags:
                flag = self.flags[title]
                flag_labels[flag.pos] = title
                flag_colors[flag.pos] = PROFILES["COLORS"]["FLAG_IN"] if flag.inv == 0 else PROFILES["COLORS"]["FLAG_OV"]
        for i in range(self.wordSize):
            self.bulbs[i] = dict()
            FarX -= self.profile['OUTER_DIAMETER']
            x1    = FarX + self.profile['BULB_SPACING'] 
            x2    = x1   + self.profile['BULB_DIAMETER']
            for state in [False,True]:
                fill    = PROFILES['LED'][self.color]["ON"]  if state else PROFILES['LED'][self.color]["OFF"]
                outline = PROFILES['LED'][self.color]["OFF"] if state else '#000'
                self.bulbs[i][state] = self.canvas.create_oval(
                    x1,y1,x2-1,y2-1,
                    fill    = fill,
                    outline = outline,
                    state   = "normal",
                    width   = 1,
                )
            # If the bitfield is a flag, label the bulb
            if self.flags is not None:
                #print(f'Labelling the bulb flag_labels[i={i}]={flag_labels[i]}')
                self.canvas.create_text(
                    x1+(self.profile["BULB_DIAMETER"]/2),
                    y1+(self.profile["BULB_DIAMETER"]/2),
                    font = self.profile["flag_font"],
                    text = flag_labels[i],
                    fill = flag_colors[i],
                )

    def update(self):
        current_value = self.get()
        if self.last_value is not None and self.last_value == current_value:
            return
        self.last_value = current_value
        for i,bit in enumerate(self):
            if self.last_sequence[i] != bit:
                self.last_sequence[i] = bit
                state   = "normal" if bit else "hidden"
                bulb_id = self.bulbs[i][True]
                self.canvas.itemconfigure(bulb_id,state=state)

    def get(self):
        if self.addr is not None:
            result = self.getAddrValue(self.addr)
            #print(f'getting value at addr {self.addr}, result={result}')
            self.iterPtr = 0
            self.iterVal = result
            return result
        return self.getValue()

    def __iter__(self):
        return self

    def __next__(self):
        if self.iterPtr is None:
            self.iterPtr = 0
            if self.iterVal is None:
                self.iterVal = self.get()
        if self.iterPtr >= self.wordSize:
            self.iterPtr = None
            self.iterVal = None
            raise StopIteration
        bIsBitLit = 0 != 0b1 << self.iterPtr & self.iterVal
        self.iterPtr += 1
        return bIsBitLit

#if __name__ == "__main__":
    #getter = lambda : 0xA5
    #r = guiBitfield(getter,8,None,None)
    #for b in r:
        #print(f'b {b}')
