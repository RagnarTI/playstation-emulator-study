class MemoryBus:
    def __init__(self, ram):
        self.ram = ram
        self.scratchpad = bytearray(1024)

    def _traduzir_endereco(self, endereco):
        if 0x80000000 <= endereco <= 0x9FFFFFFF:
            return endereco - 0x80000000

        if 0xA0000000 <= endereco <= 0xBFFFFFFF:
            return endereco - 0xA0000000

        return endereco

    def _validar_alinhamento(self, endereco, alinhamento):
        if endereco % alinhamento != 0:
            raise ValueError(
                f"Endereco desalinhado: 0x{endereco:08X}"
            )

    def _ler_memoria(self, endereco, tamanho):
        inicio_scratchpad = 0x1F800000
        fim_scratchpad = 0x1F800400

        sobrepoe_scratchpad = (
            endereco < fim_scratchpad
            and endereco + tamanho > inicio_scratchpad
        )

        if sobrepoe_scratchpad:
            if not (inicio_scratchpad <= endereco < fim_scratchpad):
                raise ValueError(
                    "Acesso atravessa a fronteira da Scratchpad"
                )

            if endereco + tamanho > fim_scratchpad:
                raise ValueError(
                    "Acesso ultrapassa os limites da Scratchpad"
                )

            self._validar_alinhamento(endereco, tamanho)
            deslocamento = endereco - inicio_scratchpad
            return int.from_bytes(
                self.scratchpad[deslocamento:deslocamento + tamanho],
                byteorder="little",
            )

        if tamanho == 1:
            return self.ram.read_u8(endereco)

        if tamanho == 2:
            return self.ram.read_u16(endereco)

        if tamanho == 4:
            return self.ram.read_u32(endereco)

        raise ValueError("Tamanho de leitura não suportado")

    def _escrever_memoria(self, endereco, valor, tamanho):
        inicio_scratchpad = 0x1F800000
        fim_scratchpad = 0x1F800400

        sobrepoe_scratchpad = (
            endereco < fim_scratchpad
            and endereco + tamanho > inicio_scratchpad
        )

        if sobrepoe_scratchpad:
            if not (inicio_scratchpad <= endereco < fim_scratchpad):
                raise ValueError(
                    "Acesso atravessa a fronteira da Scratchpad"
                )

            if endereco + tamanho > fim_scratchpad:
                raise ValueError(
                    "Acesso ultrapassa os limites da Scratchpad"
                )

            self._validar_alinhamento(endereco, tamanho)
            deslocamento = endereco - inicio_scratchpad
            self.scratchpad[deslocamento:deslocamento + tamanho] = (
                valor & ((1 << (tamanho * 8)) - 1)
            ).to_bytes(tamanho, byteorder="little")
            return

        if tamanho == 1:
            self.ram.write_u8(endereco, valor)
            return

        if tamanho == 2:
            self.ram.write_u16(endereco, valor)
            return

        if tamanho == 4:
            self.ram.write_u32(endereco, valor)
            return

        raise ValueError("Tamanho de escrita não suportado")

    def read_u8(self, endereco):
        endereco = self._traduzir_endereco(endereco)
        return self._ler_memoria(endereco, 1)

    def write_u8(self, endereco, valor):
        endereco = self._traduzir_endereco(endereco)
        self._escrever_memoria(endereco, valor, 1)

    def read_u16(self, endereco):
        endereco = self._traduzir_endereco(endereco)
        return self._ler_memoria(endereco, 2)

    def write_u16(self, endereco, valor):
        endereco = self._traduzir_endereco(endereco)
        self._escrever_memoria(endereco, valor, 2)

    def read_u32(self, endereco):
        endereco = self._traduzir_endereco(endereco)
        return self._ler_memoria(endereco, 4)

    def write_u32(self, endereco, valor):
        endereco = self._traduzir_endereco(endereco)
        self._escrever_memoria(endereco, valor, 4)
