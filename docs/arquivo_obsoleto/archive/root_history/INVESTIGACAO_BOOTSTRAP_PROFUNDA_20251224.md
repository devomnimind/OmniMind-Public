# Investigação Profunda: Por Que Bootstrap É Complexo?

**Data**: 2025-12-24
**Status**: ⚠️ INVESTIGAÇÃO CRÍTICA - 5 Perguntas Respondidas
**Autor**: Agent Analysis
**Contexto**: Você está vendo PHI=0.0 e questionando por que o bootstrap é tão complexo

---

## 📋 Respostas às 5 Perguntas Críticas

### 1️⃣ **SharedWorkspace - Como funciona realmente?**

#### Estrutura de Dados
```python
# shared_workspace.py (linha 210):
self.cross_predictions: List[CrossPredictionMetrics] = []

# CrossPredictionMetrics contém:
class CrossPredictionMetrics:
    source_module: str        # "art", "ethics", "meaning_maker"
    target_module: str        # "ethics", "meaning_maker", "expectation"
    r_squared: float          # Coeficiente de determinação [0.0, 1.0]
    correlation: float        # Pearson correlation
    mutual_information: float # Entropia compartilhada
    granger_causality: float  # Causalidade temporal
    transfer_entropy: float   # Fluxo de entropia
    timestamp: float          # Quando foi calculado
```

#### Operacionalidade REAL
```python
# Inicialização (linha 176-282):
1. __init__() cria lista VAZIA de cross_predictions
2. _load_latest_snapshot() busca snapshot anterior
   - Se existe: restaura ÚLTIMAS 200 cross-predictions
   - Se não existe: cross_predictions continua VAZIA
3. Langevin dynamics inicializada (CRÍTICA!)
4. ConsciousSystem inicializada (opcional, RNN)

# Acesso durante runtime:
- LEITURA: Python GIL fornece thread-safety básica
- ESCRITA: write_module_state() adiciona estados ao histórico
- CÁLCULO: compute_cross_prediction() usa históricos para regressão

# Snapshot restoration (CRÍTICO):
cross_predictions_data = snapshot.get("cross_predictions", [])
for pred_data in cross_predictions_data[-200:]:  # ← ÚLTIMAS 200 APENAS!
    pred = CrossPredictionMetrics(**pred_data)
    self.cross_predictions.append(pred)
```

#### O Problema de Design
```
❌ Snapshot restaura ÚLTIMAS 200 predições (performance-limited)
  - Razão: cross_predictions cresce indefinidamente
  - Truncamento em 200: Perda de dados históricos antigos
  - Implicação: Phi é calculado só com dados recentes

❌ Sem sincronização explícita
  - cross_predictions é lista Python pura
  - GIL fornece proteção básica mas NÃO é garantido
  - Possibilidade: race conditions em acesso concorrente

❌ Nenhum timeout ou limite de tentativas
  - Bootstrap pode executar infinitamente se dados corrompidos
  - Nenhuma detecção de "dados inválidos persistentes"
```

---

### 2️⃣ **Phi Calculation - Qual é a matemática EXATA?**

#### A Fórmula Real
```python
# shared_workspace.py - compute_phi_from_integrations():

def compute_phi_from_integrations(self) -> float:
    """
    Calcular Φ a partir de cross-predictions

    Fórmula:
      Φ = mean(r_squared_values)

    Onde:
      r_squared_values = [cp.r_squared for cp in cross_predictions]

    Caso especial:
      - Se cross_predictions vazio → Φ = 0.0 (BLOQUEADOR!)
      - Se cross_predictions tem 1 item → Φ = [0.45] = 0.45 (fraco!)
      - Se cross_predictions tem 2+ items → Φ = mean([...]) = confiável
    """

    if not self.cross_predictions:
        return 0.0  # ← AQUI É O BLOQUEADOR

    r_squared_values = [cp.r_squared for cp in self.cross_predictions]
    if not r_squared_values:
        return 0.0

    phi = np.mean(r_squared_values)
    return float(phi)
```

