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

class TestBGEZAL(unittest.TestCase):

    def test_bgezal_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x11, 2),
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
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgezal_falso(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x11, 2),
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
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_bgezal_negativo_nao_desvia_atualiza_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x11, 2),  # BGEZAL
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 2),   # Execução sequencial
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF, 31: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 2)

    def test_bgezal_positivo_desvia_atualiza_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x11, 2),  # BGEZAL
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),   # Destino do branch
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0x7FFFFFFF, 31: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgezal_delay_slot_sobrescreve_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x11, 2),      # BGEZAL
            0x1004: encode_i(0x09, 0, 31, 0x1234),   # Delay slot: altera $ra
            0x1008: encode_i(0x09, 0, 11, 99),       # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),        # Destino do branch
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 1, 31: 0},
        )

        self.assertEqual(registradores[31], 0x1234)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

if __name__ == "__main__":
    unittest.main()