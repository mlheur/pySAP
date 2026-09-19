from pyCPU import BusUser, Bus, ControlLine


class pyRAM(BusUser):
    def __init__(
            self,
            addr_bus            : Bus,
            data_bus            : Bus,
            phase2_control_line : ControlLine,
            rw_control_line     : ControlLine,
        ):
        super().__init__()
        self.rw  = rw_control_line
        self.ph2 = phase2_control_line
        self.busses = {
            'ADDR' : addr_bus,
            'DATA' : data_bus,
        }
        self.contents = [None] * self.connections['addr'].getWidth()

    def tick(self):
        if self.ph2.isTrue() and self.rw.isTrue():
            self.contents[self.busses['ADDR'].read()] = self.busses['DATA'].read()

    def tock(self):
        if self.ph2.isTrue() and not self.rw.isTrue():
            self.busses['DATA'].write(self.contents[self.busses['ADDR'].read()])

