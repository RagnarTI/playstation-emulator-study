import os
import sys

PASTA_PROJETO = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PASTA_PROJETO not in sys.path:
    sys.path.insert(0, PASTA_PROJETO)

from mips_interpreter import (
    encode_r,
    encode_i,
    signed_32,
    executar_programa,
    EstadoEspecial,
)
from ram import RAM
from mips_exceptions import *

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