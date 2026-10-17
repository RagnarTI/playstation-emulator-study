

from ps1.cpu.mips_interpreter import encode_i, encode_r, executar_programa
from ps1.memory.main_ram import RAM


class MemoriaEsparsa:
    """Memória auxiliar que armazena somente os endereços utilizados."""

    def __init__(self):
        self.palavras = {}

    def write_u32(self, endereco, valor):
        if endereco % 4 != 0:
            raise ValueError(
                f"Endereco desalinhado: 0x{endereco:08X}"
            )

        self.palavras[endereco] = valor & 0xFFFFFFFF

    def read_u32(self, endereco):
        if endereco % 4 != 0:
            raise ValueError(
                f"Endereco desalinhado: 0x{endereco:08X}"
            )

        return self.palavras.get(endereco, 0)


def executar_programa_teste(
    instrucoes,
    valores=None,
    pc_inicial=0x1000,
    memoria=None,
    limite=10,
    retornar_pc=False,
):
    """Prepara e executa um programa para os testes unitários."""

    if valores is None:
        valores = {}

    if memoria is None:
        memoria = RAM()

    registradores = [0] * 32

    for indice, valor in valores.items():
        if not 0 <= indice < 32:
            raise ValueError(
                f"Índice de registrador inválido: {indice}"
            )

        registradores[indice] = valor & 0xFFFFFFFF

    for endereco, instrucao in instrucoes.items():
        memoria.write_u32(endereco, instrucao)

    resultado = executar_programa(
        memoria,
        set(instrucoes.keys()),
        pc_inicial,
        registradores,
        limite=limite,
        retornar_pc=retornar_pc,
    )

    if retornar_pc:
        registradores, pc_final = resultado
        return registradores, pc_final

    return registradores