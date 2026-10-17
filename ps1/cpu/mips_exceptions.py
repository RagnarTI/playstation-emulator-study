class MIPSException(Exception):
    """Classe-base para exceções arquiteturais do MIPS R3000A."""

    codigo_cop0 = None

    def __init__(self, *args, endereco=None):
        super().__init__(*args)
        self.endereco = endereco

class IntegerOverflow(MIPSException):
    """Overflow aritmético em uma instrução MIPS com sinal."""

    codigo_cop0 = 12

class EnderecoDesalinhadoError(MIPSException, ValueError):
    """Erro ao acessar uma palavra em endereço desalinhado."""

    def __init__(self, *args, endereco=None, codigo_cop0=4):
        super().__init__(*args, endereco=endereco)
        self.codigo_cop0 = codigo_cop0


class SyscallError(MIPSException):
    """Exceção arquitetural causada pela instrução SYSCALL."""

    codigo_cop0 = 8


class BreakpointError(MIPSException):
    """Exceção arquitetural causada pela instrução BREAK."""

    codigo_cop0 = 9


class InstrucaoReservadaError(MIPSException, NotImplementedError):
    """Instrução reservada; mantém compatibilidade com NotImplementedError."""

    codigo_cop0 = 10
