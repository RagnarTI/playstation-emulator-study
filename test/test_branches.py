
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
    encode_r,
    executar_programa,
)
from ram import RAM


class MemoriaEsparsa:
    def __init__(self):
        self.palavras = {}

    def write_u32(self, endereco, valor):
        if endereco % 4 != 0:
            raise ValueError(f"Endereco desalinhado: 0x{endereco:08X}")
        self.palavras[endereco] = valor & 0xFFFFFFFF

    def read_u32(self, endereco):
        if endereco % 4 != 0:
            raise ValueError(f"Endereco desalinhado: 0x{endereco:08X}")
        return self.palavras.get(endereco, 0)



class TestBranches(unittest.TestCase):

    
    def executar_programa_teste(
        self, instrucoes, valores, pc_inicial=0x1000, memoria=None
    ):
        if memoria is None:
            memoria = RAM()

        registradores = [0] * 32

        for indice, valor in valores.items():
            registradores[indice] = valor & 0xFFFFFFFF

        for endereco, instrucao in instrucoes.items():
            memoria.write_u32(endereco, instrucao)

        executar_programa(
            memoria,
            set(instrucoes.keys()),
            pc_inicial,
            registradores,
            limite=10,
        )

        return registradores

    def test_beq_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x04, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 20, 9: 20},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_beq_falso(self):
        instrucoes = {
            0x1000: encode_i(0x04, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 20, 9: 30},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)

    def test_delay_slot(self):
        instrucoes = {
            0x1000: encode_i(0x04, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 42),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 5, 9: 5},
        )

        self.assertEqual(registradores[10], 42)
        self.assertEqual(registradores[11], 0)

    def test_jr(self):
        instrucoes = {
            0x1000: encode_r(9, 0, 0, 0x08),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {9: 0x1008},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)
    
    def test_j(self):
        instrucoes = {
            0x1000: (0x02 << 26) | (0x00001008 >> 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_jal(self):
        instrucoes = {
            0x1000: (0x03 << 26) | (0x00001010 >> 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1010: encode_i(0x09, 0, 11, 99),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)

    def test_jal_jr_retorno(self):
        instrucoes = {
            # JAL: chama a função em 0x1020.
            0x1000: (0x03 << 26) | (0x1020 >> 2),

            # Delay slot do JAL.
            0x1004: encode_i(0x09, 0, 10, 1),

            # Continuação do programa após o retorno.
            0x1008: encode_i(0x09, 0, 11, 42),
            0x100C: encode_i(0x09, 0, 12, 7),

            # Corpo da função.
            0x1020: encode_i(0x09, 0, 13, 5),

            # JR $31: retorna para o endereço salvo pelo JAL.
            0x1024: encode_r(31, 0, 0, 0x08),

            # Delay slot do JR.
            0x1028: encode_i(0x09, 0, 14, 2),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 42)
        self.assertEqual(registradores[12], 7)
        self.assertEqual(registradores[13], 5)
        self.assertEqual(registradores[14], 2)

    def test_bne_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x05, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 10, 9: 20},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)


    def test_bne_falso(self):
        instrucoes = {
            0x1000: encode_i(0x05, 8, 9, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 10, 9: 10},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_blez_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)


    def test_blez_falso(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 5},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

        
    def test_bgtz_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 5},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)


    def test_bgtz_falso(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_bltz_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x00, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bltz_falso(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x00, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_bgez_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x01, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgez_falso(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x01, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_bltzal_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x10, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bltzal_falso(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x10, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_bgezal_verdadeiro(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x11, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgezal_falso(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x11, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_blez_rt_invalido(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 1, 2),
        }

        with self.assertRaises(NotImplementedError):
            self.executar_programa_teste(
                instrucoes,
                {8: 0},
            )


    def test_bgtz_rt_invalido(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 1, 2),
        }

        with self.assertRaises(NotImplementedError):
            self.executar_programa_teste(
                instrucoes,
                {8: 1},
            )

    def test_regimm_rt_nao_suportado(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x02, 2),
        }

        with self.assertRaises(NotImplementedError):
            self.executar_programa_teste(
                instrucoes,
                {8: 1},
            )


    def test_regimm_bltz_valido(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x00, 2),
            0x1004: encode_i(0x09, 0, 10, 1),
            0x1008: encode_i(0x09, 0, 11, 99),
            0x100C: encode_i(0x09, 0, 12, 7),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_branch_tomado_executa_uma_vez(self):
        instrucoes = {
            0x1000: encode_i(0x04, 8, 9, 2),   # BEQ
            0x1004: encode_i(0x09, 10, 10, 1), # ADDIU no delay slot
            0x1008: encode_i(0x09, 0, 11, 99), # Deve ser ignorada
            0x100C: encode_i(0x09, 0, 12, 7),  # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 5, 9: 5, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_branch_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x04, 8, 9, 2),   # BEQ: não deve desviar
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99), # Próxima instrução
            0x100C: encode_i(0x09, 0, 12, 7),  # Continuação
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 5, 9: 6, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_bne_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x05, 8, 9, 2),   # BNE
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99), # Deve ser ignorada
            0x100C: encode_i(0x09, 0, 12, 7),  # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 5, 9: 6, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_bne_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x05, 8, 9, 2),   # BNE: não desvia
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99), # Próxima instrução
            0x100C: encode_i(0x09, 0, 12, 7),  # Continuação
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 5, 9: 5, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_j_executa_antes_do_salto(self):
        instrucoes = {
            
            0x1000: (0x02 << 26) | (0x00001010 >> 2),  # J para 0x1010
            0x1004: encode_i(0x09, 10, 10, 1),        # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),        # Deve ser ignorada
            0x1010: encode_i(0x09, 0, 12, 7),         # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_jr_executa_antes_do_salto(self):
        instrucoes = {
            0x1000: encode_r(8, 0, 0, 0x08),       # JR $t0
            0x1004: encode_i(0x09, 10, 10, 1),     # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),     # Deve ser ignorada
            0x1010: encode_i(0x09, 0, 12, 7),      # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0x1010, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_jal_executa_e_salva_retorno(self):
        instrucoes = {
            0x1000: (0x03 << 26) | (0x00001010 >> 2),  # JAL para 0x1010
            0x1004: encode_i(0x09, 10, 10, 1),        # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),        # Deve ser ignorada
            0x1010: encode_i(0x09, 0, 12, 7),         # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {10: 0},
            pc_inicial=0x1000,
            memoria=MemoriaEsparsa(),
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)
        self.assertEqual(registradores[31], 0x1008)

    def test_jal_preserva_regiao_de_pc_mais_quatro(self):
        instrucoes = {
            0x0FFFFFFC: (0x03 << 26) | (0x00000010 >> 2),  # JAL
            0x10000000: encode_i(0x09, 10, 10, 1),        # Delay slot
            0x10000004: encode_i(0x09, 0, 11, 99),        # Ignorada
            0x10000010: encode_i(0x09, 0, 12, 7),         # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {10: 0},
            pc_inicial=0x0FFFFFFC,
            memoria=MemoriaEsparsa(),
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)
        self.assertEqual(registradores[31], 0x10000004)

    def test_j_preserva_regiao_de_pc_mais_quatro(self):
        instrucoes = {
            0x0FFFFFFC: (0x02 << 26) | (0x00000010 >> 2),  # J
            0x10000000: encode_i(0x09, 10, 10, 1),        # Delay slot
            0x10000004: encode_i(0x09, 0, 11, 99),        # Ignorada
            0x10000010: encode_i(0x09, 0, 12, 7),         # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {10: 0},
            pc_inicial=0x0FFFFFFC,
            memoria=MemoriaEsparsa(),
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_blez_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 3),   # BLEZ $t0, destino
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99), # Deve ser ignorada
            0x1010: encode_i(0x09, 0, 12, 7),  # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_blez_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 3),   # BLEZ: não desvia
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99), # Próxima instrução
            0x100C: encode_i(0x09, 0, 12, 7),  # Continuação
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 1, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_bgtz_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 3),   # BGTZ: destino 0x1010
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99), # Deve ser ignorada
            0x1010: encode_i(0x09, 0, 12, 7),  # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 1, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_bgtz_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 3),   # BGTZ: não desvia
            0x1004: encode_i(0x09, 10, 10, 1), # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99), # Próxima instrução
            0x100C: encode_i(0x09, 0, 12, 7),  # Continuação
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_bltz_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x00, 3), # BLTZ: destino 0x1010
            0x1004: encode_i(0x09, 10, 10, 1),  # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Deve ser ignorada
            0x1010: encode_i(0x09, 0, 12, 7),   # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_bltz_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x00, 3), # BLTZ: não desvia
            0x1004: encode_i(0x09, 10, 10, 1),  # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Próxima instrução
            0x100C: encode_i(0x09, 0, 12, 7),   # Continuação
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_bgez_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x01, 3), # BGEZ: destino 0x1010
            0x1004: encode_i(0x09, 10, 10, 1),  # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Deve ser ignorada
            0x1010: encode_i(0x09, 0, 12, 7),   # Destino
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_delay_slot_bgez_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x01, 3), # BGEZ: não desvia
            0x1004: encode_i(0x09, 10, 10, 1),  # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Próxima instrução
            0x100C: encode_i(0x09, 0, 12, 7),   # Continuação
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF, 10: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)
        self.assertEqual(registradores[12], 7)

    def test_bltz_menor_inteiro_32_bits(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x00, 2),  # BLTZ
            0x1004: encode_i(0x09, 0, 10, 1),    # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),   # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),    # Destino do branch
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0x80000000},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgez_maior_inteiro_positivo_32_bits(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x01, 2),  # BGEZ
            0x1004: encode_i(0x09, 0, 10, 1),    # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),   # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),    # Destino do branch
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0x7FFFFFFF},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_blez_menor_inteiro_32_bits(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 2),    # BLEZ
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),   # Destino do branch
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0x80000000},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgtz_maior_inteiro_positivo_32_bits(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 2),    # BGTZ
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),   # Destino do branch
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0x7FFFFFFF},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bltz_zero_nao_desvia(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x00, 2),  # BLTZ
            0x1004: encode_i(0x09, 0, 10, 1),    # Delay slot
            0x1008: encode_i(0x09, 0, 11, 2),    # Execução sequencial
            0x100C: encode_i(0x09, 0, 12, 99),   # Não deve executar
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 2)
        self.assertEqual(registradores[12], 99)

    def test_bgez_zero_desvia(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x01, 2),  # BGEZ
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),   # Destino do branch
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)
        
    def test_blez_zero_desvia(self):
        instrucoes = {
            0x1000: encode_i(0x06, 8, 0, 2),    # BLEZ
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),   # Destino do branch
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgtz_zero_nao_desvia(self):
        instrucoes = {
            0x1000: encode_i(0x07, 8, 0, 2),    # BGTZ
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 2),   # Execução sequencial
            0x100C: encode_i(0x09, 0, 12, 99),  # Continuação
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 2)
        self.assertEqual(registradores[12], 99)

    def test_bltzal_zero_nao_desvia_atualiza_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x10, 2),  # BLTZAL
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 2),   # Execução sequencial
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0, 31: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 2)

    def test_bltzal_negativo_desvia_atualiza_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x10, 2),  # BLTZAL
            0x1004: encode_i(0x09, 0, 10, 1),    # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),   # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),    # Destino do branch
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF, 31: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgezal_negativo_nao_desvia_atualiza_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x11, 2),  # BGEZAL
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 2),   # Execução sequencial
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF, 31: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 2)

    def test_bgezal_positivo_desvia_atualiza_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x11, 2),  # BGEZAL
            0x1004: encode_i(0x09, 0, 10, 1),   # Delay slot
            0x1008: encode_i(0x09, 0, 11, 99),  # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),   # Destino do branch
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0x7FFFFFFF, 31: 0},
        )

        self.assertEqual(registradores[31], 0x1008)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bgezal_delay_slot_sobrescreve_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x11, 2),       # BGEZAL
            0x1004: encode_i(0x09, 0, 31, 0x1234),    # Delay slot: altera $ra
            0x1008: encode_i(0x09, 0, 11, 99),        # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),         # Destino do branch
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 1, 31: 0},
        )

        self.assertEqual(registradores[31], 0x1234)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_bltzal_delay_slot_sobrescreve_ra(self):
        instrucoes = {
            0x1000: encode_i(0x01, 8, 0x10, 2),       # BLTZAL
            0x1004: encode_i(0x09, 0, 31, 0x5678),    # Delay slot: altera $ra
            0x1008: encode_i(0x09, 0, 11, 99),        # Não deve executar
            0x100C: encode_i(0x09, 0, 12, 7),         # Destino do branch
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {8: 0xFFFFFFFF, 31: 0},
        )

        self.assertEqual(registradores[31], 0x5678)
        self.assertEqual(registradores[11], 0)
        self.assertEqual(registradores[12], 7)

    def test_beq_desvio_com_offset_negativo(self):
        instrucoes = {
            0x1000: encode_i(0x09, 0, 10, 1),  # ADDIU $10, $0, 1
            0x1004: encode_i(0x04, 10, 10, -2),  # BEQ: volta para 0x1000
            0x1008: encode_i(0x09, 0, 11, 7),  # Delay slot
            0x100C: encode_i(0x09, 0, 12, 99),  # Não deve executar
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 7)
        self.assertEqual(registradores[12], 0)

    def test_bne_offset_negativo_nao_tomado(self):
        instrucoes = {
            0x1000: encode_i(0x09, 0, 10, 1),  # ADDIU $10, $0, 1
            0x1004: encode_i(0x05, 10, 10, -2),  # BNE: condição falsa
            0x1008: encode_i(0x09, 0, 11, 7),  # Delay slot
            0x100C: encode_i(0x09, 0, 12, 9),  # Continuação
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 7)
        self.assertEqual(registradores[12], 9)


    def test_jal_na_fronteira_de_regiao(self):
        instrucoes = {
            0x0FFFFFFC: (0x03 << 26) | (0x00000004 >> 2),
            0x10000000: encode_i(0x09, 0, 10, 1),
            0x10000004: encode_i(0x09, 0, 11, 99),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
            pc_inicial=0x0FFFFFFC,
            memoria=MemoriaEsparsa(),
        )

        self.assertEqual(registradores[31], 0x10000004)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)

    def test_j_na_fronteira_de_regiao(self):
        instrucoes = {
            0x0FFFFFFC: (0x02 << 26) | (0x00000004 >> 2),
            0x10000000: encode_i(0x09, 0, 10, 1),
            0x10000004: encode_i(0x09, 0, 11, 99),
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
            pc_inicial=0x0FFFFFFC,
            memoria=MemoriaEsparsa(),
        )

        self.assertEqual(registradores[31], 0)
        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 99)

    def test_jr_registro_com_delay_slot(self):
        instrucoes = {
            0x1000: (9 << 21) | 0x08,  # JR $9
            0x1004: encode_i(0x09, 0, 10, 1),  # Delay slot
            0x1008: encode_i(0x09, 0, 12, 99),  # Nao deve executar
            0x1010: encode_i(0x09, 0, 11, 7),  # Destino do JR
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {
                9: 0x1010,
                31: 0x12345678,
            },
        )

        self.assertEqual(registradores[10], 1)
        self.assertEqual(registradores[11], 7)
        self.assertEqual(registradores[12], 0)
        self.assertEqual(registradores[31], 0x12345678)

    def test_limite_de_execucao_em_loop(self):
        instrucoes = {
            0x1000: encode_i(0x04, 0, 0, -1),  # BEQ $0, $0, -1
            0x1004: encode_i(0x09, 0, 10, 1),  # Delay slot
        }

        registradores = self.executar_programa_teste(
            instrucoes,
            {},
        )

        self.assertEqual(registradores[10], 1)

if __name__ == "__main__":
    unittest.main()
