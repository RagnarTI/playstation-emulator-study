
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
    executar_programa,
)
from ram import RAM
from memory_bus import MemoryBus


class TestMemory(unittest.TestCase):

    def executar_instrucao(self, instrucao, valores, memoria=None):
        if memoria is None:
            memoria = RAM()

        registradores = [0] * 32
        endereco_instrucao = 0x1000

        for indice, valor in valores.items():
            registradores[indice] = valor & 0xFFFFFFFF

        memoria.write_u32(endereco_instrucao, instrucao)

        executar_programa(
            memoria,
            {endereco_instrucao},
            endereco_instrucao,
            registradores,
            limite=1,
        )

        return registradores, memoria

    def test_sw(self):
        instrucao = encode_i(0x2B, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {8: 12345, 9: 0x3000},
        )

        self.assertEqual(memoria.read_u32(0x3000), 12345)
        self.assertEqual(registradores[8], 12345)
        self.assertEqual(registradores[9], 0x3000)

    def test_lw(self):
        memoria = RAM()
        memoria.write_u32(0x3000, 9876)

        instrucao = encode_i(0x23, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {9: 0x3000},
            memoria,
        )

        self.assertEqual(registradores[8], 9876)

    def test_little_endian(self):
        memoria = RAM()

        memoria.write_u32(0x2000, 0x12345678)

        self.assertEqual(memoria.read_u8(0x2000), 0x78)
        self.assertEqual(memoria.read_u8(0x2001), 0x56)
        self.assertEqual(memoria.read_u8(0x2002), 0x34)
        self.assertEqual(memoria.read_u8(0x2003), 0x12)

    def test_sw_atravessa_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x2B, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {8: 12345, 9: 0x3000},
            memoria,
        )

        self.assertEqual(memoria.read_u32(0x3000), 12345)
        self.assertEqual(ram.read_u32(0x3000), 12345)
        self.assertEqual(registradores[8], 12345)
        self.assertEqual(registradores[9], 0x3000)

    def test_lw_atravessa_memory_bus(self):
        ram = RAM()
        ram.write_u32(0x3000, 9876)
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x23, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {9: 0x3000},
            memoria,
        )

        self.assertEqual(registradores[8], 9876)

    def test_sw_kseg0_atravessa_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x2B, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {8: 12345, 9: 0x80003000},
            memoria,
        )

        self.assertEqual(ram.read_u32(0x3000), 12345)

    def test_sw_kseg1_atravessa_memory_bus(self):
        ram = RAM()
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x2B, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {8: 12345, 9: 0xA0003000},
            memoria,
        )

        self.assertEqual(ram.read_u32(0x3000), 12345)

    def test_lw_kseg0_atravessa_memory_bus(self):
        ram = RAM()
        ram.write_u32(0x3000, 9876)
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x23, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {9: 0x80003000},
            memoria,
        )

        self.assertEqual(registradores[8], 9876)

    def test_lw_kseg1_atravessa_memory_bus(self):
        ram = RAM()
        ram.write_u32(0x3000, 9876)
        memoria = MemoryBus(ram)

        instrucao = encode_i(0x23, 9, 8, 0)

        registradores, memoria = self.executar_instrucao(
            instrucao,
            {9: 0xA0003000},
            memoria,
        )

        self.assertEqual(registradores[8], 9876)
        
if __name__ == "__main__":
    unittest.main()
