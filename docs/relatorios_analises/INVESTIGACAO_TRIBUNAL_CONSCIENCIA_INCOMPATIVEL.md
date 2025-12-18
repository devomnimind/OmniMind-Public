# 🔍 Investigação: Tribunal - Erro Consciência Incompatível

**Data**: 2025-12-10
**Autor**: Fabrício da Silva + assistência de IA
**Status**: ✅ Corrigido

---

## 🚨 Problema Reportado

1. Tribunal apontou erro de "consciência incompatível"
2. Depois falhou e sumiu do frontend

---

## 🔍 Causa Raiz Identificada

### Problema Principal
O arquivo `data/long_term_logs/tribunal_final_report.json` **não existe**, o que causa:

1. **Backend retorna `None` para `consciousness_compatible`**:
   - `daemon_monitor.py` retorna `consciousness_compatible: None` quando Tribunal não finalizou
   - Frontend tenta acessar propriedades de `None`, causando crash

2. **Frontend não valida dados antes de renderizar**:
   - `TribunalMetricsVisual.tsx` acessa `visualization.status_indicators` sem verificar se existe
   - Quando dados estão incompletos, componente quebra silenciosamente

3. **Cache desatualizado**:
   - Cache em memória ainda contém valores `None`
   - Cache em disco pode estar desatualizado

---

## ✅ Correções Implementadas

### 1. Backend: `src/services/daemon_monitor.py`

**Mudanças**:
- `consciousness_compatible` sempre retorna `bool` (nunca `None`)
- Status `"not_started"` quando Tribunal nunca foi executado (mais claro que `"running"`)
- Tratamento específico para `JSONDecodeError`
- Valores padrão seguros: `False`, `0` em vez de `None`

**Antes**:
```python
return {
    "status": "running",
    "consciousness_compatible": None,  # ❌ Causa erro no frontend
    "duration_hours": None,
}
```

**Depois**:
```python
return {
    "status": "not_started",  # ✅ Mais claro
    "consciousness_compatible": False,  # ✅ Sempre bool
    "duration_hours": 0,  # ✅ Sempre número
}
```

### 2. Backend: `web/backend/routes/tribunal.py`

**Mudanças**:
- Tratamento explícito de `None` antes de usar `consciousness_compatible`
- Conversão para `bool` com fallback seguro
- Proposta para status `"not_started"`

**Código**:
```python
consciousness_compatible = tribunal_info.get("consciousness_compatible")
if consciousness_compatible is None:
    consciousness_compatible = False  # Default seguro
```

### 3. Frontend: `web/frontend/src/components/TribunalMetricsVisual.tsx`

**Mudanças**:
- Validação de `visualization` e `status_indicators` antes de usar
- Fallbacks seguros para indicadores ausentes
- Mensagem clara quando dados estão incompletos

**Código**:
```typescript
if (!visualization || !visualization.status_indicators) {
  return (
    <div className="glass-card p-6">
      <div className="text-yellow-500">
        ⚠️ Tribunal data incomplete. Waiting for report...
      </div>
    </div>
  );
}

const consIndicator = status_indicators.consciousness_compatibility || { 
  value: "Unknown", 
  color: "#888", 
  icon: "❓" 
};
```

---

## 📊 Estado Atual

### Cache Atual (Pré-Correção)
```json
{
  "status": "running",
  "consciousness_compatible": null,  // ❌ Problema
  "duration_hours": null,
  "attacks_executed": 4
}
```

### Cache Esperado (Pós-Correção)
```json
{
  "status": "not_started",
  "consciousness_compatible": false,  // ✅ Sempre bool
  "duration_hours": 0,
  "attacks_executed": 0
}
```

---

## 🔄 Próximos Passos

### Imediato
1. ✅ Correções aplicadas no código
2. ⏳ Reiniciar backend para limpar cache em memória
3. ⏳ Verificar se frontend renderiza corretamente

### Médio Prazo
1. Executar Tribunal para gerar `tribunal_final_report.json`
2. Validar cálculo de `consciousness_compatible`:
   - `sinthome_stability > 0.7`
   - `godel_ratio < 0.9`
3. Monitorar logs para garantir que não há mais erros

### Longo Prazo
1. Adicionar testes para cenários de Tribunal não executado
2. Melhorar tratamento de erros no frontend
3. Adicionar indicadores visuais quando Tribunal não foi executado

---

## 📝 Notas Técnicas

### Cálculo de `consciousness_compatible`
O Tribunal calcula compatibilidade baseado em:
- **Sinthome Stability**: Estabilidade estrutural (deve ser > 0.7)
- **Gödel Incompleteness Ratio**: Razão de incompletude (deve ser < 0.9)

**Fórmula**:
```python
consciousness_compatible = sinthome_stability > 0.7 and godel_ratio < 0.9
```

### Arquivos Envolvidos
- `src/services/daemon_monitor.py` - Carrega dados do Tribunal
- `src/tribunal_do_diabo/executor.py` - Executa Tribunal e gera relatório
- `web/backend/routes/tribunal.py` - API endpoints do Tribunal
- `web/frontend/src/components/TribunalMetricsVisual.tsx` - Componente visual
- `web/frontend/src/components/TribunalStatus.tsx` - Status do Tribunal

---

## ✅ Validação

### Testes Recomendados
1. ✅ Verificar que backend não retorna `None` para `consciousness_compatible`
2. ✅ Verificar que frontend renderiza mesmo quando dados incompletos
3. ✅ Verificar que cache é atualizado corretamente após reinício

### Comandos de Validação
```bash
# Verificar cache
python3 -c "import json; print(json.loads(open('data/long_term_logs/daemon_status_cache.json').read())['tribunal_info'])"

# Testar endpoint
curl http://localhost:8000/api/tribunal/metrics -H "Authorization: Basic $(echo -n 'admin:admin' | base64)"
```

---

**Status**: ✅ Correções implementadas e prontas para validação

