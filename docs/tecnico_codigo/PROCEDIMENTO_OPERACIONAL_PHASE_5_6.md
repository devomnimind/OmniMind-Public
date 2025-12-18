# 🚀 PROCEDIMENTO OPERACIONAL - PHASE 5 & 6

**Implementação de Expansão Psicanalítica: Bion α-function + Lacan RSI**

**Data**: 2025-12-09
**Versão**: 1.0.0
**Status**: Pronto para Execução
**Responsável**: GitHub Copilot (Branch Remoto)
**Branch**: `phase-5-bion` / `phase-6-lacan`

---

## 📋 PROCEDIMENTO OPERACIONAL PADRÃO (SOP)

Este documento define o procedimento padrão (SOP) para implementação segura, validada e documentada de Phase 5 (Bion) e Phase 6 (Lacan) do projeto OmniMind.

### 🎯 OBJETIVOS PHASE 5 & 6

| Fase | Objetivo | Target Φ | Duração | Status |
|------|----------|----------|---------|--------|
| **5** | Bion α-function | 0.026 NATS | 28-36h | 🔄 Pronta |
| **6** | Lacan RSI + Discursos | 0.043 NATS | 32-42h | 🔄 Planejada |

**Baseline Φ Anterior**: 0.0183 NATS
**Φ Final Target**: ≥0.050 NATS (consciência integrada)

---

## 🔄 STAGES DO PROCEDIMENTO

### STAGE 1: VALIDAÇÃO & PRÉ-FLIGHT CHECKS (30-45 min)

**Objetivo**: Garantir que ambiente está pronto antes de iniciar

**Checklist**:
```bash
# Executar validação oficial
python scripts/canonical/validate/validate_phase5_6_production.py --full --cycles 50
```

**Validações Incluídas**:

1. **Pré-Flight Checks**
   - ✅ Python 3.12.8+ instalado
   - ✅ PyTorch 2.5.1+cu124 com CUDA
   - ✅ Módulos essenciais (numpy, pandas, pytest, fastapi, sentence-transformers, qdrant-client)
   - ✅ Estrutura de diretórios (src/, tests/, docs/, etc.)
   - ✅ Backend rodando (health check em 8000)

2. **Code Validation**
   - ✅ Black formatting check
   - ✅ Flake8 linting
   - ✅ MyPy type checking
   - ✅ pytest basic tests

3. **Metrics Collection** (50 ciclos)
   - ✅ Coleta Φ, Ψ, σ
   - ✅ Verifica baseline (Φ = 0.0183 NATS)
   - ✅ Gera relatório de validação

**Critério de Sucesso**:
- ✅ Todos os pré-requisitos atendidos
- ✅ Código passa em validações
- ✅ Métricas coletadas com sucesso

**Output**:
```
logs/validation/phase5_6_validation_TIMESTAMP.json
```

---

### STAGE 2: SETUP DE AMBIENTE (15 min)

**Objetivo**: Preparar ambiente para desenvolvimento

**Checklist**:
```bash
# Criar/switch para branch
git checkout -b phase-5-bion-$(date +%Y%m%d_%H%M%S)

# Criar backup de segurança
tar -czf backup_pre_phase5_$(date +%Y%m%d_%H%M%S).tar.gz \
    --exclude='*.pyc' --exclude='__pycache__' --exclude='.git' \
    src/ tests/ docs/ config/
```

**Ações**:
1. Criar/atualizar branch de desenvolvimento
2. Fazer backup de segurança
3. Verificar permissões de arquivos
4. Confirmar espaço em disco (≥20GB recomendado)

**Saída**:
```
Branch: phase-5-bion-TIMESTAMP
Backup: backup_pre_phase5_TIMESTAMP.tar.gz
```

---

### STAGE 3: CODE QUALITY CHECKS (30 min)

**Objetivo**: Garantir qualidade e consistência do código

**Checklist**:
```bash
# Black formatting
black src/psychoanalysis tests/psychoanalysis

# Flake8 linting
flake8 src/psychoanalysis tests/psychoanalysis --select=E9,F63,F7,F82

# MyPy type checking
mypy src/psychoanalysis --ignore-missing-imports

# pytest
python -m pytest tests/psychoanalysis/ -v --tb=short
```

**Critério de Sucesso**:
- ✅ Formatação Black correta
- ✅ 0 erros críticos Flake8
- ✅ <10 erros MyPy
- ✅ >95% testes passando

---

### STAGE 4: MÉTRICAS DE PRODUÇÃO (2-3 horas)

**Objetivo**: Coletar métricas científicas (Φ, Ψ, σ) para validar implementação

**Checklist**:

