import os
import unittest


from ps1.cpu.mips_exceptions import MIPSException, IntegerOverflow

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
