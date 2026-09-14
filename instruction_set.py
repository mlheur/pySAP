from ctl import CtlLine


def replace_label_with_value(src,lbls,fsi,i,next_is_mri,o=0):
    if src in lbls:
        if next_is_mri:
            fsi[i] = f'0x{int(lbls[src])+int(o):04X}'
        else:
            fsi[i] = f'0x{int(lbls[src])+int(o):02X}'

# The class is where the microinstructions are figured out
# for the instruction decoder.  This implementation of SAP CPU
# is using a lookup table: for each instruction, for each t-step
# in those instructions, what is the bitwise representation of
# the various control lines that have to be pulled high and low
# to set the various Enable and Latch lines on the components.
class instruction_set(object):

    def __init__(self,word_size):
        self.MRI       = dict()
        self.word_size = word_size
        self.word_mask = (2**self.word_size)-1

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
                raise RuntimeError
                continue
            if self.oflags[f].inv == 1:
                word &= ~self.oflags[f].mask
            else:
                word |= self.oflags[f].mask
        return word

    # At runtime we can create a new assembly instruction
    # for the ROM, providing the microinstructions associated
    # with the assembly instruction.
    def addinstr(self,instr,micro,is_mri=False):
        self.MRI[instr] = is_mri
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

    def assemble_file(self,sourcefile,verbose=False,as_string=False,as_source=False):
        #print(f'self.ASM=[{self.ASM}]')
        if hasattr(self,"stringed") and self.stringed is not None and as_string:
            return self.stringed
        if hasattr(self,"source") and self.source is not None and as_source:
            return self.source
        self.stringed     = ""
        self.source       = ""

        #####
        # - Filter out all the comments, whitespace
        # - Allocate two bytes for the memory address of memory-referencing-instructions
        # - Create a list of the all the assembly words before asembly & linking
        # - get the address of all the labels
        filtered_source_words = []
        assembly              = []
        labels  = dict()
        address = 0
        fhandle = open(sourcefile,'r')
        line = fhandle.readline()
        while line != "":
            self.source += line
            words = line.rstrip().split(" ")
            for word in words:
                if word == "":
                    continue
                if word[0] == '#':
                    break
                if word[0] == ':':
                    labels[word[1:]] = address
                else:
                    filtered_source_words.append(word)
                    assembly.append(word)
                    address += 1
                    if word in self.MRI and self.MRI[word]:
                        filtered_source_words.append('HI_BYTE')
                        assembly.append("")
                        address += 1
            line = fhandle.readline()
        fhandle.close()
        filtered_source_length = len(filtered_source_words)

        #####
        # - replace all labels with their address
        next_is_mri = False
        for i in range(filtered_source_length):
            src = filtered_source_words[i]
            if src[0] == '[':
                src = src[1:-1]
                if '+' in src:
                    [src,off] = src.split('+')
                    replace_label_with_value(src,labels,filtered_source_words,i,next_is_mri,off)
                elif '-' in src:
                    [src,off] = src.split('-')
                    replace_label_with_value(src,labels,filtered_source_words,i,next_is_mri,-1*int(off))
                else:
                    replace_label_with_value(src,labels,filtered_source_words,i,next_is_mri)
            next_is_mri = src in self.MRI and self.MRI[src]

        #####
        # - Expand addresses over two bytes
        # - Replace mnemonic with binary value
        assembled = list(filtered_source_words)
        for i in range(filtered_source_length):
            src = assembled[i]
            #print(f'expanding addresses of {src}')
            if src in self.MRI and self.MRI[src]:
                address = int(assembled[i+2],16)
                hi = f'0x{address >> self.word_size & self.word_mask:02X}'
                lo = f'0x{address & self.word_mask:02X}'
                assembled[i+1] = hi
                assembly[i+1] = assembly[i+2] + "_HI"
                assembled[i+2] = lo
                assembly[i+2] = assembly[i+2] + "_LO"
            if src in self.ASM:
                assembled[i]   = f'0x{self.ASM[src]:02X}'

        # Stringify the assembly for decompiled view
        # convert all 0xXX string values to int.
        for adr,asm in enumerate(assembly):
            assembled[adr] = int(assembled[adr],16)
            self.stringed += f'addr=0x{adr:04X} data=0x{assembled[adr]:02X} source={asm}\n'

        return assembled
