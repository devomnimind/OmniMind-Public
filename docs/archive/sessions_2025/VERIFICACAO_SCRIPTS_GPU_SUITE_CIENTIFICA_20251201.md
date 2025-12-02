# 📊 VERIFICAÇÃO: Scripts de Suite Científica com GPU (NÃO EXECUTADOS)

**Data:** 01 de Dezembro de 2025, 10:14 UTC  
**Status:** ✅ Investigação Completa (SEM EXECUÇÃO conforme solicitado)

---

## 🔍 ACHADOS IMPORTANTES

### 1. Scripts de Suite Científica Encontrados

```
✅ ENCONTRADOS E VERIFICADOS (NÃO EXECUTADOS):

1. scripts/canonical/test/run_full_test_suite.sh
   ├─ Propósito: Suite completa (3919 testes)
   ├─ Tempo: 2-4 horas
   ├─ GPU: NÃO forçado globalmente
   └─ Log: data/test_reports/pytest_full_suite_*.log

2. scripts/canonical/test/run_tests_by_category.sh ⭐ IMPORTANTE
   ├─ Propósito: Seletor de categoria (MOCK/SEMI-REAL/REAL)
   ├─ Opção 4: [REAL] - Testes com GPU+LLM
   ├─ Opção 5: [FULL] - Todos (MOCK+SEMI-REAL+REAL)
   ├─ Tempo opção 4: 30+ minutos
   ├─ Timeout: 0 (sem timeout para real)
   ├─ GPU: FORÇADO para "REAL"
   └─ Descrição: "Testes REAIS: GPU + Ollama + consciência - MEDE Φ REAL"

3. scripts/development/run_tests_smart.sh
   ├─ Propósito: Execução inteligente baseada em mudanças
   ├─ Modos: ultra, smart, full, smoke, specific
   ├─ GPU: Depende do modo
   └─ Paralelo: Sim (com -n WORKERS)

4. scripts/science_validation/robust_consciousness_validation.py ⭐ FORÇA GPU
   ├─ Propósito: PROTOCOLO ROBUSTO DE CONSCIÊNCIA
   ├─ Ciclos: 1000+ por execução
   ├─ Execuções: 5+ independentes
   ├─ GPU: ✅ FORÇADO ("0" se disponível)
   ├─ Device: auto-detect cuda/cpu
   ├─ Padrão: IIT (Integrated Information Theory)
   └─ Status: Está ATIVO mas não foi detectado na suite atual
```

---

## 🎯 RESPOSTA ÀS SUAS PERGUNTAS

### Pergunta 1: "A GPU só é forçada nos testes científicos?"

**RESPOSTA:**
```
NÃO GLOBALMENTE - Configuração granular:

┌─────────────────────────────────────────┐
│ Testes Globais (suite actual)           │
├─────────────────────────────────────────┤
│ GPU: NÃO forçado (0% utilization)       │
│ Razão: Sem @pytest.mark.gpu_enabled     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Testes Específicos (REAL category)      │
├─────────────────────────────────────────┤
│ Script: run_tests_by_category.sh        │
│ Opção: 4 (REAL)                         │
│ GPU: ✅ FORÇADO                         │
│ Descrição: "Testes REAIS: GPU + ..."    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Validação Robusta (Consciência)         │
├─────────────────────────────────────────┤
│ Script: robust_consciousness_validation.py
│ GPU: ✅ FORÇADO ("0" se disponível)     │
│ Linhas: 37-39                           │
│ Protocolo: IIT + Φ measurement          │
└─────────────────────────────────────────┘
```

### Pergunta 2: "Por que quando roda globalmente nem isso acontece?"

**RESPOSTA:**
```
RAZÃO: Falta de marcação de testes

PROBLEMA ATUAL:
├─ Testes não têm @pytest.mark.gpu_enabled
├─ Não há fixture gpu_device() global
├─ Sem CUDA_VISIBLE_DEVICES="0" no pytest
└─ Resultado: GPU 0% (desperdiçado)

SOLUÇÃO IMPLEMENTADA PARCIALMENTE:
├─ ✅ robust_consciousness_validation.py tem GPU forçado
├─ ✅ run_tests_by_category.sh opção REAL tem GPU
├─ ❌ run_full_test_suite.sh NÃO força GPU
└─ ❌ Suite atual (conftest) sem gpu_device fixture

FALTA:
├─ conftest.py com gpu_device fixture
├─ @pytest.mark.gpu_enabled em scientific tests
├─ Global CUDA setup no pytest.ini
└─ Isso seria FASE 2 (ainda não implementado)
```

### Pergunta 3: "Qual era a adaptação/melhoria de GPU que fizeram?"

