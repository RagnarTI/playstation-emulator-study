import os
import unittest


from test.helpers.branch_helpers import (
    encode_i,
    executar_programa_teste,
)

class TestBGTZ(unittest.TestCase):

    def test_bgtz_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 5},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgtz_falso(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_bgtz_maior_inteiro_positivo_32_bits(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 2),    # BGTZ
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),   # Destino do branch
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0x7FFFFFFF},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgtz_zero_nao_desvia(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 2),    # BGTZ
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 2),   # Execução sequencial
            0x100C: encode_i(0x09, 0, 12, 99),  # Continuação
        }

        registradores = executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 2)
        self.assertEqual(registradores[12], 99)

    def test_delay_slot_bgtz_tomado(self):
            instrucoes = {
                0x1000: encode_i(0x07, 8, 0, 3),    # BGTZ para 0x1010
                0x1004: encode_i(0x09, 10, 10, 1),  # Delay slot
                0x1008: encode_i(0x09, 0, 11, 99),  # Deve ser ignorada
                0x1010: encode_i(0x09, 0, 12, 7),   # Destino
            }
    
            registradores = executar_programa_teste(
                instrucoes,
                {8: 1, 10: 0},
            )
    
            self.assertEqual(registradores[10], 1)
            self.assertEqual(registradores[11], 0)
            self.assertEqual(registradores[12], 7)
    
    def test_delay_slot_bgtz_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 3),    # BGTZ: não desvia
            0x1004: encode_i(0x09, 10, 10, 1),  # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Próxima instrução
            0x100C: encode_i(0x09, 0, 12, 7),   # Continuação
        }
    
        registradores = executar_programa_teste(
            instrucoes,
            {8: 0, 10: 0},
        )
    
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)
        
if __name__ == "__main__":
    unittest.main()