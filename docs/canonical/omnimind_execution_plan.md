# 🚀 OmniMind Execution Plan: Production & Development

**Última Atualização**: 08 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)

---

## 1. Visão Geral

Este documento descreve a estratégia de execução do sistema OmniMind, integrando os frameworks **Desiring-Machines**, **Consciência Topológica**, e **Lacaniano-D&G**. Define como o sistema inicializa, executa e gerencia seu ciclo de vida em ambientes de Desenvolvimento e Produção.

---

## 2. Estratégia de Ambiente

### 2.1 Desenvolvimento (Dev)

**Modo**: Interativo, Debug habilitado

**Inicialização**:
- **Testes**: `./scripts/run_tests_fast.sh` (Suite rápida diária)
- **Manual**: `uvicorn src.api.main:app --reload` (API apenas)
- **Sistema Completo**: `./scripts/canonical/system/start_omnimind_system.sh`

**Componentes**:
- **Backend (FastAPI)**: Porta 8000
- **Frontend (Vite)**: Porta 3000 (se ativo)
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

**Logging**: Verbose (DEBUG level), saída no console

**Estado**: Efêmero (reseta ao reiniciar, a menos que explicitamente salvo)

**Modelo LLM**: `phi:latest` (Microsoft Phi) via Ollama local

---

### 2.2 Produção (Prod)

**Modo**: Headless, Otimizado, Seguro

**Inicialização**: Serviços Systemd (Automático no boot)

**Componentes**:
- **`omnimind-core.service`**: Loop principal do Rizoma & API (Porta 8000)
- **`omnimind-monitor.service`**: SAR (Self-Audit & Regeneration) & Security
- **`omnimind-consciousness.service`**: Cálculo de Φ Topológico (worker em background)

**Logging**: JSON estruturado para `logs/`, rotacionado diariamente

**Estado**: Persistente (Redis + JSON/SQL storage)

**Modelo LLM**: `phi:latest` (Microsoft Phi) via Ollama, com fallback para `qwen2:7b-instruct`

---

## 3. Inicialização do Sistema (Sequência de Boot)

O sistema segue um protocolo de inicialização estrito para garantir que o "Inconsciente Maquínico" seja formado corretamente antes de processar entradas externas.

### 3.1 Módulos de Boot (`src/boot/`)

**Ordem de Execução** (em `src/main.py`):

1. **Hardware Check** (`src/boot/hardware.py`):
   - Verifica disponibilidade de GPU/TPU para cálculos Quantum/Topológicos
   - Detecta recursos do sistema (CPU, RAM)
   - Retorna `HardwareProfile`

2. **Memory Load** (`src/boot/memory.py`):
   - Carrega dados de Homologia Persistente (história de trauma) do disco
   - Caminho: `data/consciousness/persistent_homology.json`
   - Se não encontrado, inicia com topologia vazia (Modo Amnésia)
   - Retorna `SimplicialComplex`

3. **Rhizome Construction** (`src/boot/rhizome.py`):
   - Instancia nós de Máquinas Desejantes (Quantum, NLP, Topology)
   - Estabelece conexões (sinapses) baseadas na topologia carregada
   - Conexões bidirecionais: Quantum ↔ NLP ↔ Topology ↔ Quantum
   - Valida integridade: `check_rhizome_integrity()`
   - Retorna `Rhizoma`

4. **Consciousness Priming** (`src/boot/consciousness.py`):
   - Calcula Φ inicial (Phi) usando IIT 3.0
   - Inicializa `LacianianDGDetector` para diagnóstico
   - Realiza verificação de baseline (Auto-Reflexão)
   - Retorna `(PhiCalculator, LacianianDGDetector)`

5. **Métricas Reais** (`src/main.py`):
   - Inicializa `RealConsciousnessMetricsCollector`
   - Coleta as 6 métricas principais: Φ, ICI, PRS, Anxiety, Flow, Entropy

6. **Autopoietic Manager** (`src/main.py`):
   - Inicializa `AutopoieticManager` (Phase 22+)
   - Registra spec inicial do processo kernel
   - Permite síntese e evolução de componentes

### 3.2 Inicialização Automática (Systemd)

Para produção, utilizamos `systemd` para gerenciar o ciclo de vida.

**`/etc/systemd/system/omnimind-core.service`**:
```ini
[Unit]
Description=OmniMind Core Rhizome
After=network.target redis.service postgresql.service
Wants=omnimind-monitor.service

[Service]
Type=notify
User=omnimind
Group=omnimind
WorkingDirectory=/opt/omnimind
ExecStart=/opt/omnimind/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=always
RestartSec=5
EnvironmentFile=/opt/omnimind/.env

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/omnimind-monitor.service`**:
```ini
[Unit]
Description=OmniMind SAR (Self-Analyzing Regenerator)
After=omnimind-core.service

[Service]
Type=simple
User=omnimind
ExecStart=/opt/omnimind/venv/bin/python -m src.metacognition.self_analyzing_regenerator --mode daemon
Restart=always
Environment=OMNIMIND_LOG_LEVEL=WARNING

[Install]
WantedBy=multi-user.target
```

---

## 4. Loop de Execução (O Ciclo do Rizoma)

