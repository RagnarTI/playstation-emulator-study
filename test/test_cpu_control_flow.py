import os
import unittest


from ps1.cpu.mips_r3000a import CPU
from ps1.cpu.mips_interpreter import encode_i, encode_r
from ps1.memory.main_ram import RAM


class TestCPUControlFlow(unittest.TestCase):
    PC_INICIAL = 0x1000

    def setUp(self):
        self.memoria = RAM()
        self.cpu = CPU()
        self.cpu.pc = self.PC_INICIAL

    def carregar(self, instrucoes):
        for endereco, instrucao in instrucoes.items():
            self.memoria.write_u32(endereco, instrucao)

    def test_execucao_sequencial_respeita_limite_e_pc(self):
        self.carregar({
            0x1000: encode_i(0x09, 0, 8, 11),
            0x1004: encode_i(0x09, 8, 9, 7),
            0x1008: encode_i(0x09, 0, 10, 99),
        })

        self.cpu.executar(self.memoria, set(), limite=2)

        self.assertEqual(self.cpu.pc, 0x1008)
        self.assertEqual(self.cpu.registradores[8], 11)
        self.assertEqual(self.cpu.registradores[9], 18)
        self.assertEqual(self.cpu.registradores[10], 0)
        self.assertEqual(self.cpu.estado_delay, {
            "delay_slot_ativo": False,
            "destino_atrasado": None,
        })

    def test_branch_tomado_executa_slot_e_aplica_destino(self):
        self.carregar({
            0x1000: encode_i(0x04, 8, 9, 2),  # BEQ -> 0x100C
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        })
        self.cpu.registradores[8] = 5
        self.cpu.registradores[9] = 5

        self.cpu.executar(self.memoria, set(), limite=3)

        self.assertEqual(self.cpu.pc, 0x1010)
        self.assertEqual(self.cpu.registradores[10], 1)
        self.assertEqual(self.cpu.registradores[11], 0)
        self.assertEqual(self.cpu.registradores[12], 7)
        self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"])
        self.assertIsNone(self.cpu.estado_delay["destino_atrasado"])

    def test_branch_nao_tomado_executa_slot_e_segue_sequencialmente(self):
        self.carregar({
            0x1000: encode_i(0x04, 8, 9, 2),  # BEQ falso
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        })
        self.cpu.registradores[8] = 5
        self.cpu.registradores[9] = 6

        self.cpu.executar(self.memoria, set(), limite=3)

        self.assertEqual(self.cpu.pc, 0x100C)
        self.assertEqual(self.cpu.registradores[10], 1)
        self.assertEqual(self.cpu.registradores[11], 99)
        self.assertEqual(self.cpu.registradores[12], 0)
        self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"])
        self.assertIsNone(self.cpu.estado_delay["destino_atrasado"])

    def test_estado_de_salto_pendente_persiste_entre_chamadas(self):
        self.carregar({
            0x1000: encode_i(0x04, 0, 0, 2),  # BEQ -> 0x100C
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        })

        self.cpu.executar(self.memoria, set(), limite=1)

        self.assertEqual(self.cpu.pc, 0x1004)
        self.assertEqual(self.cpu.registradores[10], 0)
        self.assertTrue(self.cpu.estado_delay["delay_slot_ativo"])
        self.assertEqual(self.cpu.estado_delay["destino_atrasado"], 0x100C)

        self.cpu.executar(self.memoria, set(), limite=1)

        self.assertEqual(self.cpu.pc, 0x100C)
        self.assertEqual(self.cpu.registradores[10], 1)
        self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"])
        self.assertIsNone(self.cpu.estado_delay["destino_atrasado"])

    def test_jr_executa_delay_slot_antes_do_destino(self):
        self.carregar({
            0x1000: encode_r(8, 0, 0, 0x08),  # JR $t0
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),
            0x1010: encode_i(0x09, 0, 12, 7),  # Destino
        })
        self.cpu.registradores[8] = 0x1010

        self.cpu.executar(self.memoria, set(), limite=3)

        self.assertEqual(self.cpu.pc, 0x1014)
        self.assertEqual(self.cpu.registradores[10], 1)
        self.assertEqual(self.cpu.registradores[11], 0)
        self.assertEqual(self.cpu.registradores[12], 7)
        self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"])
        self.assertIsNone(self.cpu.estado_delay["destino_atrasado"])

    def test_jalr_escreve_link_e_executa_delay_slot(self):
        self.carregar({
            0x1000: encode_r(8, 0, 16, 0x09), # JALR $s0, $t0
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),
            0x1010: encode_i(0x09, 0, 12, 7),  # Destino
        })
        self.cpu.registradores[8] = 0x1010
        self.cpu.registradores[31] = 0xDEADBEEF

        self.cpu.executar(self.memoria, set(), limite=3)

        self.assertEqual(self.cpu.pc, 0x1014)
        self.assertEqual(self.cpu.registradores[16], 0x1008)
        self.assertEqual(self.cpu.registradores[31], 0xDEADBEEF)
        self.assertEqual(self.cpu.registradores[10], 1)
        self.assertEqual(self.cpu.registradores[11], 0)
        self.assertEqual(self.cpu.registradores[12], 7)
        self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"])
        self.assertIsNone(self.cpu.estado_delay["destino_atrasado"])


if __name__ == "__main__":
    unittest.main()
