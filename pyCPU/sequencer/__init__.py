from logger import LOGGER, TRACE, INFO

from random import randint


class Sequencer():

    def __init__(self,cpu,bits=4):
        self.Tstep              = randint(0,bits)

    def createMicroInstruction(self,ctl_list):
        result = 0
        for ctl in self.cpu.control_lines:
            control_line = self.cpu.control_lines[ctl]
            if (control_line.inverted or ctl not in ctl_list) or (not control_line.inverted and ctl in ctl_list):
                result &= ~control_line.mask
            else:
                result |= control_line.mask
        self.micro_instructions.append(result)
        return len(self.micro_instructions)

    def addInstructionEntry(self,instruction,conditions,micro_instruction_index):
        self.isntr_to_micro[instruction] = dict() if self.isntr_to_micro[instruction] is None else self.isntr_to_micro[instruction]
        self.isntr_to_micro[instruction][conditions] = micro_instruction_index

    def decode(self):
        do_clear = self.clr.istrue()
        if do_clear:
            self.micro = self.CROM[2] & ~(self.clr.mask)
        else:
            if self.Tstep <= 0x2:
                self.micro = self.CROM[self.Tstep]
            else:
                conditions = self.iflags()
                try:
                    microaddr = (self.AROM[conditions][self.cpu.ir.value]) + (self.Tstep-3)
                    self.micro = self.CROM[microaddr]
                except KeyError:
                    print(f'Invalid opcode: 0x{self.cpu.ir.value:02X} at address 0x{self.cpu.pc.value-1:02X}')
                    #input("Press [Enter] to continue")
                    for F in self.cpu.oflags:
                        self.cpu.oflags[F].settruth(False)
                    self.ResetT.settruth(True)
                    self.hlt.settruth(True)
                    self.clr.settruth(True)
                    self.invalid_opcode.settruth(True)
                    return
        for F in self.cpu.oflags:
            self.cpu.oflags[F].update(self.micro)
        return do_clear

    def clock(self,components,subscribers):
        LOGGER.log(TRACE,f'++CtlSeq:clock()')
        # Parse the subinstruction
        do_clear = self.decode()
        LOGGER.log(2,f'micro after decode:     {self.micro:b}')

        # enable to bus
        for component in components:
            component.tick()

        if do_clear:
            self.clr.value = self.clr.inv
            self.ResetT.value = self.ResetT.inv

        # Update GUI
        for subby in subscribers:
            if hasattr(subby,"clock"):
                subby.clock()

        if self.hlt.istrue():
            return

        # latch from bus
        for component in components:
            component.tock()

        # update iflags if relevant set/clr oflag is set.
        for CMD in "SC": # Set or Clr
            for FLG in "CZ": # Carry or Zero
                oCTL = f'{CMD}{FLG}'
                iCTL = f'{FLG}F'
                if self.cpu.oflags[oCTL].istrue():
                    self.cpu.iflags[iCTL].settruth(CMD == "S")

#        #print("A={:08x} B={:08x} OUT={:08x} IR={:08x} PC={:08x} MAR={:08x} ALU={:08x}".format(
#            self.cpu.a.value,
#            self.cpu.b.value,
#            self.cpu.out.value,
#            self.cpu.ir.value,
#            self.cpu.pc.value,
#            self.cpu.mar.value,
#            self.cpu.alu.value
#        ))

        # Increment the RingCounter
        if do_clear:
            for f in self.cpu.oflags:
                self.cpu.oflags[f].value = self.cpu.oflags[f].inv
            self.Tstep = 1
        elif self.micro == self.CROM[0]:
            self.Tstep = 1
        elif self.ResetT.istrue():
            self.Tstep = 1
        else:
            self.Tstep += 1
        LOGGER.log(TRACE,f'--CtlSeq:clock(): Normal exit')
