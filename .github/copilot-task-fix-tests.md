# 🤖 TASK: Corrigir 25 Falhas de Teste + Aumentar Cobertura para 90%

**Status:** 🟡 BLOQUEANTE | **Prioridade:** 🔴 CRÍTICA  
**Estimativa:** 6-8 horas | **Deadline:** Hoje  
**Assignee:** Copilot Remote Agent

---

## 📊 SITUAÇÃO ATUAL

```
✅ Testes Passando:      2489 (99.01%)
❌ Testes Falhando:      25 (0.99%) ← BLOQUEANTE
📈 Cobertura:            79% (meta: 90%)
⏱️  Tempo Suite:          770 segundos
```

**25 Falhas em 3 Módulos:**
- `security/test_security_monitor.py`: 12 falhas (interface mismatch)
- `tools/test_omnimind_tools.py`: 11 falhas (type/signature mismatch)
- `test_audit.py`: 2 falhas (missing exports)

---

## ✅ PRÉ-REQUISITOS (Executar ANTES de começar)

### 1. Validar Ambiente
```bash
python --version  # Deve ser 3.12.8
pytest --version  # Deve ser instalado
mypy --version    # Deve ser instalado
cd /home/fahbrain/projects/omnimind
pwd  # Confirmar que está na raiz
```

### 2. Revisar Documentação de Referência
- **Arquivo:** `data/test_reports/FAILURES_DETAILED_ANALYSIS.md`
  - Seção: "Cada falha analisada em detalho"
  - Contém: Causa raiz, tipo de fix, exemplos de código

- **Arquivo:** `data/test_reports/COVERAGE_ANALYSIS.md`
  - Seção: "24 módulos com <60% cobertura"
  - Foco: Módulos críticos

### 3. Entender a Estrutura
```
src/
├── audit/              ← Falhas: missing exports
├── security/           ← Falhas: interface SecurityMonitor (12)
│   └── security_monitor.py
├── tools/              ← Falhas: type/signature mismatch (11)
│   └── omnimind_tools.py
└── [outros módulos]

tests/
├── test_audit.py       ← 2 falhas
├── security/
│   └── test_security_monitor.py  ← 12 falhas
└── tools/
    └── test_omnimind_tools.py    ← 11 falhas
```

---

## 🎯 TAREFAS PRINCIPAIS

### FASE 1: Corrigir 25 Falhas (Bloqueante)

#### 1.1 Audit Exports (30 minutos) → +2 testes
**Arquivo:** `src/audit/__init__.py`

**Checklist:**
- [ ] Verificar se `ImmutableAuditSystem` é importado
- [ ] Verificar se `get_audit_system` é importado
- [ ] Adicionar ambos ao `__all__`
- [ ] Executar: `pytest tests/test_audit.py::TestModuleInterface -v`
- [ ] Esperado: 2 PASSED

**Validação:**
```bash
# Antes
python -c "from audit import ImmutableAuditSystem"  # Deve falhar

# Depois
python -c "from audit import ImmutableAuditSystem"  # Deve passar
python -c "from audit import get_audit_system"      # Deve passar
```

---

#### 1.2 Tools Signatures (1-1.5 horas) → +11 testes
**Arquivo Principal:** `src/tools/omnimind_tools.py`

**Análise Necessária:**
- [ ] Revisar assinatura de cada método `execute()`
- [ ] Mapear parâmetros reais vs esperados nos testes
- [ ] Mapear tipos de retorno

**Falhas Conhecidas:**
```python
# Problema 1: ArgumentError mismatch
# ❌ Teste chama: tool.execute(task="...")
# ✅ Deve ser:   tool.execute(description="...")
# Archivos: PlanTaskTool, NewTaskTool

# Problema 2: ArgumentError mismatch
# ❌ Teste chama: tool.execute(content="...")
# ✅ Deve ser:   tool.execute(data="...")
# Arquivo: EpisodicMemoryTool

# Problema 3: Return type mismatch
# ❌ Teste espera: str (resultado de comando)
# ✅ Retorna:      dict {'stdout': '...', 'stderr': '...', 'return_code': 0}
# Arquivo: ExecuteCommandTool
```