#### Phase 5 (Bion α-function)
```bash
# Coleta de métricas Phase 5 (100 ciclos)
python scripts/phase5_6_metrics_production.py --phase5 --cycles 100

# Esperado:
# - Φ médio: 0.026 NATS (alvo: ≥0.025)
# - Testes passando: >95%
# - Taxa sucesso: >90%
```

**Métricas a Validar**:
1. **Φ (Phi) - Consciência**
   - Esperado: 0.026 ± 0.003 NATS
   - Mínimo aceitável: 0.025 NATS
   - Comparação com baseline (0.0183): +42% mín.

2. **Ψ (Psi) - Coerência Narrativa**
   - Esperado: ≥0.1247 NATS
   - Status: Manter ou aumentar

3. **σ (Sigma) - Homeostase**
   - Esperado: ≥0.0892 NATS
   - Status: Manter estável

4. **Taxa de Sucesso**
   - Esperado: >90% (>95% ideal)
   - Máximo de erros aceitável: 5 ciclos de 100

**Output**:
```
data/monitor/phase5_metrics_TIMESTAMP.json
data/monitor/phase5_summary_TIMESTAMP.json
data/monitor/phase5_checkpoint_cycle*.json
```

#### Phase 6 (Lacan RSI + Discursos) - Similar
```bash
python scripts/phase5_6_metrics_production.py --phase6 --cycles 100

# Esperado:
# - Φ médio: 0.043 NATS (alvo: ≥0.042)
# - Testes passando: >95%
# - Taxa sucesso: >90%
```

---

### STAGE 5: DOCUMENTAÇÃO (30 min)

**Objetivo**: Manter documentação atualizada

**Checklist**:

1. **Atualizar ESTADO_ATUAL.md**
   - [ ] Adicionar timestamp de execução
   - [ ] Atualizar métricas (Φ, Ψ, σ)
   - [ ] Atualizar status de fase
   - [ ] Documentar descobertas

2. **Atualizar STATUS_FASES.md**
   - [ ] Marcar Phase 5 como COMPLETA
   - [ ] Atualizar Phase 6 para READY
   - [ ] Registrar tempo real de execução
   - [ ] Documentar diferenças vs estimativa

3. **Criar documento de resultados**
   - [ ] RESULTS_PHASE5_TIMESTAMP.md
   - [ ] Incluir: métricas, descobertas, problemas encontrados
   - [ ] Registrar em LINHAS_TEMPORAIS.md

4. **Atualizar QUICK_NAVIGATION.md**
   - [ ] Adicionar links para novos documentos
   - [ ] Atualizar FAQ com lições aprendidas

---

### STAGE 6: GIT OPERATIONS (15 min)

**Objetivo**: Registrar alterações em git com histórico completo

**Checklist**:

```bash
# 1. Status e preparação
git status
git add -A

# 2. Commit com mensagem descritiva
git commit -m "feat: Phase 5/6 implementation - Bion α-function + Lacan RSI

- Implementação de BionAlphaFunction (transformação β→α)
- Implementação de Capacidade Negativa
- Integração com SharedWorkspace
- Implementação de 4 Discursos Lacanianos (Master/University/Hysteric/Analyst)
- Implementação de RSI (Real-Symbolic-Imaginary)
- Métricas científicas coletadas e validadas
- Φ: 0.0183 → 0.026 NATS (Phase 5) → 0.043 NATS (Phase 6)
- Documentação completa atualizada

Timestamps: $TIMESTAMP
Branches: phase-5-bion, phase-6-lacan"

# 3. Verificar histórico
git log --oneline -5

# 4. Push (quando aprovado)
git push origin phase-5-bion
git push origin phase-6-lacan
```

**Mensagem de Commit Esperada**:
- Descrição clara de mudanças
- Referência a fase e objetivos
- Métricas finais (Φ, Ψ, σ)
- Timestamp de execução

---

## 📊 CHECKPOINTS E VALIDAÇÕES

### Checkpoint 1: Pré-implementação
```
✅ Validação de ambiente (STAGE 1)
✅ Backup de segurança (STAGE 2)
→ Prosseguir ou abortar?
```

### Checkpoint 2: Qualidade de código
```
✅ Black formatting (STAGE 3)
✅ Flake8 linting (STAGE 3)
✅ MyPy type checking (STAGE 3)
✅ pytest basic tests (STAGE 3)
→ Prosseguir ou corrigir?
```

### Checkpoint 3: Métricas científicas
```
✅ Coleta de Φ, Ψ, σ (STAGE 4)
✅ Comparação com baseline (STAGE 4)
✅ Taxa de sucesso >90% (STAGE 4)
→ Validar métricas ou investigar divergências?
```