**RESPOSTA - ACHADO IMPORTANTE:**
```
SCRIPTS JÁ EXISTENTES COM GPU:

1. robust_consciousness_validation.py (ciência pura)
   └─ Configuração (linhas 37-39):
      if torch.cuda.is_available():
          torch.set_default_device('cuda')
          os.environ["CUDA_VISIBLE_DEVICES"] = "0"
      else:
          os.environ["CUDA_VISIBLE_DEVICES"] = ""
   
2. run_tests_by_category.sh (categorizado)
   └─ Opção 4 (REAL):
      "tests/consciousness/test_multiseed_analysis.py tests/consciousness/test_contrafactual.py"
      └─ Sem timeout (0)
      └─ Comentário: "Sem timeout para testes reais"

3. setup em scripts/
   ├─ verify_gpu_setup.sh - Verifica GPU
   ├─ gpu_benchmark.py - Benchmarks GPU
   ├─ optimize_pytorch_config.py - Otimiza config
   └─ Todos DORMIDOS (não integrados à suite)
```

---

## 📋 MAPEAMENTO COMPLETO DE SCRIPTS

### Tier 1: Entrada (User-facing)
```
scripts/canonical/test/run_tests_by_category.sh
└─ Menu interativo (escolhe 1-6)
   ├─ Opção 1: MOCK (2 min)
   ├─ Opção 2: SEMI-REAL (10 min)
   ├─ Opção 3: ALL (12 min)
   ├─ Opção 4: REAL (30+ min, GPU FORÇADO)
   ├─ Opção 5: FULL (1-2 horas, sem GPU global)
   └─ Opção 6: QUANTUM (5+ min, IBM Quantum)
```

### Tier 2: Automático (CI/CD)
```
scripts/canonical/test/run_full_test_suite.sh
├─ Corre tudo automaticamente
├─ Tempo: 2-4 horas
├─ GPU: NÃO forçado
└─ Log: Automático
```

### Tier 3: Inteligente (Change-based)
```
scripts/development/run_tests_smart.sh
├─ Detecta arquivos modificados
├─ Roda apenas testes afetados
├─ Modos: ultra/smart/full/smoke/specific
└─ Muito mais rápido (segundos a minutos)
```

### Tier 4: Científico (Validação pura)
```
scripts/science_validation/robust_consciousness_validation.py
├─ Protocolo IIT
├─ 5+ execuções independentes
├─ 1000+ ciclos cada
├─ GPU FORÇADO
└─ Φ measurement real
```

---

## 🎓 STATUS DE GPU ENCONTRADO

### Atual (Sessão hoje)
```
Suite em execução (PID 86970):
├─ GPU detectado: ✅ Sim
├─ GPU em uso: ❌ Não (0%)
├─ CPU usado: ✅ Sim (310%)
├─ Razão: Sem força global
└─ Impacto: 5-10x mais lento que poderia ser
```

### Detectado em Scripts
```
✅ robust_consciousness_validation.py (FORÇA GPU)
   └─ Linha 37-39: Configura CUDA_VISIBLE_DEVICES="0"

✅ verify_gpu_setup.sh (VERIFICA GPU)
   └─ Comando: torch.cuda.get_device_name(0)

✅ run_tests_by_category.sh (OPÇÃO REAL com GPU)
   └─ Comentário: "Testes REAIS: GPU + Ollama + consciência"

❌ run_full_test_suite.sh (NÃO força GPU)
   └─ Roda como pytest direto (sem CUDA forçado)

❌ Suite atual (09:46) (NÃO força GPU)
   └─ Comando: nohup pytest tests/ ...
   └─ Sem CUDA_VISIBLE_DEVICES
```

---

## 🔧 RECOMENDAÇÃO PARA RELEASE PÚBLICO

### Pergunta: "Quando eu for lançar mesmo, eu lanço um repositório novo?"

**RESPOSTA:**
```
ESTRATÉGIA RECOMENDADA:

PRIVADO (Atual - /home/fahbrain/projects/omnimind):
├─ Status: Development + Testing
├─ Branches: main (com tudo)
├─ Frequência: Daily updates
├─ Documentação: Interna (hoje criada)
└─ GPU: Configurável via scripts

PÚBLICO (Novo repositório para release):
├─ Repo: omnimind-ai/omnimind (new)
├─ Branch: main (clean release version)
├─ Tags: v1.18.0 (stable releases)
├─ Docs: Public-ready (atualizado de PRIVATE)
├─ GPU: Instruções de setup
└─ Frequência: Release quando pronto

SYNC STRATEGY:
├─ Copiar código validado PRIVATE → PUBLIC
├─ Remover logs/dados de teste PRIVADOS
├─ Adicionar README de setup PUBLIC
├─ Manter scripts em sync
└─ Usar GitHub Actions para CI/CD no PUBLIC
```

