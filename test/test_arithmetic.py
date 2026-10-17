import os
import unittest


from ps1.cpu.mips_interpreter import (
    MASCARA_32,
    encode_r,
    encode_i,
    executar_programa,
    decodificar_instrucao,
    executar_operacao_logica,
    executar_deslocamento,
    executar_soma_subtracao,
    executar_comparacao,
    executar_multiplicacao,
    executar_divisao,
    executar_salto_registrador,
    calcular_destino_salto,
    calcular_destino_desvio,
    executar_lui,
    executar_addi,
    executar_addiu,
    calcular_endereco_efetivo,
    executar_lwl_lwr,
    executar_swl_swr,
    EnderecoDesalinhadoError,
    EstadoEspecial,
    IntegerOverflow, 
)
from test.helpers.arithmetic_helpers import (
    executar_instrucao as executar_instrucao_compartilhada,
)
from ps1.memory.main_ram import RAM

class TestArithmetic(unittest.TestCase):

    def executar_instrucao(self, instrucao, valores):
        return executar_instrucao_compartilhada(
            instrucao,
            valores,
            limite=1,
        )


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

    def test_decodificar_instrucao_campos_basicos(self):
        instrucao = (
            (0x09 << 26)  # opcode: ADDIU
            | (8 << 21)   # rs: $t0
            | (9 << 16)   # rt: $t1
            | 0xFFFF      # imediato: -1
        )

        campos = decodificar_instrucao(instrucao)

        self.assertEqual(campos["opcode"], 0x09)
        self.assertEqual(campos["rs"], 8)
        self.assertEqual(campos["rt"], 9)
        self.assertEqual(campos["rd"], 31)
        self.assertEqual(campos["shamt"], 31)
        self.assertEqual(campos["funct"], 0x3F)
        self.assertEqual(campos["immediate"], -1)

    def test_executar_operacao_logica(self):
        a = 0b1100
        b = 0b1010

        self.assertEqual(executar_operacao_logica(0x24, a, b), 0b1000)
        self.assertEqual(executar_operacao_logica(0x25, a, b), 0b1110)
        self.assertEqual(executar_operacao_logica(0x26, a, b), 0b0110)
        self.assertEqual(
            executar_operacao_logica(0x27, a, b),
            (~0b1110) & MASCARA_32,
        )

    def test_executar_deslocamento(self):
        self.assertEqual(
            executar_deslocamento(0x00, 3, 2),
            12,
        )

        self.assertEqual(
            executar_deslocamento(0x02, 12, 2),
            3,
        )

        self.assertEqual(
            executar_deslocamento(0x03, 0xFFFFFFF0, 2),
            0xFFFFFFFC,
        )

    def test_executar_soma_subtracao(self):
        self.assertEqual(
            executar_soma_subtracao(0x20, 10, 20),
            30,
        )

        self.assertEqual(
            executar_soma_subtracao(0x22, 20, 10),
            10,
        )

        with self.assertRaises(IntegerOverflow):
            executar_soma_subtracao(0x20, 0x7FFFFFFF, 1)

        with self.assertRaises(IntegerOverflow):
            executar_soma_subtracao(0x22, 0x80000000, 1)

    def test_executar_comparacao(self):
        self.assertEqual(executar_comparacao(0x2A, 10, 20), 1)
        self.assertEqual(executar_comparacao(0x2A, 20, 10), 0)

        # 0xFFFFFFFF representa -1 com sinal, mas é maior que 1 sem sinal.
        self.assertEqual(
            executar_comparacao(0x2A, 0xFFFFFFFF, 1),
            1,
        )
        self.assertEqual(
            executar_comparacao(0x2B, 0xFFFFFFFF, 1),
            0,
        )

    def test_executar_multiplicacao(self):
        hi, lo = executar_multiplicacao(0x18, 10, 20)
        self.assertEqual(hi, 0)
        self.assertEqual(lo, 200)

        hi, lo = executar_multiplicacao(0x19, 0xFFFFFFFF, 2)
        self.assertEqual(hi, 1)
        self.assertEqual(lo, 0xFFFFFFFE)

        hi, lo = executar_multiplicacao(0x18, 0xFFFFFFFF, 2)
        self.assertEqual(hi, 0xFFFFFFFF)
        self.assertEqual(lo, 0xFFFFFFFE)

    def test_executar_divisao(self):
        hi, lo = executar_divisao(0x1A, 20, 6)
        self.assertEqual(lo, 3)
        self.assertEqual(hi, 2)

        hi, lo = executar_divisao(0x1A, 0xFFFFFFF6, 3)
        self.assertEqual(lo, 0xFFFFFFFD)
        self.assertEqual(hi, 0xFFFFFFFF)

        hi, lo = executar_divisao(0x1B, 20, 6)
        self.assertEqual(lo, 3)
        self.assertEqual(hi, 2)

        hi, lo = executar_divisao(0x1A, 10, 0)
        self.assertEqual(lo, 0xFFFFFFFF)
        self.assertEqual(hi, 10)

        hi, lo = executar_divisao(0x1B, 10, 0)
        self.assertEqual(lo, 0xFFFFFFFF)
        self.assertEqual(hi, 10)

    def test_executar_salto_registrador(self):
        destino, link = executar_salto_registrador(
            0x08, 0x2000, 0x1000, False
        )
        self.assertEqual(destino, 0x2000)
        self.assertIsNone(link)

        destino, link = executar_salto_registrador(
            0x09, 0x3000, 0x1000, False
        )
        self.assertEqual(destino, 0x3000)
        self.assertEqual(link, 0x1008)

        with self.assertRaises(EnderecoDesalinhadoError):
            executar_salto_registrador(
                0x08, 0x2002, 0x1000, False
            )

        with self.assertRaises(NotImplementedError):
            executar_salto_registrador(
                0x08, 0x2000, 0x1000, True

        )
    def test_calcular_destino_salto(self):
        instrucao = (0x03 << 26) | 0x00000100

        destino = calcular_destino_salto(
            instrucao,
            0x80000000,
        )

        self.assertEqual(destino, 0x80000400)

    def test_calcular_destino_desvio(self):
        # Desvio para frente
        self.assertEqual(
            calcular_destino_desvio(0x1000, 2),
            0x100C,
        )

        # Desvio para trás
        self.assertEqual(
            calcular_destino_desvio(0x1000, -2),
            0x0FFC,
        )

        # O endereço permanece limitado a 32 bits
        self.assertEqual(
            calcular_destino_desvio(0xFFFFFFFC, 0),
            0x00000000,
        )

    def test_comparacao_imediata(self):
        # SLTI: comparação com sinal
        self.assertEqual(
            executar_comparacao(0x2A, 0xFFFFFFFF, 1),
            1,
        )

        # SLTIU: comparação sem sinal
        self.assertEqual(
            executar_comparacao(0x2B, 0xFFFFFFFF, 1),
            0,
        )

    def test_operacoes_logicas_com_imediato(self):
        imediato = 0x00FF
        valor = 0x12345678

        self.assertEqual(
            executar_operacao_logica(0x24, valor, imediato),
            0x00000078,
        )
        self.assertEqual(
            executar_operacao_logica(0x25, valor, imediato),
            0x123456FF,
        )
        self.assertEqual(
            executar_operacao_logica(0x26, valor, imediato),
            0x12345687,
        )

    def test_executar_lui(self):
        instrucao = (0x0F << 26) | (0x12 << 16) | 0xABCD

        self.assertEqual(
            executar_lui(instrucao),
            0xABCD0000,
        )

    def test_executar_addi(self):
        self.assertEqual(executar_addi(10, 5), 15)
        self.assertEqual(executar_addi(0xFFFFFFFF, 1), 0)

        with self.assertRaises(IntegerOverflow):
            executar_addi(0x7FFFFFFF, 1)

        with self.assertRaises(IntegerOverflow):
            executar_addi(0x80000000, -1)

    def test_executar_addiu(self):
        self.assertEqual(
            executar_addiu(10, 5),
            15,
        )

        self.assertEqual(
            executar_addiu(10, -5),
            5,
        )

        self.assertEqual(
            executar_addiu(0xFFFFFFFF, 1),
            0,
        )

    def test_calcular_endereco_efetivo(self):
        self.assertEqual(
            calcular_endereco_efetivo(0x1000, 4, "LW"),
            0x1004,
        )

        self.assertEqual(
            calcular_endereco_efetivo(0x1000, -4, "SW"),
            0x0FFC,
        )

        with self.assertRaises(EnderecoDesalinhadoError):
            calcular_endereco_efetivo(0x1000, 2, "LW")

        with self.assertRaises(EnderecoDesalinhadoError):
            calcular_endereco_efetivo(0x1000, 2, "SW")

    def test_sltiu_imediato_negativo(self):
        instrucao = (
            (0x0B << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0xFFFFFFFE},
        )

        self.assertEqual(registradores[9], 1)

    def test_addi_gera_overflow_na_execucao(self):
        instrucao = (
            (0x08 << 26)
            | (8 << 21)
            | (9 << 16)
            | 1
        )

        with self.assertRaises(IntegerOverflow):
            self.executar_instrucao(
                instrucao,
                {8: 0x7FFFFFFF},
            )
    
    def test_addiu_nao_gera_overflow_na_execucao(self):
        instrucao = (
            (0x09 << 26)
            | (8 << 21)
            | (9 << 16)
            | 1
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x7FFFFFFF},
        )

        self.assertEqual(registradores[9], 0x80000000)
    
    def test_addi_addiu_preservam_registrador_zero(self):
        instrucao_addi = (
            (0x08 << 26)
            | (8 << 21)
            | (0 << 16)
            | 5
        )

        instrucao_addiu = (
            (0x09 << 26)
            | (8 << 21)
            | (0 << 16)
            | 5
        )

        registradores_addi = self.executar_instrucao(
            instrucao_addi,
            {8: 10},
        )

        registradores_addiu = self.executar_instrucao(
            instrucao_addiu,
            {8: 10},
        )

        self.assertEqual(registradores_addi[0], 0)
        self.assertEqual(registradores_addiu[0], 0)
    
    def test_slti_e_sltiu_diferenciam_comparacao_com_sinal(self):
        instrucao_slti = (
            (0x0A << 26)
            | (8 << 21)
            | (9 << 16)
            | 1
        )

        instrucao_sltiu = (
            (0x0B << 26)
            | (8 << 21)
            | (9 << 16)
            | 1
        )

        registradores_slti = self.executar_instrucao(
            instrucao_slti,
            {8: 0xFFFFFFFF},
        )

        registradores_sltiu = self.executar_instrucao(
            instrucao_sltiu,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores_slti[9], 1)
        self.assertEqual(registradores_sltiu[9], 0)

    def test_slti_imediato_negativo(self):
        instrucao = (
            (0x0A << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0},
        )

        self.assertEqual(registradores[9], 0)

    def test_logicas_imediatas_nao_estendem_sinal(self):
        instrucao_andi = (
            (0x0C << 26)
            | (8 << 21)
            | (9 << 16)
            | 0x8000
        )

        instrucao_ori = (
            (0x0D << 26)
            | (8 << 21)
            | (9 << 16)
            | 0x8000
        )

        instrucao_xori = (
            (0x0E << 26)
            | (8 << 21)
            | (9 << 16)
            | 0x8000
        )

        registradores_andi = self.executar_instrucao(
            instrucao_andi,
            {8: 0xFFFFFFFF},
        )

        registradores_ori = self.executar_instrucao(
            instrucao_ori,
            {8: 0},
        )

        registradores_xori = self.executar_instrucao(
            instrucao_xori,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores_andi[9], 0x00008000)
        self.assertEqual(registradores_ori[9], 0x00008000)
        self.assertEqual(registradores_xori[9], 0xFFFF7FFF)
    
    def test_logicas_imediatas_preservam_registrador_zero(self):
        instrucoes = [
            (0x0C << 26) | (8 << 21) | 0xFFFF,  # ANDI
            (0x0D << 26) | (8 << 21) | 0xFFFF,  # ORI
            (0x0E << 26) | (8 << 21) | 0xFFFF,  # XORI
        ]

        for instrucao in instrucoes:
            registradores = self.executar_instrucao(
                instrucao,
                {8: 0xFFFFFFFF},
            )

            self.assertEqual(registradores[0], 0)

    def test_logicas_imediatas_alteram_apenas_rt(self):
        instrucoes = [
            (0x0C << 26) | (8 << 21) | (9 << 16) | 0x00FF,  # ANDI
            (0x0D << 26) | (8 << 21) | (9 << 16) | 0x00FF,  # ORI
            (0x0E << 26) | (8 << 21) | (9 << 16) | 0x00FF,  # XORI
        ]

        for instrucao in instrucoes:
            registradores = self.executar_instrucao(
                instrucao,
                {8: 0x12345678, 9: 0xAAAAAAAA, 10: 0x55555555},
            )

            self.assertEqual(registradores[8], 0x12345678)
            self.assertEqual(registradores[10], 0x55555555)

    def test_lui_na_execucao_integrada(self):
        instrucao = (0x0F << 26) | (9 << 16) | 0xABCD

        registradores = self.executar_instrucao(instrucao, {})

        self.assertEqual(registradores[9], 0xABCD0000)

    def test_lui_preserva_registrador_zero(self):
        instrucao = (0x0F << 26) | (0 << 16) | 0xABCD

        registradores = self.executar_instrucao(instrucao, {})

        self.assertEqual(registradores[0], 0)

    def test_lui_altera_apenas_registrador_destino(self):
        instrucao = (0x0F << 26) | (9 << 16) | 0xABCD

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12345678, 10: 0x55555555},
        )

        self.assertEqual(registradores[9], 0xABCD0000)
        self.assertEqual(registradores[8], 0x12345678)
        self.assertEqual(registradores[10], 0x55555555)

    def test_addiu_imediato_negativo_na_execucao(self):
        instrucao = (
            (0x09 << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 10},
        )

        self.assertEqual(registradores[9], 9)

    def test_addiu_limita_resultado_a_32_bits(self):
        instrucao = (
            (0x09 << 26)
            | (8 << 21)
            | (9 << 16)
            | 1
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[9], 0)

    def test_addiu_produz_resultado_negativo(self):
        instrucao = (
            (0x09 << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0},
        )

        self.assertEqual(registradores[9], 0xFFFFFFFF)

    def test_addi_imediato_negativo_na_execucao(self):
        instrucao = (
            (0x08 << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 10},
        )

        self.assertEqual(registradores[9], 9)

    def test_addi_gera_overflow_negativo_na_execucao(self):
        instrucao = (
            (0x08 << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        with self.assertRaises(IntegerOverflow):
            self.executar_instrucao(
                instrucao,
                {8: 0x80000000},
            )

    def test_addi_atinge_limite_inferior_sem_overflow(self):
        instrucao = (
            (0x08 << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x80000001},
        )

        self.assertEqual(registradores[9], 0x80000000)

    def test_addiu_ultrapassa_limite_inferior_sem_excecao(self):
        instrucao = (
            (0x09 << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x80000000},
        )

        self.assertEqual(registradores[9], 0x7FFFFFFF)

    def test_slti_com_imediato_negativo_na_execucao(self):
        instrucao = (
            (0x0A << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[9], 0)

    def test_slti_e_sltiu_com_registrador_negativo(self):
        instrucao_slti = (
            (0x0A << 26)
            | (8 << 21)
            | (9 << 16)
            | 1
        )

        instrucao_sltiu = (
            (0x0B << 26)
            | (8 << 21)
            | (9 << 16)
            | 1
        )

        registradores_slti = self.executar_instrucao(
            instrucao_slti,
            {8: 0xFFFFFFFF},
        )

        registradores_sltiu = self.executar_instrucao(
            instrucao_sltiu,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores_slti[9], 1)
        self.assertEqual(registradores_sltiu[9], 0)

    def test_sltiu_imediato_negativo_com_valor_zero(self):
        instrucao = (
            (0x0B << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0},
        )

        self.assertEqual(registradores[9], 1)

    def test_sltiu_com_operandos_iguais(self):
        instrucao = (
            (0x0B << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[9], 0)

    def test_slti_com_menor_inteiro_com_sinal(self):
        instrucao = (
            (0x0A << 26)
            | (8 << 21)
            | (9 << 16)
            | 1
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x80000000},
        )

        self.assertEqual(registradores[9], 1)

    def test_slti_com_maior_inteiro_positivo(self):
        instrucao = (
            (0x0A << 26)
            | (8 << 21)
            | (9 << 16)
            | 1
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x7FFFFFFF},
        )

        self.assertEqual(registradores[9], 0)

    def test_sltiu_com_maior_inteiro_positivo(self):
        instrucao = (
            (0x0B << 26)
            | (8 << 21)
            | (9 << 16)
            | 1
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x7FFFFFFF},
        )

        self.assertEqual(registradores[9], 0)

    def test_andi_com_imediato_zero(self):
        instrucao = (
            (0x0C << 26)
            | (8 << 21)
            | (9 << 16)
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[9], 0)

    def test_ori_com_imediato_zero(self):
        instrucao = (
            (0x0D << 26)
            | (8 << 21)
            | (9 << 16)
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12345678},
        )

        self.assertEqual(registradores[9], 0x12345678)

    def test_xori_com_imediato_zero(self):
        instrucao = (
            (0x0E << 26)
            | (8 << 21)
            | (9 << 16)
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12345678},
        )

        self.assertEqual(registradores[9], 0x12345678)

    def test_andi_com_imediato_todos_os_bits_ativos(self):
        instrucao = (
            (0x0C << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12345678},
        )

        self.assertEqual(registradores[9], 0x00005678)

    def test_ori_com_imediato_todos_os_bits_ativos(self):
        instrucao = (
            (0x0D << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12340000},
        )

        self.assertEqual(registradores[9], 0x1234FFFF)

    def test_xori_com_imediato_todos_os_bits_ativos(self):
        instrucao = (
            (0x0E << 26)
            | (8 << 21)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12345678},
        )

        self.assertEqual(registradores[9], 0x1234A987)

    def test_andi_com_mascara_seletiva(self):
        instrucao = (
            (0x0C << 26)
            | (8 << 21)
            | (9 << 16)
            | 0x0F0F
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12345678},
        )

        self.assertEqual(registradores[9], 0x00000608)

    def test_ori_com_mascara_seletiva(self):
        instrucao = (
            (0x0D << 26)
            | (8 << 21)
            | (9 << 16)
            | 0x0F0F
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12340000},
        )

        self.assertEqual(registradores[9], 0x12340F0F)

    def test_xori_com_mascara_seletiva(self):
        instrucao = (
            (0x0E << 26)
            | (8 << 21)
            | (9 << 16)
            | 0x0F0F
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12345678},
        )

        self.assertEqual(registradores[9], 0x12345977)

    def test_lui_com_imediato_zero(self):
        instrucao = (
            (0x0F << 26)
            | (9 << 16)
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0x12345678},
        )

        self.assertEqual(registradores[9], 0)
        self.assertEqual(registradores[8], 0x12345678)

    def test_lui_com_imediato_maximo(self):
        instrucao = (
            (0x0F << 26)
            | (9 << 16)
            | 0xFFFF
        )

        registradores = self.executar_instrucao(
            instrucao,
            {},
        )

        self.assertEqual(registradores[9], 0xFFFF0000)

    def test_addi_com_imediato_zero(self):
        instrucao = (
            (0x08 << 26)
            | (8 << 21)
            | (9 << 16)
        )

        registradores = self.executar_instrucao(
            instrucao,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[9], 0xFFFFFFFF)

    def test_calcular_endereco_efetivo_com_alinhamento_de_byte(self):
        endereco = calcular_endereco_efetivo(
            0x1000, 1, "LB", alinhamento=1
        )
        self.assertEqual(endereco, 0x1001)


    def test_calcular_endereco_efetivo_com_alinhamento_de_meia_palavra(self):
        endereco = calcular_endereco_efetivo(
            0x1000, 2, "LH", alinhamento=2
        )
        self.assertEqual(endereco, 0x1002)


    def test_calcular_endereco_efetivo_rejeita_meia_palavra_desalinhada(self):
        with self.assertRaises(EnderecoDesalinhadoError):
            calcular_endereco_efetivo(
                0x1000, 1, "LH", alinhamento=2
            )

    def test_calcular_endereco_efetivo_com_wraparound(self):
        endereco = calcular_endereco_efetivo(
            0xFFFFFFFF,
            1,
            "LB",
            alinhamento=1,
        )

        self.assertEqual(endereco, 0x00000000)

    def test_calcular_endereco_efetivo_com_wraparound_alinhado(self):
        endereco = calcular_endereco_efetivo(
            0xFFFFFFFF,
            1,
            "LH",
            alinhamento=2,
        )

        self.assertEqual(endereco, 0x00000000)

    def test_mfhi_copia_hi_para_rd(self):
        memoria = RAM()
        pc = 0x1000
        rd = 8
        instrucao = (rd << 11) | 0x10  # MFHI

        memoria.write_u32(pc, instrucao)
        registradores = [0] * 32
        estado_especial = EstadoEspecial()
        estado_especial.hi = 0x12345678

        executar_programa(
            memoria,
            {pc},
            pc,
            registradores,
            limite=1,
            estado_especial=estado_especial,
        )

        self.assertEqual(registradores[rd], 0x12345678)


    def test_mflo_copia_lo_para_rd(self):
        memoria = RAM()
        pc = 0x1000
        rd = 8
        instrucao = (rd << 11) | 0x12  # MFLO

        memoria.write_u32(pc, instrucao)
        registradores = [0] * 32
        estado_especial = EstadoEspecial()
        estado_especial.lo = 0x87654321

        executar_programa(
            memoria,
            {pc},
            pc,
            registradores,
            limite=1,
            estado_especial=estado_especial,
        )

        self.assertEqual(registradores[rd], 0x87654321)

    def test_mfhi_preserva_zero(self):
        memoria = RAM()
        pc = 0x1000
        instrucao = 0x10  # MFHI com rd = 0

        memoria.write_u32(pc, instrucao)
        registradores = [0] * 32
        estado_especial = EstadoEspecial()
        estado_especial.hi = 0x12345678

        executar_programa(
            memoria,
            {pc},
            pc,
            registradores,
            limite=1,
            estado_especial=estado_especial,
        )

        self.assertEqual(registradores[0], 0)


    def test_mflo_preserva_zero(self):
        memoria = RAM()
        pc = 0x1000
        instrucao = 0x12  # MFLO com rd = 0

        memoria.write_u32(pc, instrucao)
        registradores = [0] * 32
        estado_especial = EstadoEspecial()
        estado_especial.lo = 0x87654321

        executar_programa(
            memoria,
            {pc},
            pc,
            registradores,
            limite=1,
            estado_especial=estado_especial,
        )

        self.assertEqual(registradores[0], 0)

    def test_mult_seguido_de_mfhi(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd = 10

        # MULT $t0, $t1
        instrucao_mult = (rs << 21) | (rt << 16) | 0x18

        # MFHI $t2
        instrucao_mfhi = (rd << 11) | 0x10

        memoria.write_u32(pc, instrucao_mult)
        memoria.write_u32(pc + 4, instrucao_mfhi)

        registradores = [0] * 32
        registradores[rs] = 0x7FFFFFFF
        registradores[rt] = 2

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4},
            pc,
            registradores,
            limite=2,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 0)
        self.assertEqual(estado_especial.lo, 0xFFFFFFFE)
        self.assertEqual(registradores[rd], 0)

    def test_mult_seguido_de_mflo(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd = 10

        # MULT $t0, $t1
        instrucao_mult = (rs << 21) | (rt << 16) | 0x18

        # MFLO $t2
        instrucao_mflo = (rd << 11) | 0x12

        memoria.write_u32(pc, instrucao_mult)
        memoria.write_u32(pc + 4, instrucao_mflo)

        registradores = [0] * 32
        registradores[rs] = 0x7FFFFFFF
        registradores[rt] = 2

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4},
            pc,
            registradores,
            limite=2,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 0)
        self.assertEqual(estado_especial.lo, 0xFFFFFFFE)
        self.assertEqual(registradores[rd], 0xFFFFFFFE)

    def test_div_seguido_de_mfhi_e_mflo(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_hi = 10
        rd_lo = 11

        # DIV $t0, $t1
        instrucao_div = (rs << 21) | (rt << 16) | 0x1A

        # MFHI $t2
        instrucao_mfhi = (rd_hi << 11) | 0x10

        # MFLO $t3
        instrucao_mflo = (rd_lo << 11) | 0x12

        memoria.write_u32(pc, instrucao_div)
        memoria.write_u32(pc + 4, instrucao_mfhi)
        memoria.write_u32(pc + 8, instrucao_mflo)

        registradores = [0] * 32
        registradores[rs] = 17
        registradores[rt] = 5

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 2)
        self.assertEqual(estado_especial.lo, 3)
        self.assertEqual(registradores[rd_hi], 2)
        self.assertEqual(registradores[rd_lo], 3)

    def test_div_negativo_seguido_de_mfhi_e_mflo(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_hi = 10
        rd_lo = 11

        # DIV $t0, $t1
        instrucao_div = (rs << 21) | (rt << 16) | 0x1A

        # MFHI $t2
        instrucao_mfhi = (rd_hi << 11) | 0x10

        # MFLO $t3
        instrucao_mflo = (rd_lo << 11) | 0x12

        memoria.write_u32(pc, instrucao_div)
        memoria.write_u32(pc + 4, instrucao_mfhi)
        memoria.write_u32(pc + 8, instrucao_mflo)

        registradores = [0] * 32
        registradores[rs] = (-17) & 0xFFFFFFFF
        registradores[rt] = 5

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 0xFFFFFFFE)
        self.assertEqual(estado_especial.lo, 0xFFFFFFFD)
        self.assertEqual(registradores[rd_hi], 0xFFFFFFFE)
        self.assertEqual(registradores[rd_lo], 0xFFFFFFFD)

    def test_div_divisor_negativo_seguido_de_mfhi_e_mflo(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_hi = 10
        rd_lo = 11

        # DIV $t0, $t1
        instrucao_div = (rs << 21) | (rt << 16) | 0x1A

        # MFHI $t2
        instrucao_mfhi = (rd_hi << 11) | 0x10

        # MFLO $t3
        instrucao_mflo = (rd_lo << 11) | 0x12

        memoria.write_u32(pc, instrucao_div)
        memoria.write_u32(pc + 4, instrucao_mfhi)
        memoria.write_u32(pc + 8, instrucao_mflo)

        registradores = [0] * 32
        registradores[rs] = 17
        registradores[rt] = (-5) & 0xFFFFFFFF

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 2)
        self.assertEqual(estado_especial.lo, 0xFFFFFFFD)
        self.assertEqual(registradores[rd_hi], 2)
        self.assertEqual(registradores[rd_lo], 0xFFFFFFFD)

    def test_div_ambos_operandos_negativos_seguido_de_mfhi_e_mflo(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_hi = 10
        rd_lo = 11

        # DIV $t0, $t1
        instrucao_div = (rs << 21) | (rt << 16) | 0x1A

        # MFHI $t2
        instrucao_mfhi = (rd_hi << 11) | 0x10

        # MFLO $t3
        instrucao_mflo = (rd_lo << 11) | 0x12

        memoria.write_u32(pc, instrucao_div)
        memoria.write_u32(pc + 4, instrucao_mfhi)
        memoria.write_u32(pc + 8, instrucao_mflo)

        registradores = [0] * 32
        registradores[rs] = (-17) & 0xFFFFFFFF
        registradores[rt] = (-5) & 0xFFFFFFFF

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 0xFFFFFFFE)
        self.assertEqual(estado_especial.lo, 3)
        self.assertEqual(registradores[rd_hi], 0xFFFFFFFE)
        self.assertEqual(registradores[rd_lo], 3)

    def test_helper_div_por_zero_com_dividendo_positivo(self):
        hi, lo = executar_divisao(0x1A, 17, 0)

        self.assertEqual(hi, 17)
        self.assertEqual(lo, 0xFFFFFFFF)

    def test_helper_div_por_zero_com_dividendo_negativo(self):
        dividendo = (-17) & 0xFFFFFFFF

        hi, lo = executar_divisao(0x1A, dividendo, 0)

        self.assertEqual(hi, 0xFFFFFFEF)
        self.assertEqual(lo, 0x00000001)

    def test_helper_divu_por_zero(self):
        hi, lo = executar_divisao(0x1B, 17, 0)

        self.assertEqual(hi, 17)
        self.assertEqual(lo, 0xFFFFFFFF)

    def test_div_por_zero_seguido_de_mfhi_e_mflo(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_hi = 10
        rd_lo = 11

        # DIV $t0, $t1
        instrucao_div = (rs << 21) | (rt << 16) | 0x1A

        # MFHI $t2
        instrucao_mfhi = (rd_hi << 11) | 0x10

        # MFLO $t3
        instrucao_mflo = (rd_lo << 11) | 0x12

        memoria.write_u32(pc, instrucao_div)
        memoria.write_u32(pc + 4, instrucao_mfhi)
        memoria.write_u32(pc + 8, instrucao_mflo)

        registradores = [0] * 32
        registradores[rs] = 17
        registradores[rt] = 0

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 17)
        self.assertEqual(estado_especial.lo, 0xFFFFFFFF)
        self.assertEqual(registradores[rd_hi], 17)
        self.assertEqual(registradores[rd_lo], 0xFFFFFFFF)

    def test_divu_por_zero_seguido_de_mfhi_e_mflo(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_hi = 10
        rd_lo = 11

        # DIVU $t0, $t1
        instrucao_divu = (rs << 21) | (rt << 16) | 0x1B

        # MFHI $t2
        instrucao_mfhi = (rd_hi << 11) | 0x10

        # MFLO $t3
        instrucao_mflo = (rd_lo << 11) | 0x12

        memoria.write_u32(pc, instrucao_divu)
        memoria.write_u32(pc + 4, instrucao_mfhi)
        memoria.write_u32(pc + 8, instrucao_mflo)

        registradores = [0] * 32
        registradores[rs] = 17
        registradores[rt] = 0

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 17)
        self.assertEqual(estado_especial.lo, 0xFFFFFFFF)
        self.assertEqual(registradores[rd_hi], 17)
        self.assertEqual(registradores[rd_lo], 0xFFFFFFFF)

    def test_div_menor_inteiro_por_menos_um(self):
        dividendo = 0x80000000
        divisor = 0xFFFFFFFF

        hi, lo = executar_divisao(0x1A, dividendo, divisor)

        self.assertEqual(hi, 0)
        self.assertEqual(lo, 0x80000000)

    def test_divu_maior_inteiro_por_dois(self):
        dividendo = 0xFFFFFFFF
        divisor = 2

        hi, lo = executar_divisao(0x1B, dividendo, divisor)

        self.assertEqual(hi, 1)
        self.assertEqual(lo, 0x7FFFFFFF)

    def test_mthi_copia_rs_para_hi(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8

        # MTHI $t0
        instrucao = (rs << 21) | 0x11

        memoria.write_u32(pc, instrucao)

        registradores = [0] * 32
        registradores[rs] = 0x12345678

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc},
            pc,
            registradores,
            limite=1,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 0x12345678)

    def test_mtlo_copia_rs_para_lo(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8

        # MTLO $t0
        instrucao = (rs << 21) | 0x13

        memoria.write_u32(pc, instrucao)

        registradores = [0] * 32
        registradores[rs] = 0x87654321

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc},
            pc,
            registradores,
            limite=1,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.lo, 0x87654321)

    def test_mthi_mtlo_seguidos_de_mfhi_mflo(self):
        memoria = RAM()
        pc = 0x1000

        rs_hi = 8
        rs_lo = 9
        rd_hi = 10
        rd_lo = 11

        # MTHI $t0
        instrucao_mthi = (rs_hi << 21) | 0x11

        # MTLO $t1
        instrucao_mtlo = (rs_lo << 21) | 0x13

        # MFHI $t2
        instrucao_mfhi = (rd_hi << 11) | 0x10

        # MFLO $t3
        instrucao_mflo = (rd_lo << 11) | 0x12

        instrucoes = [
            instrucao_mthi,
            instrucao_mtlo,
            instrucao_mfhi,
            instrucao_mflo,
        ]

        for indice, instrucao in enumerate(instrucoes):
            memoria.write_u32(pc + indice * 4, instrucao)

        registradores = [0] * 32
        registradores[rs_hi] = 0x12345678
        registradores[rs_lo] = 0x87654321

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8, pc + 12},
            pc,
            registradores,
            limite=4,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 0x12345678)
        self.assertEqual(estado_especial.lo, 0x87654321)
        self.assertEqual(registradores[rd_hi], 0x12345678)
        self.assertEqual(registradores[rd_lo], 0x87654321)

    def test_mult_seguido_de_mfhi_mflo(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8   # $t0
        rt = 9   # $t1
        rd_hi = 10  # $t2
        rd_lo = 11  # $t3

        # MULT $t0, $t1
        instrucao_mult = (rs << 21) | (rt << 16) | 0x18

        # MFHI $t2
        instrucao_mfhi = (rd_hi << 11) | 0x10

        # MFLO $t3
        instrucao_mflo = (rd_lo << 11) | 0x12

        instrucoes = [
            instrucao_mult,
            instrucao_mfhi,
            instrucao_mflo,
        ]

        for indice, instrucao in enumerate(instrucoes):
            memoria.write_u32(pc + indice * 4, instrucao)

        registradores = [0] * 32
        registradores[rs] = 0xFFFFFFFF  # -1 em 32 bits
        registradores[rt] = 2

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 0xFFFFFFFF)
        self.assertEqual(estado_especial.lo, 0xFFFFFFFE)
        self.assertEqual(registradores[rd_hi], 0xFFFFFFFF)
        self.assertEqual(registradores[rd_lo], 0xFFFFFFFE)

    def test_multu_seguido_de_mfhi_mflo(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_hi = 10
        rd_lo = 11

        # MULTU $t0, $t1
        instrucao_multu = (rs << 21) | (rt << 16) | 0x19

        # MFHI $t2
        instrucao_mfhi = (rd_hi << 11) | 0x10

        # MFLO $t3
        instrucao_mflo = (rd_lo << 11) | 0x12

        instrucoes = [
            instrucao_multu,
            instrucao_mfhi,
            instrucao_mflo,
        ]

        for indice, instrucao in enumerate(instrucoes):
            memoria.write_u32(pc + indice * 4, instrucao)

        registradores = [0] * 32
        registradores[rs] = 0xFFFFFFFF
        registradores[rt] = 2

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.hi, 1)
        self.assertEqual(estado_especial.lo, 0xFFFFFFFE)
        self.assertEqual(registradores[rd_hi], 1)
        self.assertEqual(registradores[rd_lo], 0xFFFFFFFE)

    def test_div_seguido_de_mflo_mfhi(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_lo = 10
        rd_hi = 11

        # DIV $t0, $t1
        instrucao_div = (rs << 21) | (rt << 16) | 0x1A

        # MFLO $t2
        instrucao_mflo = (rd_lo << 11) | 0x12

        # MFHI $t3
        instrucao_mfhi = (rd_hi << 11) | 0x10

        instrucoes = [
            instrucao_div,
            instrucao_mflo,
            instrucao_mfhi,
        ]

        for indice, instrucao in enumerate(instrucoes):
            memoria.write_u32(pc + indice * 4, instrucao)

        registradores = [0] * 32
        registradores[rs] = 17
        registradores[rt] = 5

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.lo, 3)
        self.assertEqual(estado_especial.hi, 2)
        self.assertEqual(registradores[rd_lo], 3)
        self.assertEqual(registradores[rd_hi], 2)

    def test_div_negativo_seguido_de_mflo_mfhi(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_lo = 10
        rd_hi = 11

        # DIV $t0, $t1
        instrucao_div = (rs << 21) | (rt << 16) | 0x1A

        # MFLO $t2
        instrucao_mflo = (rd_lo << 11) | 0x12

        # MFHI $t3
        instrucao_mfhi = (rd_hi << 11) | 0x10

        instrucoes = [
            instrucao_div,
            instrucao_mflo,
            instrucao_mfhi,
        ]

        for indice, instrucao in enumerate(instrucoes):
            memoria.write_u32(pc + indice * 4, instrucao)

        registradores = [0] * 32
        registradores[rs] = (-17) & 0xFFFFFFFF
        registradores[rt] = 5

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.lo, 0xFFFFFFFD)  # -3
        self.assertEqual(estado_especial.hi, 0xFFFFFFFE)  # -2
        self.assertEqual(registradores[rd_lo], 0xFFFFFFFD)
        self.assertEqual(registradores[rd_hi], 0xFFFFFFFE)

    def test_divu_seguido_de_mflo_mfhi(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_lo = 10
        rd_hi = 11

        # DIVU $t0, $t1
        instrucao_divu = (rs << 21) | (rt << 16) | 0x1B

        # MFLO $t2
        instrucao_mflo = (rd_lo << 11) | 0x12

        # MFHI $t3
        instrucao_mfhi = (rd_hi << 11) | 0x10

        instrucoes = [
            instrucao_divu,
            instrucao_mflo,
            instrucao_mfhi,
        ]

        for indice, instrucao in enumerate(instrucoes):
            memoria.write_u32(pc + indice * 4, instrucao)

        registradores = [0] * 32
        registradores[rs] = 0xFFFFFFFF
        registradores[rt] = 2

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.lo, 0x7FFFFFFF)
        self.assertEqual(estado_especial.hi, 1)
        self.assertEqual(registradores[rd_lo], 0x7FFFFFFF)
        self.assertEqual(registradores[rd_hi], 1)

    def test_div_por_zero_seguido_de_mflo_mfhi(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_lo = 10
        rd_hi = 11

        # DIV $t0, $t1
        instrucao_div = (rs << 21) | (rt << 16) | 0x1A

        # MFLO $t2
        instrucao_mflo = (rd_lo << 11) | 0x12

        # MFHI $t3
        instrucao_mfhi = (rd_hi << 11) | 0x10

        instrucoes = [
            instrucao_div,
            instrucao_mflo,
            instrucao_mfhi,
        ]

        for indice, instrucao in enumerate(instrucoes):
            memoria.write_u32(pc + indice * 4, instrucao)

        registradores = [0] * 32
        registradores[rs] = 17
        registradores[rt] = 0

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.lo, 0xFFFFFFFF)
        self.assertEqual(estado_especial.hi, 17)
        self.assertEqual(registradores[rd_lo], 0xFFFFFFFF)
        self.assertEqual(registradores[rd_hi], 17)

    def test_div_negativo_por_zero_seguido_de_mflo_mfhi(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_lo = 10
        rd_hi = 11

        # DIV $t0, $t1
        instrucao_div = (rs << 21) | (rt << 16) | 0x1A

        # MFLO $t2
        instrucao_mflo = (rd_lo << 11) | 0x12

        # MFHI $t3
        instrucao_mfhi = (rd_hi << 11) | 0x10

        instrucoes = [
            instrucao_div,
            instrucao_mflo,
            instrucao_mfhi,
        ]

        for indice, instrucao in enumerate(instrucoes):
            memoria.write_u32(pc + indice * 4, instrucao)

        registradores = [0] * 32
        registradores[rs] = 0xFFFFFFFF  # -1 em 32 bits
        registradores[rt] = 0

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.lo, 0x00000001)
        self.assertEqual(estado_especial.hi, 0xFFFFFFFF)
        self.assertEqual(registradores[rd_lo], 0x00000001)
        self.assertEqual(registradores[rd_hi], 0xFFFFFFFF)

    def test_divu_por_zero_seguido_de_mflo_mfhi(self):
        memoria = RAM()
        pc = 0x1000

        rs = 8
        rt = 9
        rd_lo = 10
        rd_hi = 11

        # DIVU $t0, $t1
        instrucao_divu = (rs << 21) | (rt << 16) | 0x1B

        # MFLO $t2
        instrucao_mflo = (rd_lo << 11) | 0x12

        # MFHI $t3
        instrucao_mfhi = (rd_hi << 11) | 0x10

        instrucoes = [
            instrucao_divu,
            instrucao_mflo,
            instrucao_mfhi,
        ]

        for indice, instrucao in enumerate(instrucoes):
            memoria.write_u32(pc + indice * 4, instrucao)

        registradores = [0] * 32
        registradores[rs] = 17
        registradores[rt] = 0

        estado_especial = EstadoEspecial()

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8},
            pc,
            registradores,
            limite=3,
            estado_especial=estado_especial,
        )

        self.assertEqual(estado_especial.lo, 0xFFFFFFFF)
        self.assertEqual(estado_especial.hi, 17)
        self.assertEqual(registradores[rd_lo], 0xFFFFFFFF)
        self.assertEqual(registradores[rd_hi], 17)

    def test_j_executa_instrucao_no_delay_slot(self):
        memoria = RAM()
        pc = 0x1000
        destino = 0x1020

        # J destino
        instrucao_j = 0x08000000 | ((destino >> 2) & 0x03FFFFFF)

        # ADDIU $t0, $zero, 42 — delay slot
        instrucao_delay = (0x09 << 26) | (8 << 16) | 42

        # ADDIU $t1, $zero, 99 — destino do salto
        instrucao_destino = (0x09 << 26) | (9 << 16) | 99

        memoria.write_u32(pc, instrucao_j)
        memoria.write_u32(pc + 4, instrucao_delay)
        memoria.write_u32(destino, instrucao_destino)

        registradores = [0] * 32

        executar_programa(
            memoria,
            {pc, pc + 4, destino},
            pc,
            registradores,
            limite=3,
        )

        self.assertEqual(registradores[8], 42)
        self.assertEqual(registradores[9], 99)

    def test_beq_executa_instrucao_no_delay_slot(self):
        memoria = RAM()
        pc = 0x1000

        # BEQ $t0, $t1, destino
        # O destino fica em pc + 4 + (offset << 2).
        offset = 3
        instrucao_beq = (
            (0x04 << 26)
            | (8 << 21)
            | (9 << 16)
            | offset
        )

        # ADDIU $t2, $zero, 42 — delay slot
        instrucao_delay = (0x09 << 26) | (10 << 16) | 42

        # ADDIU $t3, $zero, 99 — destino do desvio
        instrucao_destino = (0x09 << 26) | (11 << 16) | 99

        destino = pc + 4 + (offset << 2)

        memoria.write_u32(pc, instrucao_beq)
        memoria.write_u32(pc + 4, instrucao_delay)
        memoria.write_u32(destino, instrucao_destino)

        registradores = [0] * 32
        registradores[8] = 7
        registradores[9] = 7

        executar_programa(
            memoria,
            {pc, pc + 4, destino},
            pc,
            registradores,
            limite=3,
        )

        self.assertEqual(registradores[10], 42)
        self.assertEqual(registradores[11], 99)

    def test_beq_nao_tomado_executa_delay_slot(self):
        memoria = RAM()
        pc = 0x1000

        # BEQ $t0, $t1, destino
        offset = 3
        instrucao_beq = (
            (0x04 << 26)
            | (8 << 21)
            | (9 << 16)
            | offset
        )

        # ADDIU $t2, $zero, 42 — delay slot
        instrucao_delay = (0x09 << 26) | (10 << 16) | 42

        # ADDIU $t3, $zero, 99 — caminho sequencial
        instrucao_sequencial = (0x09 << 26) | (11 << 16) | 99

        destino = pc + 4 + (offset << 2)

        memoria.write_u32(pc, instrucao_beq)
        memoria.write_u32(pc + 4, instrucao_delay)
        memoria.write_u32(pc + 8, instrucao_sequencial)
        memoria.write_u32(destino, 0)

        registradores = [0] * 32
        registradores[8] = 7
        registradores[9] = 8

        executar_programa(
            memoria,
            {pc, pc + 4, pc + 8, destino},
            pc,
            registradores,
            limite=3,
        )

        self.assertEqual(registradores[10], 42)
        self.assertEqual(registradores[11], 99)

    def test_sllv(self):
        # SLLV: deslocamento à esquerda
        instrucao = (8 << 21) | (9 << 16) | (10 << 11) | 0x04

        registradores = self.executar_instrucao(
            instrucao,
            {
                8: 2,  # rs: quantidade de deslocamento
                9: 3,  # rt: valor a deslocar
            },
        )

        self.assertEqual(registradores[10], 12)


    def test_srlv(self):
        # SRLV: deslocamento lógico à direita
        instrucao = (8 << 21) | (9 << 16) | (10 << 11) | 0x06

        registradores = self.executar_instrucao(
            instrucao,
            {
                8: 2,
                9: 16,
            },
        )

        self.assertEqual(registradores[10], 4)


    def test_srav(self):
        # SRAV: deslocamento aritmético à direita
        instrucao = (8 << 21) | (9 << 16) | (10 << 11) | 0x07

        registradores = self.executar_instrucao(
            instrucao,
            {
                8: 2,
                9: 0xFFFFFFF0,  # -16 em complemento de dois
            },
        )

        self.assertEqual(registradores[10], 0xFFFFFFFC)

    def test_lwl_alinhamento_zero(self):
        resultado = executar_lwl_lwr(
            0x22, 0xAABBCCDD, 0x11223344, 0
        )
        self.assertEqual(resultado, 0x44BBCCDD)


    def test_lwl_alinhamento_tres(self):
        resultado = executar_lwl_lwr(
            0x22, 0xAABBCCDD, 0x11223344, 3
        )
        self.assertEqual(resultado, 0x11223344)


    def test_lwr_alinhamento_zero(self):
        resultado = executar_lwl_lwr(
            0x26, 0xAABBCCDD, 0x11223344, 0
        )
        self.assertEqual(resultado, 0x11223344)


    def test_lwr_alinhamento_tres(self):
        resultado = executar_lwl_lwr(
            0x26, 0xAABBCCDD, 0x11223344, 3
        )
        self.assertEqual(resultado, 0xAABBCC11)

    def test_lwl_alinhamento_um(self):
        resultado = executar_lwl_lwr(
            0x22, 0xAABBCCDD, 0x11223344, 1
        )
        self.assertEqual(resultado, 0x3344CCDD)


    def test_lwl_alinhamento_dois(self):
        resultado = executar_lwl_lwr(
            0x22, 0xAABBCCDD, 0x11223344, 2
        )
        self.assertEqual(resultado, 0x223344DD)


    def test_lwr_alinhamento_um(self):
        resultado = executar_lwl_lwr(
            0x26, 0xAABBCCDD, 0x11223344, 1
        )
        self.assertEqual(resultado, 0xAA112233)


    def test_lwr_alinhamento_dois(self):
        resultado = executar_lwl_lwr(
            0x26, 0xAABBCCDD, 0x11223344, 2
        )
        self.assertEqual(resultado, 0xAABB1122)

    def test_lwl_integrado_memoria(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        # Registrador base aponta para os dados.
        registradores[1] = endereco_dados

        # Valor inicial do registrador de destino.
        registradores[2] = 0xAABBCCDD

        # Palavra armazenada em memória.
        memoria.write_u32(endereco_dados, 0x11223344)

        # LWL rt=2, offset=0(rs=1)
        instrucao = (
            (0x22 << 26)
            | (1 << 21)
            | (2 << 16)
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0x44BBCCDD)

    def test_lwr_integrado_memoria(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # LWR rt=2, offset=0(rs=1)
        instrucao = (
            (0x26 << 26)
            | (1 << 21)
            | (2 << 16)
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0x11223344)

    def test_lwl_integrado_deslocamento_um(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # LWL rt=2, offset=1(rs=1)
        instrucao = (
            (0x22 << 26)
            | (1 << 21)
            | (2 << 16)
            | 1
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0x3344CCDD)

    def test_lwr_integrado_deslocamento_um(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # LWR rt=2, offset=1(rs=1)
        instrucao = (
            (0x26 << 26)
            | (1 << 21)
            | (2 << 16)
            | 1
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0xAA112233)
    

    def test_lwl_integrado_deslocamento_dois(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # LWL rt=2, offset=2(rs=1)
        instrucao = (
            (0x22 << 26)
            | (1 << 21)
            | (2 << 16)
            | 2
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0x223344DD)

    def test_lwr_integrado_deslocamento_dois(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # LWR rt=2, offset=2(rs=1)
        instrucao = (
            (0x26 << 26)
            | (1 << 21)
            | (2 << 16)
            | 2
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0xAABB1122)

    def test_lwl_integrado_deslocamento_tres(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # LWL rt=2, offset=3(rs=1)
        instrucao = (
            (0x22 << 26)
            | (1 << 21)
            | (2 << 16)
            | 3
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0x11223344)


    def test_lwr_integrado_deslocamento_tres(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # LWR rt=2, offset=3(rs=1)
        instrucao = (
            (0x26 << 26)
            | (1 << 21)
            | (2 << 16)
            | 3
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(registradores[2], 0xAABBCC11)

    def test_lwl_lwr_combinados(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_programa = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0

        memoria.write_u32(endereco_dados, 0x11223344)
        memoria.write_u32(endereco_dados + 4, 0x55667788)

        # LWR rt=2, 1(rs=1)
        lwr = (
            (0x26 << 26)
            | (1 << 21)
            | (2 << 16)
            | 1
        )

        # LWL rt=2, 4(rs=1)
        lwl = (
            (0x22 << 26)
            | (1 << 21)
            | (2 << 16)
            | 4
        )

        memoria.write_u32(endereco_programa, lwr)
        memoria.write_u32(endereco_programa + 4, lwl)

        executar_programa(
            memoria,
            {endereco_programa, endereco_programa + 4},
            endereco_programa,
            registradores,
            limite=2,
        )

        self.assertEqual(registradores[2], 0x88112233)

    def test_swl_alinhamento_zero(self):
        resultado = executar_swl_swr(
            0x2A, 0xAABBCCDD, 0x11223344, 0
        )
        self.assertEqual(resultado, 0x112233AA)


    def test_swl_alinhamento_tres(self):
        resultado = executar_swl_swr(
            0x2A, 0xAABBCCDD, 0x11223344, 3
        )
        self.assertEqual(resultado, 0xAABBCCDD)


    def test_swr_alinhamento_zero(self):
        resultado = executar_swl_swr(
            0x2E, 0xAABBCCDD, 0x11223344, 0
        )
        self.assertEqual(resultado, 0xAABBCCDD)


    def test_swr_alinhamento_tres(self):
        resultado = executar_swl_swr(
            0x2E, 0xAABBCCDD, 0x11223344, 3
        )
        self.assertEqual(resultado, 0xDD223344)

    def test_swl_alinhamento_um(self):
        resultado = executar_swl_swr(
            0x2A, 0xAABBCCDD, 0x11223344, 1
        )
        self.assertEqual(resultado, 0x1122AABB)


    def test_swl_alinhamento_dois(self):
        resultado = executar_swl_swr(
            0x2A, 0xAABBCCDD, 0x11223344, 2
        )
        self.assertEqual(resultado, 0x11AABBCC)


    def test_swr_alinhamento_um(self):
        resultado = executar_swl_swr(
            0x2E, 0xAABBCCDD, 0x11223344, 1
        )
        self.assertEqual(resultado, 0xBBCCDD44)


    def test_swr_alinhamento_dois(self):
        resultado = executar_swl_swr(
            0x2E, 0xAABBCCDD, 0x11223344, 2
        )
        self.assertEqual(resultado, 0xCCDD3344)

    def test_swl_integrado_deslocamento_zero(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # SWL rt=2, offset=0(rs=1)
        instrucao = (
            (0x2A << 26)
            | (1 << 21)
            | (2 << 16)
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(
            memoria.read_u32(endereco_dados),
            0x112233AA,
        )

    def test_swr_integrado_deslocamento_zero(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # SWR rt=2, offset=0(rs=1)
        instrucao = (
            (0x2E << 26)
            | (1 << 21)
            | (2 << 16)
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(
            memoria.read_u32(endereco_dados),
            0xAABBCCDD,
        )

    def test_swl_integrado_deslocamento_um(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # SWL rt=2, offset=1(rs=1)
        instrucao = (
            (0x2A << 26)
            | (1 << 21)
            | (2 << 16)
            | 1
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(
            memoria.read_u32(endereco_dados),
            0x1122AABB,
        )

    def test_swr_integrado_deslocamento_um(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # SWR rt=2, offset=1(rs=1)
        instrucao = (
            (0x2E << 26)
            | (1 << 21)
            | (2 << 16)
            | 1
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(
            memoria.read_u32(endereco_dados),
            0xBBCCDD44,
        )

    def test_swl_integrado_deslocamento_dois(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # SWL rt=2, offset=2(rs=1)
        instrucao = (
            (0x2A << 26)
            | (1 << 21)
            | (2 << 16)
            | 2
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(
            memoria.read_u32(endereco_dados),
            0x11AABBCC,
        )

    def test_swr_integrado_deslocamento_dois(self):
        memoria = RAM()
        registradores = [0] * 32

        endereco_instrucao = 0x1000
        endereco_dados = 0x2000

        registradores[1] = endereco_dados
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(endereco_dados, 0x11223344)

        # SWR rt=2, offset=2(rs=1)
        instrucao = (
            (0x2E << 26)
            | (1 << 21)
            | (2 << 16)
            | 2
        )

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        self.assertEqual(
            memoria.read_u32(endereco_dados),
            0xCCDD3344,
        )

    def test_swl_deslocamento_tres(self):
        memoria = RAM()
        registradores = [0] * 32

        registradores[1] = 0x2000
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(0x2000, 0x11223344)

        instrucao = (
            (0x2A << 26)
            | (1 << 21)
            | (2 << 16)
            | 3
        )

        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            pc_inicial=0x1000,
            registradores=registradores,
            limite=1
        )

        self.assertEqual(
            memoria.read_u32(0x2000),
            0xAABBCCDD
        )

    def test_swr_deslocamento_tres(self):
        memoria = RAM()
        registradores = [0] * 32

        registradores[1] = 0x2000
        registradores[2] = 0xAABBCCDD

        memoria.write_u32(0x2000, 0x11223344)

        instrucao = (
            (0x2E << 26)
            | (1 << 21)
            | (2 << 16)
            | 3
        )

        memoria.write_u32(0x1000, instrucao)

        executar_programa(
            memoria,
            {0x1000},
            pc_inicial=0x1000,
            registradores=registradores,
            limite=1
        )

        self.assertEqual(
            memoria.read_u32(0x2000),
            0xDD223344
        )

if __name__ == "__main__":
    unittest.main()
