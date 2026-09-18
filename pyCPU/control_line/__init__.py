from random import randint


class ControlLine():

    _NEXT = 0

    def __init__(
            self,
            position: int = None,
            inverted: bool = False
        ):
        if position is None:
            self.position = ControlLine._NEXT
            ControlLine._NEXT += 1
        else:
            self.position = position
            ControlLine._NEXT = position + 1
        self.mask     = 1 << self.position
        self.value    = bool(randint(0,1))
        self.inverted = inverted

    def update(self,control_word):
        self.value    = ((control_word & self.mask) == 0)

    def setTruth(self,truth):
        self.value    = truth != self.inverted

    def isTrue(self):
        return not self.value == self.inverted

    def __str__(self):
        return f'ControlLine(position={self.position},mask=0x{self.mask:X},value={self.value},inverted={self.inverted},isTrue()={self.isTrue()})'
