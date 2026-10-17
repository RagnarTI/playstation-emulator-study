import os
import unittest


from test.helpers.arithmetic_helpers import (
    encode_r,
    encode_i,
    signed_32,
    executar_instrucao,
    EstadoEspecial,
    IntegerOverflow,
)


class TestOverflow(unittest.TestCase):

    def test_add_gera_overflow_com_sinal(self):
        with self.assertRaises(IntegerOverflow):
            executar_instrucao(
                encode_r(8, 9, 10, 0x20),
                valores={
                    8: 0x7FFFFFFF,
                    9: 1,
                },
            )
    
    def test_add_sem_overflow_com_sinal(self):
        registradores = executar_instrucao(
            encode_r(8, 9, 10, 0x20),
            valores={
                8: 10,
                9: 20,
            },
        )

        self.assertEqual(registradores[10], 30)

    def test_signed_32_interpreta_valor_negativo(self):
        self.assertEqual(signed_32(0x80000000), -2147483648)

    def test_sub_gera_overflow_com_sinal(self):
        with self.assertRaises(IntegerOverflow):
            executar_instrucao(
                encode_r(8, 9, 10, 0x22),
                valores={
                    8: 0x80000000,
                    9: 1,
                },
            )

    def test_add_com_operando_negativo(self):
        registradores = executar_instrucao(
            encode_r(8, 9, 10, 0x20),
            valores={
                8: 0xFFFFFFFF,  # -1
                9: 2,
            },
        )

        self.assertEqual(registradores[10], 1)
 
    def test_sub_com_operando_negativo(self):
        registradores = executar_instrucao(
            encode_r(8, 9, 10, 0x22),
            valores={
                8: 5,
                9: 0xFFFFFFFF,  # -1
            },
        )

        self.assertEqual(registradores[10], 6)
   
    def test_sub_gera_overflow_com_operando_negativo(self):
        with self.assertRaises(IntegerOverflow):
            executar_instrucao(
                encode_r(8, 9, 10, 0x22),
                valores={
                    8: 0x7FFFFFFF,  # maior inteiro positivo com sinal
                    9: 0xFFFFFFFF,  # -1
                },
            )
  
    def test_add_gera_overflow_com_operando_negativo(self):
        with self.assertRaises(IntegerOverflow):
            executar_instrucao(
                encode_r(8, 9, 10, 0x20),
                valores={
                    8: 0x80000000,  # menor inteiro negativo com sinal
                    9: 0xFFFFFFFF,  # -1
                },
            )

    def test_addi_gera_overflow_com_sinal(self):
        with self.assertRaises(IntegerOverflow):
            executar_instrucao(
                encode_i(0x08, 8, 10, 1),
                valores={
                    8: 0x7FFFFFFF,
                },
            )

    def test_addi_sem_overflow_com_sinal(self):
        registradores = executar_instrucao(
            encode_i(0x08, 8, 10, 1),
            valores={
                8: 0x7FFFFFFE,
            },
        )

        self.assertEqual(registradores[10], 0x7FFFFFFF)

if __name__ == "__main__":
    unittest.main()