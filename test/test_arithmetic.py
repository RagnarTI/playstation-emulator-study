
import os
import sys
import unittest

PASTA_PROJETO = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PASTA_PROJETO not in sys.path:
    sys.path.insert(0, PASTA_PROJETO)

from mips_interpreter import (
    write_u32,
    encode_r,
    encode_i,
    executar_programa,
)


class TestArithmetic(unittest.TestCase):

    def executar_instrucao(self, instrucao, valores):
        memoria = {}
        registradores = [0] * 32
        endereco = 0x1000

        for indice, valor in valores.items():
            registradores[indice] = valor & 0xFFFFFFFF

        write_u32(memoria, endereco, instrucao)

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


if __name__ == "__main__":
    unittest.main()