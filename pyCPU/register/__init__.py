from random import randint

from pyCPU.bus import BusUser
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyCPU import CPU


class Register(BusUser):

    def __init__(
            self,
            cpu        : "CPU",
        ):
        super().__init__()
        self.cpu         = cpu
        self.value       = randint(0,self.cpu.mask)

    def __str__(self):
        return f'0x0{self.value:{self.cpu.bits}X}'