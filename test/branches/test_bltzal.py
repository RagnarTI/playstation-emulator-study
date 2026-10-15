import os
import sys
import unittest

PASTA_TESTES = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PASTA_TESTES not in sys.path:
    sys.path.insert(0, PASTA_TESTES)

from branch_helpers import (
    encode_i,
    executar_programa_teste,
)

class TestBLTZAL(unittest.TestCase):

    def test_bltzal_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x10, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bltzal_falso(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x10, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_bltzal_zero_nao_desvia_atualiza_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x10, 2),  # BLTZAL
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 2),   # Execução sequencial
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0, 31: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 2)

    def test_bltzal_negativo_desvia_atualiza_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x10, 2),  # BLTZAL
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),   # Destino do branch
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF, 31: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bltzal_delay_slot_sobrescreve_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x10, 2),      # BLTZAL
            0x1004: encode_i(0x09, 0, 31, 0x5678),   # Delay slot: altera $ra
            0x1008: encode_i(0x09, 0, 11, 99),       # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),        # Destino do branch
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF, 31: 0},
        )

        self.assertEqual(registradores[31], 0x5678)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

if __name__ == "__main__":
    unittest.main()