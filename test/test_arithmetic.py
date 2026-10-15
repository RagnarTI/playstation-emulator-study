import os
import sys
import unittest

PASTA_PROJETO = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PASTA_PROJETO not in sys.path:
    sys.path.insert(0, PASTA_PROJETO)

from mips_interpreter import (
    encode_r,
    encode_i,
    executar_programa,
    EnderecoDesalinhadoError,
    EstadoEspecial,
)
from ram import RAM

class TestArithmetic(unittest.TestCase):

    def executar_instrucao(self, instrucao, valores):
        memoria = RAM()
        registradores = [0] * 32
        endereco = 0x1000

        for indice, valor in valores.items():
            registradores[indice] = valor & 0xFFFFFFFF

        memoria.write_u32(endereco, instrucao)

        executar_programa(
            memoria,
            {endereco},
            endereco,
            registradores,
            limite=1,
        )

        return registradores


    def test_add(self):
        instrucao = encode_r(8, 9, 10, 0x20)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 15, 9: 25},
        )

        self.assertEqual(registradores[10], 40)

    def test_sub(self):
        instrucao = encode_r(8, 9, 10, 0x22)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 30, 9: 12},
        )

        self.assertEqual(registradores[10], 18)

    def test_addi_immediate_negativo(self):
        instrucao = encode_i(0x08, 9, 8, -5)

        registradores = self.executar_instrucao(
            instrucao,
            {9: 20},
        )

        self.assertEqual(registradores[8], 15)

    def test_slt_verdadeiro(self):
        instrucao = encode_r(8, 9, 10, 0x2A)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 10, 9: 20},
        )

        self.assertEqual(registradores[10], 1)

    def test_slt_falso(self):
        instrucao = encode_r(8, 9, 10, 0x2A)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 30, 9: 20},
        )

        self.assertEqual(registradores[10], 0)

    def test_sltu_valor_alto_sem_sinal(self):
        instrucao = encode_r(8, 9, 10, 0x2B)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0xFFFFFFFF, 9: 1},
        )

        self.assertEqual(registradores[10], 0)

    def test_and(self):
        instrucao = encode_r(8, 9, 10, 0x24)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 12, 9: 10},
        )

        self.assertEqual(registradores[10], 8)

    def test_or(self):
        instrucao = encode_r(8, 9, 10, 0x25)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 12, 9: 10},
        )

        self.assertEqual(registradores[10], 14)

    
    def test_xor(self):
        instrucao = encode_r(8, 9, 10, 0x26)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 12, 9: 10},
        )

        self.assertEqual(registradores[10], 6)
    
    def test_nor(self):
        instrucao = encode_r(8, 9, 10, 0x27)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 12, 9: 10},
        )

        self.assertEqual(
            registradores[10],
            0xFFFFFFF1,
        )

    def test_sll(self):
        instrucao = encode_r(0, 9, 10, 0x00, shamt=2)

        registradores = self.executar_instrucao(
            instrucao,
            {9: 5},
        )

        self.assertEqual(registradores[10], 20)

    def test_srl(self):
        instrucao = encode_r(0, 9, 10, 0x02, shamt=2)

        registradores = self.executar_instrucao(
            instrucao,
            {9: 20},
        )

        self.assertEqual(registradores[10], 5)
        
    def test_sra_negativo(self):
        instrucao = encode_r(0, 9, 10, 0x03, shamt=2)

        registradores = self.executar_instrucao(
            instrucao,
            {9: 0xFFFFFFF8},
        )

        self.assertEqual(registradores[10], 0xFFFFFFFE)

    def test_slti_verdadeiro(self):
        instrucao = encode_i(0x0A, 8, 10, 20)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 15},
        )

        self.assertEqual(registradores[10], 1)


    def test_slti_falso(self):
        instrucao = encode_i(0x0A, 8, 10, 20)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 25},
        )

        self.assertEqual(registradores[10], 0)

    def test_sltiu_verdadeiro(self):
        instrucao = encode_i(0x0B, 8, 10, 20)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 15},
        )

        self.assertEqual(registradores[10], 1)


    def test_sltiu_falso(self):
        instrucao = encode_i(0x0B, 8, 10, 20)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 25},
        )

        self.assertEqual(registradores[10], 0)


    def test_sltiu_com_valor_negativo(self):
        instrucao = encode_i(0x0B, 8, 10, 20)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[10], 0)

    def test_andi_preserva_bits_inferiores(self):
        instrucao = encode_i(0x0C, 8, 10, 0x00FF)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12345678},
        )

        self.assertEqual(registradores[10], 0x78)


    def test_andi_imediato_com_bit_15(self):
        instrucao = encode_i(0x0C, 8, 10, 0x8000)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[10], 0x8000)

    def test_ori_ativa_bits_do_imediato(self):
        instrucao = encode_i(0x0D, 8, 10, 0x00F0)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12340005},
        )

        self.assertEqual(registradores[10], 0x123400F5)


    def test_ori_imediato_com_bit_15(self):
        instrucao = encode_i(0x0D, 8, 10, 0x8000)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0},
        )

        self.assertEqual(registradores[10], 0x00008000)

    def test_xori_inverte_bits_selecionados(self):
        instrucao = encode_i(0x0E, 8, 10, 0x00FF)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x123400FF},
        )

        self.assertEqual(registradores[10], 0x12340000)


    def test_xori_imediato_com_bit_15(self):
        instrucao = encode_i(0x0E, 8, 10, 0x8000)

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[10], 0xFFFF7FFF)

    def test_lui_carrega_metade_superior(self):
        instrucao = encode_i(0x0F, 0, 10, 0x1234)

        registradores = self.executar_instrucao(
            instrucao,
            {},
        )

        self.assertEqual(registradores[10], 0x12340000)


    def test_lui_imediato_com_bit_15(self):
        instrucao = encode_i(0x0F, 0, 10, 0x8000)

        registradores = self.executar_instrucao(
            instrucao,
            {},
        )

        self.assertEqual(registradores[10], 0x80000000)

    def test_write_u32_limita_valor_a_32_bits(self):
        memoria = RAM()

        memoria.write_u32(0x1000, 0x12345678ABCDEF01)

        self.assertEqual(
            memoria.read_u32(0x1000),
            0xABCDEF01,
        )

        self.assertEqual(memoria.read_u8(0x1000), 0x01)
        self.assertEqual(memoria.read_u8(0x1001), 0xEF)
        self.assertEqual(memoria.read_u8(0x1002), 0xCD)
        self.assertEqual(memoria.read_u8(0x1003), 0xAB)

    def test_read_u32_memoria_vazia_retorna_zero(self):
        memoria = RAM()

        resultado = memoria.read_u32(0x1000)

        self.assertEqual(resultado, 0)

    def test_read_u32_memoria_parcialmente_preenchida(self):
        memoria = RAM()

        memoria.write_u8(0x1000, 0x78)
        memoria.write_u8(0x1001, 0x56)

        resultado = memoria.read_u32(0x1000)

        self.assertEqual(resultado, 0x00005678)

    def test_write_u32_altera_apenas_quatro_bytes(self):
        memoria = RAM()

        memoria.write_u8(0x0FFF, 0xAA)
        memoria.write_u8(0x1004, 0xBB)

        memoria.write_u32(0x1000, 0x12345678)

        self.assertEqual(memoria.read_u8(0x0FFF), 0xAA)
        self.assertEqual(memoria.read_u8(0x1000), 0x78)
        self.assertEqual(memoria.read_u8(0x1001), 0x56)
        self.assertEqual(memoria.read_u8(0x1002), 0x34)
        self.assertEqual(memoria.read_u8(0x1003), 0x12)
        self.assertEqual(memoria.read_u8(0x1004), 0xBB)

    def test_write_u32_e_read_u32_preservam_valor(self):
        memoria = RAM()
        valores = [
            0x00000000,
            0x00000001,
            0x12345678,
            0xFFFFFFFF,
        ]

        for valor in valores:
            memoria.write_u32(0x1000, valor)

            resultado = memoria.read_u32(0x1000)

            self.assertEqual(resultado, valor)

    def test_sw_armazena_valor_no_endereco_calculado(self):
        instrucao = encode_i(
            0x2B,  # SW
            1,     # rs: registrador base
            2,     # rt: registrador com o valor
            4      # immediate: deslocamento
        )

        memoria = RAM()
        registradores = [0] * 32
        registradores[1] = 0x1000
        registradores[2] = 0x12345678

        memoria.write_u32(0x2000, instrucao)

        executar_programa(
            memoria,
            {0x2000},
            0x2000,
            registradores,
            limite=1,
        )

        self.assertEqual(
            memoria.read_u32(0x1004),
            0x12345678,
        )

    def test_lw_carrega_valor_do_endereco_calculado(self):
        instrucao = encode_i(
            0x23,  # LW
            1,     # rs: registrador base
            2,     # rt: registrador de destino
            4      # immediate: deslocamento
        )

        memoria = RAM()
        registradores = [0] * 32
        registradores[1] = 0x1000
        registradores[2] = 0xAAAAAAAA
        registradores[3] = 0xBBBBBBBB

        memoria.write_u32(0x2000, instrucao)
        memoria.write_u32(0x1004, 0x12345678)

        executar_programa(
            memoria,
            {0x2000},
            0x2000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0x12345678)
        self.assertEqual(registradores[1], 0x1000)
        self.assertEqual(registradores[3], 0xBBBBBBBB)
        self.assertEqual(registradores[0], 0)

    def test_lw_nao_altera_registrador_zero(self):
        instrucao = encode_i(
            0x23,  # LW
            1,     # rs: registrador base
            0,     # rt: $zero
            4      # immediate
        )

        memoria = RAM()
        registradores = [0] * 32
        registradores[1] = 0x1000

        memoria.write_u32(0x2000, instrucao)
        memoria.write_u32(0x1004, 0x12345678)

        executar_programa(
            memoria,
            {0x2000},
            0x2000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[0], 0)
    
    def test_lw_com_deslocamento_negativo(self):
        instrucao = encode_i(
            0x23,  # LW
            1,     # rs: registrador base
            2,     # rt: registrador de destino
            -4     # immediate: deslocamento negativo
        )

        memoria = RAM()
        registradores = [0] * 32
        registradores[1] = 0x1004

        memoria.write_u32(0x2000, instrucao)
        memoria.write_u32(0x1000, 0x12345678)

        executar_programa(
            memoria,
            {0x2000},
            0x2000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0x12345678)

    def test_sw_com_deslocamento_negativo(self):
        instrucao = encode_i(
            0x2B,  # SW
            1,     # rs: registrador base
            2,     # rt: registrador com o valor
            -4     # immediate: deslocamento negativo
        )

        memoria = RAM()
        registradores = [0] * 32
        registradores[1] = 0x1004
        registradores[2] = 0x12345678

        memoria.write_u32(0x2000, instrucao)

        executar_programa(
            memoria,
            {0x2000},
            0x2000,
            registradores,
            limite=1,
        )

        self.assertEqual(
            memoria.read_u32(0x1000),
            0x12345678,
        )

    def test_lw_com_endereco_desalinhado(self):
        instrucao = encode_i(
            0x23,  # LW
            1,     # rs: registrador base
            2,     # rt: registrador de destino
            0
        )

        memoria = RAM()
        registradores = [0] * 32
        registradores[1] = 0x1002
        registradores[2] = 0xAAAAAAAA

        memoria.write_u32(0x2000, instrucao)

        with self.assertRaisesRegex(
            EnderecoDesalinhadoError,
            "LW em endereco desalinhado: 0x00001002",
        ):
            executar_programa(
                memoria,
                {0x2000},
                0x2000,
                registradores,
                limite=1,
            )

        self.assertEqual(registradores[2], 0xAAAAAAAA)

    def test_sw_com_endereco_desalinhado(self):
        instrucao = encode_i(
            0x2B,  # SW
            1,     # rs: registrador base
            2,     # rt: registrador com o valor
            0
        )

        memoria = RAM()
        registradores = [0] * 32
        registradores[1] = 0x1002
        registradores[2] = 0x12345678

        memoria.write_u32(0x2000, instrucao)

        memoria_antes = [
            memoria.read_u8(endereco)
            for endereco in range(0x1000, 0x1004)
        ]

        with self.assertRaisesRegex(
            EnderecoDesalinhadoError,
            "SW em endereco desalinhado: 0x00001002",
        ):
            executar_programa(
                memoria,
                {0x2000},
                0x2000,
                registradores,
                limite=1,
            )

        memoria_depois = [
            memoria.read_u8(endereco)
            for endereco in range(0x1000, 0x1004)
        ]

        self.assertEqual(memoria_depois, memoria_antes)
    
    def test_lb_com_valor_positivo(self):
        memoria = RAM()
        registradores = [0] * 32

        memoria.write_u8(0x2000, 0x7F)
        registradores[1] = 0x2000

        # LB rt, immediate(rs): opcode 0x20
        instrucao = (0x20 << 26) | (1 << 21) | (2 << 16)
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0x7F)

    def test_lb_com_valor_negativo(self):
        memoria = RAM()
        registradores = [0] * 32

        memoria.write_u8(0x2000, 0x80)
        registradores[1] = 0x2000

        instrucao = (0x20 << 26) | (1 << 21) | (2 << 16)
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0xFFFFFF80)

    def test_lbu_nao_faz_extensao_de_sinal(self):
        memoria = RAM()
        registradores = [0] * 32

        memoria.write_u8(0x2000, 0xFF)
        registradores[1] = 0x2000

        # LBU rt, immediate(rs): opcode 0x24
        instrucao = (0x24 << 26) | (1 << 21) | (2 << 16)
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0xFF)

    def test_lb_nao_altera_registrador_zero(self):
        memoria = RAM()
        registradores = [0] * 32

        memoria.write_u8(0x2000, 0x80)
        registradores[1] = 0x2000

        # LB $zero, 0($1)
        instrucao = (0x20 << 26) | (1 << 21)
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[0], 0)

        
    def test_lh_com_valor_positivo(self):
        memoria = RAM()
        registradores = [0] * 32

        memoria.write_u16(0x2000, 0x7FFF)
        registradores[1] = 0x2000

        # LH rt, immediate(rs): opcode 0x21
        instrucao = (0x21 << 26) | (1 << 21) | (2 << 16)
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0x7FFF)

    def test_lh_com_valor_negativo(self):
        memoria = RAM()
        registradores = [0] * 32

        memoria.write_u16(0x2000, 0x8000)
        registradores[1] = 0x2000

        instrucao = (0x21 << 26) | (1 << 21) | (2 << 16)
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0xFFFF8000)

    def test_lhu_nao_faz_extensao_de_sinal(self):
        memoria = RAM()
        registradores = [0] * 32

        memoria.write_u16(0x2000, 0xFFFF)
        registradores[1] = 0x2000

        # LHU rt, immediate(rs): opcode 0x25
        instrucao = (0x25 << 26) | (1 << 21) | (2 << 16)
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0xFFFF)

    def test_lh_nao_altera_registrador_zero(self):
        memoria = RAM()
        registradores = [0] * 32

        memoria.write_u16(0x2000, 0x8000)
        registradores[1] = 0x2000

        # LH $zero, 0($1)
        instrucao = (0x21 << 26) | (1 << 21)
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[0], 0)

    def test_sb_armazena_apenas_um_byte(self):
        memoria = RAM()
        registradores = [0] * 32

        memoria.write_u32(0x2000, 0x12345678)
        registradores[1] = 0x2000
        registradores[2] = 0xABCDEF90

        # SB rt, immediate(rs): opcode 0x28
        instrucao = (0x28 << 26) | (1 << 21) | (2 << 16)
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(memoria.read_u8(0x2000), 0x90)
        self.assertEqual(memoria.read_u8(0x2001), 0x56)
        self.assertEqual(memoria.read_u8(0x2002), 0x34)
        self.assertEqual(memoria.read_u8(0x2003), 0x12)

    def test_sh_armazena_apenas_dois_bytes(self):
        memoria = RAM()
        registradores = [0] * 32

        memoria.write_u32(0x2000, 0x12345678)
        registradores[1] = 0x2000
        registradores[2] = 0xABCDEF90

        # SH rt, immediate(rs): opcode 0x29
        instrucao = (0x29 << 26) | (1 << 21) | (2 << 16)
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(memoria.read_u8(0x2000), 0x90)
        self.assertEqual(memoria.read_u8(0x2001), 0xEF)
        self.assertEqual(memoria.read_u8(0x2002), 0x34)
        self.assertEqual(memoria.read_u8(0x2003), 0x12)

    def test_sb_com_deslocamento(self):
        memoria = RAM()
        registradores = [0] * 32

        registradores[1] = 0x2000
        registradores[2] = 0xAB
        memoria.write_u8(0x2004, 0x11)

        # SB $2, 4($1)
        instrucao = (
            (0x28 << 26)
            | (1 << 21)
            | (2 << 16)
            | 4
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(memoria.read_u8(0x2004), 0xAB)

    def test_sh_com_deslocamento(self):
        memoria = RAM()
        registradores = [0] * 32

        registradores[1] = 0x2000
        registradores[2] = 0xBEEF
        memoria.write_u16(0x2004, 0x1234)

        # SH $2, 4($1)
        instrucao = (
            (0x29 << 26)
            | (1 << 21)
            | (2 << 16)
            | 4
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
        )

        self.assertEqual(memoria.read_u16(0x2004), 0xBEEF)

    def test_sh_com_endereco_desalinhado(self):
        memoria = RAM()
        registradores = [0] * 32

        registradores[1] = 0x2001
        registradores[2] = 0xBEEF

        # SH $2, 0($1)
        instrucao = (
            (0x29 << 26)
            | (1 << 21)
            | (2 << 16)
        )
        memoria.write_u32(0x1000, instrucao)

        with self.assertRaises(EnderecoDesalinhadoError):
            executar_programa(
                memoria,
                {0x1000},
                0x1000,
                registradores,
                limite=1,
            )
        
    def test_hi_lo_iniciam_em_zero(self):
        estado = EstadoEspecial()

        self.assertEqual(estado.hi, 0)
        self.assertEqual(estado.lo, 0)


    def test_hi_lo_armazenam_valores(self):
        estado = EstadoEspecial()

        estado.hi = 0x12345678
        estado.lo = 0xABCDEF90

        self.assertEqual(estado.hi, 0x12345678)
        self.assertEqual(estado.lo, 0xABCDEF90)
   
    def test_executar_programa_preserva_estado_especial(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        estado.hi = 0x12345678
        estado.lo = 0xABCDEF90

        instrucao = encode_r(
            rs=0,
            rt=0,
            rd=1,
            funct=0x20,  # ADD $1, $0, $0
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.hi, 0x12345678)
        self.assertEqual(estado.lo, 0xABCDEF90)
        self.assertEqual(registradores[1], 0)

    def test_mult_atualiza_hi_lo(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 10
        registradores[2] = 20

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x18,  # MULT $1, $2
        )

        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.lo, 200)
        self.assertEqual(estado.hi, 0)
        self.assertEqual(registradores[1], 10)
        self.assertEqual(registradores[2], 20)
        
    def test_mult_com_resultado_negativo(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 0xFFFFFFFE  # -2
        registradores[2] = 3

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x18,
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.lo, 0xFFFFFFFA)
        self.assertEqual(estado.hi, 0xFFFFFFFF)

    def test_mult_usa_hi_quando_resultado_excede_32_bits(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 0x7FFFFFFF
        registradores[2] = 2

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x18,
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.lo, 0xFFFFFFFE)
        self.assertEqual(estado.hi, 0x00000000)
        
    def test_multu_interpreta_operandos_sem_sinal(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 0xFFFFFFFF
        registradores[2] = 2

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x19,  # MULTU
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.lo, 0xFFFFFFFE)
        self.assertEqual(estado.hi, 0x00000001)

    def test_div_quociente_e_resto(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 17
        registradores[2] = 5

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x1A,  # DIV
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.lo, 3)
        self.assertEqual(estado.hi, 2)

    def test_div_com_operando_negativo(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 0xFFFFFFF9  # -7
        registradores[2] = 3

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x1A,  # DIV
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.lo, 0xFFFFFFFE)  # -2
        self.assertEqual(estado.hi, 0xFFFFFFFF)  # -1

    def test_div_por_zero_com_dividendo_positivo(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 17
        registradores[2] = 0

        # Valores sentinela para garantir que DIV os atualize.
        estado.hi = 0x12345678
        estado.lo = 0xABCDEF01

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x1A,  # DIV
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.hi, 17)
        self.assertEqual(estado.lo, 0xFFFFFFFF)

    def test_div_por_zero_com_dividendo_negativo(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 0xFFFFFFF9  # -7
        registradores[2] = 0

        estado.hi = 0x12345678
        estado.lo = 0xABCDEF01

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x1A,  # DIV
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.hi, 0xFFFFFFF9)
        self.assertEqual(estado.lo, 0x00000001)

    def test_divu_quociente_e_resto(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 17
        registradores[2] = 5

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x1B,  # DIVU
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.lo, 3)
        self.assertEqual(estado.hi, 2)

    def test_divu_interpreta_operandos_sem_sinal(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 0xFFFFFFFF
        registradores[2] = 2

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x1B,  # DIVU
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.lo, 0x7FFFFFFF)
        self.assertEqual(estado.hi, 1)

    def test_divu_por_zero(self):
        memoria = RAM()
        registradores = [0] * 32
        estado = EstadoEspecial()

        registradores[1] = 17
        registradores[2] = 0

        estado.hi = 0x12345678
        estado.lo = 0xABCDEF01

        instrucao = encode_r(
            rs=1,
            rt=2,
            rd=0,
            funct=0x1B,  # DIVU
        )
        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            0x1000,
            registradores,
            limite=1,
            estado_especial=estado,
        )

        self.assertEqual(estado.lo, 0xFFFFFFFF)
        self.assertEqual(estado.hi, 17)

    def test_delay_slot_j_executa_antes_do_salto(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco = 0x1000

        # J para 0x1010
        instrucao_j = 0x08000404

        # ADDIU $8, $0, 42 — delay slot
        instrucao_delay = encode_i(
            0x09,  # ADDIU
            0,
            8,
            42,
        )

        memoria.write_u32(endereco, instrucao_j)
        memoria.write_u32(endereco + 4, instrucao_delay)

        executar_programa(
            memoria,
            {endereco, endereco + 4},
            endereco,
            registradores,
            limite=2,
        )

        self.assertEqual(registradores[8], 42)

    def test_j_retorna_pc_final_no_destino(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco = 0x1000

        # J para 0x1010
        instrucao_j = 0x08000404

        # ADDIU $8, $0, 42 — delay slot
        instrucao_delay = encode_i(
            0x09,
            0,
            8,
            42,
        )

        memoria.write_u32(endereco, instrucao_j)
        memoria.write_u32(endereco + 4, instrucao_delay)

        registradores, pc_final = executar_programa(
            memoria,
            {endereco, endereco + 4},
            endereco,
            registradores,
            limite=2,
            retornar_pc=True,
        )

        self.assertEqual(registradores[8], 42)
        self.assertEqual(pc_final, 0x1010)

    def test_jal_salva_retorno_e_executa_delay_slot(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco = 0x1000

        # JAL para 0x1010
        instrucao_jal = 0x0C000404

        # ADDIU $8, $0, 42 — delay slot
        instrucao_delay = encode_i(
            0x09,
            0,
            8,
            42,
        )

        memoria.write_u32(endereco, instrucao_jal)
        memoria.write_u32(endereco + 4, instrucao_delay)

        registradores, pc_final = executar_programa(
            memoria,
            {endereco, endereco + 4},
            endereco,
            registradores,
            limite=2,
            retornar_pc=True,
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[8], 42)
        self.assertEqual(pc_final, 0x1010)

    def test_jr_salva_destino_e_executa_delay_slot(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco = 0x1000
        destino = 0x1020

        registradores[5] = destino

        # JR $5
        instrucao_jr = encode_r(
            rs=5,
            rt=0,
            rd=0,
            funct=0x08,
        )

        # ADDIU $8, $0, 42 — delay slot
        instrucao_delay = encode_i(
            0x09,
            0,
            8,
            42,
        )

        memoria.write_u32(endereco, instrucao_jr)
        memoria.write_u32(endereco + 4, instrucao_delay)

        registradores, pc_final = executar_programa(
            memoria,
            {endereco, endereco + 4},
            endereco,
            registradores,
            limite=2,
            retornar_pc=True,
        )

        self.assertEqual(registradores[8], 42)
        self.assertEqual(pc_final, destino)

    def test_jalr_salva_retorno_e_executa_delay_slot(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco = 0x1000
        destino = 0x1020

        registradores[5] = destino

        # JALR $10, $5
        instrucao_jalr = encode_r(
            rs=5,
            rt=0,
            rd=10,
            funct=0x09,
        )

        # ADDIU $8, $0, 42 — delay slot
        instrucao_delay = encode_i(
            0x09,
            0,
            8,
            42,
        )

        memoria.write_u32(endereco, instrucao_jalr)
        memoria.write_u32(endereco + 4, instrucao_delay)

        registradores, pc_final = executar_programa(
            memoria,
            {endereco, endereco + 4},
            endereco,
            registradores,
            limite=2,
            retornar_pc=True,
        )

        self.assertEqual(registradores[10], 0x1008)
        self.assertEqual(registradores[8], 42)
        self.assertEqual(pc_final, destino)
   
    def test_jr_com_destino_desalinhado(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco = 0x1000
        registradores[5] = 0x1021

        # JR $5
        instrucao_jr = encode_r(
            rs=5,
            rt=0,
            rd=0,
            funct=0x08,
        )

        # ADDIU $8, $0, 42 — delay slot
        instrucao_delay = encode_i(
            0x09,
            0,
            8,
            42,
        )

        memoria.write_u32(endereco, instrucao_jr)
        memoria.write_u32(endereco + 4, instrucao_delay)

        with self.assertRaises(EnderecoDesalinhadoError):
            executar_programa(
                memoria,
                {endereco, endereco + 4},
                endereco,
                registradores,
                limite=2,
                retornar_pc=True,
            )

    def test_jalr_com_destino_desalinhado(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco = 0x1000
        registradores[5] = 0x1021

        # JALR $10, $5
        instrucao_jalr = encode_r(
            rs=5,
            rt=0,
            rd=10,
            funct=0x09,
        )

        memoria.write_u32(endereco, instrucao_jalr)

        with self.assertRaises(EnderecoDesalinhadoError):
            executar_programa(
                memoria,
                {endereco},
                endereco,
                registradores,
                limite=2,
                retornar_pc=True,
            )

    def test_add_com_overflow_com_sinal(self):
        memoria = RAM(1024)

        registradores = [0] * 32
        registradores[8] = 0x7FFFFFFF
        registradores[9] = 1

        programa = [
            encode_r(8, 9, 10, 0, 0x20),  # ADD $10, $8, $9
        ]

        for i, instrucao in enumerate(programa):
            memoria.write_u32(i * 4, instrucao)

        with self.assertRaises(Exception):
            executar_programa(memoria, limite=1)

if __name__ == "__main__":
    unittest.main()