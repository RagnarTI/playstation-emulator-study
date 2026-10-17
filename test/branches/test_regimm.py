import os
import unittest


from test.helpers.branch_helpers import (
    encode_i,
    executar_programa_teste,
)

class TestREGIMM(unittest.TestCase):

    def test_regimm_rt_nao_suportado(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x02, 2),
        }

        with self.assertRaises(NotImplementedError):
            executar_programa_teste(
                instrucoes,
                {8: 1},
            )

    def test_regimm_bltz_valido(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x00, 2),
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

if __name__ == "__main__":
    unittest.main()
