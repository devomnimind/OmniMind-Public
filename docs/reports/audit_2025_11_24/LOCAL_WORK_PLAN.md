# 🛠️ PLANO DE TRABALHO LOCAL - OmniMind Phase 21
**Data:** 2025-11-24
**Duração Estimada:** 15-20 minutos
**Executor:** Desenvolvedor Local + AI Assistant
**Tipo:** Code Refactoring & Cleanup

---

## 🎯 OBJETIVO

Executar tarefas críticas de refatoração e limpeza de código identificadas no relatório de auditoria, em paralelo com o trabalho remoto de documentação.

---

## 📋 TAREFAS LOCAIS (SEM CONFLITO COM REMOTO)

### ✅ TAREFA LOCAL 1: Limpar requirements.txt (Prioridade Máxima)

**Duração:** ~10 minutos
**Severidade:** 🔴 Crítica

**Passos:**

1. **Analisar relatório de dependências**
   ```bash
   cat docs/reports/audit_2025_11_24/deps_analysis.txt
   ```

2. **Criar requirements-dev.txt** (separar dev dependencies)
   ```bash
   # Mover para requirements-dev.txt:
   black>=23.0.0
   mypy>=1.0.0
   pylint>=3.0.0
   pytest>=7.0.0
   pytest-cov>=4.0.0
   pytest-asyncio>=0.21.0
   pytest-mock>=3.10.0
   pytest-xdist>=3.0.0
   flake8>=6.0.0
   ```

3. **Remover dependências confirmadamente NÃO USADAS**
   ```
   # A remover de requirements.txt (CONFIRMA
R ANTES):
   - langchain (não usado)
   - langchain-community
   - llama-cpp-python (não usado)
   - ultralytics (não usado)
   - whisper (não usado)
   - bitsandbytes (não usado)
   - datasets (não usado)
   ```

4. **Validar que NÃO são falsos positivos:**
   - **MANTER:** transformers, torch, fastapi, pydantic, uvicorn (usados mas import via underscore ou dinâmico)
   - **VERIFICAR:** langchain-ollama (pode ser import como `langchain_ollama`)

5. **Executar testes após mudanças**
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   pytest tests/ -v --tb=short
   ```

**Arquivos Modificados:**
- `requirements.txt` (runtime only)
- `requirements-dev.txt` (novo - dev/test tools)

---

### ✅ TAREFA LOCAL 2: Consolidar MCP Client Modules

**Duração:** ~10 minutos
**Severidade:** 🔴 Alta (Código Duplicado #1)

**Passos:**

1. **Analisar diferenças**
   ```bash
   diff src/integrations/mcp_client.py src/integrations/mcp_client_enhanced.py
   ```

2. **Decisão Arquitetural:**
   - **Opção A:** Manter apenas `mcp_client_enhanced.py` e remover `mcp_client.py`
   - **Opção B:** Merge features de enhanced para client e remover enhanced

3. **Executar merge/remoção:**
   ```bash
   # Se opção A:
   git rm src/integrations/mcp_client.py

   # Se opção B:
   # Merge manual + git rm src/integrations/mcp_client_enhanced.py
   ```

4. **Atualizar imports em todo código:**
   ```bash
   grep -r "from.*mcp_client import" src/
   grep -r "import mcp_client" src/
   # Substituir por versão mantida
   ```

5. **Testar integração**
   ```bash
   pytest tests/integrations/test_mcp*.py -v
   ```

**Arquivos Modificados:**
- `src/integrations/mcp_client.py` (removido) OU
- `src/integrations/mcp_client_enhanced.py` (removido)
- Múltiplos arquivos com imports atualizados

---

### ✅ TAREFA LOCAL 3: Refatorar Top 3 Duplicações de Código

**Duração:** ~Reserva (se houver tempo)
**Severidade:** 🟡 Alta

**Duplicação #1: Swarm Memory Tracking**
```python
# Criar src/swarm/utils.py

import psutil
from typing import Dict

