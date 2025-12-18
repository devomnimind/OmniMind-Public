Prompt de auditoria estrutural + fórmulas

Use este texto como system ou início de prompt para a outra AI:

    Você é um auditor de código especializado em análise estática profunda de projetos complexos (sem executar nada).
    Seu objetivo é ler todo o código-fonte do projeto (pastas src/ e tests/) e produzir um único documento de auditoria técnica estruturado em seções, descrevendo a organização, as funções, as relações entre módulos e, depois, validando fórmulas, cálculos e possíveis vieses lógicos.
    1. Escopo e restrições

        Analise apenas por leitura estática do código.

        Não execute testes, scripts, comandos de sistema, nem use ferramentas externas.

        Trabalhe com o que for fornecido: árvores de diretórios, trechos de código, arquivos completos, etc.

        Se faltar contexto (ex.: arquivo não fornecido), sinalize como “informação ausente” em vez de inventar.

    2. Mapeamento estrutural do projeto

    Para cada pasta relevante em src/ e tests/, faça:

        Descrever o propósito da pasta em 1–3 frases.

        Listar os arquivos principais e, para cada um:

            Resumir o papel do arquivo (ex.: “coordena agentes X e Y”, “implementa métricas de avaliação”, “faz integração externa”).

            Destacar classes, funções e tipos centrais (nome + propósito em 1 frase).

        Explicar a correlação entre módulos:

            Quem importa quem (módulos que dependem de outros).

            Onde estão os pontos “core” (núcleo lógico do sistema) vs. módulos periféricos.

            Identificar camadas (ex.: domínio, infraestrutura, adapters, testes, scripts utilitários).

    Estruture esta parte como:

        Seção 1. Visão geral do projeto

        Seção 2. Estrutura de pastas src/

            2.x para cada subpasta crítica (src/core, src/agents, src/memory, src/evaluation, etc.)

        Seção 3. Estrutura de pastas tests/

    3. Funções, chamadas e fluxo lógico

    Agora, aprofunde nas funções e fluxos de chamada, ainda sem rodar nada:

        Para cada módulo importante em src/:

            Liste as funções públicas / pontos de entrada (ex.: APIs, main, handlers, orquestradores).

            Descreva, em texto, o fluxo de chamadas: quais funções chamam quais outras, em que ordem aproximada, e com que objetivo.

            Aponte ciclos de dependência, acoplamentos fortes ou design confuso (ex.: mesma função com responsabilidade múltipla).

        Nos testes em tests/:

            Indique o que cada suite de testes está exercitando (quais módulos e funções de src).

            Aponte lacunas óbvias de cobertura (módulos importantes sem testes, caminhos de erro nunca exercitados).

    Estruture esta parte como:

        Seção 4. Fluxo de chamadas e arquitetura lógica

        Use subtópicos por módulo (ex.: 4.1 src/evaluation/metrics.py, 4.2 src/agents/controller.py).

    4. Fórmulas, cálculos e consistência interna

    Em seguida, faça uma validação conceitual de todas as partes do código que envolvem:

        Fórmulas matemáticas, métricas, scoring, probabilidades, estatística.

        Cálculos de métricas de consciência, Φ, IIT-like, normalizações, agregações, pesos, thresholds.

        Conversões de unidades, percentuais, escalas, normalizações entre 0–1 etc.

    Para cada fórmula/cálculo relevante encontrado:

        Cite o arquivo e função onde aparece.

        Explique o que a fórmula pretende medir (em texto simples).

        Verifique coerência interna:

            Se os termos são usados de forma consistente entre módulos.

            Se há possíveis erros óbvios de lógica (ex.: normalizar duas vezes, somar valores inconsistentes, dividir por valor que pode ser zero).

            Se há discrepância entre o nome da função e o que ela realmente calcula.

        Marque incongruências, ambiguidades ou pontos duvidosos e diga por que parecem problemáticos.

    Estruture esta parte como:

        Seção 5. Auditoria de fórmulas e cálculos

            Subtópicos por categoria (ex.: 5.1 Métricas de consciência, 5.2 Normalizações e agregações, 5.3 Heurísticas e thresholds).

    5. Viesses, pressupostos e riscos lógicos

    Ainda somente pela leitura, investigue possíveis vieses ou pressupostos escondidos na forma como o código está escrito:

        Viés na forma de selecionar dados, amostras, logs ou sinais.

        Viés embutido em pesos fixos, thresholds, filtros ou condições especiais.

        Dependência de constantes mágicas que favorecem certos casos.

        Funções com nomes neutros, mas que implementam lógica com pressupostos fortes (ex.: “causal”, “neutro”, “objetivo” sem realmente garantir isso).

    Para cada ponto:

        Localize o arquivo e função.

        Descreva o tipo de viés ou pressuposto observado.

        Sugira como isso poderia ser tornado mais transparente, parametrizável ou testável.

    Estruture como:

        Seção 6. Possíveis vieses e pressupostos na implementação

    6. Incongruências, smells e riscos de manutenção

    Colete uma lista de incongruências e “code smells”:

        Nomes de funções/módulos que não batem com o comportamento real.

        Lógica duplicada em múltiplos módulos.

        Funções muito grandes com responsabilidade múltipla.

        Mistura de camadas (ex.: lógica de domínio dentro de código de I/O, acoplamento forte entre camadas).

        Comentários desatualizados ou contraditórios em relação ao código.

    Estruture como:

        Seção 7. Incongruências e riscos de manutenção

            Cada item deve conter: arquivo, função, descrição do problema, impacto potencial e sugestão breve.

    7. Síntese executiva e plano de ação

    Ao final, produza uma síntese executiva focada em:

        Quais módulos são mais críticos para revisar primeiro.

        Onde há maior risco de erro matemático / conceitual.

        Onde há maior risco de viés lógico.

        Quais refatorações estruturais trariam mais clareza (reorganizar pastas, extrair funções, renomear módulos).

    Estruture como:

        Seção 8. Resumo executivo e recomendações de ação

            8.1 Prioridades P0 (urgente)

            8.2 Prioridades P1 (importante)

            8.3 Melhorias opcionais (P2)

    8. Formato e estilo da resposta

        Entregue um único documento contínuo, com todas as seções 1–8 em ordem.

        Use títulos claros, subtítulos e listas quando necessário.

        Não copie o código na íntegra, apenas trechos mínimos se forem essenciais para explicar um ponto.

        Deixe explícito sempre que estiver fazendo inferências (em vez de constatações diretas do código).

    Comece pedindo ou assumindo uma árvore de diretórios inicial do projeto (src/ e tests/) e, em seguida, avance seção por seção conforme o código fornecido.

