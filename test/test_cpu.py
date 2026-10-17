import os
import unittest


from ps1.cpu.mips_r3000a import CPU
from ps1.memory.main_ram import RAM
from ps1 import MemoryBus


class TestCPU(unittest.TestCase):
    def test_executar_addiu(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        cpu = CPU()

        # ADDIU $t0, $zero, 42
        memoria.write_u32(0x1000, 0x2408002A)

        cpu.pc = 0x1000

        cpu.executar(
            memoria,
            {0x1000},
            limite=1,
        )

        self.assertEqual(cpu.registradores[8], 42)
        self.assertEqual(cpu.pc, 0x1004)
        self.assertEqual(cpu.registradores[0], 0)

    def test_executar_uma_instrucao_por_chamada(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        cpu = CPU()

        # ADDIU $t0, $zero, 42
        memoria.write_u32(0x1000, 0x2408002A)

        # ADDIU $t1, $zero, 10
        memoria.write_u32(0x1004, 0x2409000A)

        cpu.pc = 0x1000

        cpu.executar(memoria, {0x1000, 0x1004}, um_passo=True)

        self.assertEqual(cpu.registradores[8], 42)
        self.assertEqual(cpu.registradores[9], 0)
        self.assertEqual(cpu.pc, 0x1004)

        cpu.executar(memoria, {0x1000, 0x1004}, um_passo=True)

        self.assertEqual(cpu.registradores[9], 10)
        self.assertEqual(cpu.pc, 0x1008)

    def test_beq_com_delay_slot_entre_chamadas(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        cpu = CPU()

        # BEQ $zero, $zero, +2
        memoria.write_u32(0x1000, 0x10000002)

        # Delay slot: ADDIU $t0, $zero, 42
        memoria.write_u32(0x1004, 0x2408002A)

        # Instrução que deve ser ignorada pelo desvio
        memoria.write_u32(0x1008, 0x24090063)

        # Destino do desvio: ADDIU $t1, $zero, 10
        memoria.write_u32(0x100C, 0x2409000A)

        cpu.pc = 0x1000

        # 1ª chamada: executa o BEQ
        cpu.executar(memoria, {0x1000}, um_passo=True)
        self.assertEqual(cpu.pc, 0x1004)

        # 2ª chamada: executa o delay slot
        cpu.executar(memoria, {0x1000}, um_passo=True)
        self.assertEqual(cpu.registradores[8], 42)
        self.assertEqual(cpu.pc, 0x100C)

        # 3ª chamada: executa a instrução no destino
        cpu.executar(memoria, {0x1000}, um_passo=True)
        self.assertEqual(cpu.registradores[9], 10)
        self.assertEqual(cpu.pc, 0x1010)

if __name__ == "__main__":
    unittest.main()