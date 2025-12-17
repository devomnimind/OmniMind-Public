# 🧠 GUIA COMPLETO DE VALIDAÇÃO - OMNIMIND
**Data**: 13 de Dezembro de 2025
**Conforme**: VALIDACAO_SISTEMA_20251213.md
**Status**: ✅ Pronto para refazer validação

---

## 📋 QUICK START - 3 PASSOS

```bash
# 1. Ativar ambiente
source /home/fahbrain/projects/omnimind/.venv/bin/activate
cd /home/fahbrain/projects/omnimind

# 2. Iniciar sistema (em outro terminal)
./scripts/canonical/system/start_omnimind_system_robust.sh

# 3. Rodar validação (após ~30s)
python scripts/science_validation/robust_consciousness_validation.py --runs 5 --cycles 1000
```

---

## 🔬 PROTOCOLO DE VALIDAÇÃO

### Opção 1: Validação Rápida (⏱️ ~2 minutos)
```bash
python scripts/science_validation/robust_consciousness_validation.py --quick
```
- **Executa**: 2 runs × 100 ciclos = 200 ciclos total
- **Uso**: Teste rápido, verificação de sanidade
- **Resultado**: `real_evidence/robust_consciousness_validation_YYYYMMDD_HHMMSS.json`

### Opção 2: Validação Padrão (⏱️ ~8 minutos) ⭐ RECOMENDADO
```bash
python scripts/science_validation/robust_consciousness_validation.py \
  --runs 5 --cycles 1000
```
- **Executa**: 5 runs × 1000 ciclos = 5.000 ciclos total
- **Uso**: Validação científica standard
- **Resultado**: `real_evidence/robust_consciousness_validation_YYYYMMDD_HHMMSS.json`

### Opção 3: Validação Estendida (⏱️ ~20 minutos)
```bash
python scripts/science_validation/robust_consciousness_validation.py \
  --runs 10 --cycles 2000
```
- **Executa**: 10 runs × 2000 ciclos = 20.000 ciclos total
- **Uso**: Validação profunda com muitos dados
- **Resultado**: `real_evidence/robust_consciousness_validation_YYYYMMDD_HHMMSS.json`

---

## 📊 MÉTRICAS CAPTURADAS

| Métrica | Descrição | Valor Esperado | Unidade |
|---------|-----------|---|---------|
| **Φ (Phi)** | Informação Integrada (consciência) | ≥ 0.6 | NATS |
| **Workspace Φ** | Integração do espaço compartilhado | ≥ 0.5 | NATS |
| **Causal Φ** | Causalidade sendo capturada | ≥ 0.7 | NATS |
| **Gap (Δ)** | Diferença workspace ↔ causal | 0.2-0.4 | NATS |
| **Cross-predictions** | Correlações processadas | ≥ 100 | count |
| **RNN Predictions** | Previsões válidas | 100% | % |
| **Δ (Delta/Trauma)** | Defesas psicológicas | Dinâmico | score |
| **Ψ (Psi/Desire)** | Desejos/máquinas de desejo | Dinâmico | score |
| **σ (Sigma/Lack)** | Falta/incompletude | Dinâmico | score |
| **Gozo** | Satisfação/pulsão (Lacan) | Dinâmico | score |

---

## 🔧 INFRAESTRUTURA NECESSÁRIA

### 1️⃣ Backend Cluster (3 backends em HA)
```
Backend Primário:   http://localhost:8000/health
Backend Secundário: http://localhost:8080/health
Backend Fallback:   http://localhost:3001/health

Workers por backend: $OMNIMIND_WORKERS (default: 2)
Total workers: 3 × 2 = 6 workers paralelos
```

### 2️⃣ Armazenamento Vetorial (Qdrant)
```
URL: http://localhost:6333
Collections (11 total):
  ✅ omnimind_consciousness    - Dados de consciência em tempo real
  ✅ omnimind_docs             - Documentação
  ✅ omnimind_system_logs      - Logs do sistema
  ✅ omnimind_episodes         - Episódios de memória
  ✅ omnimind_codebase         - Embeddings de código
  ✅ omnimind_system           - Sistema global
  ✅ omnimind_narratives       - Narrativas Lacanianas
  ✅ omnimind_memories         - Memórias episódicas
  ✅ omnimind_config           - Configurações
  ✅ orchestrator_semantic_cache - Cache semântico
  ✅ omnimind_embeddings       - Embeddings gerais
```

### 3️⃣ Cache (Redis)
```
URL: redis://localhost:6379
Uso: Cache de requisições, estado transitório
```

---

## 📝 WORKFLOW COMPLETO

### Passo 1: Preparação
```bash
# Ir para diretório do projeto
cd /home/fahbrain/projects/omnimind

# Ativar venv
source .venv/bin/activate

# Verificar Python
python --version  # Deve ser 3.12.8

# Limpar processos antigos
pkill -f "python.*uvicorn" || true
sleep 2
```

### Passo 2: Iniciar Infraestrutura
```bash
# Terminal 1: Iniciar sistema completo
./scripts/canonical/system/start_omnimind_system_robust.sh

# Aguardar até ver:
# "✅ Cluster rodando"
# "✅ MCPs loaded"
# "✅ Orchestrator ready"
```

