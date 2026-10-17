
MASCARA_32 = 0xFFFFFFFF

# !! 1. Codificação das instruções
def encode_r(rs, rt, rd, funct, shamt=0):
    return (
        (rs << 21)
        | (rt << 16)
        | (rd << 11)
        | (shamt << 6)
        | funct
    )

def encode_i(opcode, rs, rt, immediate):
    return (
        (opcode << 26)
        | (rs << 21)
        | (rt << 16)
        | (immediate & 0xFFFF)
    )

# !! 2. Conversão de valores com sinal
def signed_32(valor):
    valor &= MASCARA_32

    if valor & 0x80000000:
        valor -= 0x100000000

    return valor

def signed_16(valor):
    valor &= 0xFFFF

    if valor & 0x8000:
        valor -= 0x10000

    return valor

# !! 3. Interpretador
from .mips_exceptions import *

class EstadoEspecial:
    def __init__(self):
        self.hi = 0
        self.lo = 0

def decodificar_instrucao(instrucao):
    return {
        "opcode": (instrucao >> 26) & 0x3F,
        "rs": (instrucao >> 21) & 0x1F,
        "rt": (instrucao >> 16) & 0x1F,
        "rd": (instrucao >> 11) & 0x1F,
        "shamt": (instrucao >> 6) & 0x1F,
        "funct": instrucao & 0x3F,
        "immediate": signed_16(instrucao),
    }

def executar_operacao_logica(funct, a, b): # !! AND, OR, XOR, NOR
    if funct == 0x24:       # AND
        return a & b

    elif funct == 0x25:     # OR
        return a | b

    elif funct == 0x26:     # XOR
        return a ^ b

    elif funct == 0x27:     # NOR
        return (~(a | b)) & MASCARA_32

    else:
        raise NotImplementedError(
            f"Operacao logica nao implementada: 0x{funct:02X}"
        )

def executar_deslocamento(funct, valor, shamt): # !! SLL, SRL, SRA
    if funct == 0x00:       # SLL
        return (valor << shamt) & MASCARA_32

    elif funct == 0x02:     # SRL
        return (valor >> shamt) & MASCARA_32

    elif funct == 0x03:     # SRA
        return (signed_32(valor) >> shamt) & MASCARA_32

    else:
        raise NotImplementedError(
            f"Deslocamento nao implementado: 0x{funct:02X}"
        )

def executar_soma_subtracao(funct, a, b):  # ADD, SUB
    if funct == 0x20:  # ADD
        resultado = signed_32(a) + signed_32(b)

        if not (-0x80000000 <= resultado <= 0x7FFFFFFF):
            raise IntegerOverflow("Overflow em ADD")

        return resultado & MASCARA_32

    elif funct == 0x22:  # SUB
        resultado = signed_32(a) - signed_32(b)

        if not (-0x80000000 <= resultado <= 0x7FFFFFFF):
            raise IntegerOverflow("Overflow em SUB")

        return resultado & MASCARA_32

    else:
        raise NotImplementedError(
            f"Soma/subtracao nao implementada: 0x{funct:02X}"
        )

def executar_soma_subtracao_sem_overflow(funct, a, b):  # !! ADDU, SUBU
    if funct == 0x21:  # ADDU
        resultado = (a & MASCARA_32) + (b & MASCARA_32)
        return resultado & MASCARA_32

    elif funct == 0x23:  # SUBU
        resultado = (a & MASCARA_32) - (b & MASCARA_32)
        return resultado & MASCARA_32

    else:
        raise NotImplementedError(
            f"Soma/subtracao sem overflow nao implementada: 0x{funct:02X}"
        )

def executar_comparacao(funct, a, b): # !! STL, SLTU
    if funct == 0x2A:       # SLT
        return 1 if signed_32(a) < signed_32(b) else 0

    elif funct == 0x2B:  # SLTU
        return 1 if (a & MASCARA_32) < (b & MASCARA_32) else 0

    else:
        raise NotImplementedError(
            f"Comparacao nao implementada: 0x{funct:02X}"
        )

