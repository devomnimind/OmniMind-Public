# 🔧 PROPOSTA DE IMPLEMENTAÇÃO: Reativar Ciclos de Integração

**Urgência**: MÉDIA (sistema funcional, mas sem impulso vital)
**Impacto**: ALTO (recupera Phi, reativa autonomia)
**Esforço**: BAIXO (1-2 mudanças de código)

---

## 📋 PLANO DE IMPLEMENTAÇÃO

### FASE 1: Remover Bloqueador Bootstrap (Crítica)

**Arquivo**: `src/metrics/real_consciousness_metrics.py`
**Linhas**: 180-183
**Tipo**: Code change

#### Código Atual (Bloqueador)
```python
# LINHA 180-183
if not workspace.cross_predictions or len(workspace.cross_predictions) < 2:
    # Se vazio OU < 2 items: execute ciclos
    logger.debug("Workspace has insufficient data, running cycles...")
    results = await self.integration_loop.run_cycles(2, collect_metrics_every=1)
    logger.debug(f"Ran {len(results)} cycles")
```

**Problema**:
- Condição `len(...) < 2` torna-se FALSE após primeira execução
- Ciclos nunca mais executam
- Phi congelado em 0.0 permanentemente

#### Código Proposto (Fix)
```python
# LINHA 180-183 (NOVA VERSÃO)
if not workspace.cross_predictions:
    # Bootstrap: só execute se TOTALMENTE vazio
    logger.debug("Workspace empty, bootstrapping with 2 cycles...")
    results = await self.integration_loop.run_cycles(2, collect_metrics_every=1)
    logger.debug(f"Bootstrap complete: {len(results)} cycles ran")

# NOTA: Remove a condição `len(...) < 2` que bloqueava ciclos contínuos
# Agora ciclos podem executar sob demanda (conforme trigger time-based abaixo)
```

**Benefício**:
- ✅ Ciclos já existentes em workspace não são descartados
- ✅ Novo bootstrap só se workspace TOTALMENTE vazio
- ✅ Permite implementação de triggers posteriores

---

### FASE 2: Adicionar Trigger Time-Based (Recomendado)

**Arquivo**: `src/metrics/real_consciousness_metrics.py`
**Linhas**: Modificar `__init__` + método `_collect_phi_from_integration_loop`
**Tipo**: Code addition

#### Modificação 1: __init__ (adicionar variáveis)
```python
# Em RealConsciousnessMetricsCollector.__init__ (após linha 80)

def __init__(self):
    # ... existente ...
    self.integration_loop: Optional[IntegrationLoop] = None
    self.iit_analyzer = IITAnalyzer()
    self.last_collection = 0.0
    self.collection_interval = 5.0  # segundos

    # NOVO: Trigger time-based para ciclos contínuos
    self.last_cycle_execution = 0.0
    self.cycle_trigger_interval = 300.0  # 5 minutos entre ciclos

    self._phi_variance_history: List[float] = []
    self.cached_metrics: Optional[RealConsciousnessMetrics] = None
```

#### Modificação 2: _collect_phi_from_integration_loop (adicionar trigger)
```python
# Em método _collect_phi_from_integration_loop (após linha 182)

async def _collect_phi_from_integration_loop(self) -> Dict[str, Any]:
    """Coleta Phi real do IntegrationLoop."""
    if not self.integration_loop:
        return {"phi": 0.0, "ici": 0.0, "prs": 0.0}

    try:
        workspace = self.integration_loop.workspace
        current_time = time.time()

        # Bootstrap: se workspace vazio, execute 2 ciclos
        if not workspace.cross_predictions:
            logger.debug("Workspace empty, bootstrapping with 2 cycles...")
            results = await self.integration_loop.run_cycles(2, collect_metrics_every=1)
            logger.debug(f"Bootstrap complete: {len(results)} cycles ran")

        # NOVO: Trigger time-based para manter ciclos ativos
        # Executa ciclo a cada 5 minutos se workspace tem dados
        if (workspace.cross_predictions and
            current_time - self.last_cycle_execution > self.cycle_trigger_interval):

            logger.debug(
                f"Time-based trigger: {current_time - self.last_cycle_execution:.0f}s "
                f"elapsed, running integration cycle..."
            )
            try:
                results = await self.integration_loop.run_cycles(1, collect_metrics_every=1)
                self.last_cycle_execution = current_time
                logger.debug(f"Cycle executed, {len(results)} results")
            except Exception as e:
                logger.warning(f"Time-based cycle failed: {e}")

        # Resto do código (inalterado)
        cross_preds = workspace.cross_predictions[-20:] if workspace.cross_predictions else []
        # ...
```