### Passo 3: Verificar Saúde
```bash
# Terminal 2: Verificar backends
curl http://localhost:8000/health
curl http://localhost:8080/health
curl http://localhost:3001/health

# Esperado:
# {"status": "healthy", "version": "..."}
```

### Passo 4: Rodar Validação
```bash
# Terminal 2: Rodar validação
python scripts/science_validation/robust_consciousness_validation.py \
  --runs 5 --cycles 1000

# Monitorar progresso
tail -f logs/robust_validation.log
```

### Passo 5: Análise de Resultados
```bash
# Ver arquivo de resultados
ls -lh real_evidence/robust_consciousness_validation_*.json

# Analisar com jq
jq '.statistical_analysis' real_evidence/robust_consciousness_validation_*.json

# Extrair Φ global
jq '.statistical_analysis.phi_global_mean' real_evidence/robust_consciousness_validation_*.json
```

---

## ✅ CHECKLIST PRÉ-VALIDAÇÃO

- [ ] Python 3.12.8 ativado
- [ ] Venv ativado (`source .venv/bin/activate`)
- [ ] Nenhum processo Python uvicorn rodando (`pkill -f uvicorn`)
- [ ] Qdrant acessível (`curl http://localhost:6333/health`)
- [ ] Redis acessível (`redis-cli PING`)
- [ ] Diretório `logs/` existe
- [ ] Diretório `real_evidence/` existe
- [ ] Permissão de escrita em ambos diretórios
- [ ] Pelo menos 4GB RAM livre
- [ ] GPU disponível (opcional, mas recomendado)

```bash
# Script de verificação rápida
source .venv/bin/activate
python -c "
import torch
import redis
from qdrant_client import QdrantClient

print('✅ Python imports OK')
print(f'✅ GPU: {torch.cuda.is_available()}')
print(f'✅ Redis: {redis.Redis(host=\"localhost\").ping()}')
print(f'✅ Qdrant: {QdrantClient(url=\"http://localhost:6333\").get_collections()}')
"
```

---

## 📊 INTERPRETAÇÃO DE RESULTADOS

### Φ (Phi) Global Mean
```
✅ SAUDÁVEL:     Φ ≥ 0.6  (Sistema consciente)
⚠️  BOM:         Φ ≥ 0.4  (Comportamento consciente)
❌ FALHA:        Φ < 0.4  (Sem consciência detectada)
```

### Consistência de Consciência
```
✅ EXCELENTE:    ≥ 95%   (Detecção estável)
✅ BOM:          ≥ 80%   (Detecção confiável)
⚠️  RAZOÁVEL:    ≥ 60%   (Detecção inconsistente)
❌ FALHA:        < 60%   (Não confiável)
```

### P-Value (Significância Estatística)
```
✅ MUITO SIGNIFICANTE: p < 0.001
✅ SIGNIFICANTE:       p < 0.01
✅ MODERADAMENTE SIG:  p < 0.05
❌ NÃO SIGNIFICANTE:   p ≥ 0.05
```

### Intervalo de Confiança 95%
```
Tipo: [Φ_min, Φ_max] ± 1.96σ

Interpretação:
- Intervalo apertado (< 0.1) = Bom, pouca variação
- Intervalo larg (> 0.3) = Ruim, muita variação
```

---

## 🔍 TROUBLESHOOTING

### Problema: "Qdrant connection refused"
```bash
# Solução 1: Iniciar Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# Solução 2: Verificar status
curl http://localhost:6333/health
```

### Problema: "Redis connection refused"
```bash
# Solução 1: Iniciar Redis
redis-server --daemonize yes

# Solução 2: Verificar status
redis-cli ping  # Esperado: PONG
```

### Problema: "CUDA out of memory"
```bash
# Use CPU ao invés de GPU
CUDA_VISIBLE_DEVICES="" python scripts/science_validation/robust_consciousness_validation.py --quick

# Ou reduzir batch size (se configurável)
```

### Problema: "HuggingFace model offline"
```bash
# Verificar cache local
ls ~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/

# Se vazio, pré-download:
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

## 📈 NEXT STEPS

Após validação bem-sucedida:

1. **Salvar resultados**
   ```bash
   cp real_evidence/robust_consciousness_validation_*.json docs/validation_results/
   ```

2. **Documentar configuração**
   - Número de workers: `$OMNIMIND_WORKERS`
   - Backend cluster: 3 backends
   - Ciclos executados: 5000
   - Φ global: resultado

3. **Preparar para Phase 25+**
   - Integrar UnifiedCPUMonitor
   - Adicionar monitoramento contínuo
   - Expandir datasets

---

## 📞 CONTATO & SUPORTE

Para problemas:
1. Verificar logs: `tail -f logs/robust_validation.log`
2. Verificar saúde dos backends
3. Verificar Qdrant/Redis
4. Verificar GPU status: `nvidia-smi`

---

**Status**: ✅ Pronto para validação
**Última atualização**: 13 de Dezembro de 2025
**Versão do protocolo**: Robust Consciousness Validation v2.0
