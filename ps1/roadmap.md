# Roadmap de desenvolvimento — emulador PlayStation 1

Os estados abaixo descrevem o conteúdo observado no código. Não foi executada a suíte nesta atualização; portanto, nenhum componente funcional recebe `[IMPLEMENTADO]` com base somente nesta inspeção. `[BÁSICO]` em `__init__.py` identifica apenas o arquivo marcador de pacote, não um componente do emulador.

## Estrutura e estado por arquivo

```text
ps1/
├── cpu/ — processador R3000A, interpretador e coprocessadores
│   ├── [BÁSICO] __init__.py — marcador de pacote
│   ├── [AVANÇADO] mips_interpreter.py — decodificação e execução de um conjunto amplo, ainda incompleto, de instruções
│   ├── [REVISÃO PENDENTE] mips_exceptions.py — tipos de exceção arquitetural atualmente modelados; cobertura não é completa
│   ├── [AVANÇADO] mips_r3000a.py — estado da CPU, ciclo de execução e integração síncrona com COP0
│   ├── [AVANÇADO] cop0.py — registradores, máscaras, exceções síncronas e RFE; interrupções de hardware não implementadas
│   ├── [PENDENTE] gte.py — sem implementação; integrar durante o desenvolvimento da GPU
│   └── [PENDENTE] cache.py — sem implementação de cache; I-cache permanece pendente
│
├── memory-bus/ — tradução de endereços e encaminhamento aos dispositivos
│   ├── [BÁSICO] __init__.py — marcador de pacote
│   ├── [PARCIAL] memory_mapping.py — RAM, BIOS e scratchpad acessíveis; várias regiões de hardware usam armazenamento provisório
│   ├── [PENDENTE] memory_control.py — sem implementação
│   └── [PENDENTE] dma_controller.py — sem implementação
│
├── memory/ — memórias e ROM do sistema
│   ├── bios/ — diretório destinado à mídia da BIOS; conteúdo de mídia não classificado neste roadmap
│   ├── [BÁSICO] __init__.py — marcador de pacote
│   ├── [REVISÃO PENDENTE] main_ram.py — armazenamento e acessos básicos à RAM; validar pela suíte atual
│   ├── [REVISÃO PENDENTE] bios_rom.py — carregamento e leitura da ROM; validar pela suíte atual
│   └── [PENDENTE] scratchpad_ram.py — módulo separado vazio; há armazenamento de scratchpad dentro do MemoryBus
│
├── gpu/ — comandos gráficos, VRAM e saída de vídeo
│   ├── [BÁSICO] __init__.py — marcador de pacote
│   ├── [PENDENTE] gpu_commands.py
│   ├── [PENDENTE] vram.py
│   └── [PENDENTE] video_output.py
│
├── spu/ — som e memória de som
│   ├── [BÁSICO] __init__.py — marcador de pacote
│   ├── [PENDENTE] audio_processing.py
│   └── [PENDENTE] sound_ram.py
│
├── cd-rom/ — leitura de discos e controlador de CD-ROM
│   ├── cd-display/ — diretório de mídia; este é o nome real atual
│   ├── [BÁSICO] __init__.py — marcador de pacote
│   ├── [PENDENTE] cd_rom_controller.py
│   └── [PENDENTE] disc_reading.py
│
├── mdec/ — decodificador de vídeo em movimento
│   ├── [BÁSICO] __init__.py — marcador de pacote
│   └── [PENDENTE] mdec.py
│
├── timers/ — temporizadores e sincronização com eventos do sistema
│   ├── [BÁSICO] __init__.py — marcador de pacote
│   └── [PENDENTE] timers.py
│
├── interrupt-controller/ — controle e identificação de fontes de interrupção
│   ├── [BÁSICO] __init__.py — marcador de pacote
│   ├── [PENDENTE] interrupt_controller.py
│   └── [PENDENTE] interrupt_sources.py
│
├── i-o/ — interfaces seriais e paralela
│   ├── [BÁSICO] __init__.py — marcador de pacote
│   ├── [PENDENTE] sio0.py
│   ├── [PENDENTE] sio1.py
│   └── [PENDENTE] pio.py
│
├── [REVISÃO PENDENTE] __init__.py — API pública com exportações sob demanda; importação dinâmica do diretório `memory-bus/` precisa de validação no ambiente atual
├── [BÁSICO] roadmap.md — painel de acompanhamento baseado em inspeção estática
└── [BÁSICO] ps1.py — composição inicial de CPU, RAM, BIOS e MemoryBus
```

## Responsabilidades e dependências

- `ps1.py` instancia CPU, RAM, BIOS e MemoryBus. A CPU busca instruções e acessa dados pelo barramento fornecido à execução.
- `memory/main_ram.py` fornece o armazenamento da RAM; `memory/bios_rom.py` fornece leitura da ROM. `memory-bus/memory_mapping.py` traduz endereços e encaminha os acessos.
- O MemoryBus também armazena bytes para scratchpad e para algumas regiões mapeadas de I/O/expansão/controle de cache. Esse armazenamento provisório **não implementa os registradores nem o comportamento dos dispositivos reais**.
- O interpretador depende dos tipos em `mips_exceptions.py`; `mips_r3000a.py` encaminha exceções síncronas reconhecidas ao COP0. O conjunto de instruções e os tipos arquiteturais ainda têm lacunas.
- Timers e dispositivos deverão sinalizar fontes ao controlador de interrupções; esse fluxo ainda precisa ser implementado e integrado à CPU/COP0. DMA depende de acesso ao barramento e de integração com os dispositivos envolvidos.
- CD-ROM alimenta dados que podem ser processados pelo MDEC e enviados à GPU. SIO0/SIO1 e PIO atendem interfaces de entrada/saída. SPU e sua RAM formam o subsistema de áudio. Esses fluxos são planejamento, não funcionalidades presentes.

## Próximas etapas sugeridas

1. Executar a suíte atual e revisar os módulos marcados `[REVISÃO PENDENTE]`; atualizar os estados somente com resultados observados.
2. Completar e validar o mapa de memória e substituir armazenamento provisório por registradores/dispositivos conforme forem implementados.
3. Implementar a I-cache dentro de `cpu/cache.py` após estabilizar os caminhos de busca e controle de cache do barramento. O GTE deve ser integrado junto ao desenvolvimento da GPU, não tratado como requisito isolado imediato.
4. Implementar o controlador de interrupções e suas fontes, depois integrar timers e eventos de dispositivos à CPU.
5. Implementar DMA e os componentes de CD-ROM, MDEC, GPU, I/O e SPU, validando cada dispositivo antes da integração entre subsistemas.

## Critério para avançar estados

- `[PENDENTE]`: implementação não iniciada; arquivos vazios de componentes ficam neste estado.
- `[BÁSICO]`: existe uma implementação inicial com funções fundamentais.
- `[PARCIAL]`: parte relevante está pronta, mas faltam funcionalidades previstas.
- `[AVANÇADO]`: implementação substancial com lacunas conhecidas.
- `[REVISÃO PENDENTE]`: o escopo aparenta estar implementado, mas falta revisão, validação ou execução de testes pertinentes.
- `[IMPLEMENTADO]`: usar somente quando o escopo definido estiver concluído e validado por testes pertinentes executados.
