from importlib import import_module

from .cpu.mips_r3000a import CPU
from .memory.bios_rom import BIOS
from .memory.main_ram import RAM

MemoryBus = import_module(
    f"{__package__}.memory-bus.memory_mapping"
).MemoryBus

class PS1:
    def __init__(self, caminho_bios):
        self.ram = RAM()
        self.bios = BIOS(caminho_bios)

        self.memory_bus = MemoryBus(
            self.ram,
            self.bios
        )

        self.cpu = CPU()
