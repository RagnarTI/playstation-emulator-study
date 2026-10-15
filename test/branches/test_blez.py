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

class TestBLEZ(unittest.TestCase):

    def test_blez_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_blez_falso(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 5},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_blez_rt_invalido(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 1, 2),
        }

        with self.assertRaises(NotImplementedError):
            executar_programa_teste(
                instrucoes,
                {8: 0},
            )

    def test_blez_menor_inteiro_32_bits(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 2),    # BLEZ
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),   # Destino do branch
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0x80000000},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_blez_zero_desvia(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 2),    # BLEZ
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),   # Destino do branch
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_blez_tomado(self):
            instrucoes = {
                0x1000: encode_i(0x06, 8, 0, 3),    # BLEZ para 0x1010
                0x1004: encode_i(0x09, 10, 10, 1),  # Delay slot
                0x1008: encode_i(0x09, 0, 11, 99),  # Deve ser ignorada
                0x1010: encode_i(0x09, 0, 12, 7),   # Destino
            }
    
            registradores = executar_programa_teste(
                instrucoes,
                {8: 0, 10: 0},
            )
    
            self.assertEqual(registradores[10], 1)
            self.assertEqual(registradores[11], 0)
            self.assertEqual(registradores[12], 7)
    
    def test_delay_slot_blez_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 3),    # BLEZ: não desvia
            0x1004: encode_i(0x09, 10, 10, 1),  # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Próxima instrução
            0x100C: encode_i(0x09, 0, 12, 7),   # Continuação
        }
    
        registradores = executar_programa_teste(
            instrucoes,
            {8: 1, 10: 0},
        )
    
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

if __name__ == "__main__":
    unittest.main()