def executar_multiplicacao(funct, a, b): # !! MULT, MULTU
    if funct == 0x18:       # MULT
        resultado = signed_32(a) * signed_32(b)

    elif funct == 0x19:     # MULTU
        resultado = (a & MASCARA_32) * (b & MASCARA_32)

    else:
        raise NotImplementedError(
            f"Multiplicacao nao implementada: 0x{funct:02X}"
        )

    resultado &= 0xFFFFFFFFFFFFFFFF

    lo = resultado & MASCARA_32
    hi = (resultado >> 32) & MASCARA_32

    return hi, lo

def executar_divisao(funct, a, b): # !! DIV, DIVU
    if funct == 0x1A:       # DIV
        dividendo = signed_32(a)
        divisor = signed_32(b)

        if divisor == 0:
            lo = (
                0xFFFFFFFF
                if dividendo >= 0
                else 0x00000001
            )
            hi = dividendo & MASCARA_32

        else:
            quociente = abs(dividendo) // abs(divisor)

            if (dividendo < 0) != (divisor < 0):
                quociente = -quociente

            resto = dividendo - quociente * divisor

            lo = quociente & MASCARA_32
            hi = resto & MASCARA_32

    elif funct == 0x1B:     # DIVU
        dividendo = a & MASCARA_32
        divisor = b & MASCARA_32

        if divisor == 0:
            lo = 0xFFFFFFFF
            hi = dividendo
        else:
            lo = (dividendo // divisor) & MASCARA_32
            hi = (dividendo % divisor) & MASCARA_32

    else:
        raise NotImplementedError(
            f"Divisao nao implementada: 0x{funct:02X}"
        )

    return hi, lo

def executar_salto_registrador(
    funct,
    destino,
    pc_atual,
    no_delay_slot,
    validar_alinhamento=True,
):
    if funct not in (0x08, 0x09):
        raise NotImplementedError(
            f"Salto por registrador nao implementado: 0x{funct:02X}"
        )

    nome = "JR" if funct == 0x08 else "JALR"

    if no_delay_slot:
        raise NotImplementedError(
            f"{nome} dentro de delay slot nao suportado."
        )

    destino &= MASCARA_32

    if validar_alinhamento and destino % 4 != 0:
        raise EnderecoDesalinhadoError(
            f"Destino de {nome} em endereco desalinhado.",
            endereco=destino,
            codigo_cop0=None,
        )

    link = None

    if funct == 0x09:
        link = (pc_atual + 8) & MASCARA_32

    return destino, link

def calcular_destino_salto(instrucao, pc_atual):
    return (
        ((pc_atual + 4) & 0xF0000000)
        | ((instrucao & 0x03FFFFFF) << 2)
    )

def calcular_destino_desvio(pc_atual, immediate):
    return (
        pc_atual + 4 + (immediate << 2)
    ) & MASCARA_32

def executar_lui(instrucao):
    imediato = instrucao & 0xFFFF
    return (imediato << 16) & MASCARA_32

def executar_addi(valor, immediate):
    resultado = signed_32(valor) + immediate

    if not (-0x80000000 <= resultado <= 0x7FFFFFFF):
        raise IntegerOverflow("Overflow em ADDI")

    return resultado & MASCARA_32

def executar_addiu(valor, immediate):
    return (valor + immediate) & MASCARA_32

def calcular_endereco_efetivo(
    base,
    immediate,
    instrucao,
    alinhamento=4,
):
    endereco = (base + immediate) & MASCARA_32

    if endereco % alinhamento != 0:
        codigo_cop0 = 5 if instrucao.startswith("S") else 4
        raise EnderecoDesalinhadoError(
            f"{instrucao} em endereco desalinhado: "
            f"0x{endereco:08X}",
            endereco=endereco,
            codigo_cop0=codigo_cop0,
        )

    return endereco

def executar_deslocamento_variavel(funct, valor, quantidade):
    quantidade = quantidade & 0x1F
    valor = valor & MASCARA_32

    if funct == 0x04:  # SLLV
        resultado = valor << quantidade

    elif funct == 0x06:  # SRLV
        resultado = valor >> quantidade

    elif funct == 0x07:  # SRAV
        resultado = signed_32(valor) >> quantidade

    else:
        raise NotImplementedError(
            f"Deslocamento variavel nao implementado: 0x{funct:02X}"
        )

    return resultado & MASCARA_32

def executar_lwl_lwr(opcode, valor_registrador, palavra_memoria, endereco):
    deslocamento = endereco & 0x03
    valor_registrador &= MASCARA_32
    palavra_memoria &= MASCARA_32

    if opcode == 0x22:  # LWL
        deslocamento_bits = (3 - deslocamento) * 8
        mascara_preservar = (1 << deslocamento_bits) - 1

        resultado = (
            (valor_registrador & mascara_preservar)
            | ((palavra_memoria << deslocamento_bits) & MASCARA_32)
        )

    elif opcode == 0x26:  # LWR
        deslocamento_bits = deslocamento * 8
        mascara_substituir = (1 << ((4 - deslocamento) * 8)) - 1
        mascara_preservar = MASCARA_32 ^ mascara_substituir

        resultado = (
            (valor_registrador & mascara_preservar)
            | ((palavra_memoria >> deslocamento_bits) & mascara_substituir)
        )

    else:
        raise NotImplementedError(
            f"LWL/LWR nao implementado: 0x{opcode:02X}"
        )

    return resultado & MASCARA_32

def executar_swl_swr(opcode, valor_registrador, palavra_memoria, endereco):
    deslocamento = endereco & 0x03
    valor_registrador &= MASCARA_32
    palavra_memoria &= MASCARA_32

    if opcode == 0x2A:  # SWL
        deslocamento_bits = (3 - deslocamento) * 8
        mascara_substituir = (1 << ((deslocamento + 1) * 8)) - 1
        mascara_preservar = MASCARA_32 ^ mascara_substituir

        resultado = (
            (palavra_memoria & mascara_preservar)
            | (
                (valor_registrador >> deslocamento_bits)
                & mascara_substituir
            )
        )

    elif opcode == 0x2E:  # SWR
        deslocamento_bits = deslocamento * 8
        mascara_substituir = (
            MASCARA_32 << deslocamento_bits
        ) & MASCARA_32
        mascara_preservar = MASCARA_32 ^ mascara_substituir

        resultado = (
            (palavra_memoria & mascara_preservar)
            | (
                (valor_registrador << deslocamento_bits)
                & mascara_substituir
            )
        )

    else:
        raise NotImplementedError(
            f"SWL/SWR nao implementado: 0x{opcode:02X}"
        )

    return resultado & MASCARA_32

def executar_programa( memoria, enderecos_programa, pc_inicial, registradores,
                    limite=100, estado_especial=None, retornar_pc=False, estado_delay=None, um_passo=False, cop0=None, estado_execucao=None, adiar_erro_destino_desalinhado=False, ):

    pc = pc_inicial
    passos = 0

    if estado_execucao is not None:
        estado_execucao["pc"] = pc

    # Controla o branch delay slot.
    if estado_delay is None:
        estado_delay = {
            "delay_slot_ativo": False,
            "destino_atrasado": None,
        }

    delay_slot_ativo = estado_delay["delay_slot_ativo"]
    destino_atrasado = estado_delay["destino_atrasado"]

    if estado_especial is None:
        estado_especial = EstadoEspecial()

    while passos < limite:
        pc_atual = pc

        # Fetch
        if pc_atual & 0x03:
            raise EnderecoDesalinhadoError(
                f"Fetch em endereco desalinhado: 0x{pc_atual:08X}",
                endereco=pc_atual,
                codigo_cop0=4,
            )

        buscar_instrucao = getattr(memoria, "fetch_u32", None)
        if callable(buscar_instrucao):
            instrucao = buscar_instrucao(pc_atual)
        else:
            instrucao = memoria.read_u32(pc_atual)

        # Guarda o estado do branch anterior.
        no_delay_slot = delay_slot_ativo
        destino = destino_atrasado

        delay_slot_ativo = False
        destino_atrasado = None

        proximo_pc = (pc_atual + 4) & MASCARA_32

        # Decode
        campos = decodificar_instrucao(instrucao)

        opcode = campos["opcode"]
        rs = campos["rs"]
        rt = campos["rt"]
        rd = campos["rd"]
        shamt = campos["shamt"]
        funct = campos["funct"]
        immediate = campos["immediate"]

        print(
            f"\nPC=0x{pc_atual:08X} "
            f"Instrucao=0x{instrucao:08X}"
        )

        # Execute: instruções R-type

        if opcode == 0x00:
            a = registradores[rs]
            b = registradores[rt]

            if funct in (0x00, 0x02, 0x03):
                resultado = executar_deslocamento(funct, b, shamt)

                if rd != 0:
                    registradores[rd] = resultado

            # SLLV, SRLV, SRAV
            elif funct in (0x04, 0x06, 0x07):
                resultado = executar_deslocamento_variavel(
                    funct, b, a
                )

                if rd != 0:
                    registradores[rd] = resultado

            # !! JR, JARL
            elif funct in (0x08, 0x09):
                destino_salto, link = executar_salto_registrador(
                    funct,
                    a,
                    pc_atual,
                    no_delay_slot,
                    validar_alinhamento=(
                        not adiar_erro_destino_desalinhado
                    ),
                )

                destino_atrasado = destino_salto
                delay_slot_ativo = True

                print(
                    f"[JR] PC=0x{pc_atual:08X} "
                    f"destino_salto=0x{destino_salto:08X} "
                    f"delay_slot_ativo={delay_slot_ativo}"
                )

                if funct == 0x09 and rd != 0:
                    registradores[rd] = link

                destino_atrasado = destino_salto
                delay_slot_ativo = True

            # !! MFHI / MTHI / MFLO / MTLO
            elif funct == 0x10:  # MFHI
                if rd != 0:
                    registradores[rd] = estado_especial.hi

            elif funct == 0x11:  # MTHI
                estado_especial.hi = registradores[rs] & MASCARA_32

            elif funct == 0x12:  # MFLO
                if rd != 0:
                    registradores[rd] = estado_especial.lo

            elif funct == 0x13:  # MTLO
                estado_especial.lo = registradores[rs] & MASCARA_32

            # !! ADD, SUB
            elif funct in (0x20, 0x22):
                resultado = executar_soma_subtracao(funct, a, b)

                if rd != 0:
                    registradores[rd] = resultado

            # !! ADDU, SUBU
            elif funct in (0x21, 0x23):
                resultado = executar_soma_subtracao_sem_overflow(funct, a, b)

                if rd != 0:
                    registradores[rd] = resultado

            elif funct in (0x24, 0x25, 0x26, 0x27):
                resultado = executar_operacao_logica(funct, a, b)

                if rd != 0:
                    registradores[rd] = resultado

            elif funct in (0x2A, 0x2B):
                resultado = executar_comparacao(funct, a, b)

                if rd != 0:
                    registradores[rd] = resultado

                print(
                    f"[SLTU] PC=0x{pc_atual:08X} "
                    f"$2=0x{registradores[2]:08X} "
                    f"$3=0x{registradores[3]:08X} "
                    f"$1=0x{registradores[1]:08X}"
                )
            
            elif funct in (0x18, 0x19):
                hi, lo = executar_multiplicacao(funct, a, b)

                estado_especial.hi = hi
                estado_especial.lo = lo

            elif funct in (0x1A, 0x1B):
                hi, lo = executar_divisao(funct, a, b)

                estado_especial.hi = hi
                estado_especial.lo = lo

            elif funct == 0x0C:  # SYSCALL
                raise SyscallError("Excecao SYSCALL")

            elif funct == 0x0D:  # BREAK
                raise BreakpointError("Excecao BREAK")

            else:
                raise InstrucaoReservadaError(
                    f"Instrucao R-type nao implementada: "
                    f"funct=0x{funct:02X}"
                )

        # !! J - Jump
        elif opcode == 0x02:
            if no_delay_slot:
                raise NotImplementedError(
                    "J dentro de delay slot nao suportado."
                )

            destino_atrasado = calcular_destino_salto(
                instrucao,
                pc_atual,
            )
            delay_slot_ativo = True

        # !! JAL - Jump and Link
        elif opcode == 0x03:
            if no_delay_slot:
                raise NotImplementedError(
                    "JAL dentro de delay slot nao suportado."
                )

            registradores[31] = (pc_atual + 8) & MASCARA_32

            destino_atrasado = calcular_destino_salto(
                instrucao,
                pc_atual,
            )
            delay_slot_ativo = True

        # !! ADDI
        elif opcode == 0x08:
            resultado = executar_addi(
                registradores[rs],
                immediate,
            )

            if rt != 0:
                registradores[rt] = resultado

            if rt == 10:
                print(
                    f"[T2] PC=0x{pc_atual:08X} "
                    f"$t2=0x{registradores[10]:08X}"
                )

        # !! ADDIU
        elif opcode == 0x09:
            resultado = executar_addiu(
                registradores[rs],
                immediate,
            )

            if rt != 0:
                registradores[rt] = resultado

        # !! COP0
        elif opcode == 0x10:
            if cop0 is None:
                raise RuntimeError(
                    "COP0 nao foi conectado ao interpretador"
                )

            # MFC0: Move From Coprocessor 0
            if rs == 0x00 and (instrucao & 0x7FF) == 0:
                if rd in cop0.INDICES_LEITURA_RESERVADA:
                    raise InstrucaoReservadaError(
                        f"Leitura MFC0 do registrador COP0 {rd} reservada."
                    )

                valor = cop0.ler_registrador(rd)

                if rt != 0:
                    registradores[rt] = valor

            # MTC0: Move To Coprocessor 0
            elif rs == 0x04 and (instrucao & 0x7FF) == 0:
                valor = registradores[rt]
                cop0.escrever_registrador(rd, valor)

            # RFE: Restore From Exception
            elif (
                rs == 0x10
                and rt == 0
                and rd == 0
                and shamt == 0
                and funct == 0x10
            ):
                cop0.rfe()

            else:
                raise InstrucaoReservadaError(
                    f"Instrucao COP0 nao implementada: "
                    f"rs=0x{rs:X}, funct=0x{funct:X}"
                )

            registradores[0] = 0

        # !! SLTI
        elif opcode == 0x0A:
            a = registradores[rs]
            resultado = executar_comparacao(
                0x2A,
                a,
                immediate,
            )

            if rt != 0:
                registradores[rt] = resultado

        # !! SLTIU
        elif opcode == 0x0B:
            a = registradores[rs]
            imediato_sem_sinal = immediate & MASCARA_32
            resultado = executar_comparacao(
                0x2B,
                a,
                imediato_sem_sinal,
            )

            if rt != 0:
                registradores[rt] = resultado

        # !! ANDI
        elif opcode == 0x0C:
            imediato = instrucao & 0xFFFF
            resultado = executar_operacao_logica(
                0x24,
                registradores[rs],
                imediato,
            )

            if rt != 0:
                registradores[rt] = resultado

        # !! ORI
        elif opcode == 0x0D:
            imediato = instrucao & 0xFFFF
            resultado = executar_operacao_logica(
                0x25,
                registradores[rs],
                imediato,
            )

            if rt != 0:
                registradores[rt] = resultado

        # !! XORI
        elif opcode == 0x0E:
            imediato = instrucao & 0xFFFF
            resultado = executar_operacao_logica(
                0x26,
                registradores[rs],
                imediato,
            )

            if rt != 0:
                registradores[rt] = resultado

        # !! LUI
        elif opcode == 0x0F:
            resultado = executar_lui(instrucao)

            if rt != 0:
                registradores[rt] = resultado

        # !! LW
        elif opcode == 0x23:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "LW",
            )

            resultado = memoria.read_u32(endereco)

            if rt != 0:
                registradores[rt] = resultado

        # !! SW
        elif opcode == 0x2B:

            # print(f"rs = {rs}, valor = 0x{registradores[rs]:08X}")
            # print(f"rt = {rt}, valor = 0x{registradores[rt]:08X}")
            # print(f"Instrucao = 0x{instrucao:08X}")

            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "SW",
            )

            if 0xBFC00230 <= pc_atual <= 0xBFC00250:
                print(
                    f"PC=0x{pc_atual:08X} "
                    f"Instrucao=0x{instrucao:08X} "
                    f"opcode=0x{opcode:02X} "
                    f"rs={rs} rt={rt} rd={rd} "
                    f"immediate=0x{immediate & 0xFFFF:04X} "
                    f"$t2=0x{registradores[10]:08X}"
                )

            memoria.write_u32(
                endereco,
                registradores[rt],
            )

        # !! LB
        elif opcode == 0x20:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "LB",
                alinhamento=1,
            )

            resultado = memoria.read_u8(endereco)

            if resultado & 0x80:
                resultado |= 0xFFFFFF00

            if rt != 0:
                registradores[rt] = resultado

        # !! LBU
        elif opcode == 0x24:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "LBU",
                alinhamento=1,
            )

            resultado = memoria.read_u8(endereco)

            if rt != 0:
                registradores[rt] = resultado

        # !! LH
        elif opcode == 0x21:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "LH",
                alinhamento=2,
            )

            resultado = memoria.read_u16(endereco)

            if resultado & 0x8000:
                resultado |= 0xFFFF0000

            if rt != 0:
                registradores[rt] = resultado

        # !! LHU
        elif opcode == 0x25:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "LHU",
                alinhamento=2,
            )

            resultado = memoria.read_u16(endereco)

            if rt != 0:
                registradores[rt] = resultado

        # !! SB
        elif opcode == 0x28:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "SB",
                alinhamento=1,
            )

            memoria.write_u8(
                endereco,
                registradores[rt],
            )

        # !! SH
        elif opcode == 0x29:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "SH",
                alinhamento=2,
            )

            memoria.write_u16(
                endereco,
                registradores[rt],
            )

        # !! LWL
        elif opcode == 0x22:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "LWL",
                alinhamento=1,
            )

            endereco_alinhado = endereco & ~0x03
            palavra_memoria = memoria.read_u32(endereco_alinhado)

            resultado = executar_lwl_lwr(
                opcode,
                registradores[rt],
                palavra_memoria,
                endereco,
            )

            if rt != 0:
                registradores[rt] = resultado

        # !! LWR
        elif opcode == 0x26:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "LWR",
                alinhamento=1,
            )
            endereco_alinhado = endereco & ~0x03
            palavra_memoria = memoria.read_u32(endereco_alinhado)
            resultado = executar_lwl_lwr(
                opcode, registradores[rt], palavra_memoria, endereco
            )
            if rt != 0:
                registradores[rt] = resultado


            if rt != 0:
                registradores[rt] = resultado

        # !! SWL
        elif opcode == 0x2A:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "SWL",
                alinhamento=1,
            )
            endereco_alinhado = endereco & ~0x03
            palavra_memoria = memoria.read_u32(endereco_alinhado)

            resultado = executar_swl_swr(
                opcode,
                registradores[rt],
                palavra_memoria,
                endereco,
            )

            memoria.write_u32(endereco_alinhado, resultado)

        # !! SWR
        elif opcode == 0x2E:
            endereco = calcular_endereco_efetivo(
                registradores[rs],
                immediate,
                "SWR",
                alinhamento=1,
            )
            endereco_alinhado = endereco & ~0x03
            palavra_memoria = memoria.read_u32(endereco_alinhado)

            resultado = executar_swl_swr(
                opcode,
                registradores[rt],
                palavra_memoria,
                endereco,
            )

            memoria.write_u32(endereco_alinhado, resultado)

        # !! BEQ
        elif opcode == 0x04:
            if no_delay_slot:
                raise NotImplementedError(
                    "BEQ dentro de delay slot nao suportado."
                )

            delay_slot_ativo = True
            desvio_tomado = registradores[rs] == registradores[rt]

            destino_log = None

            if desvio_tomado:
                destino_atrasado = calcular_destino_desvio(
                    pc_atual,
                    immediate,
                )
                destino_log = destino_atrasado

            print(
                f"[BEQ] PC=0x{pc_atual:08X} "
                f"rs=${rs}=0x{registradores[rs]:08X} "
                f"rt=${rt}=0x{registradores[rt]:08X} "
                f"tomado={desvio_tomado} "
                f"destino="
                f"{f'0x{destino_log:08X}' if destino_log is not None else 'N/A'}"
            )

        # !! BNE
        elif opcode == 0x05:
            if no_delay_slot:
                raise NotImplementedError(
                    "BNE dentro de delay slot nao suportado."
                )

            delay_slot_ativo = True
            desvio_tomado = registradores[rs] != registradores[rt]

            destino_log = None

            if desvio_tomado:
                destino_atrasado = calcular_destino_desvio(
                    pc_atual,
                    immediate,
                )
                destino_log = destino_atrasado

            print(
                f"[BNE] PC=0x{pc_atual:08X} "
                f"rs=${rs}=0x{registradores[rs]:08X} "
                f"rt=${rt}=0x{registradores[rt]:08X} "
                f"tomado={desvio_tomado} "
                f"destino="
                f"{f'0x{destino_log:08X}' if destino_log is not None else 'N/A'}"
            )

        # !! BLEZ
        elif opcode == 0x06:
            if rt != 0:
                raise InstrucaoReservadaError(
                    "BLEZ com campo rt invalido."
                )

            if no_delay_slot:
                raise NotImplementedError(
                    "BLEZ dentro de delay slot nao suportado."
                )

            delay_slot_ativo = True

            if signed_32(registradores[rs]) <= 0:
                destino_atrasado = calcular_destino_desvio(
                    pc_atual,
                    immediate,
                )

        # !! BGTZ
        elif opcode == 0x07:
            if rt != 0:
                raise InstrucaoReservadaError(
                    "BGTZ com campo rt invalido."
                )
            
            if no_delay_slot:
                raise NotImplementedError(
                    "BGTZ dentro de delay slot nao suportado."
                )

            delay_slot_ativo = True

            if signed_32(registradores[rs]) > 0:
                destino_atrasado = calcular_destino_desvio(
                    pc_atual,
                    immediate,
                )

        # !! REGIMM
        elif opcode == 0x01:

            # !! BLTZ
            if rt == 0x00:
                if no_delay_slot:
                    raise NotImplementedError(
                        "BLTZ dentro de delay slot nao suportado."
                    )

                delay_slot_ativo = True

                if signed_32(registradores[rs]) < 0:
                    destino_atrasado = calcular_destino_desvio(
                        pc_atual,
                        immediate,
                    )

            # !! BGEZ
            elif rt == 0x01:
                if no_delay_slot:
                    raise NotImplementedError(
                        "BGEZ dentro de delay slot nao suportado."
                    )

                delay_slot_ativo = True

                if signed_32(registradores[rs]) >= 0:
                    destino_atrasado = calcular_destino_desvio(
                        pc_atual,
                        immediate,
                    )

            # !! BLTZAL
            elif rt == 0x10:
                if no_delay_slot:
                    raise NotImplementedError(
                        "BLTZAL dentro de delay slot nao suportado."
                    )

                registradores[31] = (
                    pc_atual + 8
                ) & MASCARA_32

                delay_slot_ativo = True

                if signed_32(registradores[rs]) < 0:
                    destino_atrasado = calcular_destino_desvio(
                        pc_atual,
                        immediate,
                    )

            # !! BGEZAL
            elif rt == 0x11:
                if no_delay_slot:
                    raise NotImplementedError(
                        "BGEZAL dentro de delay slot nao suportado."
                    )

                registradores[31] = (
                    pc_atual + 8
                ) & MASCARA_32

                delay_slot_ativo = True

                if signed_32(registradores[rs]) >= 0:
                    destino_atrasado = calcular_destino_desvio(
                        pc_atual,
                        immediate,
                    )

            else:
                raise InstrucaoReservadaError(
                    f"REGIMM nao implementado: rt=0x{rt:02X}"
                )

        else:
            print(f"PC:        0x{pc_atual:08X}")
            print(f"Instrução: 0x{instrucao:08X}")
            print(f"Opcode:    0x{opcode:02X}")
            print(f"rs:        {rs}")
            print(f"rt:        {rt}")
            print(f"rd:        {rd}")
            print(f"funct:     0x{funct:02X}")

            if opcode in (
                0x11, 0x12, 0x13,  # COP1, COP2, COP3
                0x30, 0x31, 0x32, 0x33, 0x35,  # LWCz
                0x38, 0x39, 0x3A, 0x3B, 0x3D,  # SWCz
            ):
                raise NotImplementedError(
                    f"Opcode de coprocessador nao implementado: "
                    f"0x{opcode:02X}"
                )

            raise InstrucaoReservadaError(
                f"Opcode reservado: 0x{opcode:02X}"
            )

        # $zero sempre deve continuar valendo zero.
        registradores[0] = 0

        # Depois do delay slot, aplica o destino
        # se o branch anterior foi tomado.
        if no_delay_slot and destino is not None:
            proximo_pc = destino

        if pc_atual in (0xBFC039A4, 0xBFC039A8, 0xBFC01A78):
            print(
                f"[A-RETORNO] PC=0x{pc_atual:08X} "
                f"instrucao=0x{instrucao:08X} "
                f"no_delay_slot={no_delay_slot} "
                f"destino={destino} "
                f"proximo_pc=0x{proximo_pc:08X}"
            )

        pc = proximo_pc
        passos += 1

        if estado_execucao is not None:
            estado_execucao["pc"] = pc

        if pc_atual in (0xBFC039A4, 0xBFC039A8, 0xBFC01A78):
            print(
                f"[B-RETORNO] PC=0x{pc_atual:08X} "
                f"instrucao=0x{instrucao:08X} "
                f"no_delay_slot={no_delay_slot} "
                f"destino={destino} "
                f"proximo_pc=0x{proximo_pc:08X}"
            )

        estado_delay["delay_slot_ativo"] = delay_slot_ativo
        estado_delay["destino_atrasado"] = destino_atrasado

        if um_passo:
            print(f"[FIM-LOOP] PC=0x{pc:08X} passos={passos}")
            break

    if passos >= limite:
        print("\nLimite de instrucoes atingido.")

    print("\n--- Fim da execucao ---")
    print(f"Instrucoes executadas: {passos}")
    print(f"PC final: 0x{pc:08X}")

    if retornar_pc:
        return registradores, pc

    return registradores