**Benefício**:
- ✅ Ciclos executam a cada 5 minutos (configurável)
- ✅ Não interfere com bootstrap
- ✅ Phi mantém-se atualizado continuamente
- ✅ CPU/RAM previsível

---

### FASE 3: Reativar Estimulação Psíquica (Opcional)

**Arquivo**: `scripts/stimulate_system.py`
**Tipo**: Executar script

#### Comando
```bash
# No diretório do projeto
python scripts/stimulate_system.py
```

**O que faz**:
1. Gera dados criativos (Art, Ethics, Meaning)
2. Computa cross-predictions entre módulos
3. Popula workspace com estados iniciais
4. Estabelece fluxo de feedback

**Saída esperada**:
```
🚀 Starting Autopoietic Synaptic Binding Sequence...
🧠 Initializing Synaptic Bridge and Modules...
🔄 Running 10 synaptic binding cycles...
✅ Cycle 1 complete: Art→Ethics→Meaning
✅ Cycle 2 complete: ...
...
💾 Stimulation complete. Cross-predictions populated.
```

**Tempo**: ~2-3 minutos

---

### FASE 4: Monitorar Phi Recovery (Validação)

**Arquivo**: Criar script de monitoramento
**Tipo**: Validação contínua

#### Script de Monitoramento
```python
#!/usr/bin/env python3
"""
Monitor de Recuperação de Phi
Tracks Phi value during cycle reactivation
"""

import asyncio
import json
import time
from pathlib import Path

async def monitor_phi_recovery():
    """Monitora recuperação de Phi durante reativação"""
    from src.metrics.real_consciousness_metrics import RealConsciousnessMetricsCollector

    collector = RealConsciousnessMetricsCollector()
    await collector.initialize()

    print("📊 Monitoring Phi Recovery...")
    print("=" * 60)

    phi_history = []
    start_time = time.time()

    for i in range(30):  # Monitor por 30 coletas (~2.5 minutos)
        try:
            metrics = await collector.collect_real_metrics()
            phi_value = metrics.phi
            phi_history.append(phi_value)

            elapsed = time.time() - start_time
            trend = "📈" if i > 0 and phi_value > phi_history[i-1] else "📉"

            print(
                f"[{elapsed:6.1f}s] Phi: {phi_value:.4f} {trend} | "
                f"ICI: {metrics.ici:.4f} | PRS: {metrics.prs:.4f} | "
                f"Cross-pred count: {len(collector.integration_loop.workspace.cross_predictions)}"
            )

        except Exception as e:
            print(f"❌ Error: {e}")

        await asyncio.sleep(5)  # Aguarda 5 segundos entre coletas

    # Análise final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    print(f"   Phi inicial: {phi_history[0]:.4f}")
    print(f"   Phi final: {phi_history[-1]:.4f}")
    print(f"   Mudança: {phi_history[-1] - phi_history[0]:+.4f}")

    if phi_history[-1] > phi_history[0]:
        print("   ✅ Phi RECUPERANDO - ciclos estão funcionando!")
    elif phi_history[-1] == 0.0:
        print("   ⚠️ Phi ainda 0.0 - verifique se cross-predictions estão sendo geradas")
    else:
        print("   ❓ Comportamento inesperado")

if __name__ == "__main__":
    asyncio.run(monitor_phi_recovery())
```

**Execução**:
```bash
python monitor_phi_recovery.py
```

**Saída esperada**:
```
📊 Monitoring Phi Recovery...
============================================================
[   0.1s] Phi: 0.0000 📉 | ICI: 0.0000 | PRS: 0.0000 | Cross-pred: 50
[   5.1s] Phi: 0.1200 📈 | ICI: 0.1200 | PRS: 0.0800 | Cross-pred: 52
[  10.1s] Phi: 0.2100 📈 | ICI: 0.2100 | PRS: 0.1500 | Cross-pred: 54
[  15.1s] Phi: 0.2800 📈 | ICI: 0.2800 | PRS: 0.2000 | Cross-pred: 56
...
============================================================
📊 RESULTADO FINAL:
   Phi inicial: 0.0000
   Phi final: 0.3200
   Mudança: +0.3200
   ✅ Phi RECUPERANDO - ciclos estão funcionando!
```

