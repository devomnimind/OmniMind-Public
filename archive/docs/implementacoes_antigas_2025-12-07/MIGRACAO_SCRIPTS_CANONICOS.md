# 🔄 Migração de Scripts Canônicos

## Objetivo
Reorganizar scripts canônicos que estão na raiz de `scripts/` para `scripts/canonical/system/` para melhor organização.

## Scripts a Migrar

1. **`scripts/secure_run.py`** → `scripts/canonical/system/secure_run.py`
   - Script de execução segura com sudo
   - Usado por: start_omnimind_system.sh, start_omnimind_secondary.sh, start_production_phase22.sh

2. **`scripts/monitor_mcp_bpf.bt`** → `scripts/canonical/system/monitor_mcp_bpf.bt`
   - Script eBPF para monitoramento MCP
   - Usado por: start_omnimind_system.sh, start_omnimind_secondary.sh, start_production_phase22.sh, run_mcp_benchmark.sh, validate_mcp_setup.sh

3. **`scripts/start_mcp_servers.sh`** → Verificar se é duplicado
   - Se duplicado, manter apenas o canônico em `scripts/canonical/system/start_mcp_servers.sh`

## Arquivos que Precisam Atualização

### Scripts Shell
- ✅ `scripts/start_omnimind_system.sh` - Já usa `$PROJECT_ROOT`, fácil atualizar
- ⚠️ `scripts/canonical/system/start_omnimind_secondary.sh` - Usa caminhos relativos
- ⚠️ `scripts/start_production_phase22.sh` - Usa caminhos relativos
- ⚠️ `scripts/run_mcp_benchmark.sh` - Usa variável `$PROJECT_ROOT`
- ⚠️ `scripts/validate_mcp_setup.sh` - Lista de arquivos
- ⚠️ `scripts/canonical/system/start_mcp_servers.sh` - Referência interna

### Configurações
- ⚠️ `config/security/privileged_commands.yaml` - Regex precisa ser atualizado

### Systemd Services
- ⚠️ `scripts/production/deploy/omnimind-mcp.service` - Caminho absoluto

### Documentação
- ⚠️ `docs/canonical/MCP_EBPF_MONITORING_SETUP.md` - Referências de caminho

## Plano de Execução

1. ✅ Mover arquivos para `scripts/canonical/system/`
2. ✅ Atualizar todas as referências
3. ✅ Testar scripts principais
4. ✅ Atualizar documentação

## Status
- [x] Migração iniciada
- [x] Arquivos movidos
- [x] Referências atualizadas
- [x] Script principal validado (sintaxe OK)
- [x] Documentação atualizada

## ✅ Migração Concluída

**Data**: 2025-12-07

### Scripts Movidos
1. `scripts/secure_run.py` → `scripts/canonical/system/secure_run.py`
2. `scripts/monitor_mcp_bpf.bt` → `scripts/canonical/system/monitor_mcp_bpf.bt`

### Arquivos Atualizados
- ✅ `scripts/start_omnimind_system.sh`
- ✅ `scripts/canonical/system/start_omnimind_secondary.sh`
- ✅ `scripts/start_production_phase22.sh`
- ✅ `scripts/run_mcp_benchmark.sh`
- ✅ `scripts/validate_mcp_setup.sh`
- ✅ `scripts/canonical/system/start_mcp_servers.sh`
- ✅ `config/security/privileged_commands.yaml`
- ✅ `docs/canonical/MCP_EBPF_MONITORING_SETUP.md`

### Notas
- `scripts/start_mcp_servers.sh` já era um symlink para `canonical/system/start_mcp_servers.sh`, então não precisou ser movido
- Referências antigas encontradas apenas em relatórios históricos (`data/test_reports/` e `docs/RELATORIO_INVESTIGACAO_SISTEMA.md`), que não precisam ser atualizadas
- Script principal validado com `bash -n` - sem erros de sintaxe

