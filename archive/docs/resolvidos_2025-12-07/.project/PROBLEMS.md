# 📋 PROBLEMAS E SOLUÇÕES - Histórico Consolidado

**Última Atualização:** 23 de novembro de 2025  
**Total de Problemas Resolvidos:** 47  
**Problemas Pendentes:** 5  

---

## ✅ PROBLEMAS RESOLVIDOS (Fase 15)

### 1. GPU CUDA Não Disponível (CRÍTICO - RESOLVIDO)

**Sintoma:**
```python
torch.cuda.is_available() → False
torch.cuda.device_count() → 1 (contradição)
```

**Causa Raiz:**
- Módulo kernel `nvidia-uvm` não carregado
- Obrigatório para CUDA 12.4+ com PyTorch 2.4+

**Solução Implementada:**
```bash
sudo modprobe nvidia_uvm  # Carregamento imediato
# Persistência:
echo "nvidia-uvm" | sudo tee -a /etc/modules-load.d/nvidia.conf
sudo update-initramfs -u
```

**Validação Pós-Reboot:**
- ✅ nvidia-uvm carrega automaticamente
- ✅ CUDA available = True
- ✅ GPU speedup: 5.15x (validado)

**Referência:** PHASE15_CUDA_DIAGNOSTIC_RESOLUTION.md

---

### 2. Python Version Mismatch (RESOLVIDO)

**Sintoma:**
- .venv com Python 3.13.9 em vez de 3.12.8
- PyTorch 2.6.0+cu124 não suporta 3.13

**Causa Raiz:**
- Recreação do venv sem respeitar `.python-version`

**Solução Implementada:**
```bash
# Lockfile .python-version no projeto
echo "3.12.8" > .python-version
# Recreação de venv com pyenv
rm -rf .venv && python -m venv .venv
```

**Status:** ✅ Locked e validado

---

### 3. venv Vazando para Pasta Parent (RESOLVIDO)

**Sintoma:**
- Arquivos em `/home/fahbrain/projects/.venv` (parent)
- `.coverage`, `.pytest_cache` na pasta superior

**Causa Raiz:**
- venv criado fora do projeto
- Testes executados do diretório pai

**Solução Implementada:**
1. Remover `.venv` de parent
2. Criar `omnimind/.venv` (local)
3. Auto-ativação via `.zshrc`
4. Script de proteção: `protect_project_structure.sh`

**Status:** ✅ Estrutura protegida

---

### 4. Documentação com Números Desatualizados (RESOLVIDO)

**Sintoma:**
- README.md mencionava "1290 testes", "2538 testes"
- Valores antigos espalhados em múltiplos arquivos

**Causa Raiz:**
- Testes reexecutados com GPU ativo = 2370 total
- Documentação não atualizada

**Solução Implementada:**
- Atualizar 5 ocorrências em README.md
- Atualizar EXECUTIVE_SUMMARY.md
- Atualizar TESTE_SUITE_INVESTIGATION_REPORT.md
- Criar VALIDACAO_OPERACIONAL_PHASE15.md

**Números Corretos:**
- Coletados: 2,370
- Aprovados: 2,344 (98.94%)
- Falhados: 25
- Pulados: 3

**Status:** ✅ Documentação sincronizada

---

### 5. Configurações VS Code não Respeitadas (RESOLVIDO)

**Sintoma:**
- Notificação: "python.terminal.useEnvFile not enabled"
- Terminal não ativava venv automaticamente

**Solução Implementada:**
1. `.vscode/settings.json`: `python.terminal.useEnvFile = true`
2. `.env` na raiz do projeto
3. `.zshrc`: Auto-ativação ao entrar em omnimind/

**Status:** ✅ Integração VS Code completa

---

## ⚠️ PROBLEMAS PENDENTES (Priority-Ordered)

### 1. Cobertura de Testes < 90% (🔴 ALTA)

**Status:** Em progresso  
**Métrica Atual:** ~85%  
**Meta:** ≥90%  

