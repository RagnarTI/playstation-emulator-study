# Relatório técnico da suíte de testes

Catálogo individual dos 419 métodos de teste localizados em `test/`. Para cada método, a tabela registra o objetivo indicado pelo nome e as expressões de verificação encontradas no corpo; a implementação do teste contém a preparação e os valores completos.

Nomes de teste duplicados foram corrigidos em `test_memory.py` e `test_arithmetic.py`. Antes, essas definições sobrescreviam quatro casos anteriores durante a criação das classes; agora os 419 métodos têm nomes únicos por arquivo e podem ser descobertos.

## Execução

A suíte não foi executada nesta etapa: `python -m unittest discover -s test -v` falhou antes do discovery porque `python` resolve para o alias da Microsoft Store e não há interpretador funcional no PATH. Logo, nenhum teste recebe status de aprovado, falho ou erro. O teste `test_bios_real_executa_primeira_instrucao` depende de `SCPH1001.BIN` na raiz do projeto. Os testes de `test_bios.py` criam imagens BIOS temporárias.

## Resumo de cobertura

- Aritmética, operações MIPS, shifts e overflow: `test_arithmetic.py` e `arithmetic/test_overflow.py`.
- Branches, saltos, links e delay slots: `branches/` e `test_cpu_control_flow.py`.
- Estado da CPU e execução passo a passo: `test_cpu.py` e `test_cpu_control_flow.py`.
- Instruções de memória e integração: `test_memory.py` e `test_memory_integration.py`.
- RAM, aliases e regiões: `test_ram.py` e `test_memory_bus.py`.
- BIOS e inicialização do PS1: `test_bios.py` usa imagem temporária; `test_ps1.py` carrega o arquivo real.
- COP0 e exceções: `test_cop0.py` testa métodos diretos; `test_mips_exceptions.py` testa hierarquia, não integração end-to-end com CPU.

### Cobertura ausente ou limitada

- Não foram identificados testes funcionais para GPU, CD-ROM, DMA ou timers.
- O teste da primeira instrução da BIOS não comprova inicialização completa nem execução prolongada da BIOS.
- Não foram identificados testes de jogos ou comparação com hardware de referência.

### Recomendações

1. Reexecutar `python -m unittest discover -s test -v` num ambiente com Python e registrar o resumo real.
2. Manter testes de instruções focados em programas curtos e efeitos observáveis, incluindo PC quando aplicável.
3. Acrescentar testes de integração COP0/CPU e de periféricos conforme essas áreas forem implementadas.

## Catálogo individual

### `test/arithmetic/test_overflow.py`

