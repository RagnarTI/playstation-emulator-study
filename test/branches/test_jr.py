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
    encode_r,
    executar_programa_teste,
)

class TestJR(unittest.TestCase):

    def test_jr(self):
        instrucoes = {
            0x1000: encode_r(9, 0, 0, 0x08),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {9: 0x1008},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_jr_registro_com_delay_slot(self):
        instrucoes = {
            0x1000: (9 << 21) | 0x08,  # JR $9
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 12, 99),  # Não deve executar
            0x1010: encode_i(0x09, 0, 11, 7),   # Destino do JR
        }

        registradores = executar_programa_teste(
            instrucoes,
            {
                9: 0x1010,
                31: 0x12345678,
            },
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 7)
        self.assertEqual(registradores[12], 0)
        self.assertEqual(registradores[31], 0x12345678)

    def test_delay_slot_jr_executa_antes_do_salto(self):
            instrucoes = {
                0x1000: encode_r(8, 0, 0, 0x08),       # JR $t0
                0x1004: encode_i(0x09, 10, 10, 1),     # Delay slot
                0x1008: encode_i(0x09, 0, 11, 99),     # Deve ser ignorada
                0x1010: encode_i(0x09, 0, 12, 7),      # Destino
            }
    
            registradores = executar_programa_teste(
                instrucoes,
                {8: 0x1010, 10: 0},
            )
    
            self.assertEqual(registradores[10], 1)
            self.assertEqual(registradores[11], 0)
            self.assertEqual(registradores[12], 7)

if __name__ == "__main__":
    unittest.main()