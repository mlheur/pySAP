from threading import Thread
from time import sleep


class clock_thread(Thread):
    def __init__(self,clk):
        super().__init__()
        self.clk         = clk
        self.running     = True
        self.kill        = False

    def run(self):
        self.clk.modify(self.clk.Hz)
        while not self.kill:
            while self.running and self.clk.Hz > 0 and not self.clk.cpu.oflags['HLT'].istrue():
                self.clk.pulse()
            sleep(self.clk.NoTime)
            if not self.running:
                sleep(0.1)

    def resume(self):
        self.running = True

    def stop(self,final=False):
        self.running = False
        self.kill = final
