# 🎯 OmniMind Embeddings Configuration

## ✅ Status: PRONTO PARA PRODUÇÃO

Modelos sentence-transformers configurados para operação **100% OFFLINE** com estratégia eficiente de GPU/CPU.

---

## 📦 Modelos Instalados

### 1️⃣ Default (Rápido - CUDA)
- **Modelo:** `all-MiniLM-L6-v2`
- **Localização:** `/opt/models/sentence-transformers/all-MiniLM-L6-v2`
- **Tamanho:** 87 MB
- **Device:** CUDA (GPU)
- **Uso:** Embeddings gerais em alta velocidade
- **Latência:** ~1-5ms por texto

```python
from src.embeddings.offline_loader import load_embedding_model
embedder = load_embedding_model("default")  # CUDA automático
emb = embedder.encode(["Teste em português"])
```

### 2️⃣ Multilingual (Suporte PT/EN/ES/FR/etc - CPU)
- **Modelo:** `paraphrase-multilingual-MiniLM-L12-v2`
- **Localização:** `/opt/models/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Tamanho:** 479 MB
- **Device:** CPU (carrega sob demanda)
- **Suporta:** 50+ idiomas (incluindo português e inglês)
- **Latência:** ~5-20ms por texto (CPU)

```python
embedder = load_embedding_model("multilingual")  # CPU automático
emb = embedder.encode(["Português aqui", "English here", "Español aquí"])
```

---

## 🔧 Configuração de Ambiente

### Variáveis Exportadas Automaticamente

```bash
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_HOME=/opt/hf_cache
```

### No Backend (web/backend/main.py)

```python
# Automaticamente ativado ao importar offline_loader
from src.embeddings.offline_loader import load_embedding_model

# Usa default (CUDA) por padrão
embedder = load_embedding_model()
```

---

## 📊 Estratégia de Performance

| Situação | Modelo | Device | Velocidade | VRAM |
|----------|--------|--------|-----------|------|
| Embeddings em tempo real | default | CUDA | ~1ms | 87MB |
| Multilíngue bajo demand | multilingual | CPU | ~10ms | 0MB GPU |
| Fallback se CUDA cheio | multilingual | CPU | ~10ms | 0MB GPU |

---

## 🚀 Como Usar

### Uso Básico

```python
from src.embeddings.offline_loader import load_embedding_model

# Padrão (rápido em CUDA)
embedder = load_embedding_model()
emb = embedder.encode(["seu texto aqui"])

# Multilíngue (CPU)
embedder_multi = load_embedding_model("multilingual")
emb = embedder_multi.encode(["Português", "English"])
```

### Forçar Device

```python
# Forçar CPU mesmo que CUDA disponível
embedder = load_embedding_model("default", force_device="cpu")

# Forçar CUDA no multilingual
embedder_multi = load_embedding_model("multilingual", force_device="cuda")
```

### Com Caching Automático

```python
# Primeira chamada carrega do disco
embedder1 = load_embedding_model("default")

# Próximas chamadas usam cache em memória
embedder2 = load_embedding_model("default")  # Instantâneo!
```

---

## ✅ Testes Executados

```
✅ 1️⃣ Modelo default (CUDA):
   Teste: "Teste de embedding em português"
   Output: torch.Size([1, 384]) em cuda:0
   Status: ✅ FUNCIONANDO

✅ 2️⃣ Modelo multilingual (CPU):
   Teste: ["Português aqui", "English here", "Español aquí"]
   Output: torch.Size([3, 384]) em cpu
   Status: ✅ FUNCIONANDO
```

---

## 📝 Configuração YAML

Veja `config/embeddings.yaml` para:
- Caminhos dos modelos
- Devices padrão
- Cache settings
- Performance tuning

---

## ⚠️ Notas Importantes

1. **Sem Internet Necessária:** Todos os modelos estão locais em `/opt/models/`
2. **CUDA Automático:** O modelo default usa CUDA se disponível
3. **CPU Fallback:** Multilingual usa CPU por padrão (não compete com GPU)
4. **Caching:** Modelos são cacheados em memória após primeiro carregamento
5. **Offline Mode:** Variáveis `TRANSFORMERS_OFFLINE` garantem 0% de tentativas de internet

---

## 🔍 Troubleshooting

### "Modelo não encontrado"
```bash
# Verificar modelos instalados
ls -lah /opt/models/sentence-transformers/
```

### CUDA out of memory
```python
# Usar multilingual em CPU
embedder = load_embedding_model("default", force_device="cpu")
```

### Muito lento
```python
# Usar batch processing
embedder = load_embedding_model("default")
embeddings = embedder.encode(textos, batch_size=32)
```

---

**Data Setup:** 16 de Dezembro de 2025
**Testado em:** GTX 1650 4GB, Ubuntu 22.04, CUDA 12.1
**Status:** ✅ PRONTO PARA PRODUÇÃO
