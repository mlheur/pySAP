from ctl import CtlLine


# The class is where the microinstructions are figured out
# for the instruction decoder.  This implementation of SAP CPU
# is using a lookup table: for each instruction, for each t-step
# in those instructions, what is the bitwise representation of
# the various control lines that have to be pulled high and low
# to set the various Enable and Latch lines on the components.
class instruction_set(object):
    def __str__(self) -> str:
        ret = ""
        for cond in self.addr:
            for i,asm in enumerate(self.addr[cond]):
                ret = "{}\naddress=[0x{:02X}] condition=[0b{:02b}] asm=[0x{:02X}] microinstruction=[0x{:02X}]".format(ret,i,cond,asm,self.addr[cond][asm])
        return ret
    # mkctl generates control words that are bitwise representations
    # for the control lines, stored in CPU.oflags.
    def mkctl(self,flags=[]):
        word = self.NOP
        for f in flags:
            if f not in self.oflags:
                print("unknown control flag: [{}]".format(f))
                continue
            if self.oflags[f].inv == 1:
                word &= ~self.oflags[f].mask
            else:
                word |= self.oflags[f].mask
        return word
    # At runtime we can create a new assembly instruction
    # for the ROM, providing the microinstructions associated
    # with the assembly instruction.
    def addinstr(self,instr,micro):
        if type(micro) is list:
            for condition,value in enumerate(micro):
                if not condition in self.addr:
                    self.addr[condition] = dict()
                self.addr[condition][self.ASM[instr]] = value
        elif type(micro) is int:
            for condition in range(2**len(self.iflags)):
                if not condition in self.addr:
                    self.addr[condition] = dict()
                self.addr[condition][self.ASM[instr]] = micro
    # At runtime, we can assemble a new program into machine code,
    # usually those will get stored back into RAM for later execution.
    def assemble(self,instr,data=None):
        if instr in self.ASM:
            if data is not None:
                return [self.ASM[instr],data]
            return [self.ASM[instr]]
    def assemble_file(self,sourcefile,verbose=False):
        #print(f'self.ASM=[{self.ASM}]')
        asm = []
        src = []
        self._addr = len(asm)
        self._pointers = dict()
        def subassembly(word):
            def save(word,data):
                asm.append(data)
                src.append(word)
            self._addr = len(asm)
            #print(f'subassembly(word={word}) addr=0x{self._addr:02X}')
            if word in self.ASM:
                save(word,self.ASM[word])
            else:
                try:
                    data = int(word,16)
                    save(word,data)
                except:
                    if word == "#":
                        #print("comment")
                        return False
                    elif word == "":
                        return True
                    elif word[0] == ":":
                        ## We have found a label, get this address and save it for later use in search & replace
                        self._pointers[word[1:]] = self._addr
                        return True
                    elif word[0] == "[" and word[-1] == "]":
                        save(word,word[1:-1])
                        return True
                    print(f'WARNING: assemble_file encountered unexpected data {word}')
            return True
        try:
            with open(sourcefile, encoding="utf-8") as f:
                for line in f:
                    line = line.rstrip()
                    #print(f'assembling line=[{line}]')
                    if " " in line:
                        for word in line.split(" "):
                            if not subassembly(word):
                                break
                    else:
                        subassembly(line)
            # Assembly is complete, except labels have to be replaced with values
            for i in range(len(asm)):
                if asm[i] in self._pointers:
                    asm[i] = self._pointers[asm[i]]
                if verbose:
                    print(f'ASM: addr=0x{i:02X} data=0x{asm[i]:02X} src={src[i]}')
        except Exception as E:
            print(f'FATAL: unable assemble source file: {E}')
            pass
        self._addr = None
        del self._addr
        self._pointers = None
        del self._pointers
        return asm
