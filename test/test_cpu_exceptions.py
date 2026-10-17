import os
import unittest


from ps1.cpu.cop0 import COP0
from ps1.cpu.mips_r3000a import CPU
from ps1 import MemoryBus
from ps1.cpu.mips_interpreter import encode_i, encode_r
from ps1.memory.main_ram import RAM


class TestCPUExceptions(unittest.TestCase):
    PC_INICIAL = 0x1000

    def setUp(self):
        self.ram = RAM()
        self.memoria = MemoryBus(self.ram)
        self.cpu = CPU()
        self.cpu.pc = self.PC_INICIAL
        # Estes casos exercitam explicitamente o vetor geral com BEV limpo.
        self.cpu.cop0.escrever_registrador(COP0.STATUS, 0)

    def carregar(self, endereco, instrucao):
        self.memoria.write_u32(endereco, instrucao)

    def executar(self, limite=1):
        self.cpu.executar(self.memoria, set(), limite=limite)

    def codigo_excecao(self):
        return (self.cpu.cop0.ler_registrador(COP0.CAUSE) >> 2) & 0x1F

    def test_overflow_em_add_sub_e_addi_entra_no_cop0_sem_gravar_destino(self):
        casos = (
            (encode_r(8, 9, 10, 0x20), {8: 0x7FFFFFFF, 9: 1}),
            (encode_r(8, 9, 10, 0x22), {8: 0x80000000, 9: 1}),
            (encode_i(0x08, 8, 10, 1), {8: 0x7FFFFFFF}),
        )

        for instrucao, valores in casos:
            with self.subTest(instrucao=f"0x{instrucao:08X}"):
                self.setUp()
                self.carregar(self.PC_INICIAL, instrucao)
                self.cpu.cop0.escrever_registrador(COP0.STATUS, 0b001011)
                self.cpu.registradores[10] = 0xDEADBEEF
                for indice, valor in valores.items():
                    self.cpu.registradores[indice] = valor

                self.executar()

                self.assertEqual(self.codigo_excecao(), 12)
                self.assertEqual(
                    self.cpu.cop0.ler_registrador(COP0.EPC),
                    self.PC_INICIAL,
                )
                self.assertEqual(self.cpu.registradores[10], 0xDEADBEEF)
                self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO)
                self.assertEqual(
                    self.cpu.cop0.ler_registrador(COP0.STATUS) & 0x3F,
                    0b101100,
                )

    def test_syscall_e_break_usam_seus_codigos_e_vetor(self):
        for funct, codigo in ((0x0C, 8), (0x0D, 9)):
            with self.subTest(funct=funct):
                self.setUp()
                self.carregar(
                    self.PC_INICIAL,
                    encode_r(0, 0, 0, funct),
                )

                self.executar()

                self.assertEqual(self.codigo_excecao(), codigo)
                self.assertEqual(
                    self.cpu.cop0.ler_registrador(COP0.EPC),
                    self.PC_INICIAL,
                )
                self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO)

    def test_excecao_apos_instrucao_concluida_preserva_pc_da_instrucao_faulting(self):
        self.carregar(self.PC_INICIAL, encode_i(0x09, 0, 8, 7))
        self.carregar(
            self.PC_INICIAL + 4,
            encode_r(0, 0, 0, 0x0C),
        )

        self.executar(limite=2)

        self.assertEqual(self.cpu.registradores[8], 7)
        self.assertEqual(self.codigo_excecao(), 8)
        self.assertEqual(
            self.cpu.cop0.ler_registrador(COP0.EPC),
            self.PC_INICIAL + 4,
        )
        self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO)

    def test_instrucao_r_type_reservada_gera_ri(self):
        self.carregar(self.PC_INICIAL, encode_r(0, 0, 0, 0x3F))

        self.executar()

        self.assertEqual(self.codigo_excecao(), 10)
        self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO)

    def test_lw_desalinhado_atualiza_badvaddr_e_nao_grava_destino(self):
        self.carregar(self.PC_INICIAL, encode_i(0x23, 8, 9, 0))
        self.cpu.registradores[8] = 0x2001
        self.cpu.registradores[9] = 0xDEADBEEF

        self.executar()

        self.assertEqual(self.codigo_excecao(), 4)
        self.assertEqual(
            self.cpu.cop0.ler_registrador(COP0.BADVADDR),
            0x2001,
        )
        self.assertEqual(self.cpu.registradores[9], 0xDEADBEEF)
        self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO)

    def test_fetch_desalinhado_gera_adel_e_atualiza_badvaddr(self):
        self.cpu.pc = self.PC_INICIAL + 2

        self.executar()

        self.assertEqual(self.codigo_excecao(), 4)
        self.assertEqual(
            self.cpu.cop0.ler_registrador(COP0.BADVADDR),
            self.PC_INICIAL + 2,
        )
        self.assertEqual(
            self.cpu.cop0.ler_registrador(COP0.EPC),
            self.PC_INICIAL + 2,
        )

    def test_sw_desalinhado_atualiza_badvaddr_sem_escrita_parcial(self):
        self.carregar(self.PC_INICIAL, encode_i(0x2B, 8, 9, 0))
        self.cpu.registradores[8] = 0x2001
        self.cpu.registradores[9] = 0x12345678
        self.ram.write_u32(0x2000, 0xAABBCCDD)

        self.executar()

        self.assertEqual(self.codigo_excecao(), 5)
        self.assertEqual(
            self.cpu.cop0.ler_registrador(COP0.BADVADDR),
            0x2001,
        )
        self.assertEqual(self.ram.read_u32(0x2000), 0xAABBCCDD)

    def test_syscall_em_delay_slot_define_bd_e_epc(self):
        self.carregar(self.PC_INICIAL, encode_i(0x04, 0, 0, 2))
        self.carregar(self.PC_INICIAL + 4, encode_r(0, 0, 0, 0x0C))

        self.executar(limite=2)

        causa = self.cpu.cop0.ler_registrador(COP0.CAUSE)
        self.assertEqual((causa >> 2) & 0x1F, 8)
        self.assertNotEqual(causa & (1 << 31), 0)  # BD
        self.assertEqual(
            self.cpu.cop0.ler_registrador(COP0.EPC),
            self.PC_INICIAL,
        )
        self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO)
        self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"])
        self.assertIsNone(self.cpu.estado_delay["destino_atrasado"])

    def test_syscall_em_branch_nao_tomado_limpa_bt_e_preserva_ce_e_tar(self):
        self.carregar(self.PC_INICIAL, encode_i(0x04, 8, 9, 2))
        self.carregar(self.PC_INICIAL + 4, encode_r(0, 0, 0, 0x0C))
        self.cpu.registradores[8] = 1
        self.cpu.registradores[9] = 2
        # CE (29:28) permanece; BT (30) reflete o branch não tomado.
        self.cpu.cop0.registradores[COP0.CAUSE] = 0x70000000
        self.cpu.cop0.registradores[COP0.TAR] = 0xDEADBEEF

        self.executar(limite=2)

        causa = self.cpu.cop0.ler_registrador(COP0.CAUSE)
        self.assertEqual((causa >> 2) & 0x1F, 8)
        self.assertNotEqual(causa & (1 << 31), 0)  # BD
        self.assertEqual(causa & (1 << 30), 0)  # BT: branch não tomado
        self.assertEqual(causa & (0x3 << 28), 0x3 << 28)  # CE preservado
        self.assertEqual(
            self.cpu.cop0.ler_registrador(COP0.EPC),
            self.PC_INICIAL,
        )

        self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO)
        self.assertEqual(self.cpu.cop0.ler_registrador(COP0.TAR), 0xDEADBEEF)

    def test_syscall_em_branch_tomado_define_bt_epc_e_tar(self):
        destino = self.PC_INICIAL + 12
        self.carregar(self.PC_INICIAL, encode_i(0x04, 0, 0, 2))
        self.carregar(self.PC_INICIAL + 4, encode_r(0, 0, 0, 0x0C))
        self.cpu.cop0.registradores[COP0.CAUSE] = 0x10000000
        self.cpu.cop0.registradores[COP0.TAR] = 0xDEADBEEF

        self.executar(limite=2)

        causa = self.cpu.cop0.ler_registrador(COP0.CAUSE)
        self.assertEqual((causa >> 2) & 0x1F, 8)
        self.assertNotEqual(causa & (1 << 31), 0)  # BD
        self.assertNotEqual(causa & (1 << 30), 0)  # BT: branch tomado
        self.assertEqual(causa & (0x3 << 28), 0x1 << 28)  # CE preservado
        self.assertEqual(self.cpu.cop0.ler_registrador(COP0.EPC), self.PC_INICIAL)
        self.assertEqual(self.cpu.cop0.ler_registrador(COP0.TAR), destino)
        self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO)

    def test_bev_seleciona_vetor_de_boot(self):
        self.cpu.cop0.escrever_registrador(
            COP0.STATUS,
            COP0.MASCARA_BEV,
        )
        self.carregar(self.PC_INICIAL, encode_r(0, 0, 0, 0x0C))

        self.executar()

        self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO_BOOT)

    def test_estado_inicial_da_cpu_usa_vetor_de_boot_sem_configuracao_manual(self):
        cpu = CPU()

        class MemoriaControlada:
            def read_u32(self, endereco):
                if endereco != CPU.PC_INICIAL:
                    raise AssertionError(
                        f"Fetch inesperado em 0x{endereco:08X}"
                    )
                return encode_r(0, 0, 0, 0x0C)

        self.assertNotEqual(
            cpu.cop0.ler_registrador(COP0.STATUS) & COP0.MASCARA_BEV,
            0,
        )
        self.assertEqual(cpu.pc, CPU.PC_INICIAL)
        cpu.executar(MemoriaControlada(), set(), limite=1)

        self.assertEqual(cpu.pc, COP0.VETOR_EXCECAO_BOOT)
        self.assertEqual(
            (cpu.cop0.ler_registrador(COP0.CAUSE) >> 2) & 0x1F,
            8,
        )

    def test_bev_limpo_preserva_vetor_normal(self):
        self.carregar(
            self.PC_INICIAL,
            encode_r(0, 0, 0, 0x0C),
        )

        self.executar()

        self.assertEqual(self.cpu.pc, COP0.VETOR_EXCECAO)

    def test_jr_desalinhado_executa_slot_e_falha_no_fetch_do_destino(self):
        cpu = CPU()
        cpu.pc = self.PC_INICIAL
        memoria = MemoryBus(RAM())
        destino = 0x1011
        memoria.write_u32(
            self.PC_INICIAL,
            encode_r(8, 0, 0, 0x08),  # JR $t0
        )
        memoria.write_u32(
            self.PC_INICIAL + 4,
            encode_i(0x09, 9, 9, 1),  # Delay slot
        )
        cpu.registradores[8] = destino

        cpu.executar(memoria, set(), limite=2)

        self.assertEqual(cpu.pc, destino)
        self.assertEqual(cpu.registradores[9], 1)
        self.assertEqual(cpu.cop0.ler_registrador(COP0.CAUSE), 0)
        self.assertFalse(cpu.estado_delay["delay_slot_ativo"])

        cpu.executar(memoria, set(), limite=1)

        causa = cpu.cop0.ler_registrador(COP0.CAUSE)
        self.assertEqual((causa >> 2) & 0x1F, 4)  # AdEL
        self.assertEqual(causa & (1 << 31), 0)  # Falha no fetch após o slot
        self.assertEqual(cpu.cop0.ler_registrador(COP0.EPC), destino)
        self.assertEqual(cpu.cop0.ler_registrador(COP0.BADVADDR), destino)
        self.assertEqual(cpu.pc, COP0.VETOR_EXCECAO_BOOT)
        self.assertFalse(cpu.estado_delay["delay_slot_ativo"])
        self.assertIsNone(cpu.estado_delay["destino_atrasado"])

    def test_jalr_desalinhado_executa_slot_e_falha_no_fetch_do_destino(self):
        cpu = CPU()
        cpu.pc = self.PC_INICIAL
        memoria = MemoryBus(RAM())
        destino = 0x1011
        memoria.write_u32(
            self.PC_INICIAL,
            encode_r(8, 0, 16, 0x09),  # JALR $s0, $t0
        )
        memoria.write_u32(
            self.PC_INICIAL + 4,
            encode_i(0x09, 9, 9, 1),  # Delay slot
        )
        cpu.registradores[8] = destino

        cpu.executar(memoria, set(), limite=2)

        self.assertEqual(cpu.pc, destino)
        self.assertEqual(cpu.registradores[16], self.PC_INICIAL + 8)
        self.assertEqual(cpu.registradores[9], 1)
        self.assertEqual(cpu.cop0.ler_registrador(COP0.CAUSE), 0)
        self.assertFalse(cpu.estado_delay["delay_slot_ativo"])

        cpu.executar(memoria, set(), limite=1)

        causa = cpu.cop0.ler_registrador(COP0.CAUSE)
        self.assertEqual((causa >> 2) & 0x1F, 4)  # AdEL
        self.assertEqual(causa & (1 << 31), 0)  # Falha no fetch após o slot
        self.assertEqual(cpu.cop0.ler_registrador(COP0.EPC), destino)
        self.assertEqual(cpu.cop0.ler_registrador(COP0.BADVADDR), destino)
        self.assertEqual(cpu.pc, COP0.VETOR_EXCECAO_BOOT)
        self.assertFalse(cpu.estado_delay["delay_slot_ativo"])
        self.assertIsNone(cpu.estado_delay["destino_atrasado"])

    def test_erro_python_nao_identificado_nao_vira_excecao_cop0(self):
        self.cpu.pc = 0x00800000  # Fora do espelho de RAM mapeado.

        with self.assertRaises(ValueError):
            self.executar()

        self.assertEqual(self.cpu.cop0.ler_registrador(COP0.CAUSE), 0)
        self.assertEqual(self.cpu.cop0.ler_registrador(COP0.EPC), 0)

    def test_opcode_de_coprocessador_nao_suportado_nao_vira_ri(self):
        self.carregar(self.PC_INICIAL, 0x44000000)  # MFC1 (COP1)

        with self.assertRaises(NotImplementedError):
            self.executar()

        self.assertEqual(self.cpu.cop0.ler_registrador(COP0.CAUSE), 0)

    def test_codificacao_cop0_invalida_gera_instrucao_reservada(self):
        # MFC0 com campo de função não zero não é a codificação MIPS I válida.
        self.carregar(self.PC_INICIAL, 0x40000001)

        self.executar()

        self.assertEqual(self.codigo_excecao(), 10)
        self.assertEqual(
            self.cpu.cop0.ler_registrador(COP0.EPC),
            self.PC_INICIAL,
        )


if __name__ == "__main__":
    unittest.main()
