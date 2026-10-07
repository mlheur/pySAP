from .control_line import ControlLine, GroundLine, VccLine

def buildPinoutFromDefinition(pinout_details:list[dict[str:dict[str:object]]]):
    pins : list[ControlLine] = [None] * len(pinout_details)
    for i,pin_object in enumerate(pinout_details):
        [pin_name]    = pin_object.keys()
        [pin_details] = pin_object.values()
        if pin_name == 'GND':
            pins[i] = GroundLine(position=i)
        elif pin_name == 'Vcc':
            pins[i] = VccLine(position=i)
        elif pin_details is not None and 'pin_id' in pin_details:
            pins[i] = ControlLine(
                position = pin_details['pin_id'],
                inverted = ('inverted' in pin_details and pin_details['inverted']),
            )
    return pins

def buildPinoutFromPinCollection(
        collection:list[ControlLine],
        pin_id_list:list[int]
    ):
    pins = [None] * len(pin_id_list)
    for i in range(len(pin_id_list)):
        pins[i] = collection[pin_id_list[i]]
    return pins


class pySocket(object):

    def __init__(self,pins):
        self.pins   = pins
        self.busses = {}

    def makeBus(self,name:str,pin_id_list:list[int]) -> list[ControlLine]:
        self.busses[name] = buildPinoutFromPinCollection(self.pins,pin_id_list)

    def readPin(self,pin_id:int) -> bool:
        return self.pins[pin_id].isTrue()

    def writePin(self,pin_id:int,value:bool):
        self.pins[pin_id].setTruth(value)

    def getBus(self,name:str) -> list[ControlLine]:
        return self.busses[name]

    def attachToBus(self,bus:list[ControlLine],name:str):
        self.busses[name] = bus

    def readBus(self,name:str) -> int:
        value = 0
        bus = self.busses[name]
        for i in len(bus):
            value |= int(self.readPin(bus[i].position)) << i
        return value

    def writeBus(self,name:str,value:int):
        value = f'{value:b}'
        pins = self.busses[name]
        for i in range(len(value)):
            self.writePin(
                pin_id = pins[i].position,
                value  = value[i] != "0",
            )