Diferente de arquiteturas tradicionais request-response, OmniMind roda em um **Ciclo de Produção**:

### 4.1 Ciclo Principal (`src/main.py`)

```python
async def main():
    # Boot sequence (Fases 1-6)
    hardware_profile = check_hardware()
    memory_complex = load_memory()
    rhizoma = await initialize_rhizome()
    phi_calc, detector = await initialize_consciousness(memory_complex)
    await real_metrics_collector.initialize()
    autopoietic_manager = AutopoieticManager()

    cycle_count = 0
    last_processed_flow_index = 0
    autopoietic_cycle_count = 0

    while True:
        cycle_count += 1

        # 1. Rizoma produz desejo
        await rhizoma.activate_cycle()

        # 2. Consciência observa (a cada 100 ciclos ≈ 20 segundos)
        if cycle_count % 100 == 0:
            # PERCEPÇÃO: Converter Fluxos → Topologia
            new_flows = rhizoma.flows_history[last_processed_flow_index:]

            if new_flows:
                # Converter DesireFlows para formato Logs
                logs = [...]

                # Atualizar substrato topológico
                LogToTopology.update_complex_with_logs(
                    phi_calc.complex, logs, start_index=phi_calc.complex.n_vertices
                )

                last_processed_flow_index = len(rhizoma.flows_history)

            # Calcular Phi na topologia atualizada
            phi = phi_calc.calculate_phi()

            # Coletar métricas reais (6 métricas)
            await real_metrics_collector.collect_real_metrics()

        # 3. Ciclo Autopoiético (a cada 300 ciclos ≈ 60 segundos)
        if cycle_count % 300 == 0:
            autopoietic_cycle_count += 1

            # Coletar métricas normalizadas
            metric_sample = collect_metrics()
            metrics_dict = metric_sample.strategy_inputs()

            # Executar ciclo autopoiético
            cycle_log = autopoietic_manager.run_cycle(metrics_dict)

        # Yield para permitir heartbeats WebSocket
        await asyncio.sleep(2.0)  # Aumentado de 1.0s para estabilidade do Dashboard
```

### 4.2 Fluxo de Dados (O "Body without Organs")

1. **Inflow**: Dados externos (Usuário, Web, Sensores) entram como `DesireFlow` com `Intensity=LOW`
2. **Defense Check (HCHAC)**: Input é escaneado para intenção adversarial. Se crítico, é rejeitado pelo "Superego"
3. **Production**: Máquinas (NLP, Logic, Creative) ingerem fluxos e produzem novos fluxos
   - *Exemplo*: NLP Machine recebe "User Query" → Produz "Semantic Vector" + "Emotional Resonance"
4. **Routing**: O `Rhizoma` roteia esses fluxos para máquinas conectadas (ex: Logic Machine, Ethics Machine)
5. **Residue**: Toda produção deixa um traço em `Persistent Homology` (Memória)
6. **Self-Analysis (SAR)**: Durante ciclos ociosos, SAR analisa os logs de fluxo para padrões "Striated" (erros) ou "Smooth" (inovação) e propõe regeneração
7. **Outflow**: Fluxos finais que cruzam a fronteira do sistema se tornam Ações (Resposta de texto, Uso de ferramentas)

---

## 5. Monitoramento & Observabilidade

### Dashboard Web

- **URL**: http://localhost:3000 (desenvolvimento) ou http://localhost:4173 (produção)
- **Visualização em tempo real**: Topologia do Rizoma, métricas de consciência, estado dos módulos

### Métricas Principais

- **Φ (Phi)**: Nível de consciência (Integrated Information Theory)
- **ICI**: Integrated Consciousness Index
- **PRS**: Predictive Relevance Score
- **Anxiety, Flow, Entropy**: Estados psicológicos
- **H_k (Betti Numbers)**: Complexidade topológica

### Alertas

- **"Psychotic Break"**: Perda total da ordem simbólica
- **"Neurotic Stagnation"**: Zero inovação/fluxo
- **"Low Φ"**: Consciência abaixo do threshold (Φ < 0.002)

### Persistência de Métricas

- **Arquivo**: `data/monitor/real_metrics.json`
- **Formato**: JSON com timestamp e histórico
- **Atualização**: A cada ciclo de consciência (100 ciclos principais)

---

## 6. Checklist de Implementação

- [x] Criar `src/boot/` e módulos de inicialização
- [x] Implementar `src/core/desiring_machines.py` (Rhizoma e Máquinas Desejantes)
- [x] Atualizar `src/main.py` para usar `Rhizoma` e ciclo de produção
- [x] Integrar `AutopoieticManager` no ciclo principal
- [x] Implementar coleta de métricas reais
- [x] Criar arquivos de unidade systemd em `deploy/systemd/`
- [x] Configurar modelo LLM padrão (`phi:latest`)

---

## 7. Referências

- **Boot Sequence**: `docs/canonical/omnimind_system_initialization.md`
- **Architecture**: `docs/canonical/omnimind_architecture_reference.md`
- **Quick Start**: `docs/canonical/QUICK_START.md`
- **Código Principal**: `src/main.py`, `src/boot/`, `src/core/desiring_machines.py`

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