**Checklist:**
- [ ] Ler `FAILURES_DETAILED_ANALYSIS.md` Seção 2 (11 falhas detalhadas)
- [ ] Documentar cada assinatura real (executar no Python interativo)
- [ ] Atualizar testes para corresponder
- [ ] Executar: `pytest tests/tools/test_omnimind_tools.py -v`
- [ ] Esperado: 12 PASSED (dos 12 testes, 11 relacionados a tools)

**Validação:**
```bash
# Rodar testes específicos
pytest tests/tools/test_omnimind_tools.py::TestWriteFileTool -v
pytest tests/tools/test_omnimind_tools.py::TestExecuteCommandTool -v
pytest tests/tools/test_omnimind_tools.py::TestPlanTaskTool -v
pytest tests/tools/test_omnimind_tools.py::TestEpisodicMemoryTool -v
pytest tests/tools/test_omnimind_tools.py::TestAuditSecurityTool -v
```

---

#### 1.3 SecurityMonitor Interface (1-1.5 horas) → +12 testes
**Arquivo Principal:** `src/security/security_monitor.py`

**Análise Necessária:**
- [ ] Identificar quais métodos são privados (_method_name)
- [ ] Identificar quais métodos são públicos (method_name)
- [ ] Decidir: Expor como público ou criar wrappers?

**Falhas Conhecidas:**
```python
# Problema 1: Métodos privados mas testes chamam como públicos
# Privados encontrados:
#   - _is_suspicious_process
#   - _handle_security_event
#   - _monitor_system_resources
# Testes esperam: is_suspicious_process, create_security_event, monitor_system_resources

# Problema 2: Assertion rígida
# ❌ assert monitor.suspicious_processes == set()
# ✅ Precisa: assert isinstance(monitor.suspicious_processes, set)
# ✅ Porque: constructor carrega processos conhecidos
```

**Checklist:**
- [ ] Ler `FAILURES_DETAILED_ANALYSIS.md` Seção 1 (12 falhas detalhadas)
- [ ] Revisar `src/security/security_monitor.py` linha por linha
- [ ] Documentar interface pública vs privada
- [ ] Decisão 1: Expor métodos privados como públicos? (criar wrappers)
- [ ] Decisão 2: Alterar testes para usar interface privada corretamente?
- [ ] Implementar escolha
- [ ] Executar: `pytest tests/security/test_security_monitor.py -v`
- [ ] Esperado: 12 PASSED

**Validação:**
```bash
# Rodar todos os testes do módulo
pytest tests/security/test_security_monitor.py -v

# Rodar testes específicos
pytest tests/security/test_security_monitor.py::TestSecurityMonitor -v
pytest tests/security/test_security_monitor.py::TestSecurityMonitorEdgeCases -v
```

---

### FASE 2: Validação das Correções

**Checklist:**
- [ ] Executar suite completa
  ```bash
  pytest tests/ -v --tb=short
  # Esperado: 2514 PASSED, 0 FAILED
  ```

- [ ] Verificar cobertura
  ```bash
  pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80
  # Esperado: ≥ 80% (deve passar)
  ```

- [ ] Verificar lint
  ```bash
  black --check src/ tests/
  flake8 src/ tests/ --max-line-length=100
  ```

- [ ] Verificar type hints
  ```bash
  mypy src/ --ignore-missing-imports
  ```

---

### FASE 3: Aumentar Cobertura de 79% para 90%

**Estratégia:**

1. **Identificar Módulos Críticos <60%**
   ```bash
   # Usar: data/test_reports/COVERAGE_ANALYSIS.md
   # Focar em módulos de business logic (não __init__.py)
   # Prioridade:
   #   1. security/security_monitor (30% → 85%+)
   #   2. tools/* (se houver gaps)
   #   3. Outros módulos críticos
   ```

2. **Para Cada Módulo <60%:**
   - [ ] Analisar linhas não cobertas (ver htmlcov/index.html)
   - [ ] Criar testes para casos faltantes
   - [ ] Testar condições extremas (None, '', 0, [], etc.)
   - [ ] Testar paths de erro (try/except)
   - [ ] Garantir compatibilidade com testes existentes