def track_memory_usage() -> Dict[str, float]:
    """Track memory usage for swarm algorithms."""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent()
        }
    except Exception:
        return {"rss_mb": 0.0, "vms_mb": 0.0, "percent": 0.0}
```

Substituir em:
- `src/swarm/ant_colony.py` (linhas 81-88)
- `src/swarm/particle_swarm.py` (linhas 114-121)

**Duplicação #2: Quantum Consciousness Imports**
Criar `src/quantum_consciousness/__init__.py` com imports comuns

**Duplicação #3: Compliance Reporter**
Refatorar métodos duplicados em `src/audit/compliance_reporter.py`

---

## 🚫 CONFLITOS A EVITAR

### ❌ NÃO TOCAR (Trabalho Remoto):
- Qualquer arquivo `.md` em `docs/`
- `README.md`, `CHANGELOG.md`
- Criar `ARCHITECTURE.md`, `CONTRIBUTING.md` (remoto)
- Criar `.env.example` (remoto)

### ✅ PODE MODIFICAR (Local Only):
- `requirements.txt`, `requirements-dev.txt`
- Arquivos `.py` em `src/`
- Arquivos de teste em `tests/`
- Scripts em `scripts/`

---

## 📊 Checklist de Execução

### Antes de Começar:
- [ ] Pull do repositório: `git pull origin master`
- [ ] Confirmar que auditoria foi pushed (commit `5c74f906`)
- [ ] Criar branch de trabalho: `git checkout -b local/cleanup-and-refactor`

### Durante Execução:
- [ ] **Tarefa 1:** Limpar requirements.txt ✅
- [ ] **Tarefa 2:** Consolidar MCP clients ✅
- [ ] **Tarefa 3:** Refatorar duplicações (se houver tempo)

### Após Conclusão:
- [ ] Executar validações completas:
  ```bash
  black src/ tests/ scripts/
  flake8 src/ tests/ scripts/ --max-line-length=100
  mypy src/ --ignore-missing-imports
  pytest tests/ --cov=src --cov-fail-under=90 -v
  ```
- [ ] Commit local:
  ```bash
  git add -A
  git commit -m "refactor: cleanup dependencies and consolidate MCP clients

  - Separate runtime (requirements.txt) from dev (requirements-dev.txt)
  - Remove 8 unused dependencies confirmed by audit
  - Consolidate mcp_client.py and mcp_client_enhanced.py
  - Extract common swarm memory tracking to utils

  Related: Audit 2025-11-24 [AC-001, AC-002, DUP-001, DUP-003]"
  ```
- [ ] **NÃO FAZER PUSH AINDA** - aguardar merge do trabalho remoto

---

## 🔄 Sincronização com Trabalho Remoto

### Quando o trabalho remoto terminar:

1. **Fetch mudanças remotas:**
   ```bash
   git fetch origin master
   ```

2. **Merge trabalho remoto no local:**
   ```bash
   git merge origin/master
   # OU rebase se preferir histórico linear:
   git rebase origin/master
   ```

3. **Resolver conflitos (improvável, mas possível):**
   - Conflitos esperados: NENHUM (trabalhamos em arquivos diferentes)
   - Se houver: revisar manualmente

4. **Push final:**
   ```bash
   git push origin local/cleanup-and-refactor
   ```

5. **Criar PR no GitHub** (opcional) ou merge direto em master

---

## 📈 Resultado Esperado

### Débitos Técnicos Resolvidos:
- ✅ [AC-001] Requirements.txt limpo
- ✅ [AC-002] MCP clients consolidados
- ✅ [DUP-001] Código duplicado reduzido
- ✅ [DUP-003] Swarm utils extraído

### Métricas Antes vs Depois:
| Métrica | Antes | Depois |
|---------|-------|--------|
| Deps não usadas | 41 | ~33 (-8) |
| Blocos duplicados | 46 | ~43 (-3) |
| Módulos MCP | 2 | 1 |

---

**INÍCIO DO TRABALHO LOCAL!** 🚀