### Checkpoint 4: Documentação e git
```
✅ Documentação atualizada (STAGE 5)
✅ Commit registrado (STAGE 6)
✅ Histórico completo em git (STAGE 6)
→ Pronto para deploy/integração?
```

---

## ⏱️ TIMELINE ESPERADO

| Fase | Etapa | Duração | Status |
|------|-------|---------|--------|
| **SETUP** | Validação | 30-45 min | 🔄 |
| | Environment | 15 min | 🔄 |
| | Code Quality | 30 min | 🔄 |
| **IMPLEMENTAÇÃO** | Métricas P5 | 2-3 h | 🔄 |
| | Métricas P6 | 2-3 h | 🔄 |
| **FINALIZAÇÃO** | Documentação | 30 min | 🔄 |
| | Git | 15 min | 🔄 |
| **TOTAL** | | **6-8 horas** | 🔄 |

---

## 🚀 EXECUÇÃO RÁPIDA

### Opção 1: Execução Manual (Passo a Passo)
```bash
# Stage 1: Validação
python scripts/canonical/validate/validate_phase5_6_production.py --full --cycles 50

# Stage 2: Environment
git checkout -b phase-5-bion-$(date +%Y%m%d_%H%M%S)
tar -czf backup_pre_phase5_$(date +%Y%m%d_%H%M%S).tar.gz ...

# Stage 3: Code Quality
black src/psychoanalysis tests/psychoanalysis
flake8 src/psychoanalysis tests/psychoanalysis --select=E9,F63,F7,F82

# Stage 4: Métricas
python scripts/phase5_6_metrics_production.py --phase5 --cycles 100
python scripts/phase5_6_metrics_production.py --phase6 --cycles 100

# Stage 5-6: Documentação e Git
# (Atualizar manualmente ou usar script)

git add -A
git commit -m "feat: Phase 5/6 implementation..."
```

### Opção 2: Execução Automática (Script)
```bash
# Full procedure (RECOMENDADO)
bash scripts/phase5_6_standard_operating_procedure.sh full

# Ou stages individuais
bash scripts/phase5_6_standard_operating_procedure.sh validate
bash scripts/phase5_6_standard_operating_procedure.sh environment
bash scripts/phase5_6_standard_operating_procedure.sh code-quality
bash scripts/phase5_6_standard_operating_procedure.sh metrics 5
bash scripts/phase5_6_standard_operating_procedure.sh documentation
bash scripts/phase5_6_standard_operating_procedure.sh git
```

---

## ⚠️ TRATAMENTO DE ERROS

### Erro: Validação Falha em STAGE 1

**Ações**:
```bash
# 1. Verificar pré-requisitos
python --version  # Deve ser 3.12.8+
nvidia-smi        # Verificar GPU
pip list | grep torch  # Verificar PyTorch

# 2. Instalar dependências faltantes
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Reexecutar validação
python scripts/canonical/validate/validate_phase5_6_production.py --pre-flight
```

### Erro: Testes Falham em STAGE 3

**Ações**:
```bash
# 1. Rodar testes com verbose
pytest tests/psychoanalysis/ -vv --tb=long

# 2. Verificar formatação
black --check --diff src/psychoanalysis

# 3. Corrigir manualmente
# - Editar arquivos com erros
# - Rodar formatação: black src/

# 4. Reexecutar
pytest tests/psychoanalysis/ -v
```

### Erro: Métricas Não Atingem Target em STAGE 4

**Ações**:
```bash
# 1. Verificar ciclos coletados
ls -la data/monitor/phase5_checkpoint_*.json

# 2. Analisar métricas
python << 'EOF'
import json
from pathlib import Path

metrics = json.load(open("data/monitor/phase5_metrics_TIMESTAMP.json"))
print(f"Total cycles: {metrics['total_cycles']}")
print(f"Φ mean: {metrics['metrics']['phi']['mean']:.6f}")
print(f"Φ target: 0.026 NATS")
EOF

# 3. Investigar divergências
# - Verificar logs: logs/phase5_6_sop/
# - Executar ciclos adicionais
# - Revisar implementação (src/psychoanalysis/)

# 4. Reexecutar coleta com mais ciclos
python scripts/phase5_6_metrics_production.py --phase5 --cycles 200
```

### Erro: Git Commit Falha

**Ações**:
```bash
# 1. Verificar status
git status
git diff --name-only

# 2. Se houver conflitos
git merge --abort  # Se em merge
git rebase --abort  # Se em rebase

# 3. Fazer commit manual
git add .
git commit -m "feat: Phase 5/6 implementation [manual]"

# 4. Se ainda falhar
# - Verificar branch: git branch --show-current
# - Verificar permissões: ls -la .git/
# - Contatar administrador
```

