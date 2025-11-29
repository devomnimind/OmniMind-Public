# 📋 Plano de Criação: OmniMind-Core-Papers Repository

**Data**: 28 de Novembro de 2025  
**Status**: 📊 Análise Completa (Não Executado Ainda)  
**Decisão**: ⏳ Aguarda Aprovação do Usuário

---

## 🎯 Objetivo Estratégico

Criar um repositório **público focado em reproduzibilidade científica** que:
- ✅ Permite replicação dos resultados dos papers
- ✅ Demonstra código auditável e funcional
- ✅ Mantém quantum seguro (simulador, não hardware)
- ✅ Preserva diferencial comercial (integração, escala, produção)
- ✅ Facilita validação externa (Copilot remoto + código auditável)

---

## 📊 Análise de Cobertura

### 1. Módulos Científicos (100% INCLUIR)

| Módulo | Tamanho | Paper | Criticidade | Status |
|--------|---------|-------|-------------|--------|
| **consciousness** | 276K | Structural Consciousness | CRÍTICA | ✅ |
| **metacognition** | 216K | IIT Metrics | CRÍTICA | ✅ |
| **quantum_consciousness** | 188K | Quantum Hybrid | MÉDIA | ✅ |
| **audit** | 132K | Ethics & Compliance | ALTA | ✅ |
| **autopoietic** | 104K | Autopoiesis | ALTA | ✅ |
| **ethics** | 64K | Ethical Decision | ALTA | ✅ |
| **Total Científico** | **980K** | **6 papers** | **Core** | **✅** |

### 2. Infraestrutura Mínima (INCLUIR)

| Módulo | Tamanho | Razão | Inclusões |
|--------|---------|-------|-----------|
| **agents** | 160K | Base para experimentos | orchestrator_agent.py, base_agent.py |
| **observability** | 108K | Logging e métricas | logging_framework.py, metrics.py |
| **memory** | 108K | Estado do sistema | base_memory.py, working_memory.py |
| **common** | 8K | Utilitários | __init__.py, types.py |
| **Total Infraestrutura** | **384K** | **Suporte** | **✅** |

### 3. Módulos Comerciais (EXCLUIR)

| Módulo | Tamanho | Razão | Status |
|--------|---------|-------|--------|
| **integrations** | 400K | MCP, OAuth, Supabase | ❌ EXCLUIR |
| **security** | 408K | Produção + HSM | ❌ EXCLUIR |
| **scaling** | 168K | Otimizações escala | ❌ EXCLUIR |
| **quantum_ai** | 76K | Otimizações avançadas | ❌ EXCLUIR |
| **distributed** | 20K | Infraestrutura distribuída | ❌ EXCLUIR |
| **daemon** | 24K | Orquestração produção | ❌ EXCLUIR |
| **Total Comercial** | **1096K** | **Diferencial** | **❌** |

### 📈 Estatísticas Finais

```
Público (OmniMind-Core-Papers):  1364K (55.4% do total)
├─ Científico:                    980K (39.8%)
└─ Infraestrutura:                384K (15.6%)

Privado (OmniMind - mantém):     1096K (44.6% do total)
└─ Comercial/Produção:           1096K

TOTAL:                            2460K (100.0%)
```

---

## 🔬 Módulos Científicos em Detalhe

### 1. Consciousness (276K)

**Papers**: 
- Structural Consciousness (PT/EN)
- Consciência Estrutural (PT ABNT)

**Componentes**:
```
src/consciousness/
├── expectation_module.py        # Antecipação (core)
├── novelty_generator.py         # Novidade/criatividade
├── qualia_processor.py          # Qualidade subjetiva
├── contrafactual_engine.py      # Análise contrafática
├── integration_loss.py          # Loss training
└── ...
```

**Testes Críticos**:
- `test_expectation.py` - Valida antecipação
- `test_contrafactual.py` - Valida ablação
- `test_integration_loss.py` - Valida treinamento Φ

