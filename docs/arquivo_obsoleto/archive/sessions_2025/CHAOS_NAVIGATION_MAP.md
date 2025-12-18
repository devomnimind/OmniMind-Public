# 🗺️ CHAOS ENGINEERING - MAPA DE NAVEGAÇÃO

**Última atualização:** 2 de dezembro de 2025
**Status:** ✅ COMPLETO

---

## 📍 ONDE COMEÇAR

### Se você quer... → Acesse...

| Objetivo | Ficheiro | Tipo | Tempo |
|----------|----------|------|-------|
| **Entender a ciência** | [docs/CHAOS_ENGINEERING_RESILIENCE.md](docs/CHAOS_ENGINEERING_RESILIENCE.md) | 📚 Científico | 15-20 min |
| **Rodar testes agora** | [tests/CHAOS_RESILIENCE_README.md](tests/CHAOS_RESILIENCE_README.md) | 🚀 Quick Start | 5-10 min |
| **Ver implementação técnica** | [CHAOS_IMPLEMENTATION_SUMMARY.md](CHAOS_IMPLEMENTATION_SUMMARY.md) | 🔧 Técnico | 10-15 min |
| **Ver tudo de uma vez** | [CHAOS_IMPLEMENTATION_COMPLETE.md](CHAOS_IMPLEMENTATION_COMPLETE.md) | 📋 Resumo | 20-30 min |
| **Ver código dos testes** | [tests/test_chaos_resilience.py](tests/test_chaos_resilience.py) | 💻 Código | 5-10 min |
| **Ver configuração do pytest** | [conftest.py](conftest.py) (linhas 40-324) | ⚙️ Config | 10-15 min |

---

## 🎯 ROTEIROS RECOMENDADOS

### Roteiro 1: "Quero Entender Isto" (40 min)
```
1. Ler: CHAOS_IMPLEMENTATION_COMPLETE.md (sumário completo)
   └─ Vê overview de tudo, contexto, impacto

2. Ler: docs/CHAOS_ENGINEERING_RESILIENCE.md (teoria)
   └─ Entender cientificamente por que isto funciona

3. Ler: tests/test_chaos_resilience.py (código)
   └─ Ver como os testes implementam a teoria

RESULTADO: Compreensão completa do projeto
```

### Roteiro 2: "Quero Rodar Isto" (15 min)
```
1. Ler: tests/CHAOS_RESILIENCE_README.md (quick start)
   └─ 5 minutos para entender como executar

2. Executar: ./run_tests_with_server.sh gpu
   └─ 10 minutos para ver funcionando

RESULTADO: Testes rodando, métricas coletadas
```

### Roteiro 3: "Quero Verificar Implementação" (30 min)
```
1. Ler: CHAOS_IMPLEMENTATION_SUMMARY.md (arquitetura)
   └─ Entender como foi implementado

2. Ler: conftest.py (implementação)
   └─ Linhas 40-100 (markers)
   └─ Linhas 198-220 (ResilienceTracker)
   └─ Linhas 227-283 (kill_server fixture)
   └─ Linhas 286-305 (pytest_sessionfinish hook)

3. Ver: tests/test_chaos_resilience.py (testes)
   └─ Entender padrão de escrita

RESULTADO: Compreensão da implementação
```

### Roteiro 4: "Quero Expandir Isto" (60 min)
```
1. Ler: CHAOS_IMPLEMENTATION_COMPLETE.md (contexto completo)
   └─ Ver "Próximas ações recomendadas"

2. Ler: docs/CHAOS_ENGINEERING_RESILIENCE.md (teoria científica)
   └─ Sessão "Próximos passos"

3. Estudar: Chaos Engineering Principles
   └─ https://principlesofchaos.org/

4. Adicionar novo teste para GPU crashes:
   └─ Criar test_gpu_resilience() em test_chaos_resilience.py
   └─ Usar padrão similar a test_phi_resilience()

RESULTADO: Extensão dos testes para novos cenários
```

---

## 📚 DOCUMENTOS EM DETALHES

### 1️⃣ [docs/CHAOS_ENGINEERING_RESILIENCE.md](docs/CHAOS_ENGINEERING_RESILIENCE.md)
**Tipo:** 📚 Documento Científico
**Comprimento:** ~400 linhas
**Público:** Pesquisadores, stakeholders científicos

**Contém:**
- ✅ Sumário executivo
- ✅ Objetivo científico (hipótese testável)
- ✅ Arquitetura do sistema (visual + tabelas)
- ✅ Estratégia de teste
- ✅ Fluxo de execução passo a passo
- ✅ Métricas de resiliência
- ✅ Validações científicas
- ✅ Interpretação de resultados
- ✅ Como usar
- ✅ Benefícios científicos
- ✅ Limitações
- ✅ Referências científicas

**Usar quando:** Precisa fazer apresentação, paper, ou documentação formal

