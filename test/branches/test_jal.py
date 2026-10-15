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
    MemoriaEsparsa,
)

class TestJAL(unittest.TestCase):

    def test_jal(self):
        instrucoes = {
            0x1000: (0x03 << 26) | (0x00001010 >> 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1010: encode_i(0x09, 0, 11, 99),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)

    def test_jal_jr_retorno(self):
        instrucoes = {
            0x1000: (0x03 << 26) | (0x1020 >> 2),  # JAL: chama a função
            0x1004: encode_i(0x09, 0, 10, 1),     # Delay slot do JAL
            0x1008: encode_i(0x09, 0, 11, 42),    # Continuação após retorno
            0x100C: encode_i(0x09, 0, 12, 7),
            0x1020: encode_i(0x09, 0, 13, 5),     # Corpo da função
            0x1024: encode_r(31, 0, 0, 0x08),     # JR $31
            0x1028: encode_i(0x09, 0, 14, 2),     # Delay slot do JR
        }

        registradores = executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 42)
        self.assertEqual(registradores[12], 7)
        self.assertEqual(registradores[13], 5)
        self.assertEqual(registradores[14], 2)

    def test_jal_preserva_regiao_de_pc_mais_quatro(self):
        instrucoes = {
            0x0FFFFFFC: (0x03 << 26) | (0x00000010 >> 2),  # JAL
            0x10000000: encode_i(0x09, 10, 10, 1),        # Delay slot
            0x10000004: encode_i(0x09, 0, 11, 99),        # Ignorada
            0x10000010: encode_i(0x09, 0, 12, 7),         # Destino
        }

        registradores = executar_programa_teste(
            instrucoes,
            {10: 0},
            pc_inicial=0x0FFFFFFC,
            memoria=MemoriaEsparsa(),
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)
        self.assertEqual(registradores[31], 0x10000004)

    def test_jal_na_fronteira_de_regiao(self):
        instrucoes = {
            0x0FFFFFFC: (0x03 << 26) | (0x00000004 >> 2),
            0x10000000: encode_i(0x09, 0, 10, 1),
            0x10000004: encode_i(0x09, 0, 11, 99),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {},
            pc_inicial=0x0FFFFFFC,
            memoria=MemoriaEsparsa(),
        )

        self.assertEqual(registradores[31], 0x10000004)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)

    def test_delay_slot_jal_executa_e_salva_retorno(self):
            instrucoes = {
                0x1000: (0x03 << 26) | (0x00001010 >> 2),  # JAL para 0x1010
                0x1004: encode_i(0x09, 10, 10, 1),        # Delay slot
                0x1008: encode_i(0x09, 0, 11, 99),        # Deve ser ignorada
                0x1010: encode_i(0x09, 0, 12, 7),         # Destino
            }
    
            registradores = executar_programa_teste(
                instrucoes,
                {10: 0},
                pc_inicial=0x1000,
                memoria=MemoriaEsparsa(),
            )
    
            self.assertEqual(registradores[10], 1)
            self.assertEqual(registradores[11], 0)
            self.assertEqual(registradores[12], 7)
            self.assertEqual(registradores[31], 0x1008)
    

if __name__ == "__main__":
    unittest.main()