def executar_programa(memoria, enderecos_programa, pc_inicial,
                      registradores, limite=100):

    pc = pc_inicial
    passos = 0

    # Controla o branch delay slot.
    delay_slot_ativo = False
    destino_atrasado = None

    while pc in enderecos_programa and passos < limite:
        pc_atual = pc

        # Fetch
        instrucao = read_u32(memoria, pc_atual)

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

        elif funct == 0x08:  # JR
                        if no_delay_slot:
                            raise NotImplementedError(
                                "JR dentro de delay slot nao suportado."
                            )
        
                        destino_atrasado = a & MASCARA_32
                        delay_slot_ativo = True

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
                    
                        return registradores