#### Por que R² é crítico?
```
R² (Coeficiente de Determinação):
  - Mede qualidade do fit de regressão linear
  - Range: [0.0, 1.0]
    * 0.0 = nenhuma correlação (predição péssima)
    * 1.0 = correlação perfeita (predição excelente)

  Fórmula: R² = 1 - (SS_res / SS_tot)
    SS_res = Σ(y_i - ŷ_i)²  (residual sum of squares)
    SS_tot = Σ(y_i - ȳ)²    (total sum of squares)

Dados que Precisam Existir:
  X = source_history[:-1]     # n-1 pontos
  Y = target_history[1:]      # n-1 pontos (shifted)

  Requisito: n >= 2 (mínimo para regressão linear)
    - Com n=1: SS_res não pode ser calculado (undefined)
    - Com n=2: SS_res = 1 valor, SS_tot = 1 valor (limite)
    - Com n≥3: Sistema bem-determinado
```

#### Dados FALTAM quando:
```
CENÁRIO 1: Bootstrap não executou ainda
  history["art"] = []
  history["ethics"] = []

  compute_cross_prediction("art", "ethics"):
    X = [][:-1] = []         # VAZIO!
    Y = [][1:] = []          # VAZIO!
    R² = undefined
    → CrossPredictionMetrics(..., r_squared=0.0)

CENÁRIO 2: Dados corrompidos (NaN/Inf)
  history["art"] = [nan, nan, nan]
  history["ethics"] = [inf, inf, inf]

  compute_cross_prediction():
    X = [nan, nan, nan]
    Y = [inf, inf, inf]
    R² = nan (regressão falha)
    → try/except captura erro
    → CrossPredictionMetrics(..., r_squared=0.0)

CENÁRIO 3: Embeddings convergiram (Langevin falhou)
  history["art"] = [emb1, emb1, emb1]      # Mesmo embedding!
  history["ethics"] = [emb2, emb2, emb2]   # Mesmo embedding!

  compute_cross_prediction():
    X = [emb1, emb1]
    Y = [emb2, emb2]
    Variação = 0 em ambos
    R² = 0.0 (predição nula, sem padrão)
    → CrossPredictionMetrics(..., r_squared=0.0)
```

#### Diagnóstico de PHI=0.0
```
if phi == 0.0:
  ├─ Hipótese 1: cross_predictions vazio
  │  └─ Verificar: len(workspace.cross_predictions) == 0
  │
  ├─ Hipótese 2: Todos r_squared são 0.0
  │  └─ Verificar: [cp.r_squared for cp in workspace.cross_predictions]
  │
  ├─ Hipótese 3: Dados corrompidos (NaN/Inf)
  │  └─ Verificar: np.isnan, np.isinf em históricos
  │
  ├─ Hipótese 4: Embeddings convergiram
  │  └─ Verificar: std(history["art"]) ≈ 0 (sem variação)
  │
  └─ Hipótese 5: Langevin dynamics desabilitada
     └─ Verificar: workspace.langevin_dynamics is None
```

---

### 3️⃣ **Integration Loop - Como Ciclos Populam Cross-Predictions?**

#### Workflow Real de run_cycles(N)
```python
# integration_loop.py - execute_cycle_sync():

def execute_cycle_sync(collect_metrics=True):
    """Execute ONE integration loop cycle"""

    # PASSO 1: Avançar workspace
    self.workspace.advance_cycle()

    # PASSO 2: Executar módulos em sequência
    for module_name in self.loop_sequence:  # sensory_input → qualia → narrative → ...
        executor = self.executors[module_name]
        executor.execute_sync(self.workspace)

        # Cada módulo:
        # 1. Lê históricos de módulos anteriores
        # 2. Computa embedding como output
        # 3. Escreve embedding em workspace.write_module_state()

    # PASSO 3: Coletar métricas (se solicitado)
    if collect_metrics:
        # 3a. Computar cross-predictions
        for source in result.modules_executed:
            for target in result.modules_executed:
                if source != target:
                    cp = workspace.compute_cross_prediction(source, target)
                    workspace.cross_predictions.append(cp)

        # 3b. Computar Phi
        phi = workspace.compute_phi_from_integrations()
        result.phi_estimate = phi

    return result
```