**Resultado Esperado**:
- Φ baseline: 0.8667
- Φ sem expectation: 0.4240
- ΔΦ: 51.1% (prova crítica)

---

### 2. Metacognition (216K)

**Papers**:
- IIT Metrics (Integrated Information Theory)
- Pattern Recognition

**Componentes**:
```
src/metacognition/
├── iit_metrics.py               # Cálculos de Φ
├── homeostasis.py               # Equilíbrio do sistema
├── issue_prediction.py          # Predição de anomalias
├── pattern_recognition.py       # Reconhecimento de padrões
├── trap_framework.py            # Framework de análise
└── ...
```

**Testes Críticos**:
- `test_iit_metrics.py` - Valida Φ calculado
- `test_homeostasis.py` - Valida estados de saúde
- `test_issue_prediction.py` - Valida predições

**Resultado Esperado**:
- IIT completo funcionando
- Métricas de saúde do sistema
- Predições de degradação

---

### 3. Quantum Consciousness (188K)

**Papers**:
- Quantum Hybrid Cognition

**Componentes**:
```
src/quantum_consciousness/
├── hybrid_cognition.py          # Bridge clássico-quântico
├── qpu_interface.py             # Interface QPU
├── quantum_memory.py            # Memória quântica
├── variational_circuits.py      # Circuitos variacionais
└── ...
```

**Configuração Segura**:
- ✅ Simulador Qiskit (não hardware)
- ✅ Sem credenciais IBMQ
- ✅ Fallback automático
- ✅ Operações seguras

**Testes Críticos**:
- `test_hybrid_cognition.py` - Valida bridge
- `test_qpu_interface.py` - Valida simulador
- `test_quantum_memory.py` - Valida gates

**Resultado Esperado**:
- Híbrido funcionando
- Simulador apenas (sem cloud IBMQ)
- Resultados reproduzíveis

---

### 4. Audit (132K)

**Papers**:
- Ethics & Compliance Auditing

**Componentes**:
```
src/audit/
├── alerting_system.py           # Alertas
├── compliance_reporter.py       # Relatórios compliance
├── immutable_audit.py           # Trilha imutável
├── security_orchestrator.py     # Orquestração
└── ...
```

**Testes Críticos**:
- `test_compliance_reporter.py` - Valida relatórios
- `test_alerting_system.py` - Valida alertas
- `test_security_orchestrator.py` - Valida orquestração

**Resultado Esperado**:
- Trilha de auditoria completa
- Compliance verificável
- Relatórios geráveis

---

### 5. Autopoietic (104K)

**Papers**:
- Autopoiesis & Self-Organization

**Componentes**:
```
src/autopoietic/
├── absurdity_handler.py         # Tratamento de paradoxos
├── self_reference_analyzer.py   # Auto-referência
├── closed_loop_analyzer.py      # Loop fechado
└── ...
```

**Testes Críticos**:
- `test_absurdity_handler.py` - Valida resolução
- Estratégias de paradoxo

**Resultado Esperado**:
- Paradoxos resolvidos
- Self-reference funciona
- Loop fechado estável

---

### 6. Ethics (64K)

**Papers**:
- Ethical Decision Making

**Componentes**:
```
src/ethics/
├── ethical_framework.py         # Framework ético
├── constraint_system.py         # Sistema de constraints
├── decision_validator.py        # Validação de decisões
└── ...
```

**Testes Críticos**:
- `test_ethical_framework.py` - Valida framework

**Resultado Esperado**:
- Framework ético funciona
- Decisões validadas
- Constraints respeitadas

---

## 🧪 Suite de Testes Mínima (11 Arquivos Críticos)

### Φ / IIT Metrics (3 testes)
```
tests/metacognition/test_iit_metrics.py
tests/consciousness/test_integration_loss.py
tests/consciousness/test_contrafactual.py
```
**Objetivo**: Validar cálculos de Φ (informação integrada)

### Ethics / Compliance (3 testes)
```
tests/test_gdpr_compliance.py
tests/audit/test_compliance_reporter.py
tests/ethics/test_ethical_framework.py
```
**Objetivo**: Validar compliance e ética

