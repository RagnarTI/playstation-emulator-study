
import os
import sys
import unittest

PASTA_PROJETO = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PASTA_PROJETO not in sys.path:
    sys.path.insert(0, PASTA_PROJETO)


from mips_interpreter import (
    encode_i,
    executar_programa,
    EnderecoDesalinhadoError,
)
from ram import RAM
from memory_bus import MemoryBus


class TestMemory(unittest.TestCase):

    def executar_instrucao(self, instrucao, valores, memoria=None):
        if memoria is None:
            memoria = RAM()

        registradores = [0] * 32
        endereco_instrucao = 0x1000

        for indice, valor in valores.items():
            registradores[indice] = valor & 0xFFFFFFFF

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        return registradores, memoria

    def test_sw(self):
        instrucao = encode_i(0x2B, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {8: 12345, 9: 0x3000},
        )

        self.assertEqual(memoria.read_u32(0x3000), 12345)
        self.assertEqual(registradores[8], 12345)
        self.assertEqual(registradores[9], 0x3000)

    def test_lw(self):
        memoria = RAM()
        memoria.write_u32(0x3000, 9876)

        instrucao = encode_i(0x23, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {9: 0x3000},
            memoria,
        )

        self.assertEqual(registradores[8], 9876)

    def test_little_endian(self):
        memoria = RAM()

        memoria.write_u32(0x2000, 0x12345678)

        self.assertEqual(memoria.read_u8(0x2000), 0x78)
        self.assertEqual(memoria.read_u8(0x2001), 0x56)
        self.assertEqual(memoria.read_u8(0x2002), 0x34)
        self.assertEqual(memoria.read_u8(0x2003), 0x12)

    def test_sw_atravessa_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x2B, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {8: 12345, 9: 0x3000},
            memoria,
        )

        self.assertEqual(memoria.read_u32(0x3000), 12345)
        self.assertEqual(ram.read_u32(0x3000), 12345)
        self.assertEqual(registradores[8], 12345)
        self.assertEqual(registradores[9], 0x3000)

    def test_lw_atravessa_memory_bus(self):
        ram = RAM()
        ram.write_u32(0x3000, 9876)
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x23, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {9: 0x3000},
            memoria,
        )

        self.assertEqual(registradores[8], 9876)

    def test_sw_kseg0_atravessa_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x2B, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {8: 12345, 9: 0x80003000},
            memoria,
        )

        self.assertEqual(ram.read_u32(0x3000), 12345)

    def test_sw_kseg1_atravessa_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x2B, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {8: 12345, 9: 0xA0003000},
            memoria,
        )

        self.assertEqual(ram.read_u32(0x3000), 12345)

    def test_lw_kseg0_atravessa_memory_bus(self):
        ram = RAM()
        ram.write_u32(0x3000, 9876)
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x23, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {9: 0x80003000},
            memoria,
        )

        self.assertEqual(registradores[8], 9876)

    def test_lw_kseg1_atravessa_memory_bus(self):
        ram = RAM()
        ram.write_u32(0x3000, 9876)
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x23, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {9: 0xA0003000},
            memoria,
        )

        self.assertEqual(registradores[8], 9876)

    def test_instruction_fetch_fora_dos_enderecos_programa(self):
        memoria = RAM()
        registradores = [0] * 32
        endereco_instrucao = 0x1000

        # ADDI $t0, $zero, 42
        instrucao = (0x08 << 26) | (0 << 21) | (8 << 16) | 42
        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            set(),
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[8], 42)

    def test_instruction_fetch_instrucao_seguinte_fora_do_conjunto(self):
        memoria = RAM()
        registradores = [0] * 32
        endereco_inicial = 0x1000

        # ADDI $t0, $zero, 10
        instrucao_1 = (0x08 << 26) | (8 << 16) | 10

        # ADDI $t1, $zero, 20
        instrucao_2 = (0x08 << 26) | (9 << 16) | 20

        memoria.write_u32(endereco_inicial, instrucao_1)
        memoria.write_u32(endereco_inicial + 4, instrucao_2)

        executar_programa(
            memoria,
            {endereco_inicial},
            endereco_inicial,
            registradores,
            limite=2,
        )

        self.assertEqual(registradores[8], 10)
        self.assertEqual(registradores[9], 20)

    def test_instruction_fetch_kseg0_atravessa_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        endereco_fisico = 0x1000
        endereco_virtual = 0x80001000

        # ADDI $t0, $zero, 42
        instrucao = (0x08 << 26) | (8 << 16) | 42
        memoria.write_u32(endereco_fisico, instrucao)

        executar_programa(
            memoria,
            {endereco_virtual},
            endereco_virtual,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[8], 42)

    
    def test_instruction_fetch_kseg1_atravessa_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        endereco_fisico = 0x1000
        endereco_virtual = 0xA0001000

        # ADDI $t0, $zero, 42
        instrucao = (0x08 << 26) | (8 << 16) | 42
        memoria.write_u32(endereco_fisico, instrucao)

        executar_programa(
            memoria,
            {endereco_virtual},
            endereco_virtual,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[8], 42)

    def test_instruction_fetch_endereco_desalinhado(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        with self.assertRaises(ValueError):
            executar_programa(
                memoria,
                set(),
                0x1001,
                registradores,
                limite=1,
            )

    def test_instruction_fetch_instrucao_nula(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        memoria.write_u32(endereco_instrucao, 0x00000000)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[0], 0)
 
    def test_instruction_fetch_instrucao_nula(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        memoria.write_u32(endereco_instrucao, 0x00000000)

        registradores, pc_final = executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
            retornar_pc=True,
        )

        self.assertEqual(registradores[0], 0)
        self.assertEqual(pc_final, endereco_instrucao + 4)

    def test_instruction_fetch_instrucao_desconhecida(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        memoria.write_u32(endereco_instrucao, 0xFFFFFFFF)

        with self.assertRaises(NotImplementedError):
            executar_programa(
                memoria,
                {endereco_instrucao},
                endereco_instrucao,
                registradores,
                limite=1,
            )
    
    def test_instruction_fetch_instrucao_desconhecida_preserva_pc(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        memoria.write_u32(endereco_instrucao, 0xFFFFFFFF)

        with self.assertRaises(NotImplementedError):
            executar_programa(
                memoria,
                {endereco_instrucao},
                endereco_instrucao,
                registradores,
                limite=1,
                retornar_pc=True,
            )

    def test_jr_executa_delay_slot_antes_do_destino(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 0x2000  # $t0: destino do JR

        # JR $t0
        instrucao_jr = (8 << 21) | 0x08

        # ADDI $t1, $zero, 42
        instrucao_delay = (0x08 << 26) | (9 << 16) | 42

        # ADDI $t2, $zero, 99
        instrucao_destino = (0x08 << 26) | (10 << 16) | 99

        memoria.write_u32(0x1000, instrucao_jr)
        memoria.write_u32(0x1004, instrucao_delay)
        memoria.write_u32(0x2000, instrucao_destino)

        registradores, pc_final = executar_programa(
            memoria,
            {0x1000, 0x1004, 0x2000},
            0x1000,
            registradores,
            limite=3,
            retornar_pc=True,
        )

        self.assertEqual(registradores[9], 42)
        self.assertEqual(registradores[10], 99)
        self.assertEqual(pc_final, 0x2004)

    def test_jal_salva_endereco_retorno_e_executa_delay_slot(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        # JAL para 0x2000
        instrucao_jal = (0x03 << 26) | (0x2000 >> 2)

        # ADDI $t0, $zero, 42 — delay slot
        instrucao_delay = (0x08 << 26) | (8 << 16) | 42

        # ADDI $t1, $zero, 99 — destino
        instrucao_destino = (0x08 << 26) | (9 << 16) | 99

        memoria.write_u32(0x1000, instrucao_jal)
        memoria.write_u32(0x1004, instrucao_delay)
        memoria.write_u32(0x2000, instrucao_destino)

        registradores, pc_final = executar_programa(
            memoria,
            {0x1000, 0x1004, 0x2000},
            0x1000,
            registradores,
            limite=3,
            retornar_pc=True,
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[8], 42)
        self.assertEqual(registradores[9], 99)
        self.assertEqual(pc_final, 0x2004)

    def test_jalr_salva_endereco_retorno_e_executa_delay_slot(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 0x2000  # $t0: destino
        # JALR $s0, $t0
        instrucao_jalr = (8 << 21) | (16 << 11) | 0x09

        # ADDI $t1, $zero, 42 — delay slot
        instrucao_delay = (0x08 << 26) | (9 << 16) | 42

        # ADDI $t2, $zero, 99 — destino
        instrucao_destino = (0x08 << 26) | (10 << 16) | 99

        memoria.write_u32(0x1000, instrucao_jalr)
        memoria.write_u32(0x1004, instrucao_delay)
        memoria.write_u32(0x2000, instrucao_destino)

        registradores, pc_final = executar_programa(
            memoria,
            {0x1000, 0x1004, 0x2000},
            0x1000,
            registradores,
            limite=3,
            retornar_pc=True,
        )

        self.assertEqual(registradores[16], 0x1008)
        self.assertEqual(registradores[9], 42)
        self.assertEqual(registradores[10], 99)
        self.assertEqual(pc_final, 0x2004)

    def test_jalr_destino_desalinhado(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 0x2001  # Destino desalinhado

        # JALR $s0, $t0
        instrucao_jalr = (8 << 21) | (16 << 11) | 0x09
        memoria.write_u32(0x1000, instrucao_jalr)

        with self.assertRaises(EnderecoDesalinhadoError):
            executar_programa(
                memoria,
                {0x1000},
                0x1000,
                registradores,
                limite=1,
            )

    def test_jr_destino_desalinhado(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 0x2001  # Destino desalinhado

        # JR $t0
        instrucao_jr = (8 << 21) | 0x08
        memoria.write_u32(0x1000, instrucao_jr)

        with self.assertRaises(EnderecoDesalinhadoError):
            executar_programa(
                memoria,
                {0x1000},
                0x1000,
                registradores,
                limite=1,
            )

    def test_j_executa_delay_slot_e_salva_destino(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        # J 0x2000
        instrucao_j = (0x02 << 26) | (0x2000 >> 2)

        memoria.write_u32(0x1000, instrucao_j)
        memoria.write_u32(
            0x1004,
            (9 << 26) | (0 << 21) | (8 << 16) | 42,
        )  # ADDIU $t0, $zero, 42

        memoria.write_u32(
            0x2000,
            (9 << 26) | (0 << 21) | (9 << 16) | 99,
        )  # ADDIU $t1, $zero, 99

        _, pc_final = executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=3,
            retornar_pc=True,
        )

        self.assertEqual(registradores[8], 42)
        self.assertEqual(registradores[9], 99)
        self.assertEqual(pc_final, 0x2004)
    
    def test_j_preserva_bits_superiores_de_pc(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        pc_inicial = 0x80001000
        destino_virtual = 0x80002000

        # J 0x80002000: os 26 bits codificam o destino
        instrucao_j = (0x02 << 26) | ((destino_virtual >> 2) & 0x03FFFFFF)

        memoria.write_u32(0x1000, instrucao_j)
        memoria.write_u32(
            0x1004,
            (9 << 26) | (8 << 16) | 42,
        )  # ADDIU $t0, $zero, 42

        memoria.write_u32(
            0x2000,
            (9 << 26) | (9 << 16) | 99,
        )  # ADDIU $t1, $zero, 99

        _, pc_final = executar_programa(
            memoria,
            {pc_inicial},
            pc_inicial,
            registradores,
            limite=3,
            retornar_pc=True,
        )

        self.assertEqual(registradores[8], 42)
        self.assertEqual(registradores[9], 99)
        self.assertEqual(pc_final, 0x80002004)

    # def test_j_usa_bits_superiores_de_pc_mais_quatro(self):
    #     ram = RAM()
    #     memoria = MemoryBus(ram)
    #     registradores = [0] * 32

    #     # O PC + 4 será 0x10000000.
    #     pc_inicial = 0x0FFFFFFC

    #     # Armazena as instruções em endereços físicos acessíveis.
    #     memoria.write_u32(0x0FFFFFFC & 0x1FFFFF, (0x02 << 26) | (0x1000 >> 2))
    #     memoria.write_u32(0x0FFFFFFC & 0x1FFFFF + 4, (9 << 26) | (8 << 16) | 42)

    def test_j_calcula_destino_apos_limite_de_256_mib(self):
        pc_atual = 0x0FFFFFFC
        destino_codificado = 0x00100000

        instrucao = (0x02 << 26) | destino_codificado

        destino = (
            ((pc_atual + 4) & 0xF0000000)
            | ((instrucao & 0x03FFFFFF) << 2)
        )

        self.assertEqual(destino, 0x10400000)
    
    def test_j_calcula_destino_sem_cruzar_limite(self):
        pc_atual = 0x80001000
        destino_codificado = 0x00002000

        instrucao = (0x02 << 26) | destino_codificado

        destino = (
            ((pc_atual + 4) & 0xF0000000)
            | ((instrucao & 0x03FFFFFF) << 2)
        )

        self.assertEqual(destino, 0x80008000)

    def test_j_nao_altera_registrador_ra(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[31] = 0x12345678

        instrucao_j = (0x02 << 26) | (0x2000 >> 2)
        memoria.write_u32(0x1000, instrucao_j)

        memoria.write_u32(
            0x1004,
            (9 << 26) | (0 << 21) | (8 << 16) | 42,
        )  # ADDIU $t0, $zero, 42

        memoria.write_u32(
            0x2000,
            (9 << 26) | (0 << 21) | (9 << 16) | 99,
        )  # ADDIU $t1, $zero, 99

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=3,
        )

        self.assertEqual(registradores[31], 0x12345678)
        self.assertEqual(registradores[8], 42)
        self.assertEqual(registradores[9], 99)

    def test_jal_endereco_retorno_independe_do_delay_slot(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        # JAL 0x2000
        instrucao_jal = (0x03 << 26) | (0x2000 >> 2)
        memoria.write_u32(0x1000, instrucao_jal)

        # Delay slot: ADDIU $ra, $zero, 42
        instrucao_delay = (9 << 26) | (0 << 21) | (31 << 16) | 42
        memoria.write_u32(0x1004, instrucao_delay)

        # Destino: ADDIU $t0, $zero, 99
        instrucao_destino = (9 << 26) | (0 << 21) | (8 << 16) | 99
        memoria.write_u32(0x2000, instrucao_destino)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=3,
        )

        self.assertEqual(registradores[31], 42)
        self.assertEqual(registradores[8], 99)

    def test_jalr_com_destino_ra_zero(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 0x2000

        # JALR $zero, $t0
        instrucao_jalr = (8 << 21) | 0x09
        memoria.write_u32(0x1000, instrucao_jalr)

        # Delay slot: ADDIU $t1, $zero, 42
        memoria.write_u32(
            0x1004,
            (9 << 26) | (0 << 21) | (9 << 16) | 42,
        )

        # Destino: ADDIU $t2, $zero, 99
        memoria.write_u32(
            0x2000,
            (9 << 26) | (0 << 21) | (10 << 16) | 99,
        )

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=3,
        )

        self.assertEqual(registradores[0], 0)
        self.assertEqual(registradores[9], 42)
        self.assertEqual(registradores[10], 99)

    def test_jr_nao_altera_registradores(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 0x2000
        registradores[31] = 0x12345678

        # JR $t0
        instrucao_jr = (8 << 21) | 0x08
        memoria.write_u32(0x1000, instrucao_jr)

        # Delay slot: ADDIU $t1, $zero, 42
        memoria.write_u32(
            0x1004,
            (9 << 26) | (9 << 16) | 42,
        )

        # Destino: ADDIU $t2, $zero, 99
        memoria.write_u32(
            0x2000,
            (9 << 26) | (10 << 16) | 99,
        )

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=3,
        )

        self.assertEqual(registradores[8], 0x2000)
        self.assertEqual(registradores[31], 0x12345678)
        self.assertEqual(registradores[9], 42)
        self.assertEqual(registradores[10], 99)

    def test_beq_com_memory_bus_executa_delay_slot_e_destino(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 10
        registradores[9] = 10

        # BEQ $t0, $t1, +2
        instrucao_beq = (
            (0x04 << 26)
            | (8 << 21)
            | (9 << 16)
            | 2
        )

        memoria.write_u32(0x1000, instrucao_beq)

        # Delay slot: ADDIU $t2, $zero, 42
        memoria.write_u32(
            0x1004,
            (0x09 << 26) | (10 << 16) | 42,
        )

        # Instrução que seria executada sem o desvio
        memoria.write_u32(
            0x1008,
            (0x09 << 26) | (11 << 16) | 11,
        )

        # Destino do branch: 0x100C
        memoria.write_u32(
            0x100C,
            (0x09 << 26) | (12 << 16) | 99,
        )

        _, pc_final = executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=3,
            retornar_pc=True,
        )

        self.assertEqual(registradores[10], 42)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 99)
        self.assertEqual(pc_final, 0x1010)

    def test_beq_nao_tomado_com_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 10
        registradores[9] = 20

        # BEQ $t0, $t1, +2
        instrucao_beq = (
            (0x04 << 26)
            | (8 << 21)
            | (9 << 16)
            | 2
        )
        memoria.write_u32(0x1000, instrucao_beq)

        # Delay slot: ADDIU $t2, $zero, 42
        memoria.write_u32(
            0x1004,
            (0x09 << 26) | (10 << 16) | 42,
        )

        # Próxima instrução sequencial: ADDIU $t3, $zero, 11
        memoria.write_u32(
            0x1008,
            (0x09 << 26) | (11 << 16) | 11,
        )

        _, pc_final = executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=3,
            retornar_pc=True,
        )

        self.assertEqual(registradores[10], 42)
        self.assertEqual(registradores[11], 11)
        self.assertEqual(pc_final, 0x100C)

    def test_bne_tomado_com_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 10
        registradores[9] = 20

        # BNE $t0, $t1, +2
        instrucao_bne = (
            (0x05 << 26)
            | (8 << 21)
            | (9 << 16)
            | 2
        )
        memoria.write_u32(0x1000, instrucao_bne)

        # Delay slot: ADDIU $t2, $zero, 42
        memoria.write_u32(
            0x1004,
            (0x09 << 26) | (10 << 16) | 42,
        )

        # Instrução que deve ser ignorada
        memoria.write_u32(
            0x1008,
            (0x09 << 26) | (11 << 16) | 11,
        )

        # Destino do branch: 0x100C
        memoria.write_u32(
            0x100C,
            (0x09 << 26) | (12 << 16) | 99,
        )

        _, pc_final = executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=3,
            retornar_pc=True,
        )

        self.assertEqual(registradores[10], 42)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 99)
        self.assertEqual(pc_final, 0x1010)

    def test_bne_nao_tomado_com_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 10
        registradores[9] = 10

        # BNE $t0, $t1, +2
        instrucao_bne = (
            (0x05 << 26)
            | (8 << 21)
            | (9 << 16)
            | 2
        )
        memoria.write_u32(0x1000, instrucao_bne)

        # Delay slot: ADDIU $t2, $zero, 42
        memoria.write_u32(
            0x1004,
            (0x09 << 26) | (10 << 16) | 42,
        )

        # Próxima instrução sequencial: ADDIU $t3, $zero, 11
        memoria.write_u32(
            0x1008,
            (0x09 << 26) | (11 << 16) | 11,
        )

        _, pc_final = executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=3,
            retornar_pc=True,
        )

        self.assertEqual(registradores[10], 42)
        self.assertEqual(registradores[11], 11)
        self.assertEqual(pc_final, 0x100C)

    def test_beq_com_deslocamento_negativo_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 10
        registradores[9] = 10

        # 0x1000: ADDIU $t2, $zero, 1
        memoria.write_u32(
            0x1000,
            (0x09 << 26) | (10 << 16) | 1,
        )

        # 0x1004: BEQ $t0, $t1, -2
        instrucao_beq = (
            (0x04 << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFE
        )
        memoria.write_u32(0x1004, instrucao_beq)

        # 0x1008: Delay slot do BEQ
        memoria.write_u32(
            0x1008,
            (0x09 << 26) | (11 << 16) | 42,
        )

        _, pc_final = executar_programa(
            memoria,
            {0x1000, 0x1004},
            0x1000,
            registradores,
            limite=4,
            retornar_pc=True,
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 42)
        self.assertEqual(pc_final, 0x1004)

    def test_bne_com_deslocamento_negativo_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)
        registradores = [0] * 32

        registradores[8] = 10
        registradores[9] = 20

        # 0x1000: ADDIU $t2, $zero, 1
        memoria.write_u32(
            0x1000,
            (0x09 << 26) | (10 << 16) | 1,
        )

        # 0x1004: BNE $t0, $t1, -2
        instrucao_bne = (
            (0x05 << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFE
        )
        memoria.write_u32(0x1004, instrucao_bne)

        # 0x1008: Delay slot
        memoria.write_u32(
            0x1008,
            (0x09 << 26) | (11 << 16) | 42,
        )

        _, pc_final = executar_programa(
            memoria,
            {0x1000, 0x1004},
            0x1000,
            registradores,
            limite=4,
            retornar_pc=True,
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 42)
        self.assertEqual(pc_final, 0x1004)



if __name__ == "__main__":
    unittest.main()
