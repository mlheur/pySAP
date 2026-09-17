from . import Register


class DoubleRegister(Register):
    def __init__(self,cpu,clr,clock,latch_lo,latch_hi,enable_lo,enable_hi):
        super().__init__(cpu,2*self.cpu.bits,clr,latch_lo,enable_lo)
        self.cpu_mask   = (2**cpu.bits)-1
        self.latch_hi   = self.cpu.control_lines[latch_hi]
        self.enable_hi  = self.cpu.control_lines[enable_hi]
        self.increment  = self.cpu.control_lines[clock]

    def get_truth(self):
        tt = dict()
        tt['clock'] = self.increment.istrue()
        tt['en_hi'] = self.enable_hi.istrue()
        tt['en_lo'] = self.enable.istrue()
        tt['la_hi'] = self.latch_hi.istrue()
        tt['la_lo'] = self.latch.istrue()
        return tt

    def tick(self):
        if self.clr.istrue():
            self.value = 0
        tt = self.get_truth()
        if tt['en_lo'] and tt['en_hi']:
            self.cpu.w = self.value & self.mask
        elif tt['en_lo']:
            self.cpu.w = self.value & self.cpu_mask
        elif tt['en_hi']:
            self.cpu.w = (self.value>>self.cpu.bits) & self.cpu_mask

    def tock(self):
        tt = self.get_truth()
        if tt['clock']:
            self.value += 1
            self.value %= self.mask
        elif tt['la_lo'] and tt['la_hi']:
            self.value = self.cpu.w & self.mask
        elif tt['la_lo']:
            hi = (self.value >> self.cpu.bits) & self.cpu_mask
            lo = self.cpu.w & self.cpu_mask
            self.value = ((hi<<self.cpu.bits) + (lo)) & self.mask
        elif tt['la_hi']:
            hi = self.cpu.w & self.cpu_mask
            lo = self.value & self.cpu_mask
            self.value = ((hi<<self.cpu.bits) + (lo)) & self.mask