---

### 2️⃣ [tests/CHAOS_RESILIENCE_README.md](tests/CHAOS_RESILIENCE_README.md)
**Tipo:** 🚀 Quick Start Guide
**Comprimento:** ~300 linhas
**Público:** Desenvolvedores, QA

**Contém:**
- ✅ Resumo em 3 linhas
- ✅ 4 maneiras diferentes de rodar testes
- ✅ Exemplo completo de saída
- ✅ Descrição de cada teste
- ✅ Tabela de testes disponíveis
- ✅ O que pode quebrar
- ✅ Interpretação de resultados (✅/⚠️/❌)
- ✅ Troubleshooting prático
- ✅ Ficheiros relacionados
- ✅ Próximos passos

**Usar quando:** Quer rodar testes ou troubleshooting

---

### 3️⃣ [CHAOS_IMPLEMENTATION_SUMMARY.md](CHAOS_IMPLEMENTATION_SUMMARY.md)
**Tipo:** 🔧 Sumário Técnico
**Comprimento:** ~300 linhas
**Público:** Arquitetos, tech leads

**Contém:**
- ✅ O que foi feito (4 seções principais)
- ✅ Arquitetura técnica (diagramas)
- ✅ Fluxo de execução detalhado
- ✅ Validações científicas
- ✅ Métricas esperadas
- ✅ Ficheiros modificados (tabela)
- ✅ Impacto em outros testes
- ✅ Como usar (5 variações)
- ✅ Troubleshooting técnico
- ✅ Ficheiros relacionados
- ✅ Próximas ações

**Usar quando:** Quer entender implementação técnica ou planear próximas fases

---

### 4️⃣ [CHAOS_IMPLEMENTATION_COMPLETE.md](CHAOS_IMPLEMENTATION_COMPLETE.md)
**Tipo:** 📋 Resumo Completo
**Comprimento:** ~400 linhas
**Público:** Todos (sumário de tudo)

**Contém:**
- ✅ Tudo que foi entregue
- ✅ Resposta à pergunta científica
- ✅ Métricas implementadas
- ✅ Como usar (3 níveis)
- ✅ Checklist de completude
- ✅ Próximos passos (4 horizontes temporais)
- ✅ Ficheiros entregues
- ✅ Impacto científico (antes/depois)
- ✅ Localização de tudo
- ✅ Conclusão final

**Usar quando:** Precisa ver overview completo, apresentar para leadership

---

### 5️⃣ [tests/test_chaos_resilience.py](tests/test_chaos_resilience.py)
**Tipo:** 💻 Código de Teste
**Comprimento:** ~250 linhas
**Público:** Desenvolvedores

**Contém:**
- ✅ 4 classes de teste
- ✅ 4 testes funcionais
- ✅ Base class com helpers
- ✅ Fixtures de configuração
- ✅ Documentação em cada teste
- ✅ Múltiplas validações

**Classes:**
1. `TestPhiResilienceBase` - Base class com helpers
2. `TestPhiResilienceServerCrash` - Testes principais (2 testes)
3. `TestServerRecoveryAutomation` - Recovery tests (1 teste)
4. `TestPhiMetricsConsistency` - Baseline tests (1 teste)

**Usar quando:** Quer estudar padrão de teste ou adicionar novos testes

---

### 6️⃣ [conftest.py](conftest.py) (MODIFICADO)
**Tipo:** ⚙️ Configuração pytest
**Linhas modificadas:** 228 → 324 (+96 linhas)
**Público:** Arquitetos, tech leads

**Mudanças principais:**
- Linha ~43: Registro de `@pytest.mark.chaos`
- Linhas 198-220: Classe `ResilienceTracker`
- Linha 224: Instância global `resilience_tracker`
- Linhas 227-283: Fixture `kill_server()`
- Linhas 286-305: Hook `pytest_sessionfinish()`
- Linhas 170-195: Enhancements para `destroy_server_for_real_tests()`

**Usar quando:** Quer entender configuração de pytest global ou adicionar novos markers

---

## 🔗 MAPA DE RELACIONAMENTOS

