import os
import sys
import unittest

PASTA_PROJETO = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PASTA_PROJETO not in sys.path:
    sys.path.insert(0, PASTA_PROJETO)

from ram import RAM
from mips_interpreter import executar_programa, encode_i

class TestMemoryIntegration(unittest.TestCase):
    def setUp(self):
        self.ram = RAM()

    def test_sw_e_lw_usam_a_mesma_ram(self):
        registradores = [0] * 32

        # $t0 (registrador 8) contém o endereço de dados.
        registradores[8] = 0x100

        # $t1 (registrador 9) contém o valor a armazenar.
        registradores[9] = 0x12345678

        # SW $t1, 0($t0)
        instrucao_sw = encode_i(
            opcode=0x2B,
            rs=8,
            rt=9,
            immediate=0,
        )

        # LW $t2, 0($t0)
        instrucao_lw = encode_i(
            opcode=0x23,
            rs=8,
            rt=10,
            immediate=0,
        )

        # Coloca SW e LW na RAM.
        self.ram.write_u32(0x00, instrucao_sw)
        self.ram.write_u32(0x04, instrucao_lw)

        executar_programa(
            self.ram,
            {0x00, 0x04},
            0x00,
            registradores,
            limite=2,
        )

        self.assertEqual(self.ram.read_u32(0x100), 0x12345678)
        self.assertEqual(registradores[10], 0x12345678)
