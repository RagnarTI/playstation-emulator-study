import os
import tempfile
import unittest


from ps1.memory.main_ram import RAM
from ps1 import MemoryBus
from ps1.memory.bios_rom import BIOS

class TestBIOS(unittest.TestCase):

    def setUp(self):
        self.arquivo_temporario = tempfile.NamedTemporaryFile(
            delete=False
        )
        self.arquivo_temporario.write(bytes(BIOS.TAMANHO))
        self.arquivo_temporario.close()

        self.bios = BIOS(self.arquivo_temporario.name)

    def tearDown(self):
        os.unlink(self.arquivo_temporario.name)

    def test_tamanho_da_bios(self):
        self.assertEqual(len(self.bios.dados), 512 * 1024)

    def test_ler_u8(self):
        self.assertEqual(self.bios.ler_u8(0), 0)

    def test_ler_u16(self):
        self.assertEqual(self.bios.ler_u16(0), 0)

    def test_ler_u32(self):
        self.assertEqual(self.bios.ler_u32(0), 0)

    def test_ler_u32_little_endian(self):
        with tempfile.NamedTemporaryFile(delete=False) as arquivo:
            arquivo.write(
                b"\x78\x56\x34\x12"
                + bytes(BIOS.TAMANHO - 4)
            )
            caminho = arquivo.name

        try:
            bios = BIOS(caminho)
            self.assertEqual(bios.ler_u32(0), 0x12345678)
        finally:
            os.unlink(caminho)

    def test_endereco_negativo(self):
        with self.assertRaises(ValueError):
            self.bios.ler_u8(-1)

    def test_leitura_fora_dos_limites(self):
        with self.assertRaises(ValueError):
            self.bios.ler_u8(BIOS.TAMANHO)

    def test_leitura_u32_no_final_da_bios(self):
        with self.assertRaises(ValueError):
            self.bios.ler_u32(BIOS.TAMANHO - 3)

    def test_tamanho_invalido(self):
        with tempfile.NamedTemporaryFile(delete=False) as arquivo:
            arquivo.write(b"\x00" * 100)
            caminho = arquivo.name

        try:
            with self.assertRaises(ValueError):
                BIOS(caminho)
        finally:
            os.unlink(caminho)

    def test_leitura_u16_bios_desalinhada(self):
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False) as arquivo:
            arquivo.write(bytes(BIOS.TAMANHO))
            caminho = arquivo.name

        try:
            bios = BIOS(caminho)
            memoria = MemoryBus(RAM(), bios)

            with self.assertRaises(ValueError):
                memoria.read_u16(0x1FC00001)
        finally:
            os.unlink(caminho)

    def test_leitura_u32_bios_desalinhada(self):
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False) as arquivo:
            arquivo.write(bytes(BIOS.TAMANHO))
            caminho = arquivo.name

        try:
            bios = BIOS(caminho)
            memoria = MemoryBus(RAM(), bios)

            with self.assertRaises(ValueError):
                memoria.read_u32(0x1FC00002)
        finally:
            os.unlink(caminho)


if __name__ == "__main__":
    unittest.main()
