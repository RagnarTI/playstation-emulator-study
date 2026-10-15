class MIPSException(Exception):
    """Classe-base para exceções arquiteturais do MIPS R3000A."""

class IntegerOverflow(MIPSException):
    """Overflow aritmético em uma instrução MIPS com sinal."""

class EnderecoDesalinhadoError(MIPSException):
    """Erro ao acessar uma palavra em endereço desalinhado."""