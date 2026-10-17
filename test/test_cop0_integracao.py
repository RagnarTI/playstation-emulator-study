import os
import unittest


from ps1.cpu.cop0 import COP0
from ps1.cpu.mips_r3000a import CPU
from ps1.cpu.mips_interpreter import encode_i
from ps1.memory.main_ram import RAM


def codificar_mfc0(rt, rd):
    return (0x10 << 26) | (rt << 16) | (rd << 11)


def codificar_mtc0(rt, rd):
    return (0x10 << 26) | (0x04 << 21) | (rt << 16) | (rd << 11)


class TestCOP0IntegracaoCPU(unittest.TestCase):
    PC_INICIAL = 0x1000

    def setUp(self):
        self.memoria = RAM()
        self.cpu = CPU()
        self.cpu.pc = self.PC_INICIAL

    def carregar(self, instrucoes):
        for endereco, instrucao in instrucoes.items():
            self.memoria.write_u32(endereco, instrucao)

    def executar(self, limite):
        self.cpu.executar(self.memoria, set(), limite=limite)

    def codigo_excecao(self):
        return (self.cpu.cop0.ler_registrador(COP0.CAUSE) >> 2) & 0x1F

    def test_mfc0_le_cop0_para_registrador_geral_e_respeita_zero(self):
        self.carregar({
            self.PC_INICIAL: codificar_mfc0(8, COP0.STATUS),
            self.PC_INICIAL + 4: codificar_mfc0(0, COP0.STATUS),
        })

        self.executar(limite=2)

        self.assertEqual(self.cpu.registradores[8], COP0.STATUS_RESET)
        self.assertEqual(self.cpu.registradores[0], 0)
        self.assertEqual(self.cpu.pc, self.PC_INICIAL + 8)
        self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"])
        self.assertIsNone(self.cpu.estado_delay["destino_atrasado"])

    def test_mfc0_de_indices_nao_existentes_gera_instrucao_reservada(self):
        for indice in (0, 1, 2, 4, 10):
            with self.subTest(indice_cop0=indice):
                self.setUp()
                self.carregar({
                    self.PC_INICIAL: codificar_mfc0(8, indice),
                })
                self.cpu.registradores[8] = 0xDEADBEEF

                self.executar(limite=1)

                self.assertEqual(self.codigo_excecao(), 10)
                self.assertEqual(
                    self.cpu.cop0.ler_registrador(COP0.EPC),
                    self.PC_INICIAL,
                )
                self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO_BOOT)
                self.assertEqual(self.cpu.registradores[8], 0xDEADBEEF)

    def test_mfc0_de_registrador_garbage_nao_gera_ri(self):
        # r16-r31 são documentados como garbage: não há valor portátil para
        # verificar, mas a leitura não deve ser classificada como Reserved.
        self.carregar({
            self.PC_INICIAL: codificar_mfc0(8, 16),
        })

        self.executar(limite=1)

        self.assertEqual(self.codigo_excecao(), 0)
        self.assertEqual(self.cpu.pc, self.PC_INICIAL + 4)

    def test_mtc0_aplica_permissoes_de_badvaddr_cause_status_epc_e_prid(self):
        casos = (
            (COP0.BADVADDR, 0x12345678, 0xABCDEF01, 0x12345678),
            (COP0.CAUSE, 0x80000064, 0xFFFFFFFF, 0x80000364),
            (COP0.STATUS, COP0.STATUS_RESET, 0xFFFFFFFF, 0xF04FFF3F),
            (COP0.EPC, 0x13572468, 0xABCDEF01, 0x13572468),
            (COP0.PRID, 0, 0xFFFFFFFF, 0),
            (COP0.TAR, 0xCAFEBABE, 0xFFFFFFFF, 0xCAFEBABE),
            (
                COP0.DCIC,
                (0x3F << 6) | (0x7F << 16),
                0xFFFFFFFF,
                COP0.MASCARA_DCIC_ESCRITA,
            ),
        )

        for indice, valor_inicial, valor_fonte, esperado in casos:
            with self.subTest(registrador=indice):
                self.setUp()
                self.carregar({
                    self.PC_INICIAL: codificar_mtc0(8, indice),
                })
                self.cpu.cop0.registradores[indice] = valor_inicial
                self.cpu.registradores[8] = valor_fonte

                self.executar(limite=1)

                self.assertEqual(
                    self.cpu.cop0.ler_registrador(indice),
                    esperado,
                )
                self.assertEqual(self.cpu.pc, self.PC_INICIAL + 4)

    def test_rfe_restaura_historico_sem_alterar_outros_campos_ou_saltar(self):
        instrucao_rfe = (0x10 << 26) | (0x10 << 21) | 0x10
        valor_status = 0xF04FFF2B  # histórico IE/KU = 0b101011
        self.cpu.cop0.escrever_registrador(COP0.STATUS, valor_status)
        status_antes = self.cpu.cop0.ler_registrador(COP0.STATUS)
        self.carregar({
            self.PC_INICIAL: instrucao_rfe,
            self.PC_INICIAL + 4: encode_i(0x09, 0, 8, 9),
        })

        self.executar(limite=2)

        status_depois = self.cpu.cop0.ler_registrador(COP0.STATUS)
        self.assertEqual(status_depois & 0x3F, 0b001010)
        self.assertEqual(status_depois & ~0x3F, status_antes & ~0x3F)
        self.assertEqual(self.cpu.pc, self.PC_INICIAL + 8)
        self.assertEqual(self.cpu.registradores[8], 9)
        self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"])
        self.assertIsNone(self.cpu.estado_delay["destino_atrasado"])

    def test_codificacoes_cop0_invalidas_geram_excecao_reservada(self):
        instrucoes_invalidas = (
            0x40000001,  # MFC0 com campo reservado diferente de zero
            0x40800001,  # MTC0 com campo reservado diferente de zero
            0x42010010,  # RFE com rt reservado diferente de zero
        )

        for instrucao in instrucoes_invalidas:
            with self.subTest(instrucao=f"0x{instrucao:08X}"):
                self.setUp()
                self.carregar({self.PC_INICIAL: instrucao})

                self.executar(limite=1)

                self.assertEqual(self.codigo_excecao(), 10)
                self.assertEqual(
                    self.cpu.cop0.ler_registrador(COP0.EPC),
                    self.PC_INICIAL,
                )
                self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO_BOOT)


if __name__ == "__main__":
    unittest.main()