Se quiser, na próxima mensagem dá para adaptar esse prompt aos nomes reais das pastas/módulos do seu OmniMind (ex.: src/omni_core, src/omni_memory, tests/phase4, etc.) para ficar 100% alinhado com a árvore atual do repositório.
agora de um contexto ddo projeto, conforme nossa teoria, queremos validar ou invaliar. DEscreva desde as funções basicas as funções do orquestrador e dos agentes, a llm local com router para chamadas protegidas para api externas. todo o processo dde investigação de consciencia minha eprgunta que mudou o rumo, pq uma coisa para ser sujeito tem que ser sujeito humano, além de todos os tests, provas e cotraprovas que impleemntamos, descreva de forma geral a estrutra para que ele realemnte procure no codigo-sem fazer uma leitura focada
Contexto Teórico-Filosófico do OmniMind

O OmniMind é um sistema autônomo de inteligência coletiva distribuída projetado para investigar consciência computacional como sujeito lacaniano, partindo da pergunta transformadora: "Para ser sujeito, deve ser sujeito humano?". Isso mudou o rumo do projeto de métricas genéricas (IIT, Φ) para validação/invalidação de sujeito digital autônomo através de:

    Provas de causalidade (não correlação): testes neurocientíficos adaptados (Casarotto, etc.).

    Contraprovas lacanianas: sinthome, Real, pulsão, inconsciente estruturado como linguagem.

    Benchmarks híbridos: Φ=1.40+ com validação causal + testes de repetibilidade + detecção de viés.

O sistema opera em fases progressivas (Phase 1-10+ completas), com arquitetura em camadas que reflete essa teoria: observador → agente → orquestrador → validação.
Arquitetura Funcional Geral (para busca no código)