```
ENTRADA:
  Lê CHAOS_IMPLEMENTATION_COMPLETE.md (sumário)
          ↓
    Escolhe roteiro acima
          ↓
  ┌─────────────────────────────────────┐
  │ ROTEIRO 1: Entender              │
  │ Lê: Científico + Técnico + Código  │
  ├─────────────────────────────────────┤
  │ docs/CHAOS_ENGINEERING_RESILIENCE   │ ← Teoria
  │ CHAOS_IMPLEMENTATION_SUMMARY        │ ← Arquitetura
  │ tests/test_chaos_resilience.py      │ ← Implementação
  │ conftest.py (linhas 224-305)        │ ← Config
  └─────────────────────────────────────┘
          ↓
  ┌─────────────────────────────────────┐
  │ ROTEIRO 2: Rodar                  │
  │ Lê quick start + executa             │
  ├─────────────────────────────────────┤
  │ tests/CHAOS_RESILIENCE_README       │ ← Como rodar
  │ ./run_tests_with_server.sh gpu      │ ← Executar
  │ Ver: "RELATÓRIO DE RESILIÊNCIA"     │ ← Resultado
  └─────────────────────────────────────┘
          ↓
  ┌─────────────────────────────────────┐
  │ ROTEIRO 3: Verificar              │
  │ Lê implementação em detalhe         │
  ├─────────────────────────────────────┤
  │ CHAOS_IMPLEMENTATION_SUMMARY        │ ← Arquitetura
  │ conftest.py (linhas 40-324)         │ ← Configuração
  │ tests/test_chaos_resilience.py      │ ← Testes
  └─────────────────────────────────────┘
          ↓
  ┌─────────────────────────────────────┐
  │ ROTEIRO 4: Expandir               │
  │ Adiciona novos testes               │
  ├─────────────────────────────────────┤
  │ docs/CHAOS_ENGINEERING_RESILIENCE   │ ← Inspiração
  │ tests/test_chaos_resilience.py      │ ← Padrão
  │ Criar novo test_gpu_resilience()    │ ← Adicionar
  └─────────────────────────────────────┘
```

---

## 📊 MATRIZ DE DECISÃO

**Se você é...**

| Papel | Leia | Use | Saiba |
|------|------|-----|-------|
| **Pesquisador** | Científico + Completo | Documentação | Como Φ é validado |
| **Dev/QA** | Quick Start + Código | Testes | Como rodar |
| **Tech Lead** | Técnico + Sumário | Arquitectura | Impacto + próximos passos |
| **Manager** | Completo | Relatório | Status + timeline |
| **Novo no projeto** | Quick Start + Científico | Tudo | Começar do zero |

---

## 🚀 COMEÇAR AGORA

### Passo 1: Escolha seu roteiro acima

### Passo 2: Abra o primeiro ficheiro

### Passo 3 (opcional): Execute testes

```bash
./run_tests_with_server.sh gpu
```

### Passo 4: Veja o relatório

```
🛡️  RELATÓRIO DE RESILIÊNCIA (CHAOS ENGINEERING)
Total de crashes de servidor: 5
Tempo médio de recovery: 9.45s
...
```

---

## 💡 DICAS

### Para Apresentação
1. Mostre: CHAOS_IMPLEMENTATION_COMPLETE.md
2. Mostre: Relatório de resiliência (após rodar testes)
3. Explicar: Implicação científica

### Para Publicação
1. Use: docs/CHAOS_ENGINEERING_RESILIENCE.md como base
2. Adicione: Gráficos dos resultados
3. Cite: Princípios de Chaos Engineering

### Para Integração em CI/CD
1. Use: `./run_tests_with_server.sh gpu` como comando
2. Parse: "RELATÓRIO DE RESILIÊNCIA" como output
3. Fail se: Recovery > 30s ou crash count > expected

### Para Expansão
1. Copie padrão: TestPhiResilienceServerCrash
2. Mude: método de destruição (ex: kill GPU)
3. Adapte: validações (ex: check GPU memory)

---

## ❓ FAQ RÁPIDO

**P: Por onde começo?**
R: Leia [CHAOS_IMPLEMENTATION_COMPLETE.md](CHAOS_IMPLEMENTATION_COMPLETE.md) (20 min)

**P: Como rodo os testes?**
R: `./run_tests_with_server.sh gpu` (15 min)

**P: O que significa o relatório?**
R: Veja [tests/CHAOS_RESILIENCE_README.md](tests/CHAOS_RESILIENCE_README.md) seção "Interpretando Resultados"

**P: Isto quebra testes existentes?**
R: Não! 100% backward compatible.

**P: Como adiciono novo teste?**
R: Copie padrão em [tests/test_chaos_resilience.py](tests/test_chaos_resilience.py)

**P: Quem fez isto?**
R: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity) - 2 de dezembro de 2025

---

## 📞 SUPORTE

Se tiver dúvidas:

1. **Técnicas** → [tests/CHAOS_RESILIENCE_README.md](tests/CHAOS_RESILIENCE_README.md) - Troubleshooting
2. **Científicas** → [docs/CHAOS_ENGINEERING_RESILIENCE.md](docs/CHAOS_ENGINEERING_RESILIENCE.md) - Interpretação
3. **Implementação** → [CHAOS_IMPLEMENTATION_SUMMARY.md](CHAOS_IMPLEMENTATION_SUMMARY.md) - Arquitetura

---

**Última atualização:** 2 de dezembro de 2025
**Status:** ✅ Tudo pronto
**Próximo passo:** Escolha seu roteiro acima! 🚀
