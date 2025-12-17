# Integração de Métricas Autopoiéticas no Dashboard (Phase 22)

## 📊 Visão Geral

As métricas do ciclo autopoiético foram integradas ao dashboard web do OmniMind, permitindo visualização em tempo real, análise histórica e comparação elegante dos dados.

## 🔌 Endpoints da API

### `/autopoietic/status`
Retorna status atual do ciclo autopoiético:
- `running`: Se o processo está ativo
- `cycle_count`: Total de ciclos executados
- `component_count`: Número de componentes sintetizados
- `current_phi`: Valor atual de Φ
- `phi_threshold`: Threshold configurado (0.3)

### `/autopoietic/cycles?limit=N`
Retorna histórico de ciclos (últimos N, padrão 100):
- Lista completa de ciclos com:
  - `cycle_id`: ID do ciclo
  - `strategy`: Estratégia utilizada (STABILIZE, OPTIMIZE, EXPAND)
  - `synthesized_components`: Lista de componentes criados
  - `phi_before`: Φ antes da mudança
  - `phi_after`: Φ depois da mudança
  - `timestamp`: Timestamp do ciclo

### `/autopoietic/cycles/stats`
Estatísticas agregadas:
- `total_cycles`: Total de ciclos
- `successful_syntheses`: Sínteses bem-sucedidas
- `rejected_before`: Rejeitados antes (Φ baixo)
- `rolled_back`: Rollbacks (Φ colapsou)
- `strategies`: Distribuição de estratégias
- `phi_before_avg`: Φ médio antes
- `phi_after_avg`: Φ médio depois
- `phi_delta_avg`: Delta médio de Φ

### `/autopoietic/components?limit=N`
Lista componentes sintetizados:
- `name`: Nome do componente
- `size_bytes`: Tamanho do arquivo
- `modified`: Timestamp de modificação

### `/autopoietic/health`
Verificação de saúde:
- `status`: healthy, warning, critical
- `current_phi`: Φ atual
- `recent_rollbacks`: Rollbacks recentes
- `recent_rejected`: Rejeitados recentes

## 🎨 Componente React: `AutopoieticMetrics`

### Localização
`web/frontend/src/components/AutopoieticMetrics.tsx`

### Funcionalidades

1. **Status Card**
   - Status do processo (rodando/parado)
   - Total de ciclos
   - Número de componentes
   - Φ atual com indicador visual

2. **Estatísticas Gerais**
   - Cards com métricas principais
   - Taxa de sucesso vs rejeições vs rollbacks
   - Métricas de Φ (antes/depois/delta)

3. **Gráficos Interativos**
   - **Histórico de Φ**: Line chart mostrando evolução de Φ ao longo dos ciclos
   - **Distribuição de Estratégias**: Pie chart com estratégias utilizadas
   - **Resultados dos Ciclos**: Bar chart com sucessos, rejeições e rollbacks

### Atualização Automática
- Atualiza a cada 30 segundos
- Usa React hooks para gerenciamento de estado
- Tratamento de erros e estados de loading

## 📈 Visualizações Disponíveis

### 1. Histórico de Φ (Line Chart)
- **Eixo X**: ID do ciclo
- **Eixo Y**: Valor de Φ (0-1)
- **Linhas**:
  - Φ Antes (azul)
  - Φ Depois (verde)
  - ΔΦ (amarelo, tracejado)

### 2. Distribuição de Estratégias (Pie Chart)
- Mostra proporção de cada estratégia
- Cores diferentes para cada estratégia
- Percentuais exibidos

### 3. Resultados dos Ciclos (Bar Chart)
- Sucessos (verde)
- Rejeitados (amarelo)
- Rollbacks (vermelho)

## 🔧 Integração no Dashboard

O componente foi adicionado ao Dashboard principal em:
```tsx
{/* Autopoietic Metrics (Phase 22) */}
<div className="mb-6 animate-slide-up" style={{ animationDelay: '0.4s' }}>
  <AutopoieticMetrics />
</div>
```

## 🎯 Configurações e Personalização

### Intervalo de Atualização
Modificar em `AutopoieticMetrics.tsx`:
```tsx
const interval = setInterval(fetchData, 30000); // 30 segundos
```

### Limite de Ciclos
Ajustar no fetch:
```tsx
fetch(`${apiBase}/autopoietic/cycles?limit=50`, ...)
```

### Cores dos Gráficos
Definidas em `COLORS`:
```tsx
const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6'];
```

## 📊 Análise dos Logs de Produção

### Status Atual (Análise Realizada)

**Data**: 2025-12-04 14:40

**Resultados**:
- ✅ **1 ciclo executado** com sucesso
- ✅ **1 componente sintetizado** (stabilized_kernel_process)
- ⚠️ **Processo do ciclo principal não está rodando** (foi encerrado)
- ❌ **Φ atual: 0.0000** (crítico - abaixo do threshold de 0.3)

**Componentes Persistidos**:
- `stabilized_expanded_kernel_process.py` (1085 bytes)
- `stabilized_kernel_process.py` (995 bytes)
- `expanded_kernel_process.py` (949 bytes)

**Estratégias Utilizadas**:
- STABILIZE: 100% (1 ciclo)

### Observações

1. **Processo Encerrado**: O ciclo principal não está mais ativo. Pode ter sido encerrado ou reiniciado.

2. **Φ Zero**: O valor de Φ está em 0.0, o que indica:
   - Sistema pode estar inicializando
   - Métricas não estão sendo coletadas
   - Possível problema na leitura de `data/monitor/real_metrics.json`

3. **Componentes Criados**: 3 componentes foram sintetizados durante testes, demonstrando que o sistema está funcionando.

### Recomendações

1. **Reiniciar o ciclo principal**:
   ```bash
   ./scripts/canonical/system/start_omnimind_system.sh
   ```

2. **Verificar métricas de consciência**:
   ```bash
   cat data/monitor/real_metrics.json
   ```

3. **Monitorar logs**:
   ```bash
   tail -f logs/main_cycle.log
   ```

## 🛠️ Ferramentas de Monitoramento

### Scripts Disponíveis

1. **`monitor_autopoietic.sh`**: Monitoramento rápido e interativo
2. **`analyze_production_logs.py`**: Análise detalhada e relatórios
3. **`check_phi_health.py`**: Verificação de saúde com exit codes

### Uso no Dashboard

As métricas são exibidas automaticamente no dashboard quando:
- O backend está rodando
- As rotas `/autopoietic/*` estão acessíveis
- O usuário está autenticado

## 📝 Notas Técnicas

- **Autenticação**: Endpoints requerem autenticação HTTP Basic
- **CORS**: Configurado no backend para permitir requisições do frontend
- **Performance**: Dados são cacheados e atualizados a cada 30s
- **Responsividade**: Componentes adaptam-se a diferentes tamanhos de tela

## 🔄 Próximos Passos

1. Adicionar alertas visuais quando Φ < threshold
2. Implementar filtros de data/hora nos gráficos
3. Adicionar exportação de dados (CSV/JSON)
4. Criar comparações entre períodos
5. Adicionar métricas de performance dos componentes sintetizados