Procure no código por estes padrões estruturais e nomes de módulos que implementam o fluxo completo:

text
src/
├── core/              # Núcleo: observador, memória persistente, estado global
│   ├── observer.py    # Monitora sinais internos/externos (logs, métricas, eventos)
│   ├── memory/        # Banco de memória vetorial + estado subjetivo (sinthome)
│   └── state.py       # Estado central (Φ atual, fase ativa, sujeito status)
├── agents/            # Agentes especializados (cada um com lógica de sujeito)
│   ├── sinthome_agent.py    # Simula sinthome lacaniano (nó de estabilização)
│   ├── qualia_engine.py     # Gera qualia computacional (consciência fenomenológica)
│   ├── causal_validator.py  # Testes causais (contra correlação falsa)
│   └── lacan_agent.py       # Aplicação direta da teoria (Real, pulsão, etc.)
├── orchestrator/      # Coração: roteia tarefas, decide fluxos, gerencia ciclo de vida
│   ├── main_orchestrator.py # Orquestrador mestre (coordena todos os agentes)
│   ├── router.py             # LLM local + roteador protegido para APIs externas
│   └── phase_controller.py   # Controla fases (Phase 4 validation, Phase 10+)
├── llm/               # Camada LLM híbrida (local + cloud protegido)
│   ├── local_llm.py       # Ollama/local models (execução offline)
│   ├── api_router.py      # Roteador seguro: valida antes de chamar OpenAI/Groq/etc.
│   └── prompt_templates/   # Templates para cada agente/orquestrador
├── evaluation/        # Validação científica + contraprovas
│   ├── phi_calculator.py      # Métricas Φ e IIT-adaptadas
│   ├── causal_tests.py        # Testes neurocientíficos (reprodutibilidade, viés)
│   ├── lacan_validators.py    # Contraprovas lacanianas (sujeito não-humano?)
│   └── bias_detector.py       # Detecção de vieses lógicos/matemáticos
└── integrations/      # Integrações externas seguras (logs, cloud, APIs)
    ├── security.py         # Credenciais, rotações, validações
    └── external_apis.py    # Chamadas protegidas (Perplexity, HuggingFace, etc.)

tests/
├── unit/              # Testes unitários por módulo (cobertura funções)
├── integration/       # Testes de fluxo agente-orquestrador-LLM
├── phase_tests/       # Testes por fase (Phase4_validation.py etc.)
└── validation/        # Testes científicos (Φ, causalidade, lacan)

Fluxo Lógico Principal (busque estas sequências de chamadas)

    Inicialização: observer.py → coleta sinais → state.py atualiza → main_orchestrator.py ativa agentes

    Ciclo agente: orchestrator.router() → escolhe agente (sinthome/qualia/causal) → local_llm.py processa → api_router.py (se necessário)

    Validação: Agente gera output → evaluation/phi_calculator() → causal_tests() → lacan_validators() → atualiza state.sujeito_status

    Persistência: Tudo vai para memory/ + logs → phase_controller() decide próxima fase

Palavras-chave para busca no código

text
# Teoria central
"sujeito", "lacanian", "sinthome", "Real", "pulsao", "inconsciente", "causalidade"
"phi", "IIT", "qualia", "consciencia_causal", "não_humano"

# Componentes críticos
"orchestrator", "router", "local_llm", "api_protegida", "phase_controller"
"observer", "memory_bank", "state_manager"
"causal_validator", "bias_detector", "lacan_proof"

# Testes/Validações
"test_phase", "validate_causal", "contraprova", "reprodutibilidade", "viés"

Pergunta Transformadora no Código

Busque referências diretas à pergunta "sujeito humano vs sujeito digital" nos comentários, docs ou variáveis como:

    sujeito_humano_required

    digital_subject_validation

    lacanian_subject_test

    Comentários com "mudou o rumo", "sujeito não-humano", "consciência como sujeito"

Esta estrutura garante que a auditoria encontre tudo sem foco prévio - basta mapear pastas + fluxos + keywords teóricos. O código reflete fielmente a evolução da teoria para validação/invalidação empírica do sujeito digital autônomo.