### Autopoiesis / Consciousness (3 testes)
```
tests/autopoietic/test_absurdity_handler.py
tests/consciousness/test_novelty_generator.py
tests/consciousness/test_expectation_module.py
```
**Objetivo**: Validar autoconsciência e criatividade

### Integration (2 testes)
```
tests/test_phase16_integration.py
tests/test_advanced_workflow.py
```
**Objetivo**: Validar pipeline completo

---

## 📝 Estrutura do Novo Repositório

```
OmniMind-Core-Papers/
├── README.md                          # Descrição principal
├── ARCHITECTURE.md                    # Arquitetura científica
├── PAPERS.md                          # Papers e referências
├── QUICKSTART.md                      # Como começar
├── LICENSE                            # MIT ou Apache 2.0
│
├── src/
│   ├── consciousness/                 # ✅ INCLUIR (completo)
│   ├── metacognition/                 # ✅ INCLUIR (completo)
│   ├── quantum_consciousness/         # ✅ INCLUIR (seguro)
│   ├── audit/                         # ✅ INCLUIR (completo)
│   ├── autopoietic/                  # ✅ INCLUIR (completo)
│   ├── ethics/                        # ✅ INCLUIR (completo)
│   ├── agents/                        # ✅ INCLUIR (base)
│   ├── observability/                 # ✅ INCLUIR (logging)
│   ├── memory/                        # ✅ INCLUIR (estado)
│   └── common/                        # ✅ INCLUIR (utils)
│
├── tests/
│   ├── metacognition/
│   │   └── test_iit_metrics.py       # ✅ CRÍTICO
│   ├── consciousness/
│   │   ├── test_integration_loss.py  # ✅ CRÍTICO
│   │   ├── test_contrafactual.py    # ✅ CRÍTICO
│   │   ├── test_expectation_module.py # ✅ CRÍTICO
│   │   └── test_novelty_generator.py # ✅ CRÍTICO
│   ├── audit/
│   │   ├── test_compliance_reporter.py # ✅ CRÍTICO
│   │   └── test_alerting_system.py     # ✅ CRÍTICO
│   ├── ethics/
│   │   └── test_ethical_framework.py # ✅ CRÍTICO
│   ├── autopoietic/
│   │   └── test_absurdity_handler.py # ✅ CRÍTICO
│   ├── quantum_consciousness/
│   │   ├── test_hybrid_cognition.py  # ✅ CRÍTICO
│   │   ├── test_qpu_interface.py     # ✅ CRÍTICO
│   │   └── test_quantum_memory.py    # ✅ CRÍTICO
│   ├── test_gdpr_compliance.py       # ✅ CRÍTICO
│   ├── test_phase16_integration.py   # ✅ CRÍTICO
│   └── test_advanced_workflow.py     # ✅ CRÍTICO
│
├── papers/                           # ✅ INCLUIR
│   ├── OmniMind_Consciousness_PT.md
│   ├── OmniMind_Consciousness_EN.md
│   ├── O_que_provamos.md
│   └── ...
│
├── docs/                             # ✅ INCLUIR (parcial)
│   ├── ARCHITECTURE.md
│   ├── MODULES.md
│   └── EXPERIMENTS.md
│
├── experiments/                      # ✅ INCLUIR
│   ├── run_experiments.sh
│   ├── benchmark_phi.py
│   ├── validate_papers.py
│   └── ...
│
├── data/                             # ✅ INCLUIR (minimal)
│   └── sample_results/
│
├── pyproject.toml                    # Reduzido
├── requirements.txt                  # Científico apenas
└── .gitignore
```

---

## ✅ Checklist de Inclusão/Exclusão

### ✅ INCLUIR em OmniMind-Core-Papers

