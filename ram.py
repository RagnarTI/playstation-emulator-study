class RAM:
    def __init__(self, tamanho=2 * 1024 * 1024):
        self.tamanho = tamanho
        self.dados = bytearray(tamanho)

    def _validar_alinhamento(self, endereco, alinhamento):
        if endereco % alinhamento != 0:
            raise ValueError(
                f"Endereco desalinhado: 0x{endereco:08X}"
            )

    def _validar_endereco(self, endereco, tamanho):
        if endereco < 0 or endereco + tamanho > self.tamanho:
            raise ValueError(
                f"Endereço fora dos limites da RAM: "
                f"endereco=0x{endereco:08X}, "
                f"tamanho={tamanho}, "
                f"limite=0x{self.tamanho:08X}"
            )

    def read_u8(self, endereco):
        self._validar_endereco(endereco, 1)
        return self.dados[endereco]

    def write_u8(self, endereco, valor):
        self._validar_endereco(endereco, 1)
        self.dados[endereco] = valor & 0xFF

    def read_u16(self, endereco):
        self._validar_endereco(endereco, 2)
        self._validar_alinhamento(endereco, 2)

        valor = self.dados[endereco]
        valor |= self.dados[endereco + 1] << 8

        return valor

    def write_u16(self, endereco, valor):
        self._validar_endereco(endereco, 2)
        self._validar_alinhamento(endereco, 2)

        valor &= 0xFFFF

        self.dados[endereco] = valor & 0xFF
        self.dados[endereco + 1] = (valor >> 8) & 0xFF


    def read_u32(self, endereco):
        self._validar_endereco(endereco, 4)
        self._validar_alinhamento(endereco, 4)

        valor = (
            self.dados[endereco]
            | (self.dados[endereco + 1] << 8)
            | (self.dados[endereco + 2] << 16)
            | (self.dados[endereco + 3] << 24)
        )

        return valor

    def write_u32(self, endereco, valor):
        self._validar_endereco(endereco, 4)
        self._validar_alinhamento(endereco, 4)

        valor &= 0xFFFFFFFF

        for i in range(4):
            self.dados[endereco + i] = (
                valor >> (8 * i)
            ) & 0xFF

    def _validar_endereco(self, endereco, tamanho):
        if endereco < 0 or endereco + tamanho > self.tamanho:
            raise ValueError("Endereço fora dos limites da RAM")