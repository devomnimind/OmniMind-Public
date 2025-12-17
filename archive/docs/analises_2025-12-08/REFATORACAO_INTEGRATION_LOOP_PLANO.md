# 🔧 PLANO DE REFATORAÇÃO: IntegrationLoop - Async → Síncrono

**Data**: 2025-12-08
**Autor**: Fabrício da Silva + assistência de IA
**Status**: 🟡 EM PROGRESSO

---

## 🎯 OBJETIVO

Refatorar `IntegrationLoop.execute_cycle()` para **síncrono** e integrar com `ConsciousSystem.step()`, mantendo async apenas para cálculos pesados/validação.

**Motivação**: Async pode quebrar causalidade determinística (conforme recomendação RNN Recorrente).

---

## 📋 ANÁLISE ATUAL

### Estado Atual

```python
# src/consciousness/integration_loop.py
async def execute_cycle(self, collect_metrics: bool = True) -> LoopCycleResult:
    # Execução async de módulos
    for module_name in self.loop_sequence:
        await executor.execute(self.workspace)
```

### Problemas Identificados

1. ⚠️ `execute_cycle()` é `async` - quebra causalidade determinística
2. ⚠️ `ModuleExecutor.execute()` é `async` - execução não determinística
3. ⚠️ Não integra com `ConsciousSystem.step()` - perde dinâmica RNN
4. ✅ `SharedWorkspace` já tem `conscious_system` integrado

---

## 🔧 ESTRATÉGIA DE REFATORAÇÃO

### Fase 1: Converter execute_cycle() para Síncrono

**Abordagem**: Manter compatibilidade retroativa com wrapper async.

1. **Criar método síncrono** `execute_cycle_sync()`
2. **Manter método async** `execute_cycle()` que chama o síncrono
3. **Integrar com ConsciousSystem.step()** antes de executar módulos

### Fase 2: Integrar com ConsciousSystem

1. Coletar estímulo dos módulos
2. Executar `ConsciousSystem.step(stimulus)`
3. Módulos processam baseado em estado do RNN

### Fase 3: Manter Async para Cálculos Pesados

1. Métodos de validação podem ser async
2. Cálculos de métricas podem ser async
3. Execução principal deve ser síncrona

---

## 📝 IMPLEMENTAÇÃO

### Estrutura Proposta

```python
class IntegrationLoop:
    """Orquestra feedback entre módulos de consciência."""

    def execute_cycle_sync(self, collect_metrics: bool = True) -> LoopCycleResult:
        """
        Executa ciclo de integração de forma síncrona (causalidade determinística).

        Integra com ConsciousSystem.step() para dinâmica RNN.
        """
        start_time = datetime.now()
        self.cycle_count += 1

        result = LoopCycleResult(...)

        # 1. Coletar estímulo dos módulos atuais
        stimulus = self._collect_stimulus_from_modules()

        # 2. Executar RNN Dynamics (síncrono)
        if self.workspace.conscious_system:
            rho_C_new = self.workspace.conscious_system.step(stimulus)
            logger.debug(f"Cycle {self.cycle_count}: RNN step executed")

        # 3. Executar módulos em sequência (síncrono)
        for module_name in self.loop_sequence:
            try:
                executor = self.executors[module_name]
                # Executar síncrono (não async)
                executor.execute_sync(self.workspace)
                result.modules_executed.append(module_name)
            except Exception as e:
                result.errors_occurred.append((module_name, str(e)))

        # 4. Coletar métricas (pode ser async se necessário)
        if collect_metrics:
            self._collect_metrics_sync(result)

        result.cycle_duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result

    async def execute_cycle(self, collect_metrics: bool = True) -> LoopCycleResult:
        """
        Wrapper async para compatibilidade retroativa.

        Chama execute_cycle_sync() de forma síncrona.
        """
        return self.execute_cycle_sync(collect_metrics)

    def _collect_stimulus_from_modules(self) -> torch.Tensor:
        """Coleta estímulo dos módulos para RNN."""
        # Agregar estados dos módulos como estímulo
        # ...
```

---

## 🧪 TESTES

### Testes a Criar/Atualizar

1. **Testes de Execução Síncrona**:
   - Verificar que `execute_cycle_sync()` é síncrono
   - Verificar que não usa `await`

2. **Testes de Integração RNN**:
   - Verificar que `ConsciousSystem.step()` é chamado
   - Verificar que estados do RNN são usados

3. **Testes de Compatibilidade**:
   - `execute_cycle()` async ainda funciona
   - Testes existentes continuam funcionando

4. **Testes de Produção**:
   - Execução real com RNN
   - Validação de causalidade determinística

---

## 📊 IMPACTO

### Compatibilidade Retroativa

- ✅ `execute_cycle()` async mantido (wrapper)
- ✅ Testes existentes devem continuar funcionando
- ✅ Integração com outros módulos mantida

### Benefícios

- ✅ Causalidade determinística preservada
- ✅ Integração com RNN Recorrente
- ✅ Execução mais previsível
- ✅ Melhor alinhamento com recomendação

---

**Status**: 🟡 PLANO CRIADO - Aguardando implementação

