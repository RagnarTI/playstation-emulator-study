import os
import unittest


from test.helpers.branch_helpers import (
    encode_i,
    executar_programa_teste,
)

class TestBEQ(unittest.TestCase):

    def test_beq_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x04, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = executar_programa_teste(
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

        registradores = executar_programa_teste(
            instrucoes,
            {8: 20, 9: 30},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_beq_desvio_com_offset_negativo(self):
        instrucoes = {
            0x1000: encode_i(0x09, 0, 10, 1),
            0x1004: encode_i(0x04, 10, 0, -2),
            0x1008: encode_i(0x09, 0, 10, 1),
            0x100C: encode_i(0x09, 0, 12, 99),
        }

        registradores = executar_programa_teste(
            instrucoes,
            {10: 0},
            limite=10,
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[12], 99)

    def test_beq_tomado_retorna_pc_final_no_destino(self):
        instrucoes = {
            0x1000: encode_i(0x04, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x100C: encode_i(0x09, 0, 11, 7),
        }

        registradores, pc_final = executar_programa_teste(
            instrucoes,
            {8: 20, 9: 20},
            limite=3,
            retornar_pc=True,
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 7)
        self.assertEqual(pc_final, 0x1010)

if __name__ == "__main__":
    unittest.main()