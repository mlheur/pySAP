

class guiBitfield(object):
    def __init__(
        self,
        wordSize,
        color,
        title,
        getValue     = None,
        getAddrValue = None,
        addr         = None,
        profile      = "BIG",
        flags        = None,
    ):
        self.getValue     = getValue
        self.getAddrValue = getAddrValue
        self.addr         = addr
        self.wordSize     = wordSize
        self.iterPtr      = None
        self.iterVal      = None
        self.guiData      = {
            "title"     : title,
            "canvas"    : None,
            "label"     : None,
            "bulbs"     : list(),
            "profile"   : profile,
            "color"     : color,
            "lastValue" : None,
            "flags"     : flags,
        }

    def get(self):
        if self.addr is not None:
            return self.getAddrValue(self.addr)
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
