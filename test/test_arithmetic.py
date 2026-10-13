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

if __name__ == "__main__":
    unittest.main()