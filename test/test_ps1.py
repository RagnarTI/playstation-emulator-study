import os
import unittest

PASTA_TESTES = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


from ps1 import PS1

class TestPS1(unittest.TestCase):
    # def test_cpu_inicia_no_endereco_da_bios(self):
    #     self.assertEqual(self.ps1.cpu.pc, 0xBFC00000)

    # def test_bios_pode_ser_lida_pelo_endereco_inicial(self):
    #     instrucao = self.ps1.memory_bus.read_u32(
    #         self.ps1.cpu.pc
    #     )

    #     self.assertEqual(instrucao, 0x12345678)

    # def test_cpu_executa_instrucao_da_bios(self):
    #     # ADDIU $t0, $zero, 42
    #     self.ps1.bios.dados = (
    #         b"\x2A\x00\x08\x24"
    #         + bytes(512 * 1024 - 4)
    #     )

    #     self.ps1.cpu.executar(
    #         self.ps1.memory_bus,
    #         {0xBFC00000},
    #         limite=1,
    #     )

        # self.assertEqual(self.ps1.cpu.registradores[8], 42)
        # self.assertEqual(self.ps1.cpu.pc, 0xBFC00004)

    def test_bios_real_executa_primeira_instrucao(self):
        caminho_bios = os.path.join(PASTA_TESTES, "ps1", "memory", "bios", "SCPH1001.BIN")
        ps1 = PS1(caminho_bios)

        self.assertEqual(
            ps1.memory_bus.read_u32(ps1.cpu.pc),
            0x3C080013,  # LUI $t0, 0x0013
        )

        ps1.cpu.executar(
            ps1.memory_bus,
            set(),
            limite=1,
        )

        self.assertEqual(ps1.cpu.registradores[8], 0x00130000)
        self.assertEqual(ps1.cpu.pc, 0xBFC00004)



if __name__ == "__main__":
    unittest.main()
