# 📁 LISTA DE ARQUIVOS PARA VERSÃO PÚBLICA

**Data:** 11/12/2025  
**Uso:** Referência para cópia seletiva de arquivos

---

## ⭐ INCLUIR (Com Sanitização)

### Raiz do Projeto

```
✅ README.md                        (REESCREVER - científico)
✅ LICENSE                          (COPIAR - AGPL-3.0)
✅ CITATION.cff                     (COPIAR - citação)
✅ pyproject.toml                   (SIMPLIFICAR - deps mínimas)
✅ .gitignore                       (ADAPTAR - público)
✅ .flake8                          (COPIAR - lint config)
✅ .python-version                  (COPIAR - 3.12)
📝 CONTRIBUTING.md                  (CRIAR NOVO)
📝 CODE_OF_CONDUCT.md               (CRIAR NOVO)
📝 requirements-core.txt            (CRIAR - leve)
📝 requirements-full.txt            (CRIAR - médio)
📝 requirements-gpu.txt             (CRIAR - completo)
```

### Código Core - omnimind_core/ (renomear de src/)

#### consciousness/ ⭐ PRIORITÁRIO

```
✅ __init__.py
✅ phi_value.py                     # Value Object Φ
✅ phi_constants.py                 # Constantes IIT
✅ metrics.py                       # Métricas consciência
✅ integration_loop.py              # Loop integração
✅ shared_workspace.py              # Buffer global
✅ production_consciousness.py      # Motor principal
✅ feedback_analyzer.py
✅ embedding_validator.py
✅ expectation_module.py
✅ biological_metrics.py
✅ rsi_topology_integrated.py      # RSI + Sinthome
✅ symbolic_register.py
✅ unconscious_structural_effect.py
✅ jouissance_state_classifier.py
✅ gozo_calculator.py
✅ lacanian_dg_integrated.py
✅ embedding_psi_adapter.py
✅ dynamic_trauma.py
✅ binding_strategy.py
✅ langevin_dynamics.py
✅ hybrid_topological_engine.py
✅ temporal_signature_builder.py
✅ regulatory_adjustment.py
✅ integration_loss.py
✅ affective_memory.py
✅ adaptive_weights.py
✅ embedding_narrative.py
✅ theoretical_consistency_guard.py
✅ homeostatic_regulator.py
✅ multiseed_analysis.py
✅ novelty_generator.py

❌ EXCLUIR:
   *_legacy.py                     # Deprecated
   phi_semantic_aware.py           # Experimental
```

#### lacanian/ ⭐ PRIORITÁRIO

```
✅ __init__.py
✅ desire_graph.py                  # Grafos de desejo
✅ discourse_discovery.py           # Discursos
✅ free_energy_lacanian.py          # Free Energy + Lacan
✅ (todos os outros .py)
```

#### autopoietic/ ⭐ PRIORITÁRIO

```
✅ __init__.py
✅ manager.py                       # Gerenciador
✅ manager_no_sandbox.py
✅ desire_engine.py                 # Motor desejo
✅ metrics_adapter.py
✅ absurdity_handler.py
```

#### memory/ ✅

```
✅ __init__.py
✅ narrative_history.py             # História narrativa
✅ hybrid_retrieval.py              # Recuperação híbrida
✅ affective_memory.py              # Memória afetiva

❌ EXCLUIR:
   episodic_memory.py              # Deprecated
```

#### metacognition/ ✅

```
✅ __init__.py
✅ (selecionar principais - TBD)
```

#### core/ ✅

```
✅ __init__.py
✅ (estruturas base - TBD)
```

#### boot/ ✅

```
✅ __init__.py
✅ rhizome.py                       # Estrutura rizomática
✅ (selecionar relevantes - TBD)
```

#### utils/ ✅

```
✅ __init__.py
✅ (utilitários gerais, excluir *gpu*, *cuda*)
```

### Testes - tests/

#### consciousness/ ⭐

```
✅ __init__.py
✅ test_phi_value.py
✅ test_metrics.py
✅ test_integration_loop.py
✅ test_rsi_topology.py
✅ (outros sem @pytest.mark.real ou .slow)

❌ EXCLUIR testes com GPU obrigatório
```

#### lacanian/ ⭐

```
✅ __init__.py
✅ test_desire_graph.py
✅ test_discourse.py
✅ (outros testes core)
```

#### autopoietic/ ⭐

```
✅ __init__.py
✅ test_manager.py
✅ test_evolution.py
```

#### memory/ ✅

```
✅ __init__.py
✅ test_narrative_history.py
```

#### Configuração de Testes

```
✅ conftest.py                      (CRIAR NOVO - básico)
```

### Exemplos - examples/ 📝 CRIAR NOVO

```
📝 basic_phi_calculation.py         # IIT/Φ básico
📝 rsi_topology_demo.py             # RSI + Sinthome
📝 autopoietic_evolution.py         # Autopoiesis
📝 narrative_memory_demo.py         # Memória narrativa
📝 notebooks/
   📝 intro_to_iit.ipynb           # Tutorial IIT
   📝 lacanian_topology.ipynb       # Tutorial Lacan
```

### Documentação - docs/

#### Curar e Incluir