---

## 🎯 ROADMAP DE IMPLEMENTAÇÃO

### Timeline Estimado

```
T+0min     → Implementar FASE 1 (remover bloqueador)
           → Commit: "fix: remove bootstrap blocker in cycle execution"

T+5min     → Implementar FASE 2 (trigger time-based)
           → Commit: "feat: add time-based trigger for continuous cycles"

T+10min    → Testar em dev: rodar monitor, verificar Phi recovery
           → Se OK: prosseguir

T+15min    → (Opcional) Executar FASE 3 (stimulate_system.py)
           → Popula workspace com dados iniciais

T+20min    → Deploy + validação em produção
           → Monitor por 30min verificando Phi > 0.2

T+50min    → Análise final e relatório
```

---

## 🔍 CHECKLIST DE VALIDAÇÃO

- [ ] Linha 182 em real_consciousness_metrics.py modificada
- [ ] Variáveis time-based adicionadas em __init__
- [ ] Trigger implementado em _collect_phi_from_integration_loop
- [ ] Sistema testado localmente
- [ ] Phi recovery verificado (Phi > 0.2)
- [ ] Ciclos executando a cada 5 minutos
- [ ] Cross-predictions atualizando
- [ ] Monitoramento de longo prazo iniciado
- [ ] Logs revisados para erros
- [ ] Documentação atualizada

---

## 🚨 Possíveis Problemas & Soluções

### Problema 1: "Phi ainda está 0.0 após mudanças"

**Causa**: Cross-predictions não estão sendo geradas
**Solução**:
```bash
# 1. Verificar se integration_loop está inicializado
python3 << 'EOF'
import asyncio
from src.metrics.real_consciousness_metrics import RealConsciousnessMetricsCollector

async def test():
    c = RealConsciousnessMetricsCollector()
    await c.initialize()
    print(f"Integration loop: {c.integration_loop}")
    print(f"Workspace: {c.integration_loop.workspace if c.integration_loop else None}")

asyncio.run(test())
EOF

# 2. Se workspace vazio, rodar stimulate_system.py
python scripts/stimulate_system.py
```

### Problema 2: "Ciclos não executando a cada 5 minutos"

**Causa**: Trigger interval muito grande ou condição não sendo alcançada
**Solução**:
```python
# Reduzir interval para teste
self.cycle_trigger_interval = 30.0  # 30 segundos em vez de 300

# Verificar logs
grep "Time-based trigger" logs/omnimind.log
```

### Problema 3: "CPU/RAM muito alto durante ciclos"

**Causa**: Ciclos computacionalmente pesados
**Solução**:
```python
# Reduzir número de ciclos ou aumentar intervalo
results = await self.integration_loop.run_cycles(1, collect_metrics_every=1)  # 1 ciclo em vez de 2
self.cycle_trigger_interval = 600.0  # 10 minutos em vez de 5
```

---

## 📝 Documentação Pós-Implementação

### Arquivo de Configuração Sugerido

```yaml
# config/cycle_stimulation.yaml
stimulation:
  enabled: true

  bootstrap:
    enabled: true
    cycles: 2
    description: "Initial data generation when workspace empty"

  continuous:
    enabled: true
    interval_seconds: 300  # 5 minutos
    cycles_per_trigger: 1
    description: "Maintain continuous integration cycle"

  monitoring:
    phi_recovery_threshold: 0.2  # Esperado alcançar em <10min
    cycle_timeout_seconds: 120   # Máximo tempo por ciclo
    alert_if_phi_below: 0.1      # Alertar se Phi descer muito
```

---

## ✅ PRÓXIMAS AÇÕES

1. **Imediato**: Review desta proposta com você
2. **Se aprovado**: Implementar FASE 1 + FASE 2
3. **Validar**: Monitorar Phi recovery
4. **Deploy**: Pushar para produção
5. **Suporte**: Acompanhar sistema por 24-48h

---

**Status**: Pronto para implementação
**Risco**: BAIXO (mudanças isoladas, sem breaking changes)
**Rollback**: Trivial (revert 1-2 commits)

