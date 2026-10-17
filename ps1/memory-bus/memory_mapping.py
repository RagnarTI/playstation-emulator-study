
# Memory mapping and bus for the PlayStation 1.

class MemoryBus:
    """
    Barramento de memória do PlayStation 1.

    Responsabilidades:
    - Traduzir os aliases KSEG0 e KSEG1.
    - Identificar as regiões físicas.
    - Encaminhar acessos aos componentes implementados.
    - Sinalizar acessos a regiões não implementadas.
    """

    MASCARA_32 = 0xFFFFFFFF
    TAMANHO_RAM_FISICA = 0x00200000
    TAMANHO_ESPELHO_RAM = 0x00800000

    # Mapa físico. O endereço final é exclusivo.
    REGIOES_MEMORIA = (
        {
            "nome": "RAM",
            "inicio": 0x00000000,
            "fim": TAMANHO_ESPELHO_RAM,
            "dispositivo": "ram",
        },
        {
            "nome": "EXP1",
            "inicio": 0x1F000000,
            "fim": 0x1F800000,
            "dispositivo": "exp1",
        },
        {
            "nome": "Scratchpad",
            "inicio": 0x1F800000,
            "fim": 0x1F800400,
            "dispositivo": "scratchpad",
        },
        {
            "nome": "Registradores de I/O",
            "inicio": 0x1F801000,
            "fim": 0x1F802000,
            "dispositivo": "io",
        },
        {
            "nome": "EXP2",
            "inicio": 0x1F802000,
            "fim": 0x1F804000,
            "dispositivo": "exp2",
        },
        {
            "nome": "EXP3",
            "inicio": 0x1FA00000,
            "fim": 0x1FC00000,
            "dispositivo": "exp3",
        },
        {
            "nome": "BIOS",
            "inicio": 0x1FC00000,
            "fim": 0x1FC80000,
            "dispositivo": "bios",
        },
        {
            "nome": "Controle de cache",
            "inicio": 0xFFFE0000,
            "fim": 0xFFFE0200,
            "dispositivo": "cache_control",
        },
    )

    def __init__(self, ram, bios=None):
        self.ram = ram
        self.bios = bios

        # Memórias locais implementadas.
        self.scratchpad = bytearray(0x400)

        # Armazenamento provisório para regiões de hardware.
        # Isso NÃO implementa o comportamento real dos dispositivos.
        self.registradores_hardware = bytearray(0x1000)
        self.exp1 = bytearray(0x800000)
        self.exp2 = bytearray(0x2000)
        self.cache_control = bytearray(0x200)

    # ---------------------------------------------------------
    # Identificação de segmentos virtuais
    # ---------------------------------------------------------

    def identificar_segmento_virtual(self, endereco):
        endereco &= self.MASCARA_32

        if endereco <= 0x7FFFFFFF:
            return "KUSEG"
        if endereco <= 0x9FFFFFFF and endereco >= 0x80000000:
            return "KSEG0"
        if 0xA0000000 <= endereco <= 0xBFFFFFFF:
            return "KSEG1"

        return "KSEG2"

    def _traduzir_endereco(self, endereco):
        endereco &= self.MASCARA_32

        if 0x80000000 <= endereco <= 0x9FFFFFFF:
            return endereco - 0x80000000

        if 0xA0000000 <= endereco <= 0xBFFFFFFF:
            return endereco - 0xA0000000

        return endereco

    # ---------------------------------------------------------
    # Identificação de regiões físicas
    # ---------------------------------------------------------

    def identificar_regiao(self, endereco):
        endereco &= self.MASCARA_32

        for regiao in self.REGIOES_MEMORIA:
            if regiao["inicio"] <= endereco < regiao["fim"]:
                return regiao

        return None

    def _obter_regiao_do_acesso(self, endereco, tamanho):
        if tamanho not in (1, 2, 4):
            raise ValueError(
                f"Tamanho de acesso inválido: {tamanho}"
            )

        endereco_virtual = endereco & self.MASCARA_32
        endereco = self._traduzir_endereco(endereco_virtual)
        endereco_final = endereco + tamanho

        regiao = self.identificar_regiao(endereco)

        if regiao is None:
            raise ValueError(
                f"Endereço físico não mapeado: 0x{endereco:08X}"
            )

        # Impede que um acesso comece numa região e termine noutra.
        if endereco_final > regiao["fim"]:
            raise ValueError(
                f"Acesso atravessa o limite da região "
                f"{regiao['nome']}: 0x{endereco:08X}"
            )

        if (
            regiao["dispositivo"] == "scratchpad"
            and 0xA0000000 <= endereco_virtual <= 0xBFFFFFFF
        ):
            raise ValueError(
                "Scratchpad nao possui alias em KSEG1: "
                f"0x{endereco_virtual:08X}"
            )

        if regiao["dispositivo"] == "ram":
            endereco %= self.TAMANHO_RAM_FISICA

        return endereco, regiao

    def _validar_alinhamento(self, endereco, tamanho):
        if tamanho > 1 and endereco % tamanho != 0:
            raise ValueError(
                f"Acesso desalinhado: endereço 0x{endereco:08X}, "
                f"tamanho {tamanho}"
            )

    # ---------------------------------------------------------
    # Leitura
    # ---------------------------------------------------------

    def _ler_memoria(self, endereco, tamanho, busca_instrucao=False):
        endereco, regiao = self._obter_regiao_do_acesso(
            endereco, tamanho
        )

        self._validar_alinhamento(endereco, tamanho)

        dispositivo = regiao["dispositivo"]

        if busca_instrucao and dispositivo == "scratchpad":
            raise NotImplementedError(
                "Scratchpad nao e executavel; o tratamento do bus error "
                "arquitetural ainda nao esta implementado."
            )

        if dispositivo == "ram":
            if tamanho == 1:
                return self.ram.read_u8(endereco)
            if tamanho == 2:
                return self.ram.read_u16(endereco)
            return self.ram.read_u32(endereco)

        if dispositivo == "bios":
            if self.bios is None:
                raise RuntimeError(
                    "A BIOS nao foi conectada ao barramento."
                )

            offset = endereco - regiao["inicio"]

            if tamanho == 1:
                return self.bios.ler_u8(offset)

            if tamanho == 2:
                return self.bios.ler_u16(offset)

            if tamanho == 4:
                return self.bios.ler_u32(offset)

            raise ValueError(f"Tamanho de leitura inválido: {tamanho}")

        if dispositivo == "scratchpad":
            offset = endereco - regiao["inicio"]
            dados = self.scratchpad[offset:offset + tamanho]
            return int.from_bytes(dados, byteorder="little")

        if dispositivo == "io":
            offset = endereco - regiao["inicio"]
            dados = self.registradores_hardware[
                offset:offset + tamanho
            ]
            return int.from_bytes(dados, byteorder="little")

        if dispositivo == "exp1":
            offset = endereco - regiao["inicio"]

            return int.from_bytes(
                self.exp1[offset:offset + tamanho],
                byteorder="little"
            )

        if dispositivo == "exp2":
            offset = endereco - regiao["inicio"]
            dados = self.exp2[offset:offset + tamanho]
            return int.from_bytes(dados, byteorder="little")

        if dispositivo == "cache_control":
            offset = endereco - regiao["inicio"]
            dados = self.cache_control[offset:offset + tamanho]
            return int.from_bytes(dados, byteorder="little")

        raise NotImplementedError(
            f"Leitura ainda não implementada para "
            f"{regiao['nome']} em 0x{endereco:08X}"
        )

    def read_u8(self, endereco):
        return self._ler_memoria(endereco, 1)

    def read_u16(self, endereco):
        return self._ler_memoria(endereco, 2)

    def read_u32(self, endereco):
        return self._ler_memoria(endereco, 4)

    def fetch_u32(self, endereco):
        return self._ler_memoria(endereco, 4, busca_instrucao=True)

    # ---------------------------------------------------------
    # Escrita
    # ---------------------------------------------------------

    def _escrever_memoria(self, endereco, valor, tamanho):
        endereco, regiao = self._obter_regiao_do_acesso(
            endereco, tamanho
        )

        self._validar_alinhamento(endereco, tamanho)

        valor &= (1 << (tamanho * 8)) - 1
        dispositivo = regiao["dispositivo"]

        if dispositivo == "bios":
            raise PermissionError(
                f"Não é permitido escrever na BIOS: "
                f"0x{endereco:08X}"
            )

        if dispositivo == "ram":
            if tamanho == 1:
                self.ram.write_u8(endereco, valor)
            elif tamanho == 2:
                self.ram.write_u16(endereco, valor)
            else:
                self.ram.write_u32(endereco, valor)
            return

        if dispositivo == "scratchpad":
            offset = endereco - regiao["inicio"]
            self.scratchpad[offset:offset + tamanho] = (
                valor.to_bytes(tamanho, byteorder="little")
            )
            return

        if dispositivo == "io":
            offset = endereco - regiao["inicio"]
            self.registradores_hardware[
                offset:offset + tamanho
            ] = valor.to_bytes(tamanho, byteorder="little")
            return

        if dispositivo == "exp1":
            offset = endereco - regiao["inicio"]

            self.exp1[offset:offset + tamanho] = (
                valor & ((1 << (tamanho * 8)) - 1)
            ).to_bytes(tamanho, byteorder="little")

            return

        if dispositivo == "exp2":
            offset = endereco - regiao["inicio"]
            self.exp2[offset:offset + tamanho] = (
                valor.to_bytes(tamanho, byteorder="little")
            )
            return

        if dispositivo == "cache_control":
            offset = endereco - regiao["inicio"]
            self.cache_control[offset:offset + tamanho] = (
                valor.to_bytes(tamanho, byteorder="little")
            )
            return

        raise NotImplementedError(
            f"Escrita ainda não implementada para "
            f"{regiao['nome']} em 0x{endereco:08X}"
        )

    def write_u8(self, endereco, valor):
        self._escrever_memoria(endereco, valor, 1)

    def write_u16(self, endereco, valor):
        self._escrever_memoria(endereco, valor, 2)

    def write_u32(self, endereco, valor):
        self._escrever_memoria(endereco, valor, 4)