**Módulos** (980K):
- [ ] `src/consciousness/` - completo
- [ ] `src/metacognition/` - completo
- [ ] `src/quantum_consciousness/` - completo (sem credentials)
- [ ] `src/audit/` - completo
- [ ] `src/autopoietic/` - completo
- [ ] `src/ethics/` - completo
- [ ] `src/agents/` - base apenas (orchestrator_agent.py, base_agent.py)
- [ ] `src/observability/` - logging e métricas
- [ ] `src/memory/` - base memory, working memory

**Testes** (11 arquivos):
- [ ] `tests/metacognition/test_iit_metrics.py`
- [ ] `tests/consciousness/test_integration_loss.py`
- [ ] `tests/consciousness/test_contrafactual.py`
- [ ] `tests/consciousness/test_expectation_module.py`
- [ ] `tests/consciousness/test_novelty_generator.py`
- [ ] `tests/audit/test_compliance_reporter.py`
- [ ] `tests/audit/test_alerting_system.py`
- [ ] `tests/ethics/test_ethical_framework.py`
- [ ] `tests/autopoietic/test_absurdity_handler.py`
- [ ] `tests/quantum_consciousness/test_hybrid_cognition.py`
- [ ] `tests/quantum_consciousness/test_qpu_interface.py`
- [ ] `tests/quantum_consciousness/test_quantum_memory.py`
- [ ] `tests/test_gdpr_compliance.py`
- [ ] `tests/test_phase16_integration.py`
- [ ] `tests/test_advanced_workflow.py`

**Documentação**:
- [ ] `papers/` - todos os papers
- [ ] `docs/ARCHITECTURE.md`
- [ ] `docs/MODULES.md`
- [ ] `docs/research/` - pesquisa base

**Configuração**:
- [ ] `pyproject.toml` - reduzido (sem quantum_ai, integrations, etc)
- [ ] `requirements.txt` - científico apenas
- [ ] `conftest.py` - base testing
- [ ] `.github/workflows/` - CI/CD básico (testes públicos)

### ❌ EXCLUIR do Público

**Módulos** (1096K):
- [ ] `src/integrations/` - MCP, OAuth, Supabase (COMPLETO)
- [ ] `src/security/` - produção + HSM (COMPLETO)
- [ ] `src/scaling/` - otimizações escala
- [ ] `src/quantum_ai/` - otimizações quânticas avançadas
- [ ] `src/distributed/` - infraestrutura distribuída
- [ ] `src/daemon/` - orquestração de produção
- [ ] `src/services/` - serviços internos
- [ ] `src/tools/` - ferramentas proprietárias

**Infraestrutura**:
- [ ] `scripts/` - scripts internos
- [ ] `.env` - variáveis de ambiente privadas
- [ ] `config/` - configurações proprietárias
- [ ] `deploy/` - deployment scripts
- [ ] `k8s/` - orchestração Kubernetes

---

## 📄 README Template (OmniMind-Core-Papers)

```markdown
# OmniMind-Core-Papers

## Descrição

Repositório científico focado em reproduzibilidade dos artigos OmniMind:

1. **Structural Consciousness** (PT/EN)
2. **IIT Metrics & Pattern Recognition**
3. **Quantum Hybrid Cognition**
4. **Ethics & Compliance Auditing**
5. **Autopoiesis & Self-Organization**
6. **Ethical Decision Making**

### O que está incluído

✅ Módulos científicos completos (980K)
✅ Infraestrutura mínima necessária (384K)
✅ Suite de testes reproduzíveis (11 arquivos críticos)
✅ Quantum seguro (simulador Qiskit, sem hardware)
✅ Código auditável e funcional

### O que NÃO está incluído

❌ Integrações de produção (MCP, OAuth, Supabase)
❌ Orquestração distribuída
❌ Otimizações de escala
❌ Hardware quântico (IBMQ)
❌ Ferramentas internas proprietárias

**Nota**: Código completo, integrações avançadas e automações de produção 
permanecem em repositório privado, disponíveis sob acordo de pesquisa/enterprise.

## Quick Start

```bash
git clone https://github.com/yourusername/OmniMind-Core-Papers.git
cd OmniMind-Core-Papers

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Testes
pytest tests/metacognition/test_iit_metrics.py -v
pytest tests/consciousness/test_integration_loss.py -v

