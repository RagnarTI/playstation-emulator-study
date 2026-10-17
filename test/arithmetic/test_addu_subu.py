import os
import unittest


from ps1.cpu.mips_r3000a import CPU
from ps1 import MemoryBus
from ps1.cpu.mips_interpreter import encode_r
from ps1.memory.main_ram import RAM


class TestADDUeSUBU(unittest.TestCase):
    PC_INICIAL = 0x1000
    FUNCT_ADDU = 0x21
    FUNCT_SUBU = 0x23

    def setUp(self):
        self.ram = RAM()
        self.memoria = MemoryBus(self.ram)
        self.cpu = CPU()
        self.cpu.pc = self.PC_INICIAL

    def executar(self, funct, rs, rt, rd, valores):
        for indice, valor in valores.items():
            self.cpu.registradores[indice] = valor & 0xFFFFFFFF

        instrucao = encode_r(rs, rt, rd, funct)
        self.memoria.write_u32(self.PC_INICIAL, instrucao)
        self.cpu.executar(
            self.memoria,
            {self.PC_INICIAL},
            limite=1,
        )

    def estado_cop0(self):
        return self.cpu.cop0.registradores.copy()

    def test_addu_soma_valores_positivos_e_usa_campos_corretos(self):
        self.executar(
            self.FUNCT_ADDU,
            rs=5,
            rt=12,
            rd=17,
            valores={5: 23, 12: 19, 10: 0xA5A5A5A5, 8: 0x12345678},
        )

        self.assertEqual(self.cpu.registradores[17], 42)
        self.assertEqual(self.cpu.registradores[5], 23)
        self.assertEqual(self.cpu.registradores[12], 19)
        self.assertEqual(self.cpu.registradores[10], 0xA5A5A5A5)
        self.assertEqual(self.cpu.registradores[8], 0x12345678)

    def test_addu_soma_zero_sem_alterar_o_outro_operando(self):
        self.executar(
            self.FUNCT_ADDU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 0, 9: 0x76543210},
        )

        self.assertEqual(self.cpu.registradores[10], 0x76543210)
        self.assertEqual(self.cpu.registradores[9], 0x76543210)

    def test_addu_soma_operandos_negativos_em_complemento_de_dois(self):
        self.executar(
            self.FUNCT_ADDU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 0xFFFFFFFB, 9: 0xFFFFFFFE},  # -5 + -2
        )

        self.assertEqual(self.cpu.registradores[10], 0xFFFFFFF9)  # -7

    def test_addu_soma_com_carry_faz_wraparound_de_32_bits(self):
        self.executar(
            self.FUNCT_ADDU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 0xFFFFFFFF, 9: 1},
        )

        self.assertEqual(self.cpu.registradores[10], 0)

    def test_addu_produz_exatamente_ffffffff(self):
        self.executar(
            self.FUNCT_ADDU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 0xFFFFFFFE, 9: 1},
        )

        self.assertEqual(self.cpu.registradores[10], 0xFFFFFFFF)

    def test_addu_overflow_com_sinal_nao_atualiza_cop0(self):
        cop0_antes = self.estado_cop0()
        self.executar(
            self.FUNCT_ADDU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 0x7FFFFFFF, 9: 1},
        )

        self.assertEqual(self.cpu.registradores[10], 0x80000000)
        self.assertEqual(self.estado_cop0(), cop0_antes)

    def test_addu_preserva_zero_quando_rd_e_zero(self):
        self.executar(
            self.FUNCT_ADDU,
            rs=8,
            rt=9,
            rd=0,
            valores={8: 20, 9: 22},
        )

        self.assertEqual(self.cpu.registradores[0], 0)

    def test_subu_subtrai_valores_positivos_e_usa_campos_corretos(self):
        self.executar(
            self.FUNCT_SUBU,
            rs=5,
            rt=12,
            rd=17,
            valores={5: 73, 12: 31, 10: 0xA5A5A5A5, 8: 0x12345678},
        )

        self.assertEqual(self.cpu.registradores[17], 42)
        self.assertEqual(self.cpu.registradores[5], 73)
        self.assertEqual(self.cpu.registradores[12], 31)
        self.assertEqual(self.cpu.registradores[10], 0xA5A5A5A5)
        self.assertEqual(self.cpu.registradores[8], 0x12345678)

    def test_subu_subtrai_zero(self):
        self.executar(
            self.FUNCT_SUBU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 0x76543210, 9: 0},
        )

        self.assertEqual(self.cpu.registradores[10], 0x76543210)

    def test_subu_operandos_iguais_produzem_zero(self):
        self.executar(
            self.FUNCT_SUBU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 0x12345678, 9: 0x12345678},
        )

        self.assertEqual(self.cpu.registradores[10], 0)

    def test_subu_produz_resultado_negativo_em_32_bits(self):
        self.executar(
            self.FUNCT_SUBU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 2, 9: 5},
        )

        self.assertEqual(self.cpu.registradores[10], 0xFFFFFFFD)  # -3

    def test_subu_subtrai_operandos_negativos_em_complemento_de_dois(self):
        self.executar(
            self.FUNCT_SUBU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 0xFFFFFFFB, 9: 2},  # -5 - 2
        )

        self.assertEqual(self.cpu.registradores[10], 0xFFFFFFF9)  # -7

    def test_subu_zero_menos_um_faz_wraparound_de_32_bits(self):
        self.executar(
            self.FUNCT_SUBU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 0, 9: 1},
        )

        self.assertEqual(self.cpu.registradores[10], 0xFFFFFFFF)

    def test_subu_overflow_com_sinal_nao_atualiza_cop0(self):
        cop0_antes = self.estado_cop0()
        self.executar(
            self.FUNCT_SUBU,
            rs=8,
            rt=9,
            rd=10,
            valores={8: 0x80000000, 9: 1},
        )

        self.assertEqual(self.cpu.registradores[10], 0x7FFFFFFF)
        self.assertEqual(self.estado_cop0(), cop0_antes)

    def test_subu_preserva_zero_quando_rd_e_zero(self):
        self.executar(
            self.FUNCT_SUBU,
            rs=8,
            rt=9,
            rd=0,
            valores={8: 73, 9: 31},
        )

        self.assertEqual(self.cpu.registradores[0], 0)


if __name__ == "__main__":
    unittest.main()
