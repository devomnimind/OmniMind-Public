## 🧠 OMNIMIND TEST SUITE - SETUP RÁPIDO

### 🚀 SCRIPTS DE TESTE ATIVOS (2025-12-04)

Há 3 scripts principais para diferentes cenários:

| Script | Propósito | Tempo | GPU | Servidor |
|--------|-----------|-------|-----|----------|
| `run_tests_fast.sh` | ⚡ Testes rápidos (sem slow/real/chaos) | **60-90 min** | ✅ Forçada | ❌ Não |
| `run_tests_with_defense.sh` | 🛡️ Suite completa com autodefesa | **120-240 min** | ✅ Forçada | ❌ Não |
| `quick_test.sh` | 🧪 Testes + servidor backend | **30-45 min** | ✅ Forçada | ✅ Sim |

> ⏱️ **Tempos variam com**: Servidor Qdrant, processos do sistema, carga de GPU/CPU

### ✅ Opção 1: Testes Rápidos (RECOMENDADO PARA DEV)

```bash
./scripts/run_tests_fast.sh
```

**Características**:
- ⚡ Pula testes lentos (`@pytest.mark.slow`), integrações reais (`@pytest.mark.real`), e chaos (`@pytest.mark.chaos`)
- 🚀 GPU FORÇADA com `CUDA_VISIBLE_DEVICES=0` + `OMNIMIND_FORCE_GPU=true`
- ⏱️ **60-90 minutos** (depende servidor Qdrant, carga do sistema)
- 📁 Logs em `data/test_reports/`

### 🛡️ Opção 2: Suite Completa com Autodefesa (SEMANAL)

```bash
./scripts/run_tests_with_defense.sh
```

**Características**:
- 📊 Suite COMPLETA (~3952 testes, **SEM filtros**)
- 🔴 **INCLUI testes chaos**: Testes que destroem servidor propositalmente
- 🛡️ Autodefesa: detecta testes perigosos e padrões de crash
- 🚀 GPU FORÇADA
- ⏱️ **120-240 minutos** (depende servidor Qdrant, carga do sistema, crashes)
- 🔍 Relatório de testes perigosos ao fim
- ⚠️ **Use apenas em ambiente sandbox ou fora do horário de trabalho**

### 🧪 Opção 3: Testes + Servidor Backend (FULL INTEGRATION)

Pré-requisito UMA VEZ:
```bash
bash scripts/configure_sudo_omnimind.sh
```

Depois:
```bash
bash scripts/quick_test.sh
```

**Características**:
- 🖥️ Inicia servidor backend em localhost:8000
- 📊 Suite completa com autodefesa
- 🚀 GPU FORÇADA
- ⏱️ ~30-45 minutos
- 💾 Exige sudo configurado

### 📊 Informações da Suite

- **Total de testes**: ~3952 (completa) ou ~400 (fast)
- **Modo**: Real (venv + GPUforced, não Docker isolado)
- **Autodefesa**: ✅ ATIVADA (em run_tests_with_defense.sh e quick_test.sh)
  - Detecta testes que causam crashes
  - Marca padrões agressivos após 3 crashes em 5min
  - Gera relatório ao fim da execução

### 🛡️ O que é Autodefesa?

Sistema que aprende padrões de falha:

```
Teste derruba servidor 3x em 5min?
  ↓
Sistema DETECTA padrão
  ↓
Sistema IDENTIFICA subsistema atacado (Qdrant, GPU, etc)
  ↓
Sistema MARCA teste como "dangerous"
  ↓
Sistema RELATA ao fim da suite
```

Relatório ao fim da execução:

```
🧠 RELATÓRIO DE AUTODEFESA (OMNIMIND TEST DEFENSE)
Testes perigosos detectados: N

  ⚠️  test_different_coping_strategies_applied
     └─ Subsistema: absurdity_handler
     └─ Crashes: 3
     └─ Padrão: rapid_fire
```

### 📁 Arquivos de Log

Cada execução salva:

- `output_YYYYMMDD_HHMMSS.log` - Stdout/stderr completo
- `pytest_YYYYMMDD_HHMMSS.log` - Logs internos do pytest
- `junit_YYYYMMDD_HHMMSS.xml` - Relatório XML (para CI/CD)
- `report_YYYYMMDD_HHMMSS.html` - Dashboard HTML visual

### 🔧 Troubleshooting

**Problema**: "Connection refused" na porta 8000

```bash
# Verificar se servidor está rodando
ps aux | grep uvicorn | grep -v grep

# Limpar processos antigos
pkill -f "uvicorn web.backend.main:app"

# Verificar logs do backend
tail -f logs/backend_*.log
```

**Problema**: Sudo pede senha

```bash
# Reconfigurar sudoers
bash scripts/configure_sudo_omnimind.sh

# Testar se funciona
sudo -n bash scripts/start_omnimind_system_sudo.sh
```

**Problema**: Testes com Timeout

Timeouts são ADAPTATIVOS (não falham por timeout artificial):
- Tentativa 1: 220s
- Tentativa 2: 400s
- Tentativa 3: 600s
- Tentativa 4+: 800s (continua indefinidamente)

Veja no arquivo de log para detalhes.

### 🎯 Próximas Fases

- **Fase 2**: Docker isolamento para testes perigosos
- **Fase 3**: Klein oscillation (PS ↔ D defenses)
- **Fase 4**: Bion α-função (metabolização de crashes)
- **Fase 5**: Lacan kernel (Imaginary/Symbolic/Real)
