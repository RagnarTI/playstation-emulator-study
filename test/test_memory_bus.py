import os
import sys
import unittest

PASTA_PROJETO = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PASTA_PROJETO not in sys.path:
    sys.path.insert(0, PASTA_PROJETO)

from ram import RAM
from memory_bus import MemoryBus


class TestMemoryBus(unittest.TestCase):

    def test_leitura_e_escrita_na_ram_principal(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0x00001000, 0x12345678)

        resultado = memoria.read_u32(0x00001000)

        self.assertEqual(resultado, 0x12345678)

    def test_kseg0_acessa_a_mesma_ram_fisica(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0x00001000, 0x12345678)

        resultado = memoria.read_u32(0x80001000)

        self.assertEqual(resultado, 0x12345678)

    def test_kseg1_acessa_a_mesma_ram_fisica(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0x00001000, 0x12345678)

        resultado = memoria.read_u32(0xA0001000)

        self.assertEqual(resultado, 0x12345678)

    def test_escrita_por_kseg0_e_leitura_por_endereco_fisico(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0x80001000, 0xABCDEF12)

        resultado = memoria.read_u32(0x00001000)

        self.assertEqual(resultado, 0xABCDEF12)

    def test_escrita_por_kseg1_e_leitura_por_endereco_fisico(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0xA0001000, 0xABCDEF12)

        resultado = memoria.read_u32(0x00001000)

        self.assertEqual(resultado, 0xABCDEF12)

    def test_endereco_fisico_fora_da_ram_gera_erro(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u32(0x00200000)

    def test_scratchpad_armazena_e_le_valor(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0x1F800000, 0x12345678)

        resultado = memoria.read_u32(0x1F800000)

        self.assertEqual(resultado, 0x12345678)

    def test_scratchpad_rejeita_acesso_fora_dos_limites(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u32(0x1F800400)

    def test_scratchpad_rejeita_palavra_que_ultrapassa_limite(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u32(0x1F8003FE)

    def test_scratchpad_rejeita_escrita_que_ultrapassa_limite(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.write_u32(0x1F8003FE, 0x12345678)

    def test_scratchpad_le_u8(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.scratchpad[0x10] = 0xAB

        resultado = memoria.read_u8(0x1F800010)

        self.assertEqual(resultado, 0xAB)

    def test_scratchpad_escreve_u8(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u8(0x1F800010, 0xAB)

        self.assertEqual(memoria.scratchpad[0x10], 0xAB)

    def test_ram_principal_le_u8(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        ram.write_u8(0x1000, 0xAB)

        resultado = memoria.read_u8(0x1000)

        self.assertEqual(resultado, 0xAB)

    def test_ram_principal_escreve_u8(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u8(0x1000, 0xAB)

        resultado = ram.read_u8(0x1000)

        self.assertEqual(resultado, 0xAB)

    def test_scratchpad_le_u16(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.scratchpad[0x10] = 0x34
        memoria.scratchpad[0x11] = 0x12

        resultado = memoria.read_u16(0x1F800010)

        self.assertEqual(resultado, 0x1234)

    def test_scratchpad_escreve_u16(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u16(0x1F800010, 0x1234)

        self.assertEqual(memoria.scratchpad[0x10], 0x34)
        self.assertEqual(memoria.scratchpad[0x11], 0x12)

    def test_ram_principal_le_u16(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        ram.write_u16(0x1000, 0x1234)

        resultado = memoria.read_u16(0x1000)

        self.assertEqual(resultado, 0x1234)

    def test_ram_principal_escreve_u16(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u16(0x1000, 0x1234)

        resultado = ram.read_u16(0x1000)

        self.assertEqual(resultado, 0x1234)

    def test_scratchpad_rejeita_leitura_u16_desalinhada(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u16(0x1F800011)

    def test_scratchpad_rejeita_escrita_u16_desalinhada(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.write_u16(0x1F800011, 0x1234)

    def test_scratchpad_rejeita_leitura_u32_desalinhada(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u32(0x1F800001)


    def test_scratchpad_rejeita_escrita_u32_desalinhada(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.write_u32(0x1F800001, 0x12345678)

    def test_ram_rejeita_escrita_u16_que_ultrapassa_limite(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.write_u16(0x1FFFFF, 0x1234)

    def test_ram_rejeita_escrita_u8_fora_dos_limites(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.write_u8(0x200000, 0xAB)

    def test_ram_rejeita_leitura_u8_fora_dos_limites(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u8(0x200000)
 
    def test_kseg0_rejeita_leitura_fora_dos_limites_da_ram(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u8(0x80200000)
    
    def test_kseg1_rejeita_leitura_fora_dos_limites_da_ram(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u8(0xA0200000)

    def test_kseg0_e_kseg1_compartilham_a_mesma_memoria_fisica(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0x80001000, 0x12345678)

        self.assertEqual(memoria.read_u32(0xA0001000), 0x12345678)

    def test_kseg1_e_kseg0_compartilham_a_mesma_memoria_fisica(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0xA0001000, 0x89ABCDEF)

        self.assertEqual(memoria.read_u32(0x80001000), 0x89ABCDEF)

    def test_endereco_fisico_e_aliases_virtuais_compartilham_dados(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0x00001000, 0xCAFEBABE)

        self.assertEqual(memoria.read_u32(0x80001000), 0xCAFEBABE)
        self.assertEqual(memoria.read_u32(0xA0001000), 0xCAFEBABE)

    def test_scratchpad_e_ram_sao_regioes_independentes(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0x00000010, 0x12345678)
        memoria.write_u32(0x1F800010, 0xAABBCCDD)

        self.assertEqual(memoria.read_u32(0x00000010), 0x12345678)
        self.assertEqual(memoria.read_u32(0x1F800010), 0xAABBCCDD)

    def test_escrita_na_scratchpad_nao_altera_ram(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        ram.write_u32(0x10, 0x12345678)

        memoria.write_u32(0x1F800010, 0xAABBCCDD)

        self.assertEqual(ram.read_u32(0x10), 0x12345678)

    def test_escrita_na_ram_nao_altera_scratchpad(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0x1F800010, 0xAABBCCDD)

        ram.write_u32(0x10, 0x12345678)

        self.assertEqual(memoria.read_u32(0x1F800010), 0xAABBCCDD)

    def test_leitura_u32_que_atravessa_inicio_da_scratchpad(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u32(0x1F7FFFFE)

    def test_escrita_u32_que_atravessa_inicio_da_scratchpad(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.write_u32(0x1F7FFFFE, 0x12345678)

    def test_scratchpad_u32_no_ultimo_endereco_valido(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u32(0x1F8003FC, 0x12345678)

        self.assertEqual(memoria.read_u32(0x1F8003FC), 0x12345678)

    def test_scratchpad_rejeita_escrita_u32_no_limite_final(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.write_u32(0x1F800400, 0x12345678)

    def test_scratchpad_rejeita_escrita_u16_que_ultrapassa_limite(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.write_u16(0x1F8003FF, 0x1234)

    def test_scratchpad_rejeita_escrita_u8_no_limite_final(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.write_u8(0x1F800400, 0xAB)

    def test_scratchpad_u8_no_ultimo_endereco_valido(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        memoria.write_u8(0x1F8003FF, 0xAB)

        self.assertEqual(memoria.read_u8(0x1F8003FF), 0xAB)

    def test_scratchpad_rejeita_leitura_u8_no_limite_final(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u8(0x1F800400)

    def test_leitura_u8_na_ram_nao_acessa_scratchpad_ao_lado(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        ram.write_u8(0x1FFFFF, 0x42)

        self.assertEqual(memoria.read_u8(0x1FFFFF), 0x42)

    def test_leitura_u32_que_cruza_inicio_da_scratchpad_e_rejeitada(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.read_u32(0x1F7FFFFF)

    def test_escrita_nao_deve_encaminhar_acesso_que_cruza_inicio_scratchpad(self):
        class RAMDeTeste:
            def __init__(self):
                self.escritas = []

            def write_u32(self, endereco, valor):
                self.escritas.append((endereco, valor))

        ram = RAMDeTeste()
        memoria = MemoryBus(ram)

        with self.assertRaises(ValueError):
            memoria.write_u32(0x1F7FFFFF, 0x12345678)

        self.assertEqual(ram.escritas, [])

    def test_escrita_que_cruza_inicio_scratchpad_e_rejeitada(self):
        class RAMDeTeste:
            def __init__(self):
                self.escritas = []

            def write_u32(self, endereco, valor):
                self.escritas.append((endereco, valor))

        ram = RAMDeTeste()
        memoria = MemoryBus(ram)

        # Neutraliza o alinhamento para isolar a verificação da fronteira.
        memoria._validar_alinhamento = lambda endereco, alinhamento: None

        with self.assertRaises(ValueError):
            memoria.write_u32(0x1F7FFFFF, 0x12345678)

        self.assertEqual(ram.escritas, [])

    def test_leitura_que_cruza_inicio_scratchpad_e_rejeitada(self):
        class RAMDeTeste:
            def __init__(self):
                self.leituras = []

            def read_u32(self, endereco):
                self.leituras.append(endereco)
                return 0x12345678

        ram = RAMDeTeste()
        memoria = MemoryBus(ram)

        # Isola a validação da fronteira da validação de alinhamento.
        memoria._validar_alinhamento = lambda endereco, alinhamento: None

        with self.assertRaises(ValueError):
            memoria.read_u32(0x1F7FFFFF)

        self.assertEqual(ram.leituras, [])



if __name__ == "__main__":
    unittest.main()