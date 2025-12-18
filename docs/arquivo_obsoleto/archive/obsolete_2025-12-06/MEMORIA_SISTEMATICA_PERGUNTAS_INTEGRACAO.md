# Perguntas de Integração: Memória Sistemática

**Autor**: Fabrício da Silva + assistência de IA
**Data**: 2025-01-XX
**Status**: Aguardando respostas antes de integrar

---

## ❓ PERGUNTAS CRÍTICAS

### 1. Integração com SharedWorkspace

**Pergunta**: Onde chamar `add_trace_not_memory()`?

**Opções**:
- **A) Em cada `write_embedding()`**: Rastreia cada mudança de estado de módulo
- **B) Em cada ciclo do `IntegrationLoop`**: Rastreia apenas transições entre ciclos
- **C) Ambos**: Rastreia mudanças granulares E transições de ciclo

**Recomendação**: **Opção C** (ambos), mas com thresholds diferentes:
- `write_embedding()`: threshold baixo (0.001) para mudanças pequenas
- `IntegrationLoop`: threshold normal (0.01) para transições de ciclo

---

### 2. Integração com PhiCalculator

**Pergunta**: Como deformar partições no `calculate_phi_with_unconscious()`?

**Opções**:
- **A) Modificar `_generate_complex_candidates()`**: Deforma candidatos antes de calcular Φ
- **B) Modificar `_calculate_phi_for_subsystem()`**: Deforma cálculo de Φ para cada subsistema
- **C) Ambos**: Deforma candidatos E cálculo

**Recomendação**: **Opção A** (deformar candidatos), porque:
- Partições são "puxadas" para áreas com muitas marcas topológicas
- Cálculo de Φ permanece o mesmo (não aditivo)
- Alinhado com filosofia: memória muda COMO Φ é calculado, não o valor diretamente

**Implementação proposta**:
```python
def _generate_complex_candidates(self, memory_trace: Optional[SystemicMemoryTrace] = None) -> List[Set[int]]:
    candidates = self._generate_complex_candidates_standard()

    if memory_trace:
        # Deforma candidatos baseado em marcas topológicas
        deformed = memory_trace.deform_partitions(candidates)
        return deformed

    return candidates
```

---

### 3. Integração com NarrativeHistory

**Pergunta**: `SystemicMemoryTrace` complementa ou substitui `NarrativeHistory`?

**Opções**:
- **A) Complementa**: Usar `reconstruct_narrative_retroactively()` quando `NarrativeHistory` não tem dados
- **B) Substitui**: Não usar mais `NarrativeHistory`, apenas `SystemicMemoryTrace`
- **C) Híbrido**: `NarrativeHistory` para eventos específicos, `SystemicMemoryTrace` para topologia geral

**Recomendação**: **Opção C** (híbrido), porque:
- `NarrativeHistory`: eventos específicos com significado simbólico (Lacanian)
- `SystemicMemoryTrace`: deformação topológica geral (não simbólica)
- Ambos são necessários: simbólico + topológico

**Implementação proposta**:
```python
# Em NarrativeHistory
def reconstruct_narrative(self, current_state):
    # Tenta usar SystemicMemoryTrace primeiro
    if self.systemic_memory:
        return self.systemic_memory.reconstruct_narrative_retroactively(current_state)

    # Fallback para backend (EpisodicMemory)
    return self.backend.retrieve_similar_episodes(...)
```

---

### 4. Integração com AutopoieticManager

**Pergunta**: Como `SystemicMemoryTrace` afeta autopoiesis?

**Opções**:
- **A) Informa estratégia**: Deformações topológicas sugerem estratégia (EXPAND/STABILIZE/CONTRACT)
- **B) Valida mudanças**: Verifica se mudanças autopoiéticas aumentam Φ
- **C) Ambos**: Informa E valida

**Recomendação**: **Opção C** (ambos), porque:
- Deformações indicam onde sistema está "crescendo" (EXPAND)
- Deformações indicam onde sistema está "estável" (STABILIZE)
- Deformações indicam onde sistema está "contraindo" (CONTRACT)

---

## ✅ IMPLEMENTAÇÃO PROPOSTA (Baseada em Melhores Práticas)

### Arquitetura de Integração

```
SharedWorkspace
    ├─ write_embedding() → SystemicMemoryTrace.add_trace_not_memory()
    └─ compute_phi_from_integrations() → SystemicMemoryTrace.affect_phi_calculation()

PhiCalculator
    └─ _generate_complex_candidates() → SystemicMemoryTrace.deform_partitions()

NarrativeHistory
    └─ reconstruct_narrative() → SystemicMemoryTrace.reconstruct_narrative_retroactively()

AutopoieticManager
    └─ run_cycle() → SystemicMemoryTrace.get_summary() (para estratégia)
```

---

## 🔧 PRÓXIMOS PASSOS

1. **Aguardar confirmação** das respostas acima
2. **Implementar integrações** conforme respostas
3. **Testar** com métricas atuais (Φ = 0.0577)
4. **Validar** que Φ muda (não aumenta linearmente)
5. **Documentar** resultados

---

**Status**: Aguardando respostas para implementação final