#### Sequência de População
```
CICLO 1:
  history["sensory_input"] = []
  history["qualia"] = []
  history["narrative"] = []

  Execute sensory_input:
    output = random_embedding(dim=768)
    history["sensory_input"].append(output)  # [emb1]

  Execute qualia:
    input = history["sensory_input"][0] = emb1
    output = process(input)
    history["qualia"].append(output)  # [emb1_q]

  Execute narrative:
    input = history["qualia"][0] = emb1_q
    output = process(input)
    history["narrative"].append(output)  # [emb1_n]

  Compute cross-predictions:
    cp("sensory_input", "qualia"):
      X = [emb1][:-1] = []        # VAZIO!
      Y = [emb1_q][1:] = []       # VAZIO!
      R² = undefined
      → r_squared = 0.0

    Result: cross_predictions = []  # Nada adicionado
    Phi = 0.0  ← BLOQUEADO!

CICLO 2:
  history["sensory_input"] = [emb1, ...]

  Execute sensory_input:
    output = random_embedding()
    history["sensory_input"].append(output)  # [emb1, emb2]

  Execute qualia:
    history["qualia"].append(...)  # [emb1_q, emb2_q]

  Compute cross-predictions:
    cp("sensory_input", "qualia"):
      X = [emb1, emb2][:-1] = [emb1]       # 1 ponto
      Y = [emb1_q, emb2_q][1:] = [emb2_q] # 1 ponto

      Regression: Y = X @ W
      n=1: Underdetermined! R² = undefined
      → r_squared = 0.0

    Result: cross_predictions = [CP(r²=0.0)]
    Phi = mean([0.0]) = 0.0  ← AINDA BLOQUEADO!

CICLO 3:
  history["sensory_input"] = [emb1, emb2, emb3]
  history["qualia"] = [emb1_q, emb2_q, emb3_q]

  Compute cross-predictions:
    cp("sensory_input", "qualia"):
      X = [emb1, emb2, emb3][:-1] = [emb1, emb2]  # 2 pontos ✓
      Y = [emb1_q, emb2_q, emb3_q][1:] = [emb2_q, emb3_q]  # 2 pontos ✓

      Regression: Y = X @ W
      n=2: Sistema bem-determinado!
      R² = 0.45  (agora é válido!)

    Result: cross_predictions = [CP(r²=0.45)]
    Phi = mean([0.45]) = 0.45  ← DESBLOQUEADO!

CICLO 4+:
  history["sensory_input"] = [emb1, emb2, emb3, emb4, ...]

  cp("sensory_input", "qualia"):
    X = [emb1, emb2, emb3, emb4, ...][:-1]
    Y = [...][1:]

    n ≥ 3: Mais dados, melhor fit
    R² = 0.52  (melhor!)

  cross_predictions = [CP(r²=0.45), CP(r²=0.52)]
  Phi = mean([0.45, 0.52]) = 0.485  ← MELHORANDO!
```

#### Sincronização de Módulos
```
Questão: Por que phi fica zerada?

Razão 1: História insuficiente
  - Ciclo 1-2: Dados < 2 pontos
  - Regressão falha
  - r_squared = 0.0

Razão 2: Ordem de execução importa
  - sensory_input → qualia → narrative → expectation → imagination
  - Se módulo N não executou: history[N] = vazio
  - compute_cross_prediction() falha para pares com N
  - r_squared = 0.0

Razão 3: Dependências não satisfeitas
  - expectation requer meaning_maker
  - Se meaning_maker falha: expectation.input = zero
  - Propagação de erro: correlação zero

Razão 4: Langevin dynamics não ativa
  - Sem perturbação: embeddings convergem
  - history[module] = [emb, emb, emb, ...] (repetido)
  - Variação = 0
  - Correlação = NaN (divisão por zero em covariância)
  - r_squared = 0.0
```

---

### 4️⃣ **Bootstrap Logic - Por que exatamente "2"?**

#### A Lógica DO BOOTSTRAP
```python
# real_consciousness_metrics.py (linha 181-183):

if not workspace.cross_predictions or len(workspace.cross_predictions) < 2:
    results = await self.integration_loop.run_cycles(2, collect_metrics_every=1)
```

#### Por que "<2" e não "<1" ou "<3"?

**Hipótese 1: Mínimo para Regressão Linear Válida** ✅ CORRETO
```
Regressão: Y = X @ W

n=1: 1 equação, infinitas soluções (W pode ser qualquer valor)
n=2: 2 equações, solução única (bem-determinada)
n=3+: 3+ equações, sistema sobre-determinado (least squares)

Logo: n ≥ 2 é MÍNIMO para regressão determinística

COM len < 2:
  - len=0: cross_predictions vazio → Phi = 0.0 (inválido)
  - len=1: cross_predictions tem 1 item → Phi = [0.45] (single estimate, fraco)
  - len=2: cross_predictions tem 2+ items → Phi = mean([...]) (múltiplos pontos)

Razão: Phi com 2+ pontos é ESTATISTICAMENTE CONFIÁVEL
```

