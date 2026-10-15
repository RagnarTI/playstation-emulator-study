
MASCARA_32 = 0xFFFFFFFF

# ----------------------------------------
# 1. Codificação das instruções
# ----------------------------------------
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

# ----------------------------------------
# 2. Conversão de valores com sinal
# ----------------------------------------
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

# ----------------------------------------
# 3. Interpretador
# ----------------------------------------
from mips_exceptions import *

class EstadoEspecial:
    def __init__(self):
        self.hi = 0
        self.lo = 0
    

def executar_programa( memoria, enderecos_programa, pc_inicial, registradores,
                    limite=100, estado_especial=None, retornar_pc=False ):

    pc = pc_inicial
    passos = 0

    # Controla o branch delay slot.
    delay_slot_ativo = False
    destino_atrasado = None

    if estado_especial is None:
        estado_especial = EstadoEspecial()

    while pc in enderecos_programa and passos < limite:
        pc_atual = pc

        # Fetch
        instrucao = memoria.read_u32(pc_atual)

        # Guarda o estado do branch anterior.
        no_delay_slot = delay_slot_ativo
        destino = destino_atrasado

        delay_slot_ativo = False
        destino_atrasado = None

        proximo_pc = (pc_atual + 4) & MASCARA_32

        # Decode
        opcode = (instrucao >> 26) & 0x3F
        rs = (instrucao >> 21) & 0x1F
        rt = (instrucao >> 16) & 0x1F
        rd = (instrucao >> 11) & 0x1F
        shamt = (instrucao >> 6) & 0x1F
        funct = instrucao & 0x3F
        immediate = signed_16(instrucao)

        print(
            f"\nPC=0x{pc_atual:08X} "
            f"Instrucao=0x{instrucao:08X}"
        )

        # //! Execute: instruções R-type

        if opcode == 0x00:
            a = registradores[rs]
            b = registradores[rt]

            if funct == 0x00:       # SLL
                resultado = (b << shamt) & MASCARA_32
                if rd != 0:
                    registradores[rd] = resultado

            elif funct == 0x02:     # SRL
                resultado = (b >> shamt) & MASCARA_32
                if rd != 0:
                    registradores[rd] = resultado

            elif funct == 0x03:  # SRA
                resultado = (signed_32(b) >> shamt) & MASCARA_32
                if rd != 0:
                    registradores[rd] = resultado

            elif funct == 0x08:  # JR
                if no_delay_slot:
                    raise NotImplementedError(
                        "JR dentro de delay slot nao suportado."
                    )

                destino_jr = a & MASCARA_32

                if destino_jr % 4 != 0:
                    raise EnderecoDesalinhadoError(
                        "Destino de JR em endereco desalinhado."
                    )

                destino_atrasado = destino_jr
                delay_slot_ativo = True

            elif funct == 0x09:  # JALR
                if no_delay_slot:
                    raise NotImplementedError(
                        "JALR dentro de delay slot nao suportado."
                    )

                destino_jalr = a & MASCARA_32

                if destino_jalr % 4 != 0:
                    raise EnderecoDesalinhadoError(
                        "Destino de JALR em endereco desalinhado."
                    )

                registradores[rd] = (pc_atual + 8) & MASCARA_32
                destino_atrasado = destino_jalr
                delay_slot_ativo = True

            elif funct == 0x20:  # ADD
                resultado = signed_32(a) + signed_32(b)

                if not (-0x80000000 <= resultado <= 0x7FFFFFFF):
                    raise IntegerOverflow("Overflow em ADD")

                if rd != 0:
                    registradores[rd] = resultado & MASCARA_32

            elif funct == 0x22:  # SUB
                resultado = signed_32(a) - signed_32(b)

                if not (-0x80000000 <= resultado <= 0x7FFFFFFF):
                    raise IntegerOverflow("Overflow em SUB")

                if rd != 0:
                    registradores[rd] = resultado & MASCARA_32

            elif funct == 0x24:     # AND
                resultado = a & b
                if rd != 0:
                    registradores[rd] = resultado

            elif funct == 0x25:     # OR
                resultado = a | b
                if rd != 0:
                    registradores[rd] = resultado
            
            elif funct == 0x26:     # XOR
                resultado = a ^ b
                if rd != 0:
                    registradores[rd] = resultado

            elif funct == 0x27:     # NOR
                resultado = (~(a | b)) & MASCARA_32
                if rd != 0:
                    registradores[rd] = resultado

            elif funct == 0x2A:     # SLT
                resultado = 1 if signed_32(a) < signed_32(b) else 0
                if rd != 0:
                    registradores[rd] = resultado
   
            elif funct == 0x2B:     # SLTU
                resultado = 1 if a < b else 0
                if rd != 0:
                    registradores[rd] = resultado

            
            elif funct == 0x18:  # MULT
                resultado = signed_32(a) * signed_32(b)

                resultado &= 0xFFFFFFFFFFFFFFFF

                estado_especial.lo = resultado & MASCARA_32
                estado_especial.hi = (
                    resultado >> 32
                ) & MASCARA_32
    
            elif funct == 0x19:  # MULTU
                resultado = (a & MASCARA_32) * (b & MASCARA_32)

                resultado &= 0xFFFFFFFFFFFFFFFF

                estado_especial.lo = resultado & MASCARA_32
                estado_especial.hi = (
                    resultado >> 32
                ) & MASCARA_32

            elif funct == 0x1A:  # DIV
                divisor = signed_32(b)
                dividendo = signed_32(a)

                if divisor == 0:
                    estado_especial.hi = dividendo & MASCARA_32
                    estado_especial.lo = (
                        0xFFFFFFFF
                        if dividendo >= 0
                        else 0x00000001
                    )
                else:
                    quociente = abs(dividendo) // abs(divisor)

                    if (dividendo < 0) != (divisor < 0):
                        quociente = -quociente

                    resto = dividendo - quociente * divisor

                    estado_especial.lo = quociente & MASCARA_32
                    estado_especial.hi = resto & MASCARA_32

            elif funct == 0x1B:  # DIVU
                dividendo = a & MASCARA_32
                divisor = b & MASCARA_32

                if divisor == 0:
                    estado_especial.lo = 0xFFFFFFFF
                    estado_especial.hi = dividendo
                else:
                    estado_especial.lo = (
                        dividendo // divisor
                    ) & MASCARA_32

                    estado_especial.hi = (
                        dividendo % divisor
                    ) & MASCARA_32

            else:
                raise NotImplementedError(
                    f"Funct nao implementado: 0x{funct:02X}"
                )

        # Aqui precisamos integrar o destino
        # ao mecanismo de atualização do PC.

        elif opcode == 0x02:  # J - Jump
            if no_delay_slot:
                raise NotImplementedError(
                    "J dentro de delay slot nao suportado."
                )

            destino_atrasado = (
                ((pc_atual + 4) & 0xF0000000)
                | ((instrucao & 0x03FFFFFF) << 2)
            )
            delay_slot_ativo = True

        elif opcode == 0x03:  # JAL - Jump and Link
            if no_delay_slot:
                raise NotImplementedError(
                    "JAL dentro de delay slot nao suportado."
                )

            registradores[31] = (pc_atual + 8) & MASCARA_32

            destino_atrasado = (
                ((pc_atual + 4) & 0xF0000000)
                | ((instrucao & 0x03FFFFFF) << 2)
            )
            delay_slot_ativo = True

        # ADDI: soma com immediate e sinaliza overflow
        # ainda nao implementado nesta versao didatica.

        elif opcode == 0x08:  # ADDI
            a = signed_32(registradores[rs])
            resultado = a + immediate

            if not (-0x80000000 <= resultado <= 0x7FFFFFFF):
                raise IntegerOverflow("Overflow em ADDI")

            if rt != 0:
                registradores[rt] = resultado & MASCARA_32

        elif opcode == 0x0A:  # SLTI
            a = signed_32(registradores[rs])
            resultado = 1 if a < immediate else 0

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x0B:  # SLTIU
            a = registradores[rs] & MASCARA_32
            resultado = 1 if a < (immediate & MASCARA_32) else 0

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x0C:  # ANDI
            imediato = instrucao & 0xFFFF
            resultado = registradores[rs] & imediato

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x0D:  # ORI
            imediato = instrucao & 0xFFFF
            resultado = registradores[rs] | imediato

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x0E:  # XORI
            imediato = instrucao & 0xFFFF
            resultado = registradores[rs] ^ imediato

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x0F:  # LUI
            imediato = instrucao & 0xFFFF
            resultado = (imediato << 16) & MASCARA_32

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x09:        # ADDIU
            resultado = (
                registradores[rs] + immediate
            ) & MASCARA_32

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x23:  # LW
            endereco = (
                registradores[rs] + immediate
            ) & MASCARA_32

            if endereco % 4 != 0:
                raise EnderecoDesalinhadoError(
                    f"LW em endereco desalinhado: 0x{endereco:08X}"
                )

            resultado = memoria.read_u32(endereco)

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x2B:  # SW
            endereco = (
                registradores[rs] + immediate
            ) & MASCARA_32

            if endereco % 4 != 0:
                raise EnderecoDesalinhadoError(
                    f"SW em endereco desalinhado: 0x{endereco:08X}"
                )

            memoria.write_u32(
                endereco,
                registradores[rt]
            )

        elif opcode == 0x20:  # LB
            endereco = (
                registradores[rs] + immediate
            ) & MASCARA_32

            resultado = memoria.read_u8(endereco)

            if resultado & 0x80:
                resultado |= 0xFFFFFF00

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x24:  # LBU
            endereco = (
                registradores[rs] + immediate
            ) & MASCARA_32

            resultado = memoria.read_u8(endereco)

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x21:  # LH
            endereco = (
                registradores[rs] + immediate
            ) & MASCARA_32

            if endereco % 2 != 0:
                raise EnderecoDesalinhadoError(
                    f"LH em endereco desalinhado: 0x{endereco:08X}"
                )

            resultado = memoria.read_u16(endereco)

            if resultado & 0x8000:
                resultado |= 0xFFFF0000

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x25:  # LHU
            endereco = (
                registradores[rs] + immediate
            ) & MASCARA_32

            if endereco % 2 != 0:
                raise EnderecoDesalinhadoError(
                    f"LHU em endereco desalinhado: 0x{endereco:08X}"
                )

            resultado = memoria.read_u16(endereco)

            if rt != 0:
                registradores[rt] = resultado

        elif opcode == 0x28:  # SB
            endereco = (
                registradores[rs] + immediate
            ) & MASCARA_32

            memoria.write_u8(
                endereco,
                registradores[rt],
            )

        elif opcode == 0x29:  # SH
            endereco = (
                registradores[rs] + immediate
            ) & MASCARA_32

            if endereco % 2 != 0:
                raise EnderecoDesalinhadoError(
                    f"SH em endereco desalinhado: 0x{endereco:08X}"
                )

            memoria.write_u16(
                endereco,
                registradores[rt],
            )

        elif opcode == 0x04:        # BEQ
            if no_delay_slot:
                raise NotImplementedError(
                    "BEQ dentro de delay slot nao suportado."
                )

            delay_slot_ativo = True

            if registradores[rs] == registradores[rt]:
                destino_atrasado = (
                    pc_atual + 4 + (immediate << 2)
                ) & MASCARA_32

        elif opcode == 0x05:  # BNE
            if no_delay_slot:
                raise NotImplementedError(
                    "BNE dentro de delay slot nao suportado."
                )

            delay_slot_ativo = True

            if registradores[rs] != registradores[rt]:
                destino_atrasado = (
                    pc_atual + 4 + (immediate << 2)
                ) & MASCARA_32

        elif opcode == 0x06:  # BLEZ
            if rt != 0:
                raise NotImplementedError(
                    "BLEZ com campo rt invalido."
                )

            if no_delay_slot:
                raise NotImplementedError(
                    "BLEZ dentro de delay slot nao suportado."
                )

            delay_slot_ativo = True

            if signed_32(registradores[rs]) <= 0:
                destino_atrasado = (
                    pc_atual + 4 + (immediate << 2)
                ) & MASCARA_32

        elif opcode == 0x07:  # BGTZ
            if rt != 0:
                raise NotImplementedError(
                    "BGTZ com campo rt invalido."
                )
            
            if no_delay_slot:
                raise NotImplementedError(
                    "BGTZ dentro de delay slot nao suportado."
                )

            delay_slot_ativo = True

            if signed_32(registradores[rs]) > 0:
                destino_atrasado = (
                    pc_atual + 4 + (immediate << 2)
                ) & MASCARA_32
    
        elif opcode == 0x01:  # REGIMM
            if rt == 0x00:  # BLTZ
                if no_delay_slot:
                    raise NotImplementedError(
                        "BLTZ dentro de delay slot nao suportado."
                    )

                delay_slot_ativo = True

                if signed_32(registradores[rs]) < 0:
                    destino_atrasado = (
                        pc_atual + 4 + (immediate << 2)
                    ) & MASCARA_32

            elif rt == 0x01:  # BGEZ
                if no_delay_slot:
                    raise NotImplementedError(
                        "BGEZ dentro de delay slot nao suportado."
                    )

                delay_slot_ativo = True

                if signed_32(registradores[rs]) >= 0:
                    destino_atrasado = (
                        pc_atual + 4 + (immediate << 2)
                    ) & MASCARA_32

            elif rt == 0x10:  # BLTZAL
                if no_delay_slot:
                    raise NotImplementedError(
                        "BLTZAL dentro de delay slot nao suportado."
                    )

                registradores[31] = (
                    pc_atual + 8
                ) & MASCARA_32

                delay_slot_ativo = True

                if signed_32(registradores[rs]) < 0:
                    destino_atrasado = (
                        pc_atual + 4 + (immediate << 2)
                    ) & MASCARA_32

            elif rt == 0x11:  # BGEZAL
                if no_delay_slot:
                    raise NotImplementedError(
                        "BGEZAL dentro de delay slot nao suportado."
                    )

                registradores[31] = (
                    pc_atual + 8
                ) & MASCARA_32

                delay_slot_ativo = True

                if signed_32(registradores[rs]) >= 0:
                    destino_atrasado = (
                        pc_atual + 4 + (immediate << 2)
                    ) & MASCARA_32

            else:
                raise NotImplementedError(
                    f"REGIMM nao implementado: rt=0x{rt:02X}"
                )

        else:
            raise NotImplementedError(
                f"Opcode nao implementado: 0x{opcode:02X}"
            )

        # $zero sempre deve continuar valendo zero.
        registradores[0] = 0

        # Depois do delay slot, aplica o destino
        # se o branch anterior foi tomado.
        if no_delay_slot and destino is not None:
            proximo_pc = destino

        pc = proximo_pc
        passos += 1

    if passos >= limite:
        print("\nLimite de instrucoes atingido.")

    print("\n--- Fim da execucao ---")
    print(f"Instrucoes executadas: {passos}")
    print(f"PC final: 0x{pc:08X}")

    if retornar_pc:
        return registradores, pc

    return registradores