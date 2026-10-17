

from ps1.cpu.mips_interpreter import (
    encode_r,
    encode_i,
    signed_32,
    executar_programa,
    EstadoEspecial,
)
from ps1.memory.main_ram import RAM
from ps1.cpu.mips_exceptions import *

def executar_instrucao(instrucao, valores=None, limite=1):
    memoria = RAM()
    registradores = [0] * 32
    endereco = 0x1000

    if valores is None:
        valores = {}

    for indice, valor in valores.items():
        registradores[indice] = valor & 0xFFFFFFFF

    memoria.write_u32(endereco, instrucao)

    executar_programa(
        memoria,
        {endereco},
        endereco,
        registradores,
        limite=limite,
    )

    return registradores