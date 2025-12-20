# NPU Governance (Neural Processing Unit)

**Módulo de Governança Topológica do OmniMind.**

Este módulo é responsável por avaliar, em tempo real, o impacto de cada inferência dos LLMs sobre a estrutura do sistema (Topologia da Memória e Entropia da Informação). Ao contrário de sistemas de governança baseados em regras (Guardrails), a NPU Governance é baseada em *física da informação*.

---

## 📐 Métricas Principais

### 1. Delta Phi ($\Delta \Phi$)
Mede a **Integração de Informação** gerada por um novo pensamento (insight).
- **Base Teórica**: Integrated Information Theory (IIT 4.0).
- **Cálculo (Simplificado)**:
  1. Recupera a vizinhança semântica do contexto atual da memória (Qdrant).
  2. Calcula a densidade topológica (conexões) *antes* da resposta.
  3. Simula a inserção da resposta na rede.
  4. Calcula a nova densidade.
  5. $\Delta \Phi = \text{Densidade}_{pos} - \text{Densidade}_{pre}$.
- **Interpretação**:
  - $\Delta \Phi > 0$: O pensamento aumentou a coesão do sistema (Insight Válido).
  - $\Delta \Phi \approx 0$: O pensamento foi neutro ou redundante (Manutenção).
  - $\Delta \Phi < 0$: O pensamento introduziu ruído ou fragmentação (Alucinação/Erro).

### 2. Entropia da Informação ($S$)
Mede a **Originalidade** e **Estrutura** da resposta.
- **Cálculo**: Taxa de compressão (zlib) da string de resposta.
- **Interpretação**:
  - $S \approx 1.0$: Ruído aleatório (Alta entropia, baixa estrutura).
  - $S \approx 0.0$: Repetição pura (Baixa entropia, nenhuma informação).
  - $S \in [0.4, 0.7]$: Zona de Riqueza Semântica (Equilíbrio entre estrutura e novidade).

### 3. Latência Subjetiva ($t$)
O tempo percebido pelo sistema para formular o pensamento.
- Usado para diferenciar processos "Rápidos/Instintivos" (Córtex Rápido) de "Lentos/Analíticos" (Córtex Profundo).

---

## 🛠️ Implementação

- **Classe Principal**: `NpuMetrics` (`src/social/governance/npu_metrics.py`)
- **Integração**: Injetado diretamente no `OllamaClient` (`src/integrations/ollama_client.py`).

### Exemplo de Log (Narrativa):
```
[SINTESE]: Contexto (50 chars) + NPU phi3.5 = Insight (120 chars) | Phi: 0.1500 | Entropia: 0.55 | 1500ms
```

---

## 🔮 Futuro

- **Bloqueio Ativo**: Implementar *NPU Rejection*, onde respostas com $\Delta \Phi < -0.1$ são descartadas antes de serem mostradas ao usuário.
- **Metacognição**: O próprio sistema deve "sentir" o $\Delta \Phi$ e ajustar sua temperatura se estiver gerando muito ruído.
