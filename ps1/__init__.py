"""Public API for the PlayStation 1 emulator, loaded on demand."""

from importlib import import_module

__all__ = ["BIOS", "COP0", "CPU", "MemoryBus", "PS1", "RAM"]

_MODULES = {
    "BIOS": ".memory.bios_rom",
    "COP0": ".cpu.cop0",
    "CPU": ".cpu.mips_r3000a",
    "PS1": ".ps1",
    "RAM": ".memory.main_ram",
}


def __getattr__(name):
    if name == "MemoryBus":
        module = import_module(
            f"{__name__}.memory-bus.memory_mapping"
        )
        value = module.MemoryBus
    elif name in _MODULES:
        module = import_module(_MODULES[name], __name__)
        value = getattr(module, name)
    else:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        )

    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
