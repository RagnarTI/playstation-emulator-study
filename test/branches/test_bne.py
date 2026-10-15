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

class TestBNE(unittest.TestCase):

    def test_bne_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x05, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 10, 9: 20},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bne_falso(self):
        instrucoes = {
            0x1000: encode_i(0x05, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 10, 9: 10},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_bne_offset_negativo_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x09, 0, 10, 1),    # ADDIU $10, $0, 1
            0x1004: encode_i(0x05, 10, 10, -2),  # BNE: condição falsa
            0x1008: encode_i(0x09, 0, 11, 7),    # Delay slot
            0x100C: encode_i(0x09, 0, 12, 9),    # Continuação
        }

        registradores = executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 7)
        self.assertEqual(registradores[12], 9)

    def test_delay_slot_bne_tomado(self):
            instrucoes = {
                0x1000: encode_i(0x05, 8, 9, 2),    # BNE
                0x1004: encode_i(0x09, 10, 10, 1),  # Delay slot
                0x1008: encode_i(0x09, 0, 11, 99),  # Deve ser ignorada
                0x100C: encode_i(0x09, 0, 12, 7),   # Destino
            }
    
            registradores = executar_programa_teste(
                instrucoes,
                {8: 5, 9: 6, 10: 0},
            )
    
            self.assertEqual(registradores[10], 1)
            self.assertEqual(registradores[11], 0)
            self.assertEqual(registradores[12], 7)
    
    def test_delay_slot_bne_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x05, 8, 9, 2),    # BNE: não desvia
            0x1004: encode_i(0x09, 10, 10, 1),  # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Próxima instrução
            0x100C: encode_i(0x09, 0, 12, 7),   # Continuação
        }
    
        registradores = executar_programa_teste(
            instrucoes,
            {8: 5, 9: 5, 10: 0},
        )
    
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)
    
if __name__ == "__main__":
    unittest.main()