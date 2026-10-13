import os
import sys
import unittest

PASTA_PROJETO = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PASTA_PROJETO not in sys.path:
    sys.path.insert(0, PASTA_PROJETO)

from ram import RAM


class TestRAM(unittest.TestCase):

    def setUp(self):
        self.ram = RAM()

    def test_ram_tem_2_mib(self):
        self.assertEqual(
            self.ram.tamanho,
            2 * 1024 * 1024
        )

    def test_ram_inicia_com_zeros(self):
        self.assertEqual(
            self.ram.read_u8(0),
            0
        )

    def test_write_u8_armazena_um_byte(self):
        self.ram.write_u8(0x1000, 0xAB)

        self.assertEqual(
            self.ram.read_u8(0x1000),
            0xAB
        )

    def test_write_u8_nao_altera_endereco_vizinho(self):
        self.ram.write_u8(0x1000, 0xAB)

        self.assertEqual(
            self.ram.read_u8(0x1001),
            0
        )

    def test_read_u8_fora_dos_limites(self):
        with self.assertRaises(ValueError):
            self.ram.read_u8(2 * 1024 * 1024)

    def test_read_u8_com_endereco_negativo(self):
        with self.assertRaises(ValueError):
            self.ram.read_u8(-1)

    def test_write_u8_fora_dos_limites(self):
        with self.assertRaises(ValueError):
            self.ram.write_u8(2 * 1024 * 1024, 0xAB)

    def test_write_u8_com_endereco_negativo(self):
        with self.assertRaises(ValueError):
            self.ram.write_u8(-1, 0xAB)


    def test_write_u16_e_read_u16_preservam_valor(self):
        valores = [0x0000, 0x0001, 0x1234, 0xFFFF]

        for valor in valores:
            with self.subTest(valor=valor):
                self.ram.write_u16(0x1000, valor)
                self.assertEqual(
                    self.ram.read_u16(0x1000),
                    valor
                )

    def test_write_u16_usa_little_endian(self):
        self.ram.write_u16(0x1000, 0x1234)

        self.assertEqual(self.ram.read_u8(0x1000), 0x34)
        self.assertEqual(self.ram.read_u8(0x1001), 0x12)

    def test_write_u16_limita_valor_a_16_bits(self):
        self.ram.write_u16(0x1000, 0x12345678)

        self.assertEqual(
            self.ram.read_u16(0x1000),
            0x5678
        )

    def test_read_u16_fora_dos_limites(self):
        with self.assertRaises(ValueError):
            self.ram.read_u16(self.ram.tamanho - 1)

    def test_write_u16_fora_dos_limites(self):
        with self.assertRaises(ValueError):
            self.ram.write_u16(self.ram.tamanho - 1, 0x1234)


    def test_write_u32_e_read_u32_preservam_valor(self):
        valores = [
            0x00000000,
            0x00000001,
            0x12345678,
            0xFFFFFFFF,
        ]

        for valor in valores:
            with self.subTest(valor=valor):
                self.ram.write_u32(0x1000, valor)
                self.assertEqual(
                    self.ram.read_u32(0x1000),
                    valor
                )

    def test_write_u32_usa_little_endian(self):
        self.ram.write_u32(0x1000, 0x12345678)

        self.assertEqual(self.ram.read_u8(0x1000), 0x78)
        self.assertEqual(self.ram.read_u8(0x1001), 0x56)
        self.assertEqual(self.ram.read_u8(0x1002), 0x34)
        self.assertEqual(self.ram.read_u8(0x1003), 0x12)

    def test_write_u32_limita_valor_a_32_bits(self):
        self.ram.write_u32(0x1000, 0x12345678ABCDEF01)

        self.assertEqual(
            self.ram.read_u32(0x1000),
            0xABCDEF01
        )

    def test_read_u32_fora_dos_limites(self):
        with self.assertRaises(ValueError):
            self.ram.read_u32(self.ram.tamanho - 3)

    def test_write_u32_fora_dos_limites(self):
        with self.assertRaises(ValueError):
            self.ram.write_u32(
                self.ram.tamanho - 3,
                0x12345678
            )
            
    def test_read_u16_com_endereco_desalinhado(self):
        with self.assertRaises(ValueError):
            self.ram.read_u16(0x1001)

    def test_write_u16_com_endereco_desalinhado(self):
        with self.assertRaises(ValueError):
            self.ram.write_u16(0x1001, 0x1234)

    def test_read_u32_com_endereco_desalinhado(self):
        with self.assertRaises(ValueError):
            self.ram.read_u32(0x1002)

    def test_write_u32_com_endereco_desalinhado(self):
        with self.assertRaises(ValueError):
            self.ram.write_u32(0x1002, 0x12345678)


if __name__ == "__main__":
    unittest.main()
