from . import StdRegister
from threading import Thread


class OUT(StdRegister):
    def __init__(self,cpu,clr,latch=None,enable=None):
        super().__init__(cpu,clr,latch,enable)
        self.nROWS = 0
        self.thread = Thread(target=self.print)

    def print(self):
        if self.nROWS % 25 == 0:
            print(f'')
            print(f'SEQ |    BINARY |  HEX | DEC')
            print(f'===   =========   ====   ===')
            print(f'')
        vBIN = f'{self.value:08b}'
        vBIN = f'{vBIN[0:4]} {vBIN[3:7]}'
        vHEX = f'0x{self.value:02X}'
        vDEC = f'{self.value:03d}'
        vSEQ = f'{self.nROWS:03d}'
        print(f'{vSEQ}   {vBIN}   {vHEX}   {vDEC}')
        self.nROWS += 1
        self.thread = Thread(target=self.print)

    def tock(self):
        super().tock()
        if self.latch.istrue():
            try:
                self.thread.start()
            except:
                pass
