from .cop0 import COP0
from .mips_interpreter import (
    executar_programa,
    EstadoEspecial
)
from .mips_exceptions import MIPSException

class CPU:
    PC_INICIAL = 0xBFC00000

    def __init__(self):
        self.pc = self.PC_INICIAL
        self.registradores = [0] * 32
        self.estado_especial = EstadoEspecial()
        self.cop0 = COP0()

        self.delay_slot_ativo = False
        self.destino_atrasado = None

        self.estado_delay = {
            "delay_slot_ativo": False,
            "destino_atrasado": None,
        }

    def executar( self, memoria, enderecos_programa, limite=100, um_passo=False, ):
        estado_execucao = {"pc": self.pc}
        excecao_mips_tratada = False

        try:
            self.registradores, self.pc = executar_programa(
                memoria,
                enderecos_programa,
                self.pc,
                self.registradores,
                limite=limite,
                estado_especial=self.estado_especial,
                retornar_pc=True,
                estado_delay=self.estado_delay,
                um_passo=um_passo,
                cop0=self.cop0,
                estado_execucao=estado_execucao,
                adiar_erro_destino_desalinhado=True,
            )
        except MIPSException as erro:
            codigo = erro.codigo_cop0

            # A classe-base pode representar um erro interno sem código
            # arquitetural; somente causas MIPS identificadas são tratadas.
            if codigo is None:
                raise

            self.pc = estado_execucao["pc"]
            delay_slot = self.estado_delay["delay_slot_ativo"]

            self.cop0.registrar_excecao(
                codigo,
                self.pc,
                delay_slot=delay_slot,
                badvaddr=erro.endereco,
                destino_atrasado=(
                    self.estado_delay["destino_atrasado"]
                    if delay_slot else None
                ),
            )

            self.pc = self.cop0.obter_vetor_excecao()
            self.registradores[0] = 0
            self.estado_delay["delay_slot_ativo"] = False
            self.estado_delay["destino_atrasado"] = None
            self.delay_slot_ativo = False
            self.destino_atrasado = None
            excecao_mips_tratada = True
        finally:
            # Preserve o último PC publicado após uma instrução concluída
            # quando um erro Python escapar, sem convertê-lo em exceção MIPS.
            if not excecao_mips_tratada:
                self.pc = estado_execucao["pc"]