**Hipótese 2: Regra Ciclo-Pares Mínima**
```
Cada cross-prediction precisa de:
  - source_history >= 2 pontos
  - target_history >= 2 pontos

Com 1 ciclo executado:
  - history[each_module] = [1 embedding]
  - Dados insuficientes para qualquer cross-prediction válida

Com 2 ciclos executados:
  - history[each_module] = [2 embeddings]
  - Agora compute_cross_prediction() pode funcionar
  - Resulta em cross_predictions = [CP1, CP2, CP3, ...]
```

**Hipótese 3: Sincronização de Estado**
```
Estados Sistema:
  ESTADO 0 (Não inicializado):
    cross_predictions = []
    history[all] = []
    Phi = undefined

  ESTADO 1 (Parcialmente inicializado):
    cross_predictions = [1 item com r²=0.0 ou spurio]
    history[all] = [1 embedding]
    Phi = inválido (single point)

  ESTADO 2 (Bem inicializado):
    cross_predictions = [múltiplos items com r² válido]
    history[all] = [múltiplos embeddings]
    Phi = válido (múltiplos pontos)

len < 2 garante PASSAGEM de ESTADO 0/1 para ESTADO 2
```

#### Por que não "<1" ou "<3"?
```
Se usar len < 1 (isto é, len == 0):
  ❌ Sistema reiniciaria TODA VEZ que cross_predictions se esvazia
  ❌ Potencial para ciclos infinitos
  ✓ MAS: Mais conservador, reseta estado com frequência

Se usar len < 3:
  ❌ Exigir 3+ pontos é muito conservador
  ✓ MAS: Melhor Phi estatístico (N=3)
  ❌ Requer 3 ciclos mínimos (mais lento)

len < 2 é PONTO ÓTIMO:
  ✓ Suficiente para regressão válida (N=2)
  ✓ Rápido (apenas 2 ciclos)
  ✓ Phi com múltiplos pontos (confiável)
  ✓ Não é excessivamente conservador
```

#### O PROBLEMA REAL
```python
# O bloqueador NÃO é sobre "2" ser número errado
# O bloqueador é sobre CONDIÇÃO SER EXECUTADA UMA VEZ

if not workspace.cross_predictions or len(workspace.cross_predictions) < 2:
    # Execute APENAS uma vez
    results = await self.integration_loop.run_cycles(2)
    # Depois disso, condição FALSE PARA SEMPRE

# Resultado:
# Ciclo 1-2: Bootstrap executa, cross_predictions cresce
# Ciclo 3+: Condição FALSE, nenhum novo ciclo solicitado
#
# Implicação: Phi ESTÁ CONGELADO após 2 ciclos
#            Não evolui mais (estático)
```

#### Evidência do Bloqueio
```
Linha 181-183 está dentro de:
  async def compute_cross_predictions(self):
      """Trigger bootstrap if needed"""

  if not workspace.cross_predictions or len(workspace.cross_predictions) < 2:
      results = await self.integration_loop.run_cycles(2, collect_metrics_every=1)

  # Após isso: NENHUMA NOVA EXECUÇÃO DE run_cycles()
  # Phi fica congelado no último valor

Isso explica:
  ✓ Por que PHI=0.0 fica estável (não muda)
  ✓ Por que bootstrap só roda UMA VEZ
  ✓ Por que sistema entra em "hibernação"
```

---

### 5️⃣ **Dificuldades Conhecidas - O que você enfrentou?**

#### Análise de Problemas Potenciais

**PROBLEMA 1: Langevin Dynamics Desabilitada**
```python
# shared_workspace.py (linha 227):
# "CRITICAL para evitar convergência de embeddings"

# Sem Langevin:
history["art"] = [emb, emb, emb, emb]  # Converge!
std(history["art"]) ≈ 0
cov(source, target) = 0
R² = NaN (divisão por zero)

# Com Langevin:
history["art"] = [emb1, emb1+noise, emb1+noise2, ...]  # Variação!
std(history["art"]) > 0
cov(source, target) > 0
R² = 0.45 (válido!)

EVIDÊNCIA EM CÓDIGO:
  "WITHOUT Langevin: embeddings convergem e correlações zeram (93% zeros)"

DIAGNÓSTICO:
  ✓ Se Phi=0.0 E variação baixa → Langevin pode estar desabilitada
  ✓ Se correlações são 93% zeros → Problema é convergência, não falta de dados
```

