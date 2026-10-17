class COP0:
    INDICES_LEITURA_RESERVADA = frozenset((0, 1, 2, 4, 10))
    TAR = 6
    DCIC = 7
    BADVADDR = 8
    STATUS = 12
    CAUSE = 13
    EPC = 14
    PRID = 15

    VETOR_EXCECAO = 0x80000080
    VETOR_EXCECAO_BOOT = 0xBFC00180
    MASCARA_BEV = 1 << 22
    STATUS_RESET = MASCARA_BEV

    # No COP0 do PlayStation, Cause só permite escrita nos bits de
    # interrupção por software (9:8). Status: campos graváveis documentados
    # para o núcleo LSI usado no PS1; bits reservados/PE/TS não são graváveis.
    MASCARA_CAUSE_ESCRITA = 0x00000300
    MASCARA_STATUS_ESCRITA = 0xF04FFF3F
    # Bits DCIC 6-11 e 16-22 são somente leitura e permanecem zero.
    MASCARA_DCIC_ESCRITA = 0xFF80F03F

    def __init__(self):
        self.registradores = [0] * 32
        self.registradores[self.STATUS] = self.STATUS_RESET

    def ler_registrador(self, numero):
        if not 0 <= numero < 32:
            raise ValueError("Numero de registrador COP0 invalido")

        return self.registradores[numero]

    def escrever_registrador(self, numero, valor):
        if not 0 <= numero < 32:
            raise ValueError("Numero de registrador COP0 invalido")

        valor &= 0xFFFFFFFF

        if numero in (
            self.TAR,
            self.BADVADDR,
            self.EPC,
            self.PRID,
        ):  # somente leitura
            return

        if numero == self.DCIC:
            self.registradores[numero] = valor & self.MASCARA_DCIC_ESCRITA
            return

        if numero == self.CAUSE:
            mascara = self.MASCARA_CAUSE_ESCRITA
            atual = self.registradores[numero]
            self.registradores[numero] = (
                (atual & ~mascara) | (valor & mascara)
            ) & 0xFFFFFFFF
            return

        if numero == self.STATUS:
            mascara = self.MASCARA_STATUS_ESCRITA
            atual = self.registradores[numero]
            self.registradores[numero] = (
                (atual & ~mascara) | (valor & mascara)
            ) & 0xFFFFFFFF
            return

        self.registradores[numero] = valor

    def registrar_excecao(
        self,
        codigo,
        endereco,
        delay_slot=False,
        badvaddr=None,
        destino_atrasado=None,
    ):
        if not 0 <= codigo <= 31:
            raise ValueError("Codigo de excecao COP0 invalido")

        causa = self.registradores[self.CAUSE]

        # Atualiza ExcCode (bits 6–2) e BD (bit 31).
        causa &= ~(0x1F << 2)
        causa &= ~(1 << 31)
        causa |= (codigo & 0x1F) << 2

        if delay_slot:
            causa |= 1 << 31
            # No PS1, BT só é significativo quando BD está definido.
            # destino_atrasado=None representa um branch não tomado.
            if destino_atrasado is None:
                causa &= ~(1 << 30)
            else:
                causa |= 1 << 30
                self.registradores[self.TAR] = destino_atrasado & 0xFFFFFFFF

        self.registradores[self.CAUSE] = causa & 0xFFFFFFFF

        # No delay slot, EPC aponta para a instrução de desvio anterior.
        if delay_slot:
            endereco_epc = (endereco - 4) & 0xFFFFFFFF
        else:
            endereco_epc = endereco & 0xFFFFFFFF

        self.registradores[self.EPC] = endereco_epc

        if badvaddr is not None:
            self.registradores[self.BADVADDR] = badvaddr & 0xFFFFFFFF

        # Atualiza o histórico dos modos de Status.
        self.entrar_em_excecao()

    def obter_vetor_excecao(self):
        status = self.registradores[self.STATUS]
        if status & self.MASCARA_BEV:
            return self.VETOR_EXCECAO_BOOT
        return self.VETOR_EXCECAO

    def entrar_em_excecao(self):
        status = self.registradores[self.STATUS]

        mascara_historico = 0x3F

        historico_anterior = status & mascara_historico
        historico_novo = (historico_anterior << 2) & mascara_historico

        status = (status & ~mascara_historico) | historico_novo

        self.registradores[self.STATUS] = status & 0xFFFFFFFF

    def rfe(self):
        status = self.registradores[self.STATUS]

        mascara_historico = 0x3F
        historico_anterior = status & mascara_historico
        historico_restaurado = historico_anterior >> 2

        status = (
            (status & ~mascara_historico)
            | historico_restaurado
        )

        self.registradores[self.STATUS] = status & 0xFFFFFFFF
