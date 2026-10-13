
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
    encode_i,
    encode_r,
    executar_programa,
)


class TestBranches(unittest.TestCase):

    def executar_programa_teste(self, instrucoes, valores):
        memoria = {}
        registradores = [0] * 32

        for indice, valor in valores.items():
            registradores[indice] = valor & 0xFFFFFFFF

        for endereco, instrucao in instrucoes.items():
            write_u32(memoria, endereco, instrucao)

        executar_programa(
            memoria,
            set(instrucoes.keys()),
            0x1000,
            registradores,
            limite=10,
        )

        return registradores

    def test_beq_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x04, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 20, 9: 20},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_beq_falso(self):
        instrucoes = {
            0x1000: encode_i(0x04, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 20, 9: 30},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)

    def test_delay_slot(self):
        instrucoes = {
            0x1000: encode_i(0x04, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 42),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 5, 9: 5},
        )

        self.assertEqual(registradores[10], 42)
        self.assertEqual(registradores[11], 0)

    def test_jr(self):
        instrucoes = {
            0x1000: encode_r(9, 0, 0, 0x08),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {9: 0x1008},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)
    
    def test_j(self):
        instrucoes = {
            0x1000: (0x02 << 26) | (0x00001008 >> 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_jal(self):
        instrucoes = {
            0x1000: (0x03 << 26) | (0x00001010 >> 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1010: encode_i(0x09, 0, 11, 99),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)

    def test_jal_jr_retorno(self):
        instrucoes = {
            # JAL: chama a função em 0x1020.
            0x1000: (0x03 << 26) | (0x1020 >> 2),

            # Delay slot do JAL.
            0x1004: encode_i(0x09, 0, 10, 1),

            # Continuação do programa após o retorno.
            0x1008: encode_i(0x09, 0, 11, 42),
            0x100C: encode_i(0x09, 0, 12, 7),

            # Corpo da função.
            0x1020: encode_i(0x09, 0, 13, 5),

            # JR $31: retorna para o endereço salvo pelo JAL.
            0x1024: encode_r(31, 0, 0, 0x08),

            # Delay slot do JR.
            0x1028: encode_i(0x09, 0, 14, 2),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 42)
        self.assertEqual(registradores[12], 7)
        self.assertEqual(registradores[13], 5)
        self.assertEqual(registradores[14], 2)


if __name__ == "__main__":
    unittest.main()