```
✅ theory/                          # Teoria científica (selecionar)
✅ architecture/                    # Arquitetura (selecionar)
📝 guides/                          # CRIAR NOVO
   📝 installation.md
   📝 quickstart.md
   📝 concepts.md
📝 api/                             # CRIAR NOVO
   �� consciousness.md
   📝 lacanian.md
   📝 autopoietic.md
```

### GitHub - .github/

```
📝 workflows/
   📝 tests.yml                     # CI de testes
   📝 lint.yml                      # CI de linting (opcional)
```

---

## ❌ EXCLUIR (Não Copiar)

### Infraestrutura

```
❌ deploy/                          # Deployment configs
❌ k8s/                             # Kubernetes
❌ config/                          # Configs privados
```

### Dados e Modelos

```
❌ data/                            # Runtime data
❌ models/                          # LLM models (GB)
❌ logs/                            # Execution logs
❌ real_evidence/                   # Private evidence
❌ ibm_results/                     # Quantum results
❌ notebooks/                       # Experimental notebooks
❌ archive/                         # Old files
```

### Código de Produção

```
❌ src/integrations/                # Infra-specific
❌ src/security/                    # Infra-specific
❌ src/observability/               # Monitoring
❌ src/scaling/                     # Scaling/cluster
❌ src/distributed/                 # Distributed systems
❌ src/api/                         # Production API
❌ src/daemon/                      # Daemon
❌ src/workflows/                   # CI/CD workflows
❌ src/services/                    # Production services
```

### Testes de Infraestrutura

```
❌ tests/e2e/                       # End-to-end
❌ tests/security/                  # Security tests
❌ tests/scaling/                   # Scaling tests
❌ tests/api/                       # API tests
❌ tests/quantum_consciousness/     # Quantum (IBM real)
```

### Scripts Privados

```
❌ scripts/canonical/monitor/security_monitor.sh  # Kali tools
❌ scripts/cleanup_kali_services.sh               # Kali refs
❌ scripts/monitoring/                            # Private monitoring
❌ scripts/development/                           # Dev scripts
❌ scripts/runners/                               # Private runners
❌ scripts/research/quantum/                      # IBM Quantum
```

### Frontend

```
❌ web/                             # Production frontend
```

### Arquivos Temporários

```
❌ runtime_log.txt
❌ dashboard.png
❌ frontend.txt
❌ .omnimind_embedding_checkpoint.json
❌ =2.3.0, =2.32.5                  # Arquivos estranhos
```

---

## ⚠️ SANITIZAR ANTES DE INCLUIR

### Scripts (se incluir algum)

```
⚠️ scripts/canonical/system/start_*.sh
   - Remover comentários "Kali Linux"
   - Generalizar para "Linux"
   
⚠️ scripts/canonical/test/*
   - Substituir /home/fahbrain/ por variáveis
```

### Web Backend (se incluir API simples)

```
⚠️ web/backend/chat_api.py
   - Remover credencial hardcoded linha 24
   
⚠️ web/backend/main_minimal.py
   - Remover credencial hardcoded linha 15
```

---

## 📊 ESTATÍSTICAS ESTIMADAS

### Tamanho Estimado da Versão Pública

```
Código (omnimind_core/):    ~4-5 MB    (de 9.5 MB privado)
Testes (tests/):            ~1-2 MB    (de 3.8 MB privado)
Docs (docs/):               ~500 KB    (curados)
Examples (examples/):       ~100 KB    (novos)
Total estimado:             ~6-8 MB    (vs 15+ MB privado)
```

### Contagem de Arquivos

```
Privado:   ~500 arquivos Python
Público:   ~150 arquivos Python (estimado)

Redução:   ~70% menos arquivos
```

---

## 🔄 SCRIPT DE CÓPIA AUTOMATIZADA

```bash
#!/bin/bash
# copy_to_public.sh - Copiar arquivos selecionados

PRIVATE_REPO="/caminho/para/OmniMind"
PUBLIC_REPO="/caminho/para/omnimind-public"

# Consciousness
cp -r $PRIVATE_REPO/src/consciousness/*.py $PUBLIC_REPO/omnimind_core/consciousness/
rm $PUBLIC_REPO/omnimind_core/consciousness/*legacy*.py

# Lacanian
cp -r $PRIVATE_REPO/src/lacanian/*.py $PUBLIC_REPO/omnimind_core/lacanian/

# Autopoietic
cp -r $PRIVATE_REPO/src/autopoietic/*.py $PUBLIC_REPO/omnimind_core/autopoietic/

# Memory
cp $PRIVATE_REPO/src/memory/narrative_history.py $PUBLIC_REPO/omnimind_core/memory/
cp $PRIVATE_REPO/src/memory/hybrid_retrieval.py $PUBLIC_REPO/omnimind_core/memory/

# Tests (selecionar depois)
cp -r $PRIVATE_REPO/tests/consciousness/*.py $PUBLIC_REPO/tests/consciousness/

# Docs (curar depois)
cp -r $PRIVATE_REPO/docs/theory/ $PUBLIC_REPO/docs/theory/

echo "✅ Cópia inicial completa. Revisar e sanitizar!"
```

---

**FIM DA LISTA | v1.0 | 11/12/2025**