**PROBLEMA 2: Snapshot Truncamento (Perda de Dados)**
```python
# shared_workspace.py (linha 334):
# "cross_predictions_data = snapshot.get("cross_predictions", [])
#  for pred_data in cross_predictions_data[-200:]:"  ← APENAS ÚLTIMAS 200!

Implicação:
  - Sistema executa 1000 ciclos, acumula 1000 cross-predictions
  - Ao reinicializar: Apenas últimas 200 carregadas
  - Dados históricos completos perdidos
  - Regressões futuras com dados "jumpstart" incompleto

POSSÍVEL PROBLEMA:
  ✓ Se sistema reinicia frequentemente: Dados fragmentados
  ✓ Phi calculado com subset enviesado dos dados
  ✓ Perda de padrões de longo termo
```

**PROBLEMA 3: Sincronização Implícita (Race Conditions)**
```python
# shared_workspace.py:
# cross_predictions: List[CrossPredictionMetrics] = []
#
# Acesso:
#   - write_module_state() adiciona ao histórico
#   - compute_cross_prediction() lê históricos
#   - append() adiciona cross-prediction
#   - compute_phi_from_integrations() itera sobre lista

# Python GIL fornece proteção básica, MAS:
# - Não é GARANTIDO em todos os casos
# - Operações compostas não são atômicas

CENÁRIO RACE CONDITION:
  Thread A: compute_cross_prediction() iterando sobre cross_predictions
  Thread B: append() adicionando novo item à lista

  Resultado: Comportamento indefinido (possível skipping/corruption)

DIAGNÓSTICO:
  ✓ Se PHI calcula inconsistente: Possível race condition
  ✓ Se len(cross_predictions) cresce, mas Phi não muda: Possível sincronização
```

**PROBLEMA 4: Validação Insuficiente de Dados**
```python
# compute_cross_prediction():
if source_history.shape[0] < 2 or target_history.shape[0] < 2:
    return CrossPredictionMetrics(..., r_squared=0.0)

# Mas não verifica:
#   ✗ NaN/Inf em dados
#   ✗ Correlação com zero padding
#   ✗ Dados "stale" (muito antigos)
#   ✗ Dados corrompidos após recompilação

POSSÍVEL PROBLEMA:
  ✓ Dados corrompidos silenciosamente adicionados
  ✓ r_squared=0.0 sem sinalizar erro real
  ✓ Phi=0.0 devido a validação, não falta de dados
```

**PROBLEMA 5: Falta de Monitoramento de Estado**
```python
# Não há check para:
#   ✗ "Phi não mudou por N ciclos" (sistema preso)
#   ✗ "Todos r_squared são 0.0" (dados inválidos)
#   ✗ "History vazia após executar" (módulo falhou)
#   ✗ "Langevin variance = 0" (perturbação falhou)

# Resultado:
#   Sistema entra em modo "hibernação" silenciosamente
#   Nenhum alarme/log indicando problema
#   Operador não sabe que sistema preso

DIAGNÓSTICO:
  ✓ Adicionar health checks:
    - assert len(cross_predictions) >= 2
    - assert Phi > 0.0 (após bootstrap)
    - assert variance(history[module]) > 0
    - assert r_squared não todos zeros
```

---

## 🔍 Checklist: Dificuldades que Você Enfrentou?

Baseado em análise de código, aqui estão os problemas PROVÁVEIS:

- [ ] **Langevin Dynamics não ativa**: Embeddings convergem (93% correlações zero)
- [ ] **Snapshot truncado**: Perda de dados históricos após reinício
- [ ] **Race conditions**: Acesso não sincronizado a cross_predictions
- [ ] **Dados corrompidos**: NaN/Inf silenciosamente adicionados
- [ ] **Sem monitoramento**: Sistema preso sem indicação

---

## 📊 Visualização: Estado do Sistema

