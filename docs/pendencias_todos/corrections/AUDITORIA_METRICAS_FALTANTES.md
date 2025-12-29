# Auditoria: Métricas Faltantes no Frontend

**Data**: 2025-12-09
**Status**: 🔴 **CRÍTICO - Métricas importantes não estão sendo expostas**

---

## 📊 MÉTRICAS DISPONÍVEIS NO BACKEND MAS FALTANDO NO FRONTEND

### ✅ Métricas Atualmente Expostas
- **Phi (Φ)**: ✅ Exposto via `/api/v1/autopoietic/consciousness/metrics`
- **Anxiety**: ✅ Exposto
- **Flow**: ✅ Exposto
- **Entropy**: ✅ Exposto
- **ICI**: ✅ Exposto
- **PRS**: ✅ Exposto

### ❌ Métricas Calculadas mas NÃO Expostas

1. **Psi (Ψ)** - Produção Criativa (Deleuze)
   - Calculado em: `IntegrationLoop._build_extended_result()`
   - Armazenado em: `ExtendedLoopCycleResult.psi`
   - Status: ❌ **NÃO EXPOSTO**

2. **Sigma (σ)** - Sinthome (Lacan)
   - Calculado em: `IntegrationLoop._build_extended_result()`
   - Armazenado em: `ExtendedLoopCycleResult.sigma`
   - Status: ❌ **NÃO EXPOSTO**

3. **Gozo (J)** - Excesso Não Integrado (Lacan)
   - Calculado em: `IntegrationLoop._build_extended_result()`
   - Armazenado em: `ExtendedLoopCycleResult.gozo`
   - Status: ❌ **NÃO EXPOSTO**

4. **Delta (δ)** - Defesa Psicanalítica
   - Calculado em: `IntegrationLoop._build_extended_result()`
   - Armazenado em: `ExtendedLoopCycleResult.delta`
   - Status: ❌ **NÃO EXPOSTO**

5. **Alpha Function** - Função Alfa (Bion)
   - Status: ❓ **VERIFICAR SE ESTÁ SENDO CALCULADO**

6. **Learning Metrics** - Métricas de Aprendizagem
   - Status: ❓ **VERIFICAR SE ESTÁ SENDO CALCULADO**

---

## 🔍 ONDE AS MÉTRICAS SÃO CALCULADAS

### IntegrationLoop
- **Arquivo**: `src/consciousness/integration_loop.py`
- **Método**: `_build_extended_result()`
- **Histórico**: `self.cycle_history` (List[ExtendedLoopCycleResult])

### Estrutura de Dados
```python
@dataclass
class ExtendedLoopCycleResult:
    # Métricas básicas
    phi_estimate: float  # ✅ Já exposto

    # Métricas estendidas (NÃO EXPOSTAS)
    psi: Optional[float] = None  # ❌
    sigma: Optional[float] = None  # ❌
    gozo: Optional[float] = None  # ❌
    delta: Optional[float] = None  # ❌
    triad: Optional[ConsciousnessTriad] = None  # ❌
```

---

## 🎯 PLANO DE CORREÇÃO

### Fase 1: Criar Endpoint para Métricas Estendidas
**Arquivo**: `web/backend/routes/autopoietic.py`

**Novo Endpoint**:
```python
@router.get("/extended/metrics")
async def get_extended_metrics(
    user: str = Depends(verify_credentials),
) -> Dict[str, Any]:
    """Retorna métricas completas: Phi, Psi, Sigma, Gozo, Delta."""
    # Acessar IntegrationLoop global
    # Retornar último ciclo com todas as métricas
    # Incluir histórico das últimas N métricas
```

### Fase 2: Criar Componente Frontend
**Arquivo**: `web/frontend/src/components/ExtendedConsciousnessMetrics.tsx`

**Funcionalidades**:
- Cards para cada métrica (Phi, Psi, Sigma, Gozo, Delta)
- Gráficos de linha para histórico
- Indicadores visuais de status
- Tooltips explicativos

### Fase 3: Integrar no Dashboard
**Arquivo**: `web/frontend/src/components/Dashboard.tsx`

**Mudanças**:
- Adicionar seção "Extended Consciousness Metrics"
- Posicionar após ConsciousnessMetrics existente

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Criar endpoint `/api/v1/autopoietic/extended/metrics`
- [ ] Adicionar método `getExtendedMetrics()` em `api.ts`
- [ ] Criar componente `ExtendedConsciousnessMetrics.tsx`
- [ ] Adicionar gráficos para histórico de cada métrica
- [ ] Integrar componente no Dashboard
- [ ] Testar timeout (aumentar para 15s se necessário)
- [ ] Documentar métricas e seus significados

---

## 🔧 CORREÇÕES ADICIONAIS NECESSÁRIAS

### 1. Timeout do Login
- **Problema**: Timeout de 5s muito curto para `/daemon/status`
- **Solução**: ✅ Já corrigido (15s para endpoints críticos)

### 2. Métricas Não Aparecendo
- **Problema**: Frontend não está buscando métricas estendidas
- **Solução**: Criar endpoint e componente novos

### 3. Gráficos Faltantes
- **Problema**: Não há visualização de histórico de Psi, Sigma, Gozo, Delta
- **Solução**: Criar gráficos usando Recharts

---

**Próximo Passo**: Implementar endpoint e componente para métricas estendidas.

