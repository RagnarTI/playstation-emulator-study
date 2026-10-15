import os
import sys
import unittest

PASTA_TESTES = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PASTA_TESTES not in sys.path:
    sys.path.insert(0, PASTA_TESTES)

from mips_exceptions import MIPSException, IntegerOverflow

class TestMIPSExceptions(unittest.TestCase):

    def test_integer_overflow_e_uma_excecao_mips(self):
        erro = IntegerOverflow("Overflow em ADD")

        self.assertIsInstance(erro, MIPSException)
        self.assertIsInstance(erro, Exception)

    
    def test_integer_overflow_e_identificado_especificamente(self):
        erro = IntegerOverflow("Overflow em ADD")

        with self.assertRaises(IntegerOverflow):
            raise erro

        with self.assertRaises(MIPSException):
            raise IntegerOverflow("Overflow em SUB")



if __name__ == "__main__":
    unittest.main()
