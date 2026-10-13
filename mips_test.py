import os
import sys

pasta_projeto = os.path.dirname(os.path.abspath(__file__))

if pasta_projeto not in sys.path:
    sys.path.insert(0, pasta_projeto)

from mips_interpreter import (
    MASCARA_32,
    read_u32,
    write_u32,
    encode_r,
    encode_i,
    executar_programa,
)

def testar_programa_basico():
    memoria = {}
    registradores = [0] * 32

    pc_inicial = 0x1000
    endereco_dados = 0x3000

    registradores[13] = endereco_dados

    # Monta o programa de teste.
    programa = {
        0x1000: encode_i(0x09, 0, 8, 30),    # ADDIU
        0x1004: encode_i(0x09, 0, 9, 20),    # ADDIU
        0x1008: encode_r(8, 9, 10, 0x2A),    # SLT
        0x100C: encode_i(0x04, 10, 0, 2),    # BEQ
        0x1010: encode_r(8, 9, 11, 0x20),    # ADD (delay slot)
        0x1014: encode_i(0x09, 0, 12, 99),   # ADDIU ignorado
        0x1018: encode_i(0x2B, 13, 11, 0),   # SW
        0x101C: encode_i(0x23, 13, 14, 0),   # LW
    }

    # Carrega o programa na memória.
    for endereco, instrucao in programa.items():
        write_u32(memoria, endereco, instrucao)

    # Executa o interpretador.
    resultado = executar_programa(
        memoria,
        set(programa.keys()),
        pc_inicial,
        registradores,
    )

    # Verifica os resultados.
    assert resultado[8] == 30
    assert resultado[9] == 20
    assert resultado[10] == 0
    assert resultado[11] == 50
    assert resultado[12] == 0
    assert resultado[14] == 50

    assert read_u32(memoria, endereco_dados) == 50

    print("\nTESTE APROVADO: programa basico")


if __name__ == "__main__":
    testar_programa_basico()