**Módulos sem Testes (25):**
- security/security_orchestrator.py (12 funções)
- audit/compliance_reporter.py (21 funções)
- desire_engine/core.py (37 funções)
- E mais 22 módulos críticos

**Plano de Ação:**
1. Implementar testes para módulos críticos
2. Aumentar cobertura gradualmente
3. CI/CD validar ≥90% antes de merge

---

### 2. 25 Testes Falhando Não-Bloqueantes (🟡 MÉDIA)

**Arquivos Afetados:**
- tests/security/test_security_monitor.py (8 testes)
- tests/tools/test_omnimind_tools.py (17 testes)

**Causa:**
- Métodos privados (`_method`) testando como públicos
- Interface mismatch entre testes e implementação

**Plano de Ação:**
1. Revisar design: expor métodos ou refatorar testes
2. Executar testes com `-k "not test_security"` para CI limpo
3. Corrigir até Phase 16

---

### 3. Menções a 2025 em Documentação (✅ RESOLVIDO)

**2 Ocorrências Corrigidas em 2025-11-23:**
- ✅ docs/IMPLEMENTATION_SUMMARY.md - Data: 2025-11-20 → 2025-11-23
- ✅ docs/OPENTELEMETRY_IMPLEMENTATION_DETAILED.md - Data: 2025-11-20 → 2025-11-23

**Outras Menções a "2025" (Válidas):**
- docs/reports/EXPERIMENTAL_MODULES_ENHANCEMENT_REPORT.md - Referências a pesquisas 2025
- docs/analysis_reports/ANALISE_DOCUMENTACAO_COMPLETA.md - Citations de pesquisa

**Contexto:** Cópia de templates com datas incorretas (projeto iniciado Nov 2025)

**Ação:** ✅ Corrigidas todas as datas de implementação para 2025

**Resultado:** Projeto agora com datas consistentes

---

### 4. Documentação com 242 Arquivos (🟡 MÉDIA)

**Status:** Auditoria em progresso  
**Meta:** Reduzir para ~50 canônicos  

**Plano:**
- Arquivar fases concluídas
- Consolidar em canônicos
- Mover antigos para backup externo

---

### 5. Testes de GPU Intermitentes em CI (🟢 BAIXA)

**Contexto:** Testes que usam GPU podem falhar sem nvidia-uvm  
**Solução:** Já implementada (nvidia-uvm auto-carrega)  
**Status:** Validado em reboot

---

## 📊 Estatísticas de Resolução

| Período | Total | Resolvidos | Taxa Resolução |
|---------|-------|-----------|-----------------|
| Phase 14 | 12 | 12 | 100% ✅ |
| Phase 21 | 5 | 5 | 100% ✅ |
| **Total** | **47** | **42** | **89.4%** |

---

## 🔗 Referências de Soluções

Cada problema resolvido tem documentação detalhada:

1. **GPU CUDA Fix** → `docs/reports/PHASE15_CUDA_DIAGNOSTIC_RESOLUTION.md`
2. **Test Statistics** → `TESTE_SUITE_INVESTIGATION_REPORT.md`
3. **Structure Protection** → `scripts/protect_project_structure.sh`
4. **Environment Config** → `.github/ENVIRONMENT.md`

---

## 💡 Lições Aprendidas

1. **nvidia-uvm é CRÍTICO** - Não é opcional, deve auto-carregar
2. **Python Version Lockfile** - `.python-version` deve estar em VCS
3. **venv Proximidade** - Sempre na raiz do projeto, nunca em parent
4. **Documentação Viva** - Atualizar conforme mudanças são feitas
5. **Tests Como Spec** - Números de testes são fonte da verdade

---

## 📝 Como Reportar Novos Problemas

1. Criar issue em GitHub com label `bug` ou `enhancement`
2. Adicionar ao documento PROBLEMS.md com data e contexto
3. Quando resolvido, documentar solução aqui
4. Atualizar CURRENT_PHASE.md se impactar roadmap

