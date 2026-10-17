import os
import unittest


from ps1.cpu.cop0 import COP0

class TestCOP0(unittest.TestCase):

    def test_inicializacao_dos_registradores(self):
        cop0 = COP0()

        for numero in range(32):
            esperado = (
                COP0.STATUS_RESET
                if numero == COP0.STATUS
                else 0
            )
            self.assertEqual(
                cop0.ler_registrador(numero),
                esperado,
            )

        status = cop0.ler_registrador(COP0.STATUS)
        self.assertEqual(status, 0x00400000)
        self.assertNotEqual(status & COP0.MASCARA_BEV, 0)

    def test_escrever_e_ler_registrador(self):
        cop0 = COP0()

        cop0.escrever_registrador(COP0.STATUS, 0x12345678)

        self.assertEqual(
            cop0.ler_registrador(COP0.STATUS),
            0x10045638,
        )

    def test_escrita_em_badvaddr_e_ignorada(self):
        cop0 = COP0()
        cop0.registradores[COP0.BADVADDR] = 0x12345678

        cop0.escrever_registrador(COP0.BADVADDR, 0xABCDEF01)

        self.assertEqual(cop0.ler_registrador(COP0.BADVADDR), 0x12345678)

    def test_excecao_ainda_atualiza_badvaddr(self):
        cop0 = COP0()

        cop0.registrar_excecao(4, 0x1000, badvaddr=0x2001)

        self.assertEqual(cop0.ler_registrador(COP0.BADVADDR), 0x2001)

    def test_cause_permite_escrita_somente_nos_bits_sw(self):
        cop0 = COP0()
        causa_hardware = 0x80000064
        cop0.registradores[COP0.CAUSE] = causa_hardware

        cop0.escrever_registrador(COP0.CAUSE, 0xFFFFFFFF)

        causa_final = cop0.ler_registrador(COP0.CAUSE)
        self.assertEqual(causa_final, 0x80000364)

    def test_cause_permite_limpar_bits_sw_sem_apagar_exc_code(self):
        cop0 = COP0()
        cop0.registrar_excecao(9, 0x2000)
        causa_com_excecao = cop0.ler_registrador(COP0.CAUSE)
        cop0.escrever_registrador(COP0.CAUSE, 0)

        self.assertEqual(
            cop0.ler_registrador(COP0.CAUSE),
            causa_com_excecao & ~0x00000300,
        )

    def test_status_aplica_mascara_de_escrita_ps1(self):
        cop0 = COP0()
        valor = 0xFFFFFFFF

        cop0.escrever_registrador(COP0.STATUS, valor)

        self.assertEqual(
            cop0.ler_registrador(COP0.STATUS),
            0xF04FFF3F,
        )

    def test_status_preserva_bev_ate_software_limpa_o_bit(self):
        cop0 = COP0()
        self.assertEqual(cop0.obter_vetor_excecao(), 0xBFC00180)

        cop0.escrever_registrador(COP0.STATUS, 0)

        self.assertEqual(cop0.ler_registrador(COP0.STATUS) & COP0.MASCARA_BEV, 0)
        self.assertEqual(cop0.obter_vetor_excecao(), 0x80000080)

    def test_status_permite_definir_bev_posteriormente(self):
        cop0 = COP0()
        cop0.escrever_registrador(COP0.STATUS, 0)

        cop0.escrever_registrador(COP0.STATUS, COP0.MASCARA_BEV)

        self.assertNotEqual(
            cop0.ler_registrador(COP0.STATUS) & COP0.MASCARA_BEV,
            0,
        )
        self.assertEqual(cop0.obter_vetor_excecao(), 0xBFC00180)

    def test_valor_limitado_a_32_bits(self):
        cop0 = COP0()

        cop0.escrever_registrador(12, 0x123456789)

        self.assertEqual(
            cop0.ler_registrador(12),
            0x20456709,
        )

    def test_numero_de_registrador_invalido(self):
        cop0 = COP0()

        with self.assertRaises(ValueError):
            cop0.ler_registrador(32)

        with self.assertRaises(ValueError):
            cop0.escrever_registrador(-1, 0)

    def test_prid_nao_pode_ser_escrito(self):
        cop0 = COP0()

        valor_inicial = cop0.ler_registrador(15)
        cop0.escrever_registrador(15, 0x12345678)

        self.assertEqual(
            cop0.ler_registrador(15),
            valor_inicial
        )

    def test_registrar_excecao_atualiza_cause_e_epc(self):
        cop0 = COP0()

        cop0.registrar_excecao(8, 0x1000)

        self.assertEqual(
            (cop0.ler_registrador(COP0.CAUSE) >> 2) & 0x1F,
            8
        )
        self.assertEqual(
            cop0.ler_registrador(COP0.EPC),
            0x1000
        )

    def test_registrar_excecao_preserva_outros_bits_de_cause(self):
        cop0 = COP0()
        # Este teste valida a atualização de campos por hardware feita pela
        # exceção, não a permissão de escrita de MTC0.
        cop0.registradores[COP0.CAUSE] = 0xB0000003

        cop0.registrar_excecao(9, 0x2000)

        self.assertEqual(
            cop0.ler_registrador(COP0.CAUSE) & ~(0x1F << 2) & ~(1 << 31),
            0xB0000003 & ~(1 << 31)
        )

    def test_entrar_em_excecao_desloca_historico(self):
        cop0 = COP0()

        cop0.escrever_registrador(COP0.STATUS, 0b101011)

        cop0.entrar_em_excecao()

        self.assertEqual(
            cop0.ler_registrador(COP0.STATUS) & 0x3F,
            0b101100
        )

    def test_entrar_em_excecao_preserva_bits_superiores(self):
        cop0 = COP0()

        valor_inicial = 0x1234562B
        cop0.registradores[COP0.STATUS] = valor_inicial

        cop0.entrar_em_excecao()

        status_final = cop0.ler_registrador(COP0.STATUS)

        self.assertEqual(
            status_final & ~0x3F,
            valor_inicial & ~0x3F
        )

    def test_excecao_normal(self):
        cop0 = COP0()

        cop0.registrar_excecao(8, 0x1000)

        self.assertEqual(
            (cop0.ler_registrador(COP0.CAUSE) >> 2) & 0x1F,
            8
        )
        self.assertEqual(
            cop0.ler_registrador(COP0.EPC),
            0x1000
        )
        self.assertEqual(
            cop0.ler_registrador(COP0.CAUSE) & (1 << 31),
            0
        )

    def test_excecao_em_delay_slot(self):
        cop0 = COP0()

        cop0.registrar_excecao(9, 0x1004, delay_slot=True)

        self.assertEqual(
            (cop0.ler_registrador(COP0.CAUSE) >> 2) & 0x1F,
            9
        )
        self.assertEqual(
            cop0.ler_registrador(COP0.EPC),
            0x1000
        )
        self.assertNotEqual(
            cop0.ler_registrador(COP0.CAUSE) & (1 << 31),
            0
        )

    def test_excecao_atualiza_status(self):
        cop0 = COP0()
        cop0.escrever_registrador(COP0.STATUS, 0b001011)

        cop0.registrar_excecao(8, 0x1000)

        self.assertEqual(
            cop0.ler_registrador(COP0.STATUS) & 0x3F,
            0b101100
        )

    def test_vetor_excecao(self):
        self.assertEqual(COP0.VETOR_EXCECAO, 0x80000080)

if __name__ == "__main__":
    unittest.main()
