


class Bus(object):
    def __init__(self,width):
        self.value = 0
        self.width = width
        self.mask = 2**width - 1
    def enable(self,value):
        self.value = self.mask & self.value
    def latch(self):
        return self.mask & self.value



class Tap(object):
    def __init__(self,bus):
        self.bus = bus