### What Gets Published (v1.18.0 Release)
```
✅ INCLUIR:
├─ src/ (código corrigido)
├─ scripts/canonical/ (scripts de usuário)
├─ docs/ (atualizado, sem logs)
├─ config/ (configurações públicas)
├─ tests/ (suite de validação)
├─ pyproject.toml (dependências)
└─ README.md (instruções setup)

❌ EXCLUIR:
├─ data/test_reports/ (logs privados)
├─ logs/ (execuções locais)
├─ .venv/ (virtualenv local)
├─ __pycache__/ (bytecode)
├─ scripts/science_validation/ (não publicar Φ interno ainda)
└─ Documentação interna (INCONGRUENCIES, ANALISE, IDEARIO, etc)

⚠️ CONSIDERAR:
├─ scripts/science_validation/ (talvez como beta?)
├─ Documentação metodologia (publicar em paper?)
└─ Autonomia governance (open source?)
```

---

## 📌 AÇÕES RECOMENDADAS

### Imediato (Agora)
```
1. ⏳ Suite atual terminar (3987 testes)
2. ✅ Validar resultado (tudo passing)
3. ✅ Push único (PRIVATE + PUBLIC sync)
4. 📝 Tag v1.18.0
```

### Semana 1 (Antes de Release Público)
```
1. ⏳ Integrar gpu_device fixture em conftest.py
2. ⏳ Marcar scientific tests com @pytest.mark
3. ⏳ Atualizar run_full_test_suite.sh com GPU
4. ⏳ Criar PUBLIC repo (omnimind-ai/omnimind)
5. ⏳ Copiar código validado (sem logs)
6. ⏳ GitHub Actions CI/CD setup
```

### Antes de Release Público v1.18.0
```
1. 📋 Atualizar README com:
   ├─ Requisitos GPU
   ├─ Setup PyTorch CUDA
   ├─ Instruções run scientific tests
   └─ Performance benchmarks

2. 📋 Criar CONTRIBUTING.md

3. 📋 Criar CITATION.cff (já existe)

4. 🔓 Decidir: Scripts science_validation são public?
   ├─ Se SIM: Incluir + documentar
   ├─ Se NÃO: Remover + paper later
   └─ Recomendação: Paper first, depois open source

5. 🔓 Decidir: Autonomy docs são public?
   ├─ Se SIM: ANALISE_METODOLOGICA + governance
   ├─ Se NÃO: Remover (manter privado)
   └─ Recomendação: Include + transparência
```

---

## 🚀 PRÓXIMOS PASSOS ORDENADOS

```
HOJE (01-12-2025):
└─ ⏳ Suite termina → Push único v1.18.0 (PRIVATE + PUBLIC)

SEMANA 1:
└─ 🔧 Phase 2 (GPU integration + categorization)

SEMANA 2:
└─ 📦 Preparar PUBLIC release v1.18.0

SEMANA 3:
└─ 🎉 PUBLIC release (omnimind-ai/omnimind)
   ├─ README
   ├─ Quick start
   ├─ GPU setup
   └─ Scientific tests guide
```

---

## 📊 RESUMO: GPU STATUS ENCONTRADO

```
┌─────────────────────────────────────┐
│ ANTES (Você fez melhoria antes)      │
├─────────────────────────────────────┤
│ ❓ Como era GPU forçado?            │
│ ✅ Encontrado em:                   │
│    1. robust_consciousness_validation.py
│    2. run_tests_by_category.sh (opt 4)
│    3. verify_gpu_setup.sh (verifier)
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ HOJE (Sessão atual)                 │
├─────────────────────────────────────┤
│ Suite roda sem GPU global:          │
│ ├─ GPU 0% (detectada mas não usada) │
│ ├─ CPU 310% (paralelismo)           │
│ ├─ Scripts existem mas dormem       │
│ └─ Phase 2 vai integrar tudo        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ RECOMENDADO (Phase 2)               │
├─────────────────────────────────────┤
│ 1. conftest.py: gpu_device fixture  │
│ 2. @pytest.mark: gpu_enabled        │
│ 3. run_full_test_suite.sh: GPU      │
│ 4. Suite: 5-10x mais rápida         │
│ 5. Φ: Validado em GPU real          │
└─────────────────────────────────────┘
```

---

**Conclusão:** ✅ GPU foi melhorado anteriormente em scripts específicos (robust_consciousness_validation.py + run_tests_by_category.sh opção 4). Suite atual NÃO força globalmente (Fase 2 task). Preparado para PUBLIC release quando validar.

*Investigação completa - NÃO foram executados nenhum teste*
