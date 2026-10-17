class BIOS:
    TAMANHO = 512 * 1024  # 512 KiB

    def __init__(self, caminho):
        with open(caminho, "rb") as arquivo:
            self.dados = arquivo.read()

        if len(self.dados) != self.TAMANHO:
            raise ValueError(
                f"BIOS invalida: esperado {self.TAMANHO} bytes, "
                f"recebido {len(self.dados)} bytes"
            )

    def ler_u8(self, endereco):
        self._validar_endereco(endereco, 1)
        return self.dados[endereco]

    def ler_u16(self, endereco):
        self._validar_endereco(endereco, 2)
        return int.from_bytes(
            self.dados[endereco:endereco + 2],
            byteorder="little"
        )

    def ler_u32(self, endereco):
        self._validar_endereco(endereco, 4)
        return int.from_bytes(
            self.dados[endereco:endereco + 4],
            byteorder="little"
        )

    def _validar_endereco(self, endereco, quantidade):
        if endereco < 0 or endereco + quantidade > self.TAMANHO:
            raise ValueError("Endereco fora dos limites da BIOS")
