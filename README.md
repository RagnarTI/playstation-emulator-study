# PS1 Emulator

Emulador de PlayStation 1 desenvolvido em Python, com foco no estudo da arquitetura do console, na emulação de hardware e na implementação gradual de seus principais componentes.

> **Status:** Em desenvolvimento ativo. A CPU MIPS R3000A possui uma implementação substancial, enquanto os demais subsistemas estão sendo desenvolvidos progressivamente.

## Objetivos

- Compreender e reproduzir a arquitetura do primeiro PlayStation.
- Implementar os componentes de hardware de forma modular.
- Desenvolver uma CPU MIPS R3000A com suporte às instruções do processador.
- Construir um barramento de memória capaz de integrar CPU, memória e periféricos.
- Implementar progressivamente os subsistemas gráficos, sonoros e de entrada e saída.
- Utilizar testes para verificar o comportamento e a compatibilidade entre os componentes.

## Tecnologias

- **Linguagem:** Python
- **Plataforma-alvo:** Sony PlayStation (PS1)
- **Abordagem:** emulação modular de hardware

## Arquitetura do projeto

O projeto está organizado em módulos separados para facilitar o desenvolvimento, os testes e a integração dos componentes.

| Diretório ou arquivo | Responsabilidade |
|---|---|
| `cpu/` | CPU MIPS R3000A, interpretador, COP0, exceções, cache e GTE |
| `memory/` | RAM principal, BIOS ROM e scratchpad |
| `memory-bus/` | Mapeamento de memória, controle de memória e DMA |
| `gpu/` | Processamento gráfico, VRAM e saída de vídeo |
| `spu/` | Processamento de áudio e memória sonora |
| `cd-rom/` | Controle do CD-ROM e leitura de discos |
| `mdec/` | Decodificação de dados de imagem e vídeo |
| `timers/` | Contadores e temporizadores de hardware |
| `interrupt-controller/` | Gerenciamento de interrupções dos dispositivos |
| `i-o/` | Interfaces de entrada e saída serial e paralela |
| `ps1.py` | Composição dos componentes principais do sistema |
| `roadmap.md` | Estado dos módulos e planejamento do desenvolvimento |

A existência de um módulo ou de uma região mapeada não significa que o componente esteja completamente implementado. O progresso individual de cada arquivo pode ser consultado em `roadmap.md`.

## Estado atual

O projeto está em fase de implementação.

- **CPU:** implementação substancial do MIPS R3000A.
- **Interpretador MIPS:** conjunto de instruções parcialmente implementado.
- **COP0 e exceções:** implementação dos recursos atualmente modelados.
- **RAM e BIOS ROM:** módulos de armazenamento e acesso existentes.
- **Barramento de memória:** roteamento implementado para as regiões já suportadas, com algumas regiões ainda utilizando armazenamento provisório.
- **GPU, SPU, CD-ROM, DMA e outros periféricos:** implementação planejada ou pendente conforme o estado de cada arquivo.

Consulte [`roadmap.md`](roadmap.md) para obter o detalhamento atualizado.

## Requisitos

- Python compatível com a versão utilizada no desenvolvimento.
- Git para clonar e versionar o projeto.
- Uma imagem de BIOS compatível, fornecida pelo próprio usuário e obtida legalmente, caso seja necessária para executar os recursos que dependem dela.

As dependências adicionais e a versão mínima de Python deverão ser documentadas aqui quando forem formalmente definidas no projeto.

## Como obter o projeto

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd <DIRETORIO_DO_REPOSITORIO>
```

Substitua os marcadores pelo endereço e pelo nome reais do seu repositório.

## Testes

Os testes são importantes para preservar o comportamento dos componentes já implementados durante a evolução do emulador.

Execute a suíte de testes utilizando o comando definido pela configuração atual do projeto. Se os testes forem organizados com `pytest`, por exemplo:

```bash
python -m pytest
```

Esse comando é apenas uma sugestão caso `pytest` seja o executor utilizado. Consulte a configuração existente antes de adotá-lo como procedimento oficial.

## BIOS e arquivos proprietários

A BIOS original do PlayStation é um firmware proprietário da Sony e **não é distribuída com este projeto**.

O diretório local destinado à BIOS deve permanecer fora do versionamento. A regra correspondente deve ser mantida no `.gitignore`.

O usuário é responsável por obter e utilizar os arquivos necessários de acordo com a legislação aplicável. Este projeto não fornece instruções para obter cópias não autorizadas de firmware.

## Escopo e limitações

Este projeto tem finalidade educacional e experimental. A compatibilidade com jogos comerciais, a precisão temporal do hardware e a execução completa do sistema ainda dependem da implementação e validação dos subsistemas.

Não há garantia de compatibilidade com todos os jogos ou de funcionamento completo do console.

## Contribuições

Durante o desenvolvimento, recomenda-se:

1. Consultar o `roadmap.md` antes de iniciar um componente.
2. Preservar as interfaces existentes entre os módulos.
3. Adicionar ou atualizar testes para as funcionalidades implementadas.
4. Executar os testes de regressão após alterações relevantes.
5. Não incluir BIOS ou outros arquivos proprietários no repositório.

## Aviso legal

Este projeto é independente, educacional e não oficial. Não é afiliado, patrocinado ou endossado pela Sony Interactive Entertainment.

PlayStation e PS1 são marcas registradas de seus respectivos titulares.

## Licença

A licença do projeto ainda deve ser definida. Antes de publicar o repositório, escolha uma licença compatível com o código que você escreveu e com eventuais dependências utilizadas.