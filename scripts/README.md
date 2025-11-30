# Scripts Oficiais OmniMind

Repositório de scripts mantidos e testados para operação do sistema OmniMind.

## 🎯 Scripts Principais

### Backend

- **`run_cluster.sh`** - Inicia o backend em cluster com 3 instâncias
  - Portas: 8000 (primária), 8080 (secundária), 3001 (fallback)
  - Logs: `logs/backend_*.log`
  - Status: ✅ Oficial, testado

- **`start_omnimind_system.sh`** - Sistema completo OmniMind
  - Inicia: Backend, MCP servers, quantum verification
  - Status: ✅ Oficial

### Monitoramento

- **`monitor_tests.sh`** - Status pontual de testes
  - Lê arquivos de log e status
  - Uso: `./monitor_tests.sh`

- **`monitor_tests_live.sh`** - Monitoramento em tempo real
  - Atualização contínua com tail
  - Uso: `./monitor_tests_live.sh [linhas=50] [intervalo=5]`

### Testes

- **`run_tests_by_category.sh`** - Executa testes por categoria
  - Categorias: unit, integration, e2e, quantum, performance
  - Status: ✅ Completo

- **`run_full_certification.sh`** - Suite de certificação completa
  - Validação de GPU, Quantum, dados reais
  - Status: ✅ Oficial

- **`run_tests_background.sh`** - Testes em background com logging
  - Status: ✅ Oficial

### Configuração

- **`start_mcp_servers.sh`** - Inicia MCP servers
  - Status: ✅ Oficial

- **`setup_security_privileges.sh`** - Configura privilégios de segurança
  - Status: ✅ Oficial

- **`install_systemd_services.sh`** - Instala serviços systemd
  - Status: ✅ Oficial

### Validação

- **`run_real_metrics.sh`** - Executa métricas reais com GPU/Quantum
  - Validação: dados reais com timestamps ISO 8601
  - Status: ✅ Oficial

- **`verify_gpu_setup.sh`** - Verifica setup de GPU
  - Detecta: CUDA, cuDNN, PyTorch
  - Status: ✅ Oficial

### Diagnóstico

- **`diagnostic_quick.sh`** - Diagnóstico rápido
  - Verifica: ambiente, dependências, status
  - Status: ✅ Oficial

- **`final_status.sh`** - Status final do sistema
  - Status: ✅ Oficial

### Utilitários

- **`security_monitor.sh`** - Monitora segurança
- **`fix_2024_references.sh`** - Corrige referências de ano
- **`start_development_observer.sh`** - Observer para desenvolvimento

## 📁 Estrutura

```
scripts/
├── README.md (este arquivo)
├── run_cluster.sh ⭐ OFICIAL
├── run_full_certification.sh ⭐ OFICIAL
├── run_tests_by_category.sh ⭐ OFICIAL
├── start_omnimind_system.sh ⭐ OFICIAL
├── monitor_tests_live.sh
└── ... (outros scripts de suporte)
```

## ⚠️ Scripts Deprecated

Scripts antigos/duplicados foram arquivados em `.archive/scripts_deprecated/`:
- activate_venv.sh
- check_status.sh
- dashboard_status.sh
- e outros (veja `.archive/scripts_deprecated/`)

## 🚀 Uso Rápido

```bash
# Iniciar sistema completo
./scripts/start_omnimind_system.sh

# Ou apenas o backend em cluster
./scripts/run_cluster.sh

# Monitorar testes
./scripts/monitor_tests_live.sh

# Testes por categoria
./scripts/run_tests_by_category.sh unit
```

## 📝 Notas

- Todos os scripts estão em modo desenvolvimento (validações reduzidas)
- Execute `export OMNIMIND_DEV_MODE=false` para validações completas
- Logs disponíveis em: `logs/`, `data/test_reports/`