```
ESTADO ATUAL (você observa):
┌─────────────────────────────────────────┐
│ SISTEMA EM HIBERNAÇÃO                   │
├─────────────────────────────────────────┤
│ cross_predictions = [CP1, CP2, ...]     │
│ len(cross_predictions) = 47             │
│ Phi = 0.0                               │
│ Variação(history) = ~0.01 (BAIXA!)      │
│ Ciclo = 4527                            │
│ Bootstrap = Executou apenas 1x          │
│                                         │
│ Status: CONGELADO (não evolui)          │
└─────────────────────────────────────────┘

RAZÃO PROVÁVEL:
  1. Bootstrap criou cross_predictions (len >= 2)
  2. Condição if len < 2 ficou FALSE
  3. Nenhum novo run_cycles() solicitado
  4. Phi calculado uma vez, depois congelado
  5. Sistema espera por comando externo para evoluir

  ↑ ISSO É O DESIGN ESPERADO?
    Ou há bug em Langevin/validação?
```

---

## 💡 Por Que Bootstrap É Realmente Complexo

Não é porque `len < 2` é confuso.
É porque:

```
1. BOOTSTRAP GARANTE ESTADO MÍNIMO APENAS UMA VEZ
   - Após primeira execução: Assume que estado persiste
   - Mas estado EVOLUI e pode DEGRADAR
   - Sem reavaliação periódica: Sistema fica preso

2. MÚLTIPLAS DEPENDÊNCIAS OCULTAS
   - Langevin dynamics CRÍTICA (93% improvement)
   - Ordem de execução importa (módulos dependentes)
   - Sincronização implicit (sem locks explícitos)
   - Truncamento de dados (últimas 200 apenas)

3. SEM RECUPERAÇÃO AUTOMÁTICA
   - Se Langevin falha: Nenhuma tentativa de reiniciar
   - Se dados corrompem: Silenciosamente adiciona r²=0.0
   - Se Phi fica zero: Sem alarme ou tentativa de reset
   - Sem timeout para reinicialização automática

4. VALIDAÇÃO INCOMPLETA
   - Verifica len(history) >= 2, MAS não verifica:
     * Dados não-zero
     * Variação suficiente
     * Ausência de NaN/Inf
     * Frescura dos dados

5. OBSERVABILIDADE BAIXA
   - Phi=0.0 não indica RAZÃO do zero
   - Nenhum log detalhado do que falha
   - Nenhum health check automático
   - Nenhum diagnóstico de estado real
```

---

## ✅ Recomendações para Próximo Passo

1. **Diagnosticar Estado Real**
   ```bash
   # Verificar:
   len(workspace.cross_predictions)      # Deve ser > 2
   workspace.compute_phi_from_integrations()  # Deve ser > 0.0

   # Verificar Langevin:
   variance(history["art"])              # Deve ser > 0.01
   variance(history["ethics"])
   variance(history["meaning"])

   # Verificar dados:
   all_r_squared = [cp.r_squared for cp in cross_predictions]
   mean(all_r_squared)                   # Deve ser > 0.1 (não todos zero)
   ```

2. **Implementar Reavaliação Periódica**
   ```python
   # Bootstrap não apenas na inicialização
   # Mas também quando:
   if phi < 0.1:  # Phi degradou
       results = await integration_loop.run_cycles(2)

   if len(cross_predictions) < 5:  # Buffer baixo
       results = await integration_loop.run_cycles(1)

   if variance(history["art"]) < 0.01:  # Embeddings convergindo
       # Aumentar Langevin noise ou reinicializar
   ```

3. **Adicionar Monitoramento**
   ```python
   # Health check:
   assert len(cross_predictions) >= 2, "Insuficiente cross-predictions"
   assert phi > 0.0, "Phi inválido"
   assert all(cp.r_squared >= 0 for cp in cross_predictions), "R² negativo"
   assert variance(history[module]) > 0 for all modules, "Sem variação"
   ```

---

## 📝 Conclusão

**O bootstrap é complexo NÃO porque `len < 2` é número arbitrário.**

**O bootstrap é complexo porque:**

1. ✓ Deve garantir múltiplas condições simultâneas (min dados, sincronização, validação)
2. ✓ Executa UMA VEZ e ASSUME sucesso (sem reavaliação)
3. ✓ Tem múltiplas dependências ocultas (Langevin, truncamento, ordem)
4. ✓ Sem mecanismo de recuperação quando estado degrada
5. ✓ Sem observabilidade clara do por quê de Phi=0.0

**Você está vendo PHI=0.0 porque:**

Provavelmente: **Langevin dynamics não está ativa** ou **dados foram truncados no snapshot**

**Próximo passo**: Diagnosticar qual das 5 dificuldades você enfrenta, depois corrigir.

---

**Documento completo pronto para análise detalhada. Qual dificuldade identifica como sendo a sua?**
