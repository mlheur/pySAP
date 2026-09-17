from random import randint


class ControlLine():

    def __init__(self,position,inverted):
        self.position   = position
        self.mask       = 1 << self.position
        self.value      = bool(randint(0,1))
        self.inverted   = inverted

    def update(self,word):
        self.value      = (word & self.mask) >> self.position

    def settruth(self,truth):
        self.value = int(truth != self.inv)

    def istrue(self):
        return not self.value == self.inv