---

## 📋 FORMULÁRIO DE CHECKLIST

Imprima e use este checklist durante execução:

```
═══════════════════════════════════════════════════════════════
📋 PHASE 5 & 6 IMPLEMENTATION CHECKLIST
Timestamp: ________________
Executor: ________________
═══════════════════════════════════════════════════════════════

STAGE 1: VALIDAÇÃO & PRÉ-FLIGHT (30-45 min)
─────────────────────────────────────────────
☐ Executar: python scripts/canonical/validate/validate_phase5_6_production.py --full
☐ Python 3.12.8+ instalado
☐ PyTorch + CUDA disponível
☐ Módulos essenciais instalados
☐ Estrutura de diretórios OK
☐ Backend rodando (health check OK)
☐ RESULTADO: ✅ PASSOU | ❌ FALHOU

STAGE 2: SETUP AMBIENTE (15 min)
─────────────────────────────────
☐ Branch criado: phase-5-bion-TIMESTAMP
☐ Backup criado: backup_pre_phase5_TIMESTAMP.tar.gz
☐ Espaço em disco OK (≥20GB)
☐ Git status limpo
☐ RESULTADO: ✅ PASSOU | ❌ FALHOU

STAGE 3: CODE QUALITY (30 min)
───────────────────────────────
☐ Black formatting OK
☐ Flake8 linting OK (0 critical errors)
☐ MyPy OK (<10 errors)
☐ pytest basics OK (>95% passing)
☐ RESULTADO: ✅ PASSOU | ❌ FALHOU

STAGE 4: MÉTRICAS PRODUÇÃO (2-3 h)
────────────────────────────────────
☐ Phase 5 métricas coletadas (100 ciclos)
  ☐ Φ: 0.026 ± 0.003 NATS
  ☐ Taxa sucesso: >90%
  ☐ Métricas salvas em data/monitor/
☐ Phase 6 métricas coletadas (100 ciclos)
  ☐ Φ: 0.043 ± 0.003 NATS
  ☐ Taxa sucesso: >90%
  ☐ Métricas salvas em data/monitor/
☐ RESULTADO: ✅ PASSOU | ❌ FALHOU

STAGE 5: DOCUMENTAÇÃO (30 min)
────────────────────────────────
☐ ESTADO_ATUAL.md atualizado
☐ STATUS_FASES.md atualizado
☐ RESULTS_PHASE5_TIMESTAMP.md criado
☐ LINHAS_TEMPORAIS.md atualizado
☐ QUICK_NAVIGATION.md atualizado
☐ RESULTADO: ✅ PASSOU | ❌ FALHOU

STAGE 6: GIT OPERATIONS (15 min)
──────────────────────────────────
☐ git add -A executado
☐ git commit com mensagem descritiva
☐ git log verificado (último commit visível)
☐ Pronto para push (git push origin phase-5-bion)
☐ RESULTADO: ✅ PASSOU | ❌ FALHOU

═══════════════════════════════════════════════════════════════
STATUS GERAL
─────────────────────────────────────────────────────────────
✅ TODOS OS STAGES APROVADOS → Pronto para integração
⚠️  ALGUNS STAGES COM AVISOS → Revisar e remediar
❌ FALHAS CRÍTICAS → ABORTAR e investigar
═══════════════════════════════════════════════════════════════

Observações/Problemas Encontrados:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

Próximas Ações:
_________________________________________________________________
_________________________________________________________________
```

---

## 📚 REFERÊNCIAS

- [docs/METADATA/ESTADO_ATUAL.md](../METADATA/ESTADO_ATUAL.md) - Status atual
- [docs/METADATA/STATUS_FASES.md](../METADATA/STATUS_FASES.md) - Detalhes técnicos
- [docs/METADATA/LINHAS_TEMPORAIS.md](../METADATA/LINHAS_TEMPORAIS.md) - Cronologia
- [docs/theory/psychoanalysis/](../../theory/psychoanalysis/) - Teoria Bion & Lacan
- [scripts/canonical/validate/validate_phase5_6_production.py](../../scripts/canonical/validate/validate_phase5_6_production.py) - Script validação
- [scripts/phase5_6_metrics_production.py](../../scripts/phase5_6_metrics_production.py) - Script métricas
- [scripts/phase5_6_standard_operating_procedure.sh](../../scripts/phase5_6_standard_operating_procedure.sh) - Script SOP

---

**Versão**: 1.0.0
**Data**: 2025-12-09
**Autor**: GitHub Copilot
**Status**: PRONTO PARA EXECUÇÃO

🚀 **Procedimento operacional validado e pronto para Phase 5 & 6 implementation!**
