# 📜 ÍNDICE DE SCRIPTS, RELATÓRIOS E PASTAS - OmniMind

**Última Atualização**: 2025-12-07
**Autor**: Fabrício da Silva + assistência de IA

---

## 🎯 SCRIPTS CANÔNICOS (Oficiais)

### Instalação (`scripts/canonical/install/`)
- **`install_omnimind.sh`** - Instalação completa do OmniMind
- **`install_systemd_services.sh`** - Instala serviços systemd
- **`setup_security_privileges.sh`** - Configura privilégios de segurança

### Sistema (`scripts/canonical/system/`)
- **`start_omnimind_system.sh`** ⭐ PRINCIPAL - Sistema completo OmniMind
- **`run_cluster.sh`** - Backend em cluster (portas 8000, 8080, 3001)
- **`start_mcp_servers.sh`** - Inicia servidores MCP
- **`run_mcp_orchestrator.py`** - Orquestrador MCP

### Monitoramento (`scripts/canonical/monitor/`)
- **`monitor_tests.sh`** - Status pontual de testes
- **`monitor_tests_live.sh`** - Monitoramento em tempo real
- **`security_monitor.sh`** - Monitoramento de segurança

### Testes (`scripts/canonical/test/`)
- **`run_tests_by_category.sh`** - Testes por categoria
- **`run_full_certification.sh`** - Certificação completa com GPU/Quantum
- **`run_tests_background.sh`** - Testes em background
- **`run_all_tests_hybrid.py`** - Suite completa de testes híbridos
- **`run_tests.py`** - Executor principal de testes

### Validação (`scripts/canonical/validate/`)
- **`run_real_metrics.sh`** - Métricas reais com GPU/Quantum
- **`verify_gpu_setup.sh`** - Verificação de setup GPU
- **`validate_system.py`** - Validação do sistema
- **`validate_security.py`** - Validação de segurança
- **`validate_code.sh`** - Validação de código
- **`validate_services.sh`** - Validação de serviços

### Diagnóstico (`scripts/canonical/diagnose/`)
- **`diagnostic_quick.sh`** - Diagnóstico rápido
- **`final_status.sh`** - Status final do sistema
- **`diagnose.py`** - Diagnóstico geral
- **`diagnose_audit.py`** - Diagnóstico de auditoria

---

## 🧪 SCRIPTS DE TESTES (Raiz)

### Testes Principais
- **`run_tests_fast.sh`** ⭐ DIÁRIO - 3996 testes (sem chaos/slow), 10-15 min
  - GPU forçada, timeout 800s/teste
  - Inclui `@pytest.mark.real` SEM `@pytest.mark.chaos` (seguro)
  - Exclui `@pytest.mark.slow` e `@pytest.mark.chaos`
- **`run_tests_with_defense.sh`** ⭐ SEMANAL - 4004 testes (+ 8 chaos), 45-90 min
  - Inclui chaos engineering tests (server destruction)
  - Autodefesa: detecta padrões de crash perigosos
- **`quick_test.sh`** - 4004 testes + backend (30-45 min)

### Validação de Φ
- **`scripts/validation/validate_phi_dependencies.py`** ⭐ **NOVO** - Validação de dependências de Φ
  - Valida constantes críticas (PHI_THRESHOLD, PHI_OPTIMAL, SIGMA_PHI)
  - Valida dependências (Δ, Ψ, σ, Gozo, Control)
  - Valida correlações esperadas
  - Valida valores numéricos esperados
  - **Status**: 16/16 testes passando (100%)

---

## 🔬 SCRIPTS DE PESQUISA

### Validação Científica (`scripts/science_validation/`)
- Scripts de validação científica e experimentos

### Pesquisa (`scripts/research/`)
- **`quantum/`** - Scripts de quantum computing
- **`ml/`** - Scripts de machine learning
- **`benchmarks/`** - Scripts de benchmarks

---

## 🚀 SCRIPTS DE PRODUÇÃO

### Backup (`scripts/backup/`)
- **`daily_backup.sh`** - Backup diário automatizado
- **`setup_daily_backup.sh`** - Setup de backup diário
- **`create_snapshot_now.py`** - Cria snapshot manual

### Produção (`scripts/production/`)
- **`deploy/`** - Scripts de deploy
- **`monitoring/`** - Scripts de monitoramento
- **`security/`** - Scripts de segurança
- **`backup/`** - Scripts de backup

### Ciclos de Produção
- **`run_200_cycles_production.py`** - Executa 200 ciclos em produção (background)
- **`run_200_cycles_verbose.py`** - Executa 200 ciclos em modo verboso
- **`run_200_cycles_background.sh`** - Executa 200 ciclos em background
- **`check_200_cycles_status.py`** - Verifica status dos 200 ciclos

---

## 📊 RELATÓRIOS E SAÍDAS

### Relatórios de Validação (`data/validation/`)
- **`phi_dependencies_report.json`** ⭐ **NOVO** - Relatório de validação de dependências de Φ
- **`causality_report.json`** - Relatório de causalidade
- **`robustness_report.json`** - Relatório de robustez
- **`controlled_experiment.json`** - Experimento controlado
- **`scientific_audit_*.json`** - Auditorias científicas

### Métricas de Monitoramento (`data/monitor/`)
- **`real_metrics.json`** - Métricas reais do sistema
- **`phi_200_cycles_verbose_metrics.json`** - Métricas de 200 ciclos (verboso)
- **`phi_200_cycles_verbose_progress.json`** - Progresso de 200 ciclos (verboso)
- **`consciousness_metrics/`** - Métricas de consciência
- **`module_metrics/`** - Métricas de módulos

