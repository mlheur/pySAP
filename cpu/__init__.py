from .control_line import ControlLine
from .sequencer import Sequencer


class CPU(object):

    def __init__(self,bits,address_space):
        self.address_space   = address_space
        self.bits            = bits
        self.mask            = (2**self.bits)-1
        self.bus             = 0
        self.flags           = dict()
        self.control_lines   = dict()
        self.components      = dict()
        self.assert_on_reset = list()
        self.sequencer       = Sequencer(self)

    def _getBinarySequence(self,from_dict):
        result = 0
        for flag in from_dict:
            result |= from_dict[flag].value << from_dict[flag].pos
        return result

    def getFlags(self):
        return self._getBinarySequence(self.flags)

    def getControlLines(self):
        return self._getBinarySequence(self.control_lines)

    def _addLine(self,to_dict,name,position,inverted,**args):
        to_dict[name] = ControlLine(position,inverted)
        if "assert_on_reset" in args and args["assert_on_reset"]:
            self.assert_on_reset.append(to_dict[name])

    def addFlag(self,**args):
        self._addLine(self.flags,**args)

    def addControlLine(self,**args):
        self._addLine(self.flags,**args)

    def addComponent(self,name,component):
        self.components[name] = component

    def clock(self,subscribers=[]):
        self.sequencer.clock(subscribers)

    def addAssemblyInstruction(self,instruction,arg,*args):
        if type(arg) is int:
            for flags in range(len(self.flags)):
                self.sequencer.addInstructionEntry(
                    instruction,
                    conditions=flags,
                    micro_instruction=arg
                )
            return len(self.sequencer.micro_instructions)
        if type(arg) is dict:
            for flags in range(len(self.flags)):
                if flags not in arg:
                    self.sequencer.addInstructionEntry(
                        instruction,
                        conditions=flags,
                        micro_instruction=arg[flags]
                    )
                else:
                    self.sequencer.addInstructionEntry(
                        instruction,
                        conditions=flags,
                        micro_instruction=args[0]
                    )

    def reset(self):
        for flag in self.assert_on_reset:
            flag.settruth(True)

