import os
import unittest


from test.helpers.branch_helpers import (
    encode_i,
    executar_programa_teste,
    MemoriaEsparsa,
)

class TestJ(unittest.TestCase):

    def test_j(self):
        instrucoes = {
            0x1000: (0x02 << 26) | (0x00001008 >> 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_j_preserva_regiao_de_pc_mais_quatro(self):
        instrucoes = {
            0x0FFFFFFC: (0x02 << 26) | (0x00000010 >> 2),  # J
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

    def test_j_na_fronteira_de_regiao(self):
        instrucoes = {
            0x0FFFFFFC: (0x02 << 26) | (0x00000004 >> 2),
            0x10000000: encode_i(0x09, 0, 10, 1),
            0x10000004: encode_i(0x09, 0, 11, 99),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {},
            pc_inicial=0x0FFFFFFC,
            memoria=MemoriaEsparsa(),
        )

        self.assertEqual(registradores[31], 0)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)

    def test_delay_slot_j_executa_antes_do_salto(self):
            instrucoes = {
                0x1000: (0x02 << 26) | (0x00001010 >> 2),  # J para 0x1010
                0x1004: encode_i(0x09, 10, 10, 1),        # Delay slot
                0x1008: encode_i(0x09, 0, 11, 99),        # Deve ser ignorada
                0x1010: encode_i(0x09, 0, 12, 7),         # Destino
            }
    
            registradores = executar_programa_teste(
                instrucoes,
                {10: 0},
            )
    
            self.assertEqual(registradores[10], 1)
            self.assertEqual(registradores[11], 0)
            self.assertEqual(registradores[12], 7)

if __name__ == "__main__":
    unittest.main()