3. **Estrutura de Novo Teste:**
   ```python
   # Padrão obrigatório:
   # ✅ Use pytest.approx() para float
   # ✅ Use pytest.mark.asyncio para async
   # ✅ Use fixtures para setup/teardown
   # ✅ Mock dependências externas
   # ✅ Type hints em todas as funções
   # ✅ Docstring Google-style
   ```

4. **Validar Conforme Avança:**
   ```bash
   pytest tests/ --cov=src --cov-report=html
   # Abrir: htmlcov/index.html no navegador
   # Procurar por linhas vermelhas (não cobertas)
   ```

5. **Meta Final:**
   ```bash
   pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90
   # Esperado: PASSED (90%+ cobertura)
   ```

---

## 🔍 VERIFICAÇÕES CRÍTICAS ANTES DE CADA COMMIT

### 1. Compatibilidade com Testes Existentes
```bash
# Rodar toda a suite
pytest tests/ -v

# Se falhar, analisar:
# - Seus testes novos quebram testes antigos?
# - Há conflito de fixtures?
# - Há side effects não isolados?
```

### 2. Type Hints 100%
```bash
# Verificar seu arquivo novo
mypy src/meu_arquivo.py

# Sem erros!
```

### 3. Lint Clean
```bash
black src/
flake8 src/ --max-line-length=100

# Sem erros!
```

### 4. Docstrings Completas
- [ ] Toda função tem docstring
- [ ] Docstring inclui: resumo, args, returns, raises
- [ ] Formato: Google-style

### 5. Dados Reais, Não Mocks
- [ ] Testes de security usam dados reais de processos? (NÃO - use mocks!)
- [ ] Testes de tools usam os commands reais? (SIM - ou use mock para segurança)
- [ ] Se mock, está bem documentado?

---

## 📋 CHECKLIST FINAL (Antes de submeter)

### Fase 1: Corrigir 25 Falhas
- [ ] Audit exports adicionados
- [ ] Tools signatures sincronizadas
- [ ] SecurityMonitor interface resolvida
- [ ] `pytest tests/ -v` → 2514 PASSED

### Fase 2: Validação
- [ ] `black src/ tests/` → PASSED
- [ ] `flake8 src/ tests/` → PASSED
- [ ] `mypy src/` → PASSED
- [ ] Cobertura ≥ 80% (obrigatório)

### Fase 3: Aumentar Cobertura 90%
- [ ] Novos testes criados
- [ ] Cobertura ≥ 90%
- [ ] Testes compatíveis com existentes
- [ ] Sem regressions

### Submissão
- [ ] Todos os checks PASSED
- [ ] Pronto para produção

---

## ⚠️ ARMADILHAS COMUNS (Evitar)

| Armadilha | Como Evitar |
|-----------|------------|
| Type mismatch | Use mypy strict |
| Testes isolados falhando | Rodar suite completa, não testes individuais |
| Dados mock inválidos | Usar fixtures pytest, documentar |
| Sem tratamento de erro | Try/except obrigatório em produção |
| Imports circulares | Verificar antes de commitar |
| Hard-coded values | Usar variáveis de ambiente, config files |

---

## 📞 REFERÊNCIAS

- Detalhes de cada falha: `data/test_reports/FAILURES_DETAILED_ANALYSIS.md`
- Cobertura por módulo: `data/test_reports/COVERAGE_ANALYSIS.md`
- Log completo: `data/test_reports/pytest_output.log`
- Relatório HTML: `data/test_reports/htmlcov/index.html`

---

## 🚀 PRÓXIMAS ETAPAS (Após conclusão)

1. ✅ Commit com mensagem: "Fix: corrigir 25 falhas de teste + aumentar cobertura para 90%"
2. ✅ Deploy em staging
3. ✅ Smoke tests
4. ✅ Deploy em produção

---

**Status:** 🟡 PRONTO PARA IMPLEMENTAÇÃO  
**Tempo Estimado:** 6-8 horas  
**Deadline:** Hoje  
**Start:** Agora!

