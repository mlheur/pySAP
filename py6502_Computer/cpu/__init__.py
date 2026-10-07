from pyCPU import pyCPU


class py6502(pyCPU):

    def __init__(
            self,
            socket,
        ):
        super().__init__(bits=8,socket=socket)

    def _updateControlLine(self,control_name,direction):
        self.external_control_tracker[control_name] += direction
        self.external_control_lines[control_name].setTruth(self.external_control_tracker[control_name]>0)

    def assertControlLine(self,control_name):
        self._updateControlLine(control_name,1)

    def releaseControlLine(self,control_name):
        self._updateControlLine(control_name,-1)


