
import os
import sys
import unittest

PASTA_PROJETO = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PASTA_PROJETO not in sys.path:
    sys.path.insert(0, PASTA_PROJETO)

from mips_interpreter import (
    write_u32,
    read_u32,
    encode_i,
    executar_programa,
)


class TestMemory(unittest.TestCase):

    def executar_instrucao(self, instrucao, valores, memoria=None):
        if memoria is None:
            memoria = {}

        registradores = [0] * 32
        endereco_instrucao = 0x1000

        for indice, valor in valores.items():
            registradores[indice] = valor & 0xFFFFFFFF

        write_u32(memoria, endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        return registradores, memoria

    def test_sw(self):
        instrucao = encode_i(0x2B, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {8: 12345, 9: 0x3000},
        )

        self.assertEqual(read_u32(memoria, 0x3000), 12345)

    def test_lw(self):
        memoria = {}
        write_u32(memoria, 0x3000, 9876)

        instrucao = encode_i(0x23, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {9: 0x3000},
            memoria,
        )

        self.assertEqual(registradores[8], 9876)

    def test_little_endian(self):
        memoria = {}

        write_u32(memoria, 0x2000, 0x12345678)

        self.assertEqual(memoria[0x2000], 0x78)
        self.assertEqual(memoria[0x2001], 0x56)
        self.assertEqual(memoria[0x2002], 0x34)
        self.assertEqual(memoria[0x2003], 0x12)


if __name__ == "__main__":
    unittest.main()
