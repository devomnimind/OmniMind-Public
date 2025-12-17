# Integração Completa das Métricas de Consciência - Phase 22

## 📊 Resumo

Integração completa das **6 métricas de consciência** (phi, anxiety, flow, entropy, ici, prs) + **dados brutos** das predições causais no frontend.

## ✅ Implementações

### 1. Backend - Endpoint Completo

**Rota**: `/api/v1/autopoietic/consciousness/metrics?include_raw=true`

**Retorna**:
- 6 métricas principais: `phi`, `anxiety`, `flow`, `entropy`, `ici`, `prs`
- Componentes: `ici_components`, `prs_components`
- Histórico: `history` (últimos 20 valores)
- Interpretação: `interpretation` (mensagem AI + confiança)
- **Dados brutos** (quando `include_raw=true`):
  - Predições causais (25 últimas)
  - Estatísticas dos módulos
  - Workspace cycle
  - Total de módulos

### 2. Frontend - Componente Atualizado

**Componente**: `ConsciousnessMetrics.tsx`

**Funcionalidades**:
- ✅ Busca dados diretamente da API (atualização a cada 10s)
- ✅ Exibe todas as 6 métricas com barras de progresso
- ✅ Mostra componentes (ICI e PRS breakdown)
- ✅ Interpretação AI com nível de confiança
- ✅ **Seção de dados brutos** (expansível):
  - Estatísticas resumidas (predições válidas, ciclo workspace, módulos)
  - Lista de predições causais (últimas 10)
  - Estatísticas por módulo

### 3. Dados Brutos Expostos

**Predições Causais**:
- `source_module` → `target_module`
- `r_squared` (qualidade da predição)
- `granger_causality` (causalidade de Granger)
- `transfer_entropy` (entropia de transferência)
- `computation_time_ms` (tempo de computação)

**Estatísticas dos Módulos**:
- Histórico de cada módulo
- Última atualização
- Total de módulos ativos

## 🔧 Como Usar

### Backend

```python
# Endpoint já está disponível
GET /api/v1/autopoietic/consciousness/metrics?include_raw=true
```

### Frontend

O componente `ConsciousnessMetrics` já está integrado no Dashboard e:
- Atualiza automaticamente a cada 10 segundos
- Exibe todas as 6 métricas
- Permite expandir dados brutos clicando em "Mostrar Dados Brutos"

## 📈 Métricas Expostas

1. **Phi (Φ)**: Integração de informação (0.0-1.0)
2. **Anxiety**: Tensão e conflitos do sistema (0.0-1.0)
3. **Flow**: Fluidez cognitiva (0.0-1.0)
4. **Entropy**: Desordem e complexidade (0.0-1.0)
5. **ICI**: Índice de coerência integrada (0.0-1.0)
6. **PRS**: Score de ressonância panárquica (0.0-1.0)

## 🎯 Dados Brutos

### Predições Causais

Exemplo:
```json
{
  "source_module": "qualia",
  "target_module": "narrative",
  "r_squared": 0.8542,
  "granger_causality": 0.7234,
  "transfer_entropy": 0.6891,
  "computation_time_ms": 12.5
}
```

### Estatísticas do Sistema

- **Predições válidas**: X/Y (taxa de validação)
- **Ciclo workspace**: Número do ciclo atual
- **Total de módulos**: Quantidade de módulos ativos
- **Taxa de validação**: % de predições válidas

## 🔄 Atualização Automática

- **Intervalo**: 10 segundos
- **Fonte**: API endpoint `/api/v1/autopoietic/consciousness/metrics`
- **Cache**: Backend cache de 5 segundos (evita coleta excessiva)

## 📝 Notas

- Os dados brutos são opcionais (parâmetro `include_raw=true`)
- O frontend mostra apenas as últimas 10 predições (para performance)
- Todas as métricas são normalizadas no range [0, 1]
- A interpretação AI é gerada automaticamente baseada nos valores

---

**Status**: ✅ **Implementado e Funcional**