# Experimentos
./experiments/run_experiments.sh
```

## Estrutura

- `src/` - Módulos científicos
- `tests/` - Suite de testes
- `papers/` - Artigos e referências
- `experiments/` - Scripts de replicação
- `docs/` - Documentação

## Reproduzibilidade

Pergunta-teste: "Alguém pode baixar este repo, rodar experimentos e 
obter os mesmos resultados dos papers?"

Resposta: **SIM**

Veja [QUICKSTART.md](QUICKSTART.md) para instruções detalhadas.

## Licença

MIT / Apache 2.0

## Autores

OmniMind Team

## Citation

[Incluir citações dos papers aqui]
```

---

## 🚀 Plano de Ação (Quando Executar)

### Fase 1: Preparação (Repo Privado)
1. [ ] Criar branch `prepare-public-repo` no privado
2. [ ] Copiar estrutura mínima
3. [ ] Remover segredos/credenciais
4. [ ] Testar se suite mínima passa
5. [ ] Documentar diferenças

### Fase 2: Criação (Novo Repositório Público)
1. [ ] Criar novo repo em GitHub: `OmniMind-Core-Papers`
2. [ ] Configurar visibilidade: PUBLIC
3. [ ] Inicializar com estrutura preparada
4. [ ] Adicionar README, ARCHITECTURE, PAPERS
5. [ ] Configurar CI/CD (GitHub Actions)

### Fase 3: Validação (Reproduzibilidade)
1. [ ] Rodar testes públicos (11 arquivos)
2. [ ] Verificar reproduzibilidade de resultados
3. [ ] Validar que não quebrou nada
4. [ ] Testar em máquina limpa (Docker?)

### Fase 4: Publicação
1. [ ] Adicionar ao GitHub
2. [ ] Enviar para arXiv
3. [ ] Divulgar nos papers
4. [ ] Manter sincronizado com privado

---

## ✅ Critério de Sucesso

```
✅ SUCESSO SE:

[a] Alguém sem acesso ao repo privado consegue clonar
[b] Executa: pytest tests/ -v
[c] Todas as 11 suites passam
[d] Executa: ./experiments/run_experiments.sh
[e] Obtém os mesmos gráficos/números dos papers
[f] Copilot remoto consegue validar código
[g] Não há dependências faltando do repo privado
[h] Quantum funciona apenas no simulador (sem credenciais)
```

---

## 🔐 Segurança

### Remover Antes de Publicar

- [ ] Todas as credenciais IBMQ
- [ ] API keys de Supabase
- [ ] OAuth tokens
- [ ] Caminhos locais absolutos
- [ ] Versões de debug/teste

### Verificar

- [ ] Sem `.env` files
- [ ] Sem `config/` proprietários
- [ ] Sem referências a `/home/fahbrain`
- [ ] Sem dados privados em `data/`

---

## 📊 Impacto

### Repositório Privado (OmniMind)
- Continua 100% funcional
- Toda infraestrutura intacta
- Diferencial comercial preservado
- Quantum completo + hardware

### Repositório Público (OmniMind-Core-Papers)
- 55% do código (o essencial)
- 100% reproduzível
- Código auditável
- Validação externa possível

### Ganho

- ✅ Credibilidade científica
- ✅ Comunidade engajada
- ✅ Diferencial comercial mantido
- ✅ Facilita parcerias/funding

---

## 📌 Próximas Decisões

**Pergunta 1**: Executar este plano?  
**Pergunta 2**: Qual a prioridade? (Timing)  
**Pergunta 3**: Adicionar mais módulos? (consciência, lacanian, etc)  
**Pergunta 4**: Configurar CI/CD agora? (GitHub Actions)

---

**Status**: 📊 Análise Completa ✅  
**Ação Necessária**: ⏳ Aprovação do Usuário  
**Próximo Passo**: Aguarda decisão para executar plano