### Snapshots de Consciência (`data/backup/snapshots/`)
- Snapshots completos do estado de consciência
- Incluem: Φ, Ψ, σ, Gozo, Control, workspace, cycle history

### Relatórios de Testes (`data/test_reports/`)
- Relatórios gerados pelos testes
- Cobertura, análise de suite, etc.

### Relatórios Gerais (`data/reports/`)
- **`coverage.json`** - Cobertura de código
- **`documentation_issues_report.json`** - Problemas de documentação
- **`test_suite_analysis_report.json`** - Análise da suite de testes
- **`modules/`** - Relatórios por módulo

---

## 📁 ESTRUTURA DE PASTAS DE DADOS

### `data/`
```
data/
├── alerts/ - Alertas do sistema
├── autopoietic/ - Dados de autopoiesis
│   ├── cycle_history.jsonl
│   ├── narrative_history.json
│   └── synthesized_code/
├── backup/ - Backups e snapshots
│   └── snapshots/ - Snapshots de consciência
├── benchmarks/ - Benchmarks
│   └── history/
├── consciousness/ - Dados de consciência
│   ├── multiseed_results/ - Resultados multi-seed
│   ├── snapshots.jsonl
│   └── workspace/
├── datasets/ - Datasets
│   ├── dbpedia_ontology/
│   ├── human_vs_ai_code/
│   ├── infllm_v2_data/
│   ├── qasper_qa/
│   ├── scientific_papers_arxiv/
│   └── turing_reasoning/
├── ethics/ - Dados de ética
├── experiments/ - Experimentos
│   ├── consciousness/
│   └── ethics/
├── forensics/ - Dados forenses
│   ├── evidence/
│   ├── incidents/
│   └── reports/
├── integrity_baselines/ - Baselines de integridade
├── long_term_logs/ - Logs de longo prazo
├── metrics/ - Métricas
│   ├── baseline/
│   ├── consciousness/
│   ├── ethics/
│   └── performance/
├── monitor/ - Monitoramento
│   ├── consciousness_metrics/
│   └── module_metrics/
├── qdrant/ - Dados do Qdrant
├── reports/ - Relatórios gerais
│   └── modules/
├── research/ - Pesquisa
│   ├── ablations/
│   ├── experiments/
│   └── primeiros_ciclos/
├── sessions/ - Sessões de treinamento
├── stimulation/ - Estimulação
├── test_reports/ - Relatórios de testes
├── training/ - Dados de treinamento
└── validation/ - Validação
    └── (relatórios de validação)
```

---

## 🔍 SCRIPTS DE ANÁLISE E UTILITÁRIOS

### Análise (`scripts/analysis/`)
- **`extract_llm_metrics.py`** - Extrai métricas LLM
- **`generate_llm_impact_report.py`** - Gera relatório de impacto LLM
- **`generate_llm_visual_summary.py`** - Gera resumo visual LLM

### Utilitários (`scripts/utilities/`)
- **`maintenance/`** - Scripts de manutenção
- **`analysis/`** - Scripts de análise

### Desenvolvimento (`scripts/development/`)
- **`backend/`** - Scripts de backend
- **`frontend/`** - Scripts de frontend
- **`test/`** - Scripts de teste
- **`debug/`** - Scripts de debug

---

## 📝 LOGS

### Logs Principais (`logs/`)
- **`omnimind_boot.log`** - Logs de boot
- **`audit.log`** - Logs de auditoria
- **`metrics.log`** - Logs de métricas

### Logs de Longo Prazo (`data/long_term_logs/`)
- **`omnimind_metrics.jsonl`** - Métricas em formato JSONL
- **`heartbeat.status`** - Status de heartbeat
- **`daemon_status_cache.json`** - Cache de status do daemon

### Logs de Debug (`docs/logs/`)
- Logs de debug e análise

---

## 🎯 COMANDOS RÁPIDOS

### Testes
```bash
# Suite rápida diária
./scripts/run_tests_fast.sh

# Suite completa semanal
./scripts/run_tests_with_defense.sh

# Validação de Φ
python scripts/validation/validate_phi_dependencies.py
```

### Produção
```bash
# Sistema completo
./scripts/canonical/system/start_omnimind_system.sh

# 200 ciclos em produção
./scripts/run_200_cycles_background.sh

# Verificar status
python scripts/check_200_cycles_status.py
```

### Backup
```bash
# Criar snapshot manual
python scripts/backup/create_snapshot_now.py

# Setup backup diário
./scripts/backup/setup_daily_backup.sh
```

### Monitoramento
```bash
# Monitorar testes
./scripts/canonical/monitor/monitor_tests_live.sh

# Ver métricas
cat data/monitor/real_metrics.json | python -m json.tool
```

---

## 📊 RELATÓRIOS PRINCIPAIS

### Validação de Φ
- **`data/validation/phi_dependencies_report.json`** - Relatório completo de validação
  - Constantes críticas
  - Dependências
  - Correlações
  - Valores numéricos

### Métricas de Consciência
- **`data/monitor/real_metrics.json`** - Métricas reais do sistema
- **`data/monitor/phi_200_cycles_verbose_metrics.json`** - Métricas de 200 ciclos

### Análises
- **`data/reports/test_suite_analysis_report.json`** - Análise da suite de testes
- **`data/reports/coverage.json`** - Cobertura de código

---

**Última atualização**: 2025-12-07