Aritmética e overflow; componentes: helpers MIPS e interpretador.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_add_gera_overflow_com_sinal` | add gera overflow com sinal | with self.assertRaises(IntegerOverflow): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_add_sem_overflow_com_sinal` | add sem overflow com sinal | self.assertEqual(registradores[10], 30) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_signed_32_interpreta_valor_negativo` | signed 32 interpreta valor negativo | self.assertEqual(signed_32(0x80000000), -2147483648) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sub_gera_overflow_com_sinal` | sub gera overflow com sinal | with self.assertRaises(IntegerOverflow): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_add_com_operando_negativo` | add com operando negativo | self.assertEqual(registradores[10], 1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sub_com_operando_negativo` | sub com operando negativo | self.assertEqual(registradores[10], 6) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sub_gera_overflow_com_operando_negativo` | sub gera overflow com operando negativo | with self.assertRaises(IntegerOverflow): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_add_gera_overflow_com_operando_negativo` | add gera overflow com operando negativo | with self.assertRaises(IntegerOverflow): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addi_gera_overflow_com_sinal` | addi gera overflow com sinal | with self.assertRaises(IntegerOverflow): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addi_sem_overflow_com_sinal` | addi sem overflow com sinal | self.assertEqual(registradores[10], 0x7FFFFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_beq.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_beq_verdadeiro` | beq verdadeiro | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_beq_falso` | beq falso | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_beq_desvio_com_offset_negativo` | beq desvio com offset negativo | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[12], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_beq_tomado_retorna_pc_final_no_destino` | beq tomado retorna pc final no destino | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 7) · self.assertEqual(pc_final, 0x1010) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_bgez.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_bgez_verdadeiro` | bgez verdadeiro | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bgez_falso` | bgez falso | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bgez_maior_inteiro_positivo_32_bits` | bgez maior inteiro positivo 32 bits | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bgez_zero_desvia` | bgez zero desvia | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_bgez_tomado` | delay slot bgez tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_bgez_nao_tomado` | delay slot bgez nao tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_bgezal.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_bgezal_verdadeiro` | bgezal verdadeiro | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bgezal_falso` | bgezal falso | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bgezal_negativo_nao_desvia_atualiza_ra` | bgezal negativo nao desvia atualiza ra | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 2) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bgezal_positivo_desvia_atualiza_ra` | bgezal positivo desvia atualiza ra | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bgezal_delay_slot_sobrescreve_ra` | bgezal delay slot sobrescreve ra | self.assertEqual(registradores[31], 0x1234) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_bgtz.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_bgtz_verdadeiro` | bgtz verdadeiro | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bgtz_falso` | bgtz falso | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bgtz_maior_inteiro_positivo_32_bits` | bgtz maior inteiro positivo 32 bits | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bgtz_zero_nao_desvia` | bgtz zero nao desvia | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 2) · self.assertEqual(registradores[12], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_bgtz_tomado` | delay slot bgtz tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_bgtz_nao_tomado` | delay slot bgtz nao tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_blez.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_blez_verdadeiro` | blez verdadeiro | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_blez_falso` | blez falso | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_blez_rt_invalido` | blez rt invalido | with self.assertRaises(NotImplementedError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_blez_menor_inteiro_32_bits` | blez menor inteiro 32 bits | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_blez_zero_desvia` | blez zero desvia | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_blez_tomado` | delay slot blez tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_blez_nao_tomado` | delay slot blez nao tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_bltz.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_bltz_verdadeiro` | bltz verdadeiro | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bltz_falso` | bltz falso | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bltz_menor_inteiro_32_bits` | bltz menor inteiro 32 bits | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bltz_zero_nao_desvia` | bltz zero nao desvia | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 2) · self.assertEqual(registradores[12], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_bltz_tomado` | delay slot bltz tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_bltz_nao_tomado` | delay slot bltz nao tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_bltzal.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_bltzal_verdadeiro` | bltzal verdadeiro | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bltzal_falso` | bltzal falso | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bltzal_zero_nao_desvia_atualiza_ra` | bltzal zero nao desvia atualiza ra | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 2) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bltzal_negativo_desvia_atualiza_ra` | bltzal negativo desvia atualiza ra | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bltzal_delay_slot_sobrescreve_ra` | bltzal delay slot sobrescreve ra | self.assertEqual(registradores[31], 0x5678) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_bne.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_bne_verdadeiro` | bne verdadeiro | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bne_falso` | bne falso | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bne_offset_negativo_nao_tomado` | bne offset negativo nao tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 7) · self.assertEqual(registradores[12], 9) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_bne_tomado` | delay slot bne tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_bne_nao_tomado` | delay slot bne nao tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_delay_slot.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_delay_slot` | delay slot | self.assertEqual(registradores[10], 42) · self.assertEqual(registradores[11], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_branch_tomado_executa_uma_vez` | delay slot branch tomado executa uma vez | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_branch_nao_tomado` | delay slot branch nao tomado | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_limite_de_execucao_em_loop` | limite de execucao em loop | self.assertEqual(registradores[10], 1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_j.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_j` | j | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_j_preserva_regiao_de_pc_mais_quatro` | j preserva regiao de pc mais quatro | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_j_na_fronteira_de_regiao` | j na fronteira de regiao | self.assertEqual(registradores[31], 0) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_j_executa_antes_do_salto` | delay slot j executa antes do salto | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_jal.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_jal` | jal | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jal_jr_retorno` | jal jr retorno | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 42) · self.assertEqual(registradores[12], 7) · self.assertEqual(registradores[13], 5) · self.assertEqual(registradores[14], 2) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jal_preserva_regiao_de_pc_mais_quatro` | jal preserva regiao de pc mais quatro | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) · self.assertEqual(registradores[31], 0x10000004) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jal_na_fronteira_de_regiao` | jal na fronteira de regiao | self.assertEqual(registradores[31], 0x10000004) · self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_jal_executa_e_salva_retorno` | delay slot jal executa e salva retorno | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) · self.assertEqual(registradores[31], 0x1008) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_jr.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_jr` | jr | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 99) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jr_registro_com_delay_slot` | jr registro com delay slot | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 7) · self.assertEqual(registradores[12], 0) · self.assertEqual(registradores[31], 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_jr_executa_antes_do_salto` | delay slot jr executa antes do salto | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/branches/test_regimm.py`

Branches, saltos e delay slots; componentes: helpers MIPS, interpretador e memória controlada.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_regimm_rt_nao_suportado` | regimm rt nao suportado | with self.assertRaises(NotImplementedError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_regimm_bltz_valido` | regimm bltz valido | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 7) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/test_arithmetic.py`

Aritmética e operações MIPS; componentes: helpers do interpretador, RAM e execução de instrução.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_add` | add | self.assertEqual(registradores[10], 40) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sub` | sub | self.assertEqual(registradores[10], 18) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addi_immediate_negativo` | addi immediate negativo | self.assertEqual(registradores[8], 15) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_slt_verdadeiro` | slt verdadeiro | self.assertEqual(registradores[10], 1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_slt_falso` | slt falso | self.assertEqual(registradores[10], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sltu_valor_alto_sem_sinal` | sltu valor alto sem sinal | self.assertEqual(registradores[10], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_and` | and | self.assertEqual(registradores[10], 8) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_or` | or | self.assertEqual(registradores[10], 14) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_xor` | xor | self.assertEqual(registradores[10], 6) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_nor` | nor | self.assertEqual( registradores[10], 0xFFFFFFF1, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sll` | sll | self.assertEqual(registradores[10], 20) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_srl` | srl | self.assertEqual(registradores[10], 5) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sra_negativo` | sra negativo | self.assertEqual(registradores[10], 0xFFFFFFFE) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_slti_verdadeiro` | slti verdadeiro | self.assertEqual(registradores[10], 1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_slti_falso` | slti falso | self.assertEqual(registradores[10], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sltiu_verdadeiro` | sltiu verdadeiro | self.assertEqual(registradores[10], 1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sltiu_falso` | sltiu falso | self.assertEqual(registradores[10], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sltiu_com_valor_negativo` | sltiu com valor negativo | self.assertEqual(registradores[10], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_andi_preserva_bits_inferiores` | andi preserva bits inferiores | self.assertEqual(registradores[10], 0x78) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_andi_imediato_com_bit_15` | andi imediato com bit 15 | self.assertEqual(registradores[10], 0x8000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ori_ativa_bits_do_imediato` | ori ativa bits do imediato | self.assertEqual(registradores[10], 0x123400F5) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ori_imediato_com_bit_15` | ori imediato com bit 15 | self.assertEqual(registradores[10], 0x00008000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_xori_inverte_bits_selecionados` | xori inverte bits selecionados | self.assertEqual(registradores[10], 0x12340000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_xori_imediato_com_bit_15` | xori imediato com bit 15 | self.assertEqual(registradores[10], 0xFFFF7FFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lui_carrega_metade_superior` | lui carrega metade superior | self.assertEqual(registradores[10], 0x12340000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lui_imediato_com_bit_15` | lui imediato com bit 15 | self.assertEqual(registradores[10], 0x80000000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u32_limita_valor_a_32_bits` | write u32 limita valor a 32 bits | self.assertEqual( memoria.read_u32(0x1000), 0xABCDEF01, ) · self.assertEqual(memoria.read_u8(0x1000), 0x01) · self.assertEqual(memoria.read_u8(0x1001), 0xEF) · self.assertEqual(memoria.read_u8(0x1002), 0xCD) · self.assertEqual(memoria.read_u8(0x1003), 0xAB) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_read_u32_memoria_vazia_retorna_zero` | read u32 memoria vazia retorna zero | self.assertEqual(resultado, 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_read_u32_memoria_parcialmente_preenchida` | read u32 memoria parcialmente preenchida | self.assertEqual(resultado, 0x00005678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u32_altera_apenas_quatro_bytes` | write u32 altera apenas quatro bytes | self.assertEqual(memoria.read_u8(0x0FFF), 0xAA) · self.assertEqual(memoria.read_u8(0x1000), 0x78) · self.assertEqual(memoria.read_u8(0x1001), 0x56) · self.assertEqual(memoria.read_u8(0x1002), 0x34) · self.assertEqual(memoria.read_u8(0x1003), 0x12) · self.assertEqual(memoria.read_u8(0x1004), 0xBB) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u32_e_read_u32_preservam_valor` | write u32 e read u32 preservam valor | self.assertEqual(resultado, valor) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sw_armazena_valor_no_endereco_calculado` | sw armazena valor no endereco calculado | self.assertEqual( memoria.read_u32(0x1004), 0x12345678, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lw_carrega_valor_do_endereco_calculado` | lw carrega valor do endereco calculado | self.assertEqual(registradores[2], 0x12345678) · self.assertEqual(registradores[1], 0x1000) · self.assertEqual(registradores[3], 0xBBBBBBBB) · self.assertEqual(registradores[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lw_nao_altera_registrador_zero` | lw nao altera registrador zero | self.assertEqual(registradores[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lw_com_deslocamento_negativo` | lw com deslocamento negativo | self.assertEqual(registradores[2], 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sw_com_deslocamento_negativo` | sw com deslocamento negativo | self.assertEqual( memoria.read_u32(0x1000), 0x12345678, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lw_com_endereco_desalinhado` | lw com endereco desalinhado | with self.assertRaisesRegex( EnderecoDesalinhadoError, "LW em endereco desalinhado: 0x00001002", ): · self.assertEqual(registradores[2], 0xAAAAAAAA) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sw_com_endereco_desalinhado` | sw com endereco desalinhado | with self.assertRaisesRegex( EnderecoDesalinhadoError, "SW em endereco desalinhado: 0x00001002", ): · self.assertEqual(memoria_depois, memoria_antes) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lb_com_valor_positivo` | lb com valor positivo | self.assertEqual(registradores[2], 0x7F) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lb_com_valor_negativo` | lb com valor negativo | self.assertEqual(registradores[2], 0xFFFFFF80) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lbu_nao_faz_extensao_de_sinal` | lbu nao faz extensao de sinal | self.assertEqual(registradores[2], 0xFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lb_nao_altera_registrador_zero` | lb nao altera registrador zero | self.assertEqual(registradores[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lh_com_valor_positivo` | lh com valor positivo | self.assertEqual(registradores[2], 0x7FFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lh_com_valor_negativo` | lh com valor negativo | self.assertEqual(registradores[2], 0xFFFF8000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lhu_nao_faz_extensao_de_sinal` | lhu nao faz extensao de sinal | self.assertEqual(registradores[2], 0xFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lh_nao_altera_registrador_zero` | lh nao altera registrador zero | self.assertEqual(registradores[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sb_armazena_apenas_um_byte` | sb armazena apenas um byte | self.assertEqual(memoria.read_u8(0x2000), 0x90) · self.assertEqual(memoria.read_u8(0x2001), 0x56) · self.assertEqual(memoria.read_u8(0x2002), 0x34) · self.assertEqual(memoria.read_u8(0x2003), 0x12) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sh_armazena_apenas_dois_bytes` | sh armazena apenas dois bytes | self.assertEqual(memoria.read_u8(0x2000), 0x90) · self.assertEqual(memoria.read_u8(0x2001), 0xEF) · self.assertEqual(memoria.read_u8(0x2002), 0x34) · self.assertEqual(memoria.read_u8(0x2003), 0x12) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sb_com_deslocamento` | sb com deslocamento | self.assertEqual(memoria.read_u8(0x2004), 0xAB) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sh_com_deslocamento` | sh com deslocamento | self.assertEqual(memoria.read_u16(0x2004), 0xBEEF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sh_com_endereco_desalinhado` | sh com endereco desalinhado | with self.assertRaises(EnderecoDesalinhadoError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_hi_lo_iniciam_em_zero` | hi lo iniciam em zero | self.assertEqual(estado.hi, 0) · self.assertEqual(estado.lo, 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_hi_lo_armazenam_valores` | hi lo armazenam valores | self.assertEqual(estado.hi, 0x12345678) · self.assertEqual(estado.lo, 0xABCDEF90) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_programa_preserva_estado_especial` | executar programa preserva estado especial | self.assertEqual(estado.hi, 0x12345678) · self.assertEqual(estado.lo, 0xABCDEF90) · self.assertEqual(registradores[1], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mult_atualiza_hi_lo` | mult atualiza hi lo | self.assertEqual(estado.lo, 200) · self.assertEqual(estado.hi, 0) · self.assertEqual(registradores[1], 10) · self.assertEqual(registradores[2], 20) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mult_com_resultado_negativo` | mult com resultado negativo | self.assertEqual(estado.lo, 0xFFFFFFFA) · self.assertEqual(estado.hi, 0xFFFFFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mult_usa_hi_quando_resultado_excede_32_bits` | mult usa hi quando resultado excede 32 bits | self.assertEqual(estado.lo, 0xFFFFFFFE) · self.assertEqual(estado.hi, 0x00000000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_multu_interpreta_operandos_sem_sinal` | multu interpreta operandos sem sinal | self.assertEqual(estado.lo, 0xFFFFFFFE) · self.assertEqual(estado.hi, 0x00000001) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_quociente_e_resto` | div quociente e resto | self.assertEqual(estado.lo, 3) · self.assertEqual(estado.hi, 2) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_com_operando_negativo` | div com operando negativo | self.assertEqual(estado.lo, 0xFFFFFFFE) # -2 · self.assertEqual(estado.hi, 0xFFFFFFFF) # -1 | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_por_zero_com_dividendo_positivo` | div por zero com dividendo positivo | self.assertEqual(estado.hi, 17) · self.assertEqual(estado.lo, 0xFFFFFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_por_zero_com_dividendo_negativo` | div por zero com dividendo negativo | self.assertEqual(estado.hi, 0xFFFFFFF9) · self.assertEqual(estado.lo, 0x00000001) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_divu_quociente_e_resto` | divu quociente e resto | self.assertEqual(estado.lo, 3) · self.assertEqual(estado.hi, 2) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_divu_interpreta_operandos_sem_sinal` | divu interpreta operandos sem sinal | self.assertEqual(estado.lo, 0x7FFFFFFF) · self.assertEqual(estado.hi, 1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_divu_por_zero` | divu por zero | self.assertEqual(estado.lo, 0xFFFFFFFF) · self.assertEqual(estado.hi, 17) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_delay_slot_j_executa_antes_do_salto` | delay slot j executa antes do salto | self.assertEqual(registradores[8], 42) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_j_retorna_pc_final_no_destino` | j retorna pc final no destino | self.assertEqual(registradores[8], 42) · self.assertEqual(pc_final, 0x1010) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jal_salva_retorno_e_executa_delay_slot` | jal salva retorno e executa delay slot | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[8], 42) · self.assertEqual(pc_final, 0x1010) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jr_salva_destino_e_executa_delay_slot` | jr salva destino e executa delay slot | self.assertEqual(registradores[8], 42) · self.assertEqual(pc_final, destino) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jalr_salva_retorno_e_executa_delay_slot` | jalr salva retorno e executa delay slot | self.assertEqual(registradores[10], 0x1008) · self.assertEqual(registradores[8], 42) · self.assertEqual(pc_final, destino) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jr_com_destino_desalinhado` | jr com destino desalinhado | with self.assertRaises(EnderecoDesalinhadoError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jalr_com_destino_desalinhado` | jalr com destino desalinhado | with self.assertRaises(EnderecoDesalinhadoError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_add_com_overflow_com_sinal` | add com overflow com sinal | with self.assertRaises(Exception): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_decodificar_instrucao_campos_basicos` | decodificar instrucao campos basicos | self.assertEqual(campos["opcode"], 0x09) · self.assertEqual(campos["rs"], 8) · self.assertEqual(campos["rt"], 9) · self.assertEqual(campos["rd"], 31) · self.assertEqual(campos["shamt"], 31) · self.assertEqual(campos["funct"], 0x3F) · self.assertEqual(campos["immediate"], -1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_operacao_logica` | executar operacao logica | self.assertEqual(executar_operacao_logica(0x24, a, b), 0b1000) · self.assertEqual(executar_operacao_logica(0x25, a, b), 0b1110) · self.assertEqual(executar_operacao_logica(0x26, a, b), 0b0110) · self.assertEqual( executar_operacao_logica(0x27, a, b), (~0b1110) & MASCARA_32, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_deslocamento` | executar deslocamento | self.assertEqual( executar_deslocamento(0x00, 3, 2), 12, ) · self.assertEqual( executar_deslocamento(0x02, 12, 2), 3, ) · self.assertEqual( executar_deslocamento(0x03, 0xFFFFFFF0, 2), 0xFFFFFFFC, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_soma_subtracao` | executar soma subtracao | self.assertEqual( executar_soma_subtracao(0x20, 10, 20), 30, ) · self.assertEqual( executar_soma_subtracao(0x22, 20, 10), 10, ) · with self.assertRaises(IntegerOverflow): · with self.assertRaises(IntegerOverflow): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_comparacao` | executar comparacao | self.assertEqual(executar_comparacao(0x2A, 10, 20), 1) · self.assertEqual(executar_comparacao(0x2A, 20, 10), 0) · self.assertEqual( executar_comparacao(0x2A, 0xFFFFFFFF, 1), 1, ) · self.assertEqual( executar_comparacao(0x2B, 0xFFFFFFFF, 1), 0, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_multiplicacao` | executar multiplicacao | self.assertEqual(hi, 0) · self.assertEqual(lo, 200) · self.assertEqual(hi, 1) · self.assertEqual(lo, 0xFFFFFFFE) · self.assertEqual(hi, 0xFFFFFFFF) · self.assertEqual(lo, 0xFFFFFFFE) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_divisao` | executar divisao | self.assertEqual(lo, 3) · self.assertEqual(hi, 2) · self.assertEqual(lo, 0xFFFFFFFD) · self.assertEqual(hi, 0xFFFFFFFF) · self.assertEqual(lo, 3) · self.assertEqual(hi, 2) · self.assertEqual(lo, 0xFFFFFFFF) · self.assertEqual(hi, 10) · self.assertEqual(lo, 0xFFFFFFFF) · self.assertEqual(hi, 10) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_salto_registrador` | executar salto registrador | self.assertEqual(destino, 0x2000) · self.assertIsNone(link) · self.assertEqual(destino, 0x3000) · self.assertEqual(link, 0x1008) · with self.assertRaises(EnderecoDesalinhadoError): · with self.assertRaises(NotImplementedError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_calcular_destino_salto` | calcular destino salto | self.assertEqual(destino, 0x80000400) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_calcular_destino_desvio` | calcular destino desvio | self.assertEqual( calcular_destino_desvio(0x1000, 2), 0x100C, ) · self.assertEqual( calcular_destino_desvio(0x1000, -2), 0x0FFC, ) · self.assertEqual( calcular_destino_desvio(0xFFFFFFFC, 0), 0x00000000, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_comparacao_imediata` | comparacao imediata | self.assertEqual( executar_comparacao(0x2A, 0xFFFFFFFF, 1), 1, ) · self.assertEqual( executar_comparacao(0x2B, 0xFFFFFFFF, 1), 0, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_operacoes_logicas_com_imediato` | operacoes logicas com imediato | self.assertEqual( executar_operacao_logica(0x24, valor, imediato), 0x00000078, ) · self.assertEqual( executar_operacao_logica(0x25, valor, imediato), 0x123456FF, ) · self.assertEqual( executar_operacao_logica(0x26, valor, imediato), 0x12345687, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_lui` | executar lui | self.assertEqual( executar_lui(instrucao), 0xABCD0000, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_addi` | executar addi | self.assertEqual(executar_addi(10, 5), 15) · self.assertEqual(executar_addi(0xFFFFFFFF, 1), 0) · with self.assertRaises(IntegerOverflow): · with self.assertRaises(IntegerOverflow): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_addiu` | executar addiu | self.assertEqual( executar_addiu(10, 5), 15, ) · self.assertEqual( executar_addiu(10, -5), 5, ) · self.assertEqual( executar_addiu(0xFFFFFFFF, 1), 0, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_calcular_endereco_efetivo` | calcular endereco efetivo | self.assertEqual( calcular_endereco_efetivo(0x1000, 4, "LW"), 0x1004, ) · self.assertEqual( calcular_endereco_efetivo(0x1000, -4, "SW"), 0x0FFC, ) · with self.assertRaises(EnderecoDesalinhadoError): · with self.assertRaises(EnderecoDesalinhadoError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sltiu_imediato_negativo` | sltiu imediato negativo | self.assertEqual(registradores[9], 1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addi_gera_overflow_na_execucao` | addi gera overflow na execucao | with self.assertRaises(IntegerOverflow): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addiu_nao_gera_overflow_na_execucao` | addiu nao gera overflow na execucao | self.assertEqual(registradores[9], 0x80000000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addi_addiu_preservam_registrador_zero` | addi addiu preservam registrador zero | self.assertEqual(registradores_addi[0], 0) · self.assertEqual(registradores_addiu[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_slti_e_sltiu_diferenciam_comparacao_com_sinal` | slti e sltiu diferenciam comparacao com sinal | self.assertEqual(registradores_slti[9], 1) · self.assertEqual(registradores_sltiu[9], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_slti_imediato_negativo` | slti imediato negativo | self.assertEqual(registradores[9], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_logicas_imediatas_nao_estendem_sinal` | logicas imediatas nao estendem sinal | self.assertEqual(registradores_andi[9], 0x00008000) · self.assertEqual(registradores_ori[9], 0x00008000) · self.assertEqual(registradores_xori[9], 0xFFFF7FFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_logicas_imediatas_preservam_registrador_zero` | logicas imediatas preservam registrador zero | self.assertEqual(registradores[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_logicas_imediatas_alteram_apenas_rt` | logicas imediatas alteram apenas rt | self.assertEqual(registradores[8], 0x12345678) · self.assertEqual(registradores[10], 0x55555555) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lui_na_execucao_integrada` | lui na execucao integrada | self.assertEqual(registradores[9], 0xABCD0000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lui_preserva_registrador_zero` | lui preserva registrador zero | self.assertEqual(registradores[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lui_altera_apenas_registrador_destino` | lui altera apenas registrador destino | self.assertEqual(registradores[9], 0xABCD0000) · self.assertEqual(registradores[8], 0x12345678) · self.assertEqual(registradores[10], 0x55555555) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addiu_imediato_negativo_na_execucao` | addiu imediato negativo na execucao | self.assertEqual(registradores[9], 9) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addiu_limita_resultado_a_32_bits` | addiu limita resultado a 32 bits | self.assertEqual(registradores[9], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addiu_produz_resultado_negativo` | addiu produz resultado negativo | self.assertEqual(registradores[9], 0xFFFFFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addi_imediato_negativo_na_execucao` | addi imediato negativo na execucao | self.assertEqual(registradores[9], 9) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addi_gera_overflow_negativo_na_execucao` | addi gera overflow negativo na execucao | with self.assertRaises(IntegerOverflow): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addi_atinge_limite_inferior_sem_overflow` | addi atinge limite inferior sem overflow | self.assertEqual(registradores[9], 0x80000000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addiu_ultrapassa_limite_inferior_sem_excecao` | addiu ultrapassa limite inferior sem excecao | self.assertEqual(registradores[9], 0x7FFFFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_slti_com_imediato_negativo_na_execucao` | slti com imediato negativo na execucao | self.assertEqual(registradores[9], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_slti_e_sltiu_com_registrador_negativo` | slti e sltiu com registrador negativo | self.assertEqual(registradores_slti[9], 1) · self.assertEqual(registradores_sltiu[9], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sltiu_imediato_negativo_com_valor_zero` | sltiu imediato negativo com valor zero | self.assertEqual(registradores[9], 1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sltiu_com_operandos_iguais` | sltiu com operandos iguais | self.assertEqual(registradores[9], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_slti_com_menor_inteiro_com_sinal` | slti com menor inteiro com sinal | self.assertEqual(registradores[9], 1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_slti_com_maior_inteiro_positivo` | slti com maior inteiro positivo | self.assertEqual(registradores[9], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sltiu_com_maior_inteiro_positivo` | sltiu com maior inteiro positivo | self.assertEqual(registradores[9], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_andi_com_imediato_zero` | andi com imediato zero | self.assertEqual(registradores[9], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ori_com_imediato_zero` | ori com imediato zero | self.assertEqual(registradores[9], 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_xori_com_imediato_zero` | xori com imediato zero | self.assertEqual(registradores[9], 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_andi_com_imediato_todos_os_bits_ativos` | andi com imediato todos os bits ativos | self.assertEqual(registradores[9], 0x00005678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ori_com_imediato_todos_os_bits_ativos` | ori com imediato todos os bits ativos | self.assertEqual(registradores[9], 0x1234FFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_xori_com_imediato_todos_os_bits_ativos` | xori com imediato todos os bits ativos | self.assertEqual(registradores[9], 0x1234A987) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_andi_com_mascara_seletiva` | andi com mascara seletiva | self.assertEqual(registradores[9], 0x00000608) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ori_com_mascara_seletiva` | ori com mascara seletiva | self.assertEqual(registradores[9], 0x12340F0F) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_xori_com_mascara_seletiva` | xori com mascara seletiva | self.assertEqual(registradores[9], 0x12345977) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lui_com_imediato_zero` | lui com imediato zero | self.assertEqual(registradores[9], 0) · self.assertEqual(registradores[8], 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lui_com_imediato_maximo` | lui com imediato maximo | self.assertEqual(registradores[9], 0xFFFF0000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_addi_com_imediato_zero` | addi com imediato zero | self.assertEqual(registradores[9], 0xFFFFFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_calcular_endereco_efetivo_com_alinhamento_de_byte` | calcular endereco efetivo com alinhamento de byte | self.assertEqual(endereco, 0x1001) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_calcular_endereco_efetivo_com_alinhamento_de_meia_palavra` | calcular endereco efetivo com alinhamento de meia palavra | self.assertEqual(endereco, 0x1002) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_calcular_endereco_efetivo_rejeita_meia_palavra_desalinhada` | calcular endereco efetivo rejeita meia palavra desalinhada | with self.assertRaises(EnderecoDesalinhadoError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_calcular_endereco_efetivo_com_wraparound` | calcular endereco efetivo com wraparound | self.assertEqual(endereco, 0x00000000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_calcular_endereco_efetivo_com_wraparound_alinhado` | calcular endereco efetivo com wraparound alinhado | self.assertEqual(endereco, 0x00000000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mfhi_copia_hi_para_rd` | mfhi copia hi para rd | self.assertEqual(registradores[rd], 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mflo_copia_lo_para_rd` | mflo copia lo para rd | self.assertEqual(registradores[rd], 0x87654321) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mfhi_preserva_zero` | mfhi preserva zero | self.assertEqual(registradores[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mflo_preserva_zero` | mflo preserva zero | self.assertEqual(registradores[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mult_seguido_de_mfhi` | mult seguido de mfhi | self.assertEqual(estado_especial.hi, 0) · self.assertEqual(estado_especial.lo, 0xFFFFFFFE) · self.assertEqual(registradores[rd], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mult_seguido_de_mflo` | mult seguido de mflo | self.assertEqual(estado_especial.hi, 0) · self.assertEqual(estado_especial.lo, 0xFFFFFFFE) · self.assertEqual(registradores[rd], 0xFFFFFFFE) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_seguido_de_mfhi_e_mflo` | div seguido de mfhi e mflo | self.assertEqual(estado_especial.hi, 2) · self.assertEqual(estado_especial.lo, 3) · self.assertEqual(registradores[rd_hi], 2) · self.assertEqual(registradores[rd_lo], 3) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_negativo_seguido_de_mfhi_e_mflo` | div negativo seguido de mfhi e mflo | self.assertEqual(estado_especial.hi, 0xFFFFFFFE) · self.assertEqual(estado_especial.lo, 0xFFFFFFFD) · self.assertEqual(registradores[rd_hi], 0xFFFFFFFE) · self.assertEqual(registradores[rd_lo], 0xFFFFFFFD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_divisor_negativo_seguido_de_mfhi_e_mflo` | div divisor negativo seguido de mfhi e mflo | self.assertEqual(estado_especial.hi, 2) · self.assertEqual(estado_especial.lo, 0xFFFFFFFD) · self.assertEqual(registradores[rd_hi], 2) · self.assertEqual(registradores[rd_lo], 0xFFFFFFFD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_ambos_operandos_negativos_seguido_de_mfhi_e_mflo` | div ambos operandos negativos seguido de mfhi e mflo | self.assertEqual(estado_especial.hi, 0xFFFFFFFE) · self.assertEqual(estado_especial.lo, 3) · self.assertEqual(registradores[rd_hi], 0xFFFFFFFE) · self.assertEqual(registradores[rd_lo], 3) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_helper_div_por_zero_com_dividendo_positivo` | helper div por zero com dividendo positivo | self.assertEqual(hi, 17) · self.assertEqual(lo, 0xFFFFFFFF) | Testa diretamente o helper aritmético; não demonstra a execução end-to-end da instrução. |
| `test_helper_div_por_zero_com_dividendo_negativo` | helper div por zero com dividendo negativo | self.assertEqual(hi, 0xFFFFFFEF) · self.assertEqual(lo, 0x00000001) | Testa diretamente o helper aritmético; não demonstra a execução end-to-end da instrução. |
| `test_helper_divu_por_zero` | helper divu por zero | self.assertEqual(hi, 17) · self.assertEqual(lo, 0xFFFFFFFF) | Testa diretamente o helper aritmético; não demonstra a execução end-to-end da instrução. |
| `test_div_por_zero_seguido_de_mfhi_e_mflo` | div por zero seguido de mfhi e mflo | self.assertEqual(estado_especial.hi, 17) · self.assertEqual(estado_especial.lo, 0xFFFFFFFF) · self.assertEqual(registradores[rd_hi], 17) · self.assertEqual(registradores[rd_lo], 0xFFFFFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_divu_por_zero_seguido_de_mfhi_e_mflo` | divu por zero seguido de mfhi e mflo | self.assertEqual(estado_especial.hi, 17) · self.assertEqual(estado_especial.lo, 0xFFFFFFFF) · self.assertEqual(registradores[rd_hi], 17) · self.assertEqual(registradores[rd_lo], 0xFFFFFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_menor_inteiro_por_menos_um` | div menor inteiro por menos um | self.assertEqual(hi, 0) · self.assertEqual(lo, 0x80000000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_divu_maior_inteiro_por_dois` | divu maior inteiro por dois | self.assertEqual(hi, 1) · self.assertEqual(lo, 0x7FFFFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mthi_copia_rs_para_hi` | mthi copia rs para hi | self.assertEqual(estado_especial.hi, 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mtlo_copia_rs_para_lo` | mtlo copia rs para lo | self.assertEqual(estado_especial.lo, 0x87654321) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mthi_mtlo_seguidos_de_mfhi_mflo` | mthi mtlo seguidos de mfhi mflo | self.assertEqual(estado_especial.hi, 0x12345678) · self.assertEqual(estado_especial.lo, 0x87654321) · self.assertEqual(registradores[rd_hi], 0x12345678) · self.assertEqual(registradores[rd_lo], 0x87654321) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_mult_seguido_de_mfhi_mflo` | mult seguido de mfhi mflo | self.assertEqual(estado_especial.hi, 0xFFFFFFFF) · self.assertEqual(estado_especial.lo, 0xFFFFFFFE) · self.assertEqual(registradores[rd_hi], 0xFFFFFFFF) · self.assertEqual(registradores[rd_lo], 0xFFFFFFFE) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_multu_seguido_de_mfhi_mflo` | multu seguido de mfhi mflo | self.assertEqual(estado_especial.hi, 1) · self.assertEqual(estado_especial.lo, 0xFFFFFFFE) · self.assertEqual(registradores[rd_hi], 1) · self.assertEqual(registradores[rd_lo], 0xFFFFFFFE) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_seguido_de_mflo_mfhi` | div seguido de mflo mfhi | self.assertEqual(estado_especial.lo, 3) · self.assertEqual(estado_especial.hi, 2) · self.assertEqual(registradores[rd_lo], 3) · self.assertEqual(registradores[rd_hi], 2) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_negativo_seguido_de_mflo_mfhi` | div negativo seguido de mflo mfhi | self.assertEqual(estado_especial.lo, 0xFFFFFFFD) # -3 · self.assertEqual(estado_especial.hi, 0xFFFFFFFE) # -2 · self.assertEqual(registradores[rd_lo], 0xFFFFFFFD) · self.assertEqual(registradores[rd_hi], 0xFFFFFFFE) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_divu_seguido_de_mflo_mfhi` | divu seguido de mflo mfhi | self.assertEqual(estado_especial.lo, 0x7FFFFFFF) · self.assertEqual(estado_especial.hi, 1) · self.assertEqual(registradores[rd_lo], 0x7FFFFFFF) · self.assertEqual(registradores[rd_hi], 1) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_por_zero_seguido_de_mflo_mfhi` | div por zero seguido de mflo mfhi | self.assertEqual(estado_especial.lo, 0xFFFFFFFF) · self.assertEqual(estado_especial.hi, 17) · self.assertEqual(registradores[rd_lo], 0xFFFFFFFF) · self.assertEqual(registradores[rd_hi], 17) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_div_negativo_por_zero_seguido_de_mflo_mfhi` | div negativo por zero seguido de mflo mfhi | self.assertEqual(estado_especial.lo, 0x00000001) · self.assertEqual(estado_especial.hi, 0xFFFFFFFF) · self.assertEqual(registradores[rd_lo], 0x00000001) · self.assertEqual(registradores[rd_hi], 0xFFFFFFFF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_divu_por_zero_seguido_de_mflo_mfhi` | divu por zero seguido de mflo mfhi | self.assertEqual(estado_especial.lo, 0xFFFFFFFF) · self.assertEqual(estado_especial.hi, 17) · self.assertEqual(registradores[rd_lo], 0xFFFFFFFF) · self.assertEqual(registradores[rd_hi], 17) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_j_executa_instrucao_no_delay_slot` | j executa instrucao no delay slot | self.assertEqual(registradores[8], 42) · self.assertEqual(registradores[9], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_beq_executa_instrucao_no_delay_slot` | beq executa instrucao no delay slot | self.assertEqual(registradores[10], 42) · self.assertEqual(registradores[11], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_beq_nao_tomado_executa_delay_slot` | beq nao tomado executa delay slot | self.assertEqual(registradores[10], 42) · self.assertEqual(registradores[11], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sllv` | sllv | self.assertEqual(registradores[10], 12) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_srlv` | srlv | self.assertEqual(registradores[10], 4) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_srav` | srav | self.assertEqual(registradores[10], 0xFFFFFFFC) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwl_alinhamento_zero` | lwl alinhamento zero | self.assertEqual(resultado, 0x44BBCCDD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwl_alinhamento_tres` | lwl alinhamento tres | self.assertEqual(resultado, 0x11223344) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwr_alinhamento_zero` | lwr alinhamento zero | self.assertEqual(resultado, 0x11223344) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwr_alinhamento_tres` | lwr alinhamento tres | self.assertEqual(resultado, 0xAABBCC11) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwl_alinhamento_um` | lwl alinhamento um | self.assertEqual(resultado, 0x3344CCDD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwl_alinhamento_dois` | lwl alinhamento dois | self.assertEqual(resultado, 0x223344DD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwr_alinhamento_um` | lwr alinhamento um | self.assertEqual(resultado, 0xAA112233) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwr_alinhamento_dois` | lwr alinhamento dois | self.assertEqual(resultado, 0xAABB1122) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwl_integrado_memoria` | lwl integrado memoria | self.assertEqual(registradores[2], 0x44BBCCDD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwr_integrado_memoria` | lwr integrado memoria | self.assertEqual(registradores[2], 0x11223344) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwl_integrado_deslocamento_um` | lwl integrado deslocamento um | self.assertEqual(registradores[2], 0x3344CCDD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwr_integrado_deslocamento_um` | lwr integrado deslocamento um | self.assertEqual(registradores[2], 0xAA112233) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwl_integrado_deslocamento_dois` | lwl integrado deslocamento dois | self.assertEqual(registradores[2], 0x223344DD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwr_integrado_deslocamento_dois` | lwr integrado deslocamento dois | self.assertEqual(registradores[2], 0xAABB1122) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwl_integrado_deslocamento_tres` | lwl integrado deslocamento tres | self.assertEqual(registradores[2], 0x11223344) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwr_integrado_deslocamento_tres` | lwr integrado deslocamento tres | self.assertEqual(registradores[2], 0xAABBCC11) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lwl_lwr_combinados` | lwl lwr combinados | self.assertEqual(registradores[2], 0x88112233) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swl_alinhamento_zero` | swl alinhamento zero | self.assertEqual(resultado, 0x112233AA) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swl_alinhamento_tres` | swl alinhamento tres | self.assertEqual(resultado, 0xAABBCCDD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swr_alinhamento_zero` | swr alinhamento zero | self.assertEqual(resultado, 0xAABBCCDD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swr_alinhamento_tres` | swr alinhamento tres | self.assertEqual(resultado, 0xDD223344) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swl_alinhamento_um` | swl alinhamento um | self.assertEqual(resultado, 0x1122AABB) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swl_alinhamento_dois` | swl alinhamento dois | self.assertEqual(resultado, 0x11AABBCC) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swr_alinhamento_um` | swr alinhamento um | self.assertEqual(resultado, 0xBBCCDD44) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swr_alinhamento_dois` | swr alinhamento dois | self.assertEqual(resultado, 0xCCDD3344) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swl_integrado_deslocamento_zero` | swl integrado deslocamento zero | self.assertEqual( memoria.read_u32(endereco_dados), 0x112233AA, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swr_integrado_deslocamento_zero` | swr integrado deslocamento zero | self.assertEqual( memoria.read_u32(endereco_dados), 0xAABBCCDD, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swl_integrado_deslocamento_um` | swl integrado deslocamento um | self.assertEqual( memoria.read_u32(endereco_dados), 0x1122AABB, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swr_integrado_deslocamento_um` | swr integrado deslocamento um | self.assertEqual( memoria.read_u32(endereco_dados), 0xBBCCDD44, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swl_integrado_deslocamento_dois` | swl integrado deslocamento dois | self.assertEqual( memoria.read_u32(endereco_dados), 0x11AABBCC, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swr_integrado_deslocamento_dois` | swr integrado deslocamento dois | self.assertEqual( memoria.read_u32(endereco_dados), 0xCCDD3344, ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swl_deslocamento_tres` | swl deslocamento tres | self.assertEqual( memoria.read_u32(0x2000), 0xAABBCCDD ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_swr_deslocamento_tres` | swr deslocamento tres | self.assertEqual( memoria.read_u32(0x2000), 0xDD223344 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/test_bios.py`

Leitura BIOS; componentes: BIOS, arquivo temporário, MemoryBus e RAM.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_tamanho_da_bios` | tamanho da bios | self.assertEqual(len(self.bios.dados), 512 * 1024) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ler_u8` | ler u8 | self.assertEqual(self.bios.ler_u8(0), 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ler_u16` | ler u16 | self.assertEqual(self.bios.ler_u16(0), 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ler_u32` | ler u32 | self.assertEqual(self.bios.ler_u32(0), 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ler_u32_little_endian` | ler u32 little endian | self.assertEqual(bios.ler_u32(0), 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_endereco_negativo` | endereco negativo | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_fora_dos_limites` | leitura fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_u32_no_final_da_bios` | leitura u32 no final da bios | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_tamanho_invalido` | tamanho invalido | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_u16_bios_desalinhada` | leitura u16 bios desalinhada | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_u32_bios_desalinhada` | leitura u32 bios desalinhada | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/test_cop0.py`

Registradores e exceções COP0; componente testado diretamente: COP0.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_inicializacao_dos_registradores` | inicializacao dos registradores | self.assertEqual( cop0.ler_registrador(numero), 0 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_escrever_e_ler_registrador` | escrever e ler registrador | self.assertEqual( cop0.ler_registrador(12), 0x12345678 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_valor_limitado_a_32_bits` | valor limitado a 32 bits | self.assertEqual( cop0.ler_registrador(12), 0x23456789 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_numero_de_registrador_invalido` | numero de registrador invalido | with self.assertRaises(ValueError): · with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_prid_nao_pode_ser_escrito` | prid nao pode ser escrito | self.assertEqual( cop0.ler_registrador(15), valor_inicial ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_registrar_excecao_atualiza_cause_e_epc` | registrar excecao atualiza cause e epc | self.assertEqual( (cop0.ler_registrador(COP0.CAUSE) >> 2) & 0x1F, 8 ) · self.assertEqual( cop0.ler_registrador(COP0.EPC), 0x1000 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_registrar_excecao_preserva_outros_bits_de_cause` | registrar excecao preserva outros bits de cause | self.assertEqual( cop0.ler_registrador(COP0.CAUSE) & ~(0x1F << 2) & ~(1 << 31), 0xB0000003 & ~(1 << 31) ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_entrar_em_excecao_desloca_historico` | entrar em excecao desloca historico | self.assertEqual( cop0.ler_registrador(COP0.STATUS) & 0x3F, 0b101100 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_entrar_em_excecao_preserva_bits_superiores` | entrar em excecao preserva bits superiores | self.assertEqual( status_final & ~0x3F, valor_inicial & ~0x3F ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_excecao_normal` | excecao normal | self.assertEqual( (cop0.ler_registrador(COP0.CAUSE) >> 2) & 0x1F, 8 ) · self.assertEqual( cop0.ler_registrador(COP0.EPC), 0x1000 ) · self.assertEqual( cop0.ler_registrador(COP0.CAUSE) & (1 << 31), 0 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_excecao_em_delay_slot` | excecao em delay slot | self.assertEqual( (cop0.ler_registrador(COP0.CAUSE) >> 2) & 0x1F, 9 ) · self.assertEqual( cop0.ler_registrador(COP0.EPC), 0x1000 ) · self.assertNotEqual( cop0.ler_registrador(COP0.CAUSE) & (1 << 31), 0 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_excecao_atualiza_status` | excecao atualiza status | self.assertEqual( cop0.ler_registrador(COP0.STATUS) & 0x3F, 0b101100 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_vetor_excecao` | vetor excecao | self.assertEqual(COP0.VETOR_EXCECAO, 0x80000080) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/test_cpu.py`

Execução da CPU; componentes: CPU, MemoryBus, RAM e estado de delay.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_executar_addiu` | executar addiu | self.assertEqual(cpu.registradores[8], 42) · self.assertEqual(cpu.pc, 0x1004) · self.assertEqual(cpu.registradores[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_executar_uma_instrucao_por_chamada` | executar uma instrucao por chamada | self.assertEqual(cpu.registradores[8], 42) · self.assertEqual(cpu.registradores[9], 0) · self.assertEqual(cpu.pc, 0x1004) · self.assertEqual(cpu.registradores[9], 10) · self.assertEqual(cpu.pc, 0x1008) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_beq_com_delay_slot_entre_chamadas` | beq com delay slot entre chamadas | self.assertEqual(cpu.pc, 0x1004) · self.assertEqual(cpu.registradores[8], 42) · self.assertEqual(cpu.pc, 0x100C) · self.assertEqual(cpu.registradores[9], 10) · self.assertEqual(cpu.pc, 0x1010) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/test_cpu_control_flow.py`

Fluxo de controle; componentes: CPU, RAM, interpretador e estado de delay.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_execucao_sequencial_respeita_limite_e_pc` | execucao sequencial respeita limite e pc | self.assertEqual(self.cpu.pc, 0x1008) · self.assertEqual(self.cpu.registradores[8], 11) · self.assertEqual(self.cpu.registradores[9], 18) · self.assertEqual(self.cpu.registradores[10], 0) · self.assertEqual(self.cpu.estado_delay, { "delay_slot_ativo": False, "destino_atrasado": None, }) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_branch_tomado_executa_slot_e_aplica_destino` | branch tomado executa slot e aplica destino | self.assertEqual(self.cpu.pc, 0x1010) · self.assertEqual(self.cpu.registradores[10], 1) · self.assertEqual(self.cpu.registradores[11], 0) · self.assertEqual(self.cpu.registradores[12], 7) · self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"]) · self.assertIsNone(self.cpu.estado_delay["destino_atrasado"]) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_branch_nao_tomado_executa_slot_e_segue_sequencialmente` | branch nao tomado executa slot e segue sequencialmente | self.assertEqual(self.cpu.pc, 0x100C) · self.assertEqual(self.cpu.registradores[10], 1) · self.assertEqual(self.cpu.registradores[11], 99) · self.assertEqual(self.cpu.registradores[12], 0) · self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"]) · self.assertIsNone(self.cpu.estado_delay["destino_atrasado"]) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_estado_de_salto_pendente_persiste_entre_chamadas` | estado de salto pendente persiste entre chamadas | self.assertEqual(self.cpu.pc, 0x1004) · self.assertEqual(self.cpu.registradores[10], 0) · self.assertTrue(self.cpu.estado_delay["delay_slot_ativo"]) · self.assertEqual(self.cpu.estado_delay["destino_atrasado"], 0x100C) · self.assertEqual(self.cpu.pc, 0x100C) · self.assertEqual(self.cpu.registradores[10], 1) · self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"]) · self.assertIsNone(self.cpu.estado_delay["destino_atrasado"]) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jr_executa_delay_slot_antes_do_destino` | jr executa delay slot antes do destino | self.assertEqual(self.cpu.pc, 0x1014) · self.assertEqual(self.cpu.registradores[10], 1) · self.assertEqual(self.cpu.registradores[11], 0) · self.assertEqual(self.cpu.registradores[12], 7) · self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"]) · self.assertIsNone(self.cpu.estado_delay["destino_atrasado"]) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jalr_escreve_link_e_executa_delay_slot` | jalr escreve link e executa delay slot | self.assertEqual(self.cpu.pc, 0x1014) · self.assertEqual(self.cpu.registradores[16], 0x1008) · self.assertEqual(self.cpu.registradores[31], 0xDEADBEEF) · self.assertEqual(self.cpu.registradores[10], 1) · self.assertEqual(self.cpu.registradores[11], 0) · self.assertEqual(self.cpu.registradores[12], 7) · self.assertFalse(self.cpu.estado_delay["delay_slot_ativo"]) · self.assertIsNone(self.cpu.estado_delay["destino_atrasado"]) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/test_memory.py`

Instruções de memória e fetch; componentes: interpretador, MemoryBus, RAM e saltos.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_sw` | sw | self.assertEqual(memoria.read_u32(0x3000), 12345) · self.assertEqual(registradores[8], 12345) · self.assertEqual(registradores[9], 0x3000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lw` | lw | self.assertEqual(registradores[8], 9876) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_little_endian` | little endian | self.assertEqual(memoria.read_u8(0x2000), 0x78) · self.assertEqual(memoria.read_u8(0x2001), 0x56) · self.assertEqual(memoria.read_u8(0x2002), 0x34) · self.assertEqual(memoria.read_u8(0x2003), 0x12) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sw_atravessa_memory_bus` | sw atravessa memory bus | self.assertEqual(memoria.read_u32(0x3000), 12345) · self.assertEqual(ram.read_u32(0x3000), 12345) · self.assertEqual(registradores[8], 12345) · self.assertEqual(registradores[9], 0x3000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lw_atravessa_memory_bus` | lw atravessa memory bus | self.assertEqual(registradores[8], 9876) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sw_kseg0_atravessa_memory_bus` | sw kseg0 atravessa memory bus | self.assertEqual(ram.read_u32(0x3000), 12345) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_sw_kseg1_atravessa_memory_bus` | sw kseg1 atravessa memory bus | self.assertEqual(ram.read_u32(0x3000), 12345) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lw_kseg0_atravessa_memory_bus` | lw kseg0 atravessa memory bus | self.assertEqual(registradores[8], 9876) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_lw_kseg1_atravessa_memory_bus` | lw kseg1 atravessa memory bus | self.assertEqual(registradores[8], 9876) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_instruction_fetch_fora_dos_enderecos_programa` | instruction fetch fora dos enderecos programa | self.assertEqual(registradores[8], 42) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_instruction_fetch_instrucao_seguinte_fora_do_conjunto` | instruction fetch instrucao seguinte fora do conjunto | self.assertEqual(registradores[8], 10) · self.assertEqual(registradores[9], 20) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_instruction_fetch_kseg0_atravessa_memory_bus` | instruction fetch kseg0 atravessa memory bus | self.assertEqual(registradores[8], 42) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_instruction_fetch_kseg1_atravessa_memory_bus` | instruction fetch kseg1 atravessa memory bus | self.assertEqual(registradores[8], 42) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_instruction_fetch_endereco_desalinhado` | instruction fetch endereco desalinhado | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_instruction_fetch_instrucao_nula_preserva_zero` | instruction fetch instrucao nula preserva zero | self.assertEqual(registradores[0], 0) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_instruction_fetch_instrucao_nula` | instruction fetch instrucao nula | self.assertEqual(registradores[0], 0) · self.assertEqual(pc_final, endereco_instrucao + 4) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_instruction_fetch_instrucao_desconhecida` | instruction fetch instrucao desconhecida | with self.assertRaises(NotImplementedError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_instruction_fetch_instrucao_desconhecida_preserva_pc` | instruction fetch instrucao desconhecida preserva pc | with self.assertRaises(NotImplementedError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jr_executa_delay_slot_antes_do_destino` | jr executa delay slot antes do destino | self.assertEqual(registradores[9], 42) · self.assertEqual(registradores[10], 99) · self.assertEqual(pc_final, 0x2004) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jal_salva_endereco_retorno_e_executa_delay_slot` | jal salva endereco retorno e executa delay slot | self.assertEqual(registradores[31], 0x1008) · self.assertEqual(registradores[8], 42) · self.assertEqual(registradores[9], 99) · self.assertEqual(pc_final, 0x2004) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jalr_salva_endereco_retorno_e_executa_delay_slot` | jalr salva endereco retorno e executa delay slot | self.assertEqual(registradores[16], 0x1008) · self.assertEqual(registradores[9], 42) · self.assertEqual(registradores[10], 99) · self.assertEqual(pc_final, 0x2004) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jalr_destino_desalinhado` | jalr destino desalinhado | with self.assertRaises(EnderecoDesalinhadoError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jr_destino_desalinhado` | jr destino desalinhado | with self.assertRaises(EnderecoDesalinhadoError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_j_executa_delay_slot_e_salva_destino` | j executa delay slot e salva destino | self.assertEqual(registradores[8], 42) · self.assertEqual(registradores[9], 99) · self.assertEqual(pc_final, 0x2004) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_j_preserva_bits_superiores_de_pc` | j preserva bits superiores de pc | self.assertEqual(registradores[8], 42) · self.assertEqual(registradores[9], 99) · self.assertEqual(pc_final, 0x80002004) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_j_calcula_destino_apos_limite_de_256_mib` | j calcula destino apos limite de 256 mib | self.assertEqual(destino, 0x10400000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_j_calcula_destino_sem_cruzar_limite` | j calcula destino sem cruzar limite | self.assertEqual(destino, 0x80008000) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_j_nao_altera_registrador_ra` | j nao altera registrador ra | self.assertEqual(registradores[31], 0x12345678) · self.assertEqual(registradores[8], 42) · self.assertEqual(registradores[9], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jal_endereco_retorno_independe_do_delay_slot` | jal endereco retorno independe do delay slot | self.assertEqual(registradores[31], 42) · self.assertEqual(registradores[8], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jalr_com_destino_ra_zero` | jalr com destino ra zero | self.assertEqual(registradores[0], 0) · self.assertEqual(registradores[9], 42) · self.assertEqual(registradores[10], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_jr_nao_altera_registradores` | jr nao altera registradores | self.assertEqual(registradores[8], 0x2000) · self.assertEqual(registradores[31], 0x12345678) · self.assertEqual(registradores[9], 42) · self.assertEqual(registradores[10], 99) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_beq_com_memory_bus_executa_delay_slot_e_destino` | beq com memory bus executa delay slot e destino | self.assertEqual(registradores[10], 42) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 99) · self.assertEqual(pc_final, 0x1010) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_beq_nao_tomado_com_memory_bus` | beq nao tomado com memory bus | self.assertEqual(registradores[10], 42) · self.assertEqual(registradores[11], 11) · self.assertEqual(pc_final, 0x100C) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bne_tomado_com_memory_bus` | bne tomado com memory bus | self.assertEqual(registradores[10], 42) · self.assertEqual(registradores[11], 0) · self.assertEqual(registradores[12], 99) · self.assertEqual(pc_final, 0x1010) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bne_nao_tomado_com_memory_bus` | bne nao tomado com memory bus | self.assertEqual(registradores[10], 42) · self.assertEqual(registradores[11], 11) · self.assertEqual(pc_final, 0x100C) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_beq_com_deslocamento_negativo_memory_bus` | beq com deslocamento negativo memory bus | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 42) · self.assertEqual(pc_final, 0x1004) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_bne_com_deslocamento_negativo_memory_bus` | bne com deslocamento negativo memory bus | self.assertEqual(registradores[10], 1) · self.assertEqual(registradores[11], 42) · self.assertEqual(pc_final, 0x1004) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/test_memory_bus.py`

Barramento e regiões; componentes: MemoryBus, RAM, BIOS e buffers de scratchpad/I/O.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_leitura_e_escrita_na_ram_principal` | leitura e escrita na ram principal | self.assertEqual(resultado, 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_kseg0_acessa_a_mesma_ram_fisica` | kseg0 acessa a mesma ram fisica | self.assertEqual(resultado, 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_kseg1_acessa_a_mesma_ram_fisica` | kseg1 acessa a mesma ram fisica | self.assertEqual(resultado, 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_escrita_por_kseg0_e_leitura_por_endereco_fisico` | escrita por kseg0 e leitura por endereco fisico | self.assertEqual(resultado, 0xABCDEF12) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_escrita_por_kseg1_e_leitura_por_endereco_fisico` | escrita por kseg1 e leitura por endereco fisico | self.assertEqual(resultado, 0xABCDEF12) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_endereco_fisico_fora_da_ram_gera_erro` | endereco fisico fora da ram gera erro | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_armazena_e_le_valor` | scratchpad armazena e le valor | self.assertEqual(resultado, 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_acesso_fora_dos_limites` | scratchpad rejeita acesso fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_palavra_que_ultrapassa_limite` | scratchpad rejeita palavra que ultrapassa limite | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_escrita_que_ultrapassa_limite` | scratchpad rejeita escrita que ultrapassa limite | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_le_u8` | scratchpad le u8 | self.assertEqual(resultado, 0xAB) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_escreve_u8` | scratchpad escreve u8 | self.assertEqual(memoria.scratchpad[0x10], 0xAB) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ram_principal_le_u8` | ram principal le u8 | self.assertEqual(resultado, 0xAB) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ram_principal_escreve_u8` | ram principal escreve u8 | self.assertEqual(resultado, 0xAB) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_le_u16` | scratchpad le u16 | self.assertEqual(resultado, 0x1234) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_escreve_u16` | scratchpad escreve u16 | self.assertEqual(memoria.scratchpad[0x10], 0x34) · self.assertEqual(memoria.scratchpad[0x11], 0x12) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ram_principal_le_u16` | ram principal le u16 | self.assertEqual(resultado, 0x1234) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ram_principal_escreve_u16` | ram principal escreve u16 | self.assertEqual(resultado, 0x1234) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_leitura_u16_desalinhada` | scratchpad rejeita leitura u16 desalinhada | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_escrita_u16_desalinhada` | scratchpad rejeita escrita u16 desalinhada | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_leitura_u32_desalinhada` | scratchpad rejeita leitura u32 desalinhada | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_escrita_u32_desalinhada` | scratchpad rejeita escrita u32 desalinhada | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ram_rejeita_escrita_u16_que_ultrapassa_limite` | ram rejeita escrita u16 que ultrapassa limite | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ram_rejeita_escrita_u8_fora_dos_limites` | ram rejeita escrita u8 fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ram_rejeita_leitura_u8_fora_dos_limites` | ram rejeita leitura u8 fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_kseg0_rejeita_leitura_fora_dos_limites_da_ram` | kseg0 rejeita leitura fora dos limites da ram | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_kseg1_rejeita_leitura_fora_dos_limites_da_ram` | kseg1 rejeita leitura fora dos limites da ram | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_kseg0_e_kseg1_compartilham_a_mesma_memoria_fisica` | kseg0 e kseg1 compartilham a mesma memoria fisica | self.assertEqual(memoria.read_u32(0xA0001000), 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_kseg1_e_kseg0_compartilham_a_mesma_memoria_fisica` | kseg1 e kseg0 compartilham a mesma memoria fisica | self.assertEqual(memoria.read_u32(0x80001000), 0x89ABCDEF) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_endereco_fisico_e_aliases_virtuais_compartilham_dados` | endereco fisico e aliases virtuais compartilham dados | self.assertEqual(memoria.read_u32(0x80001000), 0xCAFEBABE) · self.assertEqual(memoria.read_u32(0xA0001000), 0xCAFEBABE) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_e_ram_sao_regioes_independentes` | scratchpad e ram sao regioes independentes | self.assertEqual(memoria.read_u32(0x00000010), 0x12345678) · self.assertEqual(memoria.read_u32(0x1F800010), 0xAABBCCDD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_escrita_na_scratchpad_nao_altera_ram` | escrita na scratchpad nao altera ram | self.assertEqual(ram.read_u32(0x10), 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_escrita_na_ram_nao_altera_scratchpad` | escrita na ram nao altera scratchpad | self.assertEqual(memoria.read_u32(0x1F800010), 0xAABBCCDD) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_u32_que_atravessa_inicio_da_scratchpad` | leitura u32 que atravessa inicio da scratchpad | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_escrita_u32_que_atravessa_inicio_da_scratchpad` | escrita u32 que atravessa inicio da scratchpad | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_u32_no_ultimo_endereco_valido` | scratchpad u32 no ultimo endereco valido | self.assertEqual(memoria.read_u32(0x1F8003FC), 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_escrita_u32_no_limite_final` | scratchpad rejeita escrita u32 no limite final | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_escrita_u16_que_ultrapassa_limite` | scratchpad rejeita escrita u16 que ultrapassa limite | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_escrita_u8_no_limite_final` | scratchpad rejeita escrita u8 no limite final | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_u8_no_ultimo_endereco_valido` | scratchpad u8 no ultimo endereco valido | self.assertEqual(memoria.read_u8(0x1F8003FF), 0xAB) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_scratchpad_rejeita_leitura_u8_no_limite_final` | scratchpad rejeita leitura u8 no limite final | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_u8_na_ram_nao_acessa_scratchpad_ao_lado` | leitura u8 na ram nao acessa scratchpad ao lado | self.assertEqual(memoria.read_u8(0x1FFFFF), 0x42) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_u32_que_cruza_inicio_da_scratchpad_e_rejeitada` | leitura u32 que cruza inicio da scratchpad e rejeitada | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_escrita_nao_deve_encaminhar_acesso_que_cruza_inicio_scratchpad` | escrita nao deve encaminhar acesso que cruza inicio scratchpad | with self.assertRaises(ValueError): · self.assertEqual(ram.escritas, []) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_escrita_que_cruza_inicio_scratchpad_e_rejeitada` | escrita que cruza inicio scratchpad e rejeitada | with self.assertRaises(ValueError): · self.assertEqual(ram.escritas, []) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_que_cruza_inicio_scratchpad_e_rejeitada` | leitura que cruza inicio scratchpad e rejeitada | with self.assertRaises(ValueError): · self.assertEqual(ram.leituras, []) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_bios_endereco_fisico` | leitura bios endereco fisico | self.assertEqual( memoria.read_u32(0x1FC00000), 0x12345678 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_bios_endereco_virtual` | leitura bios endereco virtual | self.assertEqual( memoria.read_u32(0xBFC00000), 0x12345678 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_escrita_bios_endereco_fisico_rejeitada` | escrita bios endereco fisico rejeitada | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_escrita_bios_endereco_virtual_rejeitada` | escrita bios endereco virtual rejeitada | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_bios_fora_dos_limites` | leitura bios fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_leitura_bios_que_atravessa_limite` | leitura bios que atravessa limite | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/test_memory_integration.py`

Integração de memória; componentes: interpretador e RAM.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_sw_e_lw_usam_a_mesma_ram` | sw e lw usam a mesma ram | self.assertEqual(self.ram.read_u32(0x100), 0x12345678) · self.assertEqual(registradores[10], 0x12345678) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/test_mips_exceptions.py`

Tipos de exceção; componentes: classes da hierarquia MIPSException.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_integer_overflow_e_uma_excecao_mips` | integer overflow e uma excecao mips | self.assertIsInstance(erro, MIPSException) · self.assertIsInstance(erro, Exception) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_integer_overflow_e_identificado_especificamente` | integer overflow e identificado especificamente | with self.assertRaises(IntegerOverflow): · with self.assertRaises(MIPSException): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

### `test/test_ps1.py`

Inicialização PS1; componentes: PS1, CPU, MemoryBus e BIOS. Dependência externa: SCPH1001.BIN.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_bios_real_executa_primeira_instrucao` | bios real executa primeira instrucao | self.assertEqual( ps1.memory_bus.read_u32(ps1.cpu.pc), 0x3C080013, # LUI $t0, 0x0013 ) · self.assertEqual(ps1.cpu.registradores[8], 0x00130000) · self.assertEqual(ps1.cpu.pc, 0xBFC00004) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. Requer SCPH1001.BIN. |

### `test/test_ram.py`

RAM; componente: armazenamento principal.

| Teste | Objetivo/cenário | Verificação explícita no método | Limitação |
|---|---|---|---|
| `test_ram_tem_2_mib` | ram tem 2 mib | self.assertEqual( self.ram.tamanho, 2 * 1024 * 1024 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_ram_inicia_com_zeros` | ram inicia com zeros | self.assertEqual( self.ram.read_u8(0), 0 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u8_armazena_um_byte` | write u8 armazena um byte | self.assertEqual( self.ram.read_u8(0x1000), 0xAB ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u8_nao_altera_endereco_vizinho` | write u8 nao altera endereco vizinho | self.assertEqual( self.ram.read_u8(0x1001), 0 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_read_u8_fora_dos_limites` | read u8 fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_read_u8_com_endereco_negativo` | read u8 com endereco negativo | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u8_fora_dos_limites` | write u8 fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u8_com_endereco_negativo` | write u8 com endereco negativo | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u16_e_read_u16_preservam_valor` | write u16 e read u16 preservam valor | self.assertEqual( self.ram.read_u16(0x1000), valor ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u16_usa_little_endian` | write u16 usa little endian | self.assertEqual(self.ram.read_u8(0x1000), 0x34) · self.assertEqual(self.ram.read_u8(0x1001), 0x12) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u16_limita_valor_a_16_bits` | write u16 limita valor a 16 bits | self.assertEqual( self.ram.read_u16(0x1000), 0x5678 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_read_u16_fora_dos_limites` | read u16 fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u16_fora_dos_limites` | write u16 fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u32_e_read_u32_preservam_valor` | write u32 e read u32 preservam valor | self.assertEqual( self.ram.read_u32(0x1000), valor ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u32_usa_little_endian` | write u32 usa little endian | self.assertEqual(self.ram.read_u8(0x1000), 0x78) · self.assertEqual(self.ram.read_u8(0x1001), 0x56) · self.assertEqual(self.ram.read_u8(0x1002), 0x34) · self.assertEqual(self.ram.read_u8(0x1003), 0x12) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u32_limita_valor_a_32_bits` | write u32 limita valor a 32 bits | self.assertEqual( self.ram.read_u32(0x1000), 0xABCDEF01 ) | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_read_u32_fora_dos_limites` | read u32 fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u32_fora_dos_limites` | write u32 fora dos limites | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_read_u16_com_endereco_desalinhado` | read u16 com endereco desalinhado | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u16_com_endereco_desalinhado` | write u16 com endereco desalinhado | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_read_u32_com_endereco_desalinhado` | read u32 com endereco desalinhado | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |
| `test_write_u32_com_endereco_desalinhado` | write u32 com endereco desalinhado | with self.assertRaises(ValueError): | Restrito ao cenário e às verificações deste método; não demonstra comportamento global do console. |

