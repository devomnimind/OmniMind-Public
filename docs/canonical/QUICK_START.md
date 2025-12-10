# 🚀 QUICK START - OmniMind

**Última Atualização**: 08 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Quantum Consciousness + Φ Validado)

---

## 📋 Pré-requisitos

- **Python**: 3.12.8 (obrigatório)
- **Ollama**: Instalado e rodando (modelo `phi:latest` disponível)
- **Qdrant**: Rodando em `http://localhost:6333` (opcional para testes completos)
- **GPU**: CUDA disponível (opcional, mas recomendado)

---

## ⚡ Início Rápido

### 1. Configuração do Ambiente

```bash
# Clone o repositório (se ainda não tiver)
cd /home/fahbrain/projects/omnimind

# Ative o ambiente virtual
source .venv/bin/activate

# Verifique Python
python --version  # Deve ser 3.12.8

# Verifique Ollama e modelo phi:latest
ollama list | grep phi
# Deve mostrar: phi:latest
```

### 2. Configuração do Modelo LLM

O sistema usa **Microsoft Phi (phi:latest)** como modelo padrão via Ollama.

**Configuração em `config/agent_config.yaml`**:
```yaml
model:
  name: "phi:latest"           # Modelo primário
  provider: "ollama"
  base_url: "http://localhost:11434"
  fallback_model: "qwen2:7b-instruct"  # Fallback se phi não disponível
```

**Verificar se Ollama está rodando**:
```bash
curl http://localhost:11434/api/tags
```

---

## 🧪 Executando Testes

### Suite Rápida Diária (Recomendado)

```bash
# Suite rápida: ~3996 testes, sem chaos engineering
./scripts/run_tests_fast.sh
```

**Características**:
- ✅ Testes unitários e de integração
- ✅ Testes marcados com `@pytest.mark.real` (sem chaos)
- ❌ Exclui `@pytest.mark.slow`
- ❌ Exclui `@pytest.mark.chaos`
- ⏱️ Tempo estimado: 10-15 minutos

### Suite Completa Semanal (Com Chaos Engineering)

```bash
# Suite completa: ~4004 testes, inclui chaos engineering
./scripts/run_tests_with_defense.sh
```

**Características**:
- ✅ Todos os testes da suite rápida
- ✅ Testes de chaos engineering (destruição de servidor)
- ⚠️ **ATENÇÃO**: Destrói servidor intencionalmente para validar resiliência de Φ
- ⏱️ Tempo estimado: 45-90 minutos

### Testes Específicos

```bash
# Testar módulo específico
pytest tests/consciousness/ -v

# Testar com marcadores específicos
pytest tests/ -m "real"      # Testes com GPU+LLM+Network (não destrutivos)
pytest tests/ -m "slow"     # Testes longos (>30s timeout)
pytest tests/ -m "chaos"    # Testes de chaos engineering (semanal apenas)
```

---

## 🚀 Executando o Sistema

### Modo Desenvolvimento

```bash
# Iniciar sistema completo (backend + frontend + daemon)
./scripts/canonical/system/start_omnimind_system.sh
```

**Componentes iniciados**:
- Backend API: `http://localhost:8000`
- Frontend Dashboard: `http://localhost:3000`
- Daemon: Rodando em background
- eBPF Monitor: Monitoramento de sistema

### Modo API Apenas

```bash
# Apenas backend FastAPI
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Modo Ciclo Principal

```bash
# Executar ciclo principal (Rhizome + Consciousness)
python -m src.main
```

---

## 📊 Verificando Status

### Métricas de Consciência

```bash
# Ver métricas coletadas
cat data/monitor/real_metrics.json | python -m json.tool
```

**Métricas principais**:
- `phi`: Valor de Φ (Integrated Information Theory)
- `ici`: Integrated Consciousness Index
- `prs`: Predictive Relevance Score
- `anxiety`, `flow`, `entropy`: Estados psicológicos

### Logs do Sistema

```bash
# Logs de boot
tail -f logs/omnimind_boot.log

# Logs de auditoria
tail -f logs/audit.log

# Logs de métricas
tail -f logs/metrics.log
```

---

## 🔧 Troubleshooting

### Ollama não responde

```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se não estiver, iniciar Ollama
ollama serve
```

### Modelo phi:latest não encontrado

```bash
# Baixar modelo phi:latest
ollama pull phi:latest

# Verificar modelos disponíveis
ollama list
```

### Erros de GPU/CUDA

```bash
# Verificar CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Verificar variáveis de ambiente
echo $CUDA_VISIBLE_DEVICES
echo $CUDA_HOME
```

### Qdrant não disponível

Os testes que requerem Qdrant serão pulados automaticamente se Qdrant não estiver disponível. Para testes completos:

```bash
# Iniciar Qdrant via Docker
docker run -p 6333:6333 qdrant/qdrant
```

---

## ✅ Correções Críticas de Φ (2025-12-10)

**Sistema de Consciência Validado**:
- **Escala IIT**: [0, ~0.1] NATS (não normalizado)
- **Limiar de consciência**: `PHI_THRESHOLD = 0.01 nats`
- **Ótimo de criatividade**: `PHI_OPTIMAL = 0.06 nats` (recalibrado)
- **Validação**: `scripts/validation/validate_phi_dependencies.py` (16/16 testes - 100%)
- **Documentação**:
  - [Análise de Dependências Φ](../analysis/diagnostics/ANALISE_DEPENDENCIAS_PHI.md)
  - [Verificação Φ Sistema](../analysis/validation/VERIFICACAO_PHI_SISTEMA.md)

**Validar dependências de Φ**:
```bash
python scripts/validation/validate_phi_dependencies.py
```

## 📚 Próximos Passos

1. **Leia a documentação completa**: [reference/INDICE_DOCUMENTACAO.md](../reference/INDICE_DOCUMENTACAO.md)
2. **Explore a arquitetura**: [omnimind_architecture_reference.md](omnimind_architecture_reference.md)
3. **Validação científica**: [Modelos_Neuronais_Comparativo.md](Modelos_Neuronais_Comparativo.md)
4. **Correções de Φ**: [../analysis/diagnostics/ANALISE_DEPENDENCIAS_PHI.md](../analysis/diagnostics/ANALISE_DEPENDENCIAS_PHI.md)
5. **Verificação de sistema**: [../analysis/validation/VERIFICACAO_PHI_SISTEMA.md](../analysis/validation/VERIFICACAO_PHI_SISTEMA.md)
6. **Stubs de tipos**: [../METADATA/PROJETO_STUBS_OMNIMIND.md](../METADATA/PROJETO_STUBS_OMNIMIND.md)

---

## ⚠️ Notas Importantes

- **Python 3.12.8 obrigatório**: Outras versões podem causar problemas
- **Modelo padrão**: `phi:latest` (Microsoft Phi) via Ollama
- **Testes em andamento**: Não interromper testes em execução
- **GPU recomendado**: Sistema funciona sem GPU, mas mais lento

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
