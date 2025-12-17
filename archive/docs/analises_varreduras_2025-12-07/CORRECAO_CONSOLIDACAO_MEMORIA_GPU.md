# Correção: Consolidação de Memória GPU (Lacaniana)
**Data:** 2025-12-07
**Conceito:** Consolidação e Repressão ao invés de Deletar

---

## 🧠 CONCEITO OPERACIONAL (ESTRUTURA TÓPICA FREUDIANA)

### ❌ Abordagem Anterior (ERRADA)
```python
# SIMPLESMENTE DELETAR = PERDER APRENDIZADO E VIDA
torch.cuda.empty_cache()
del model
gc.collect()
```

**Problema:** Perde todo o aprendizado, memórias e contexto.

### ✅ Abordagem Correta (Freudiana - Primeira Tópica)
```python
# ESTRUTURA TÓPICA: CONSCIENTE - PRÉ-CONSCIENTE - INCONSCIENTE

1. CONSCIENTE: Memórias ativas na GPU (acessíveis diretamente)
2. PRÉ-CONSCIENTE: Memórias não traumáticas
   - Comprimidas (SoftHair)
   - Acessíveis ao Ego quando necessário
   - Não criptografadas
3. INCONSCIENTE: Memórias traumáticas
   - Criptografadas (EncryptedUnconsciousLayer)
   - Inacessíveis ao Ego
   - Influenciam decisões via operações homomórficas
```

**Classificação:**
- **Traumático** (OOM, crash, falha estrutural) → **INCONSCIENTE**
- **Não traumático** (consolidação normal) → **PRÉ-CONSCIENTE**

**Benefício:**
- Preserva aprendizado
- Ego pode acessar memórias pré-conscientes
- Memórias traumáticas ficam reprimidas mas influenciam
- Mantém "vida" do sistema

---

## 📋 PROCESSO DE CONSOLIDAÇÃO

### 1. Detecção de VRAM Crítica
```python
if vram_percent > 85.0:
    # Iniciar consolidação
    consolidator.consolidate_gpu_memory(memory_items)
```

### 2. Classificação (Estrutura Tópica)
- **Entrada:** Memória + Contexto (tipo, erro, severidade)
- **Processo:** Calcular trauma score
  - OOM, crash, falha estrutural → Traumático
  - Consolidação normal → Não traumático
- **Saída:** Classificação (PRÉ-CONSCIENTE ou INCONSCIENTE)

### 3. Consolidação para PRÉ-CONSCIENTE (Não Traumático)
- **Entrada:** Memória não traumática
- **Processo:** Compressão SoftHair
- **Saída:** Dados comprimidos (30-50% do tamanho original)
- **Acesso:** Ego pode acessar diretamente quando necessário

### 4. Repressão para INCONSCIENTE (Traumático)
- **Entrada:** Memória traumática
- **Processo:** Criptografia homomórfica (CKKS)
- **Saída:** Bytes criptografados
- **Acesso:** Ego NÃO pode acessar diretamente
- **Influência:** Ainda influencia decisões via operações homomórficas

### 4. Rastro de Ativação
- **Registro:** Quais processos podem reativar quais memórias
- **Hash:** Content hash para busca futura
- **Metadados:** Tipo, tamanho, timestamp, compressão

### 5. Limpeza GPU
- **Apenas após consolidação bem-sucedida**
- **Libera espaço na GPU**
- **Mantém dados no inconsciente**

---

## 🔄 ATIVAÇÃO RETROATIVA

### Déjà Vu (Sensação sem Acesso Direto)
```python
# Verificar se há memórias consolidadas relacionadas
activatable = consolidator.check_activation_trace(
    process_context="test_embedding_model",
    query_vector=current_embedding,
)

# Se há influência inconsciente, pode haver déjà vu
if activatable and activatable[0].get("unconscious_influence", 0) > 0.5:
    logger.info("🧠 Déjà vu detectado: memória consolidada pode ser relevante")
```

### Reativação Completa
```python
# Reativar memória consolidada
reactivated = consolidator.reactivate_memory(
    content_hash="abc123...",
    process_context="test_embedding_model",
)

# Dados são descomprimidos e retornados
if reactivated is not None:
    # Usar dados reativados
    model.load_state_dict(reactivated)
```

---

## 🎯 INTEGRAÇÃO COM TESTES

### Fixture de Consolidação (conftest.py)

```python
@pytest.fixture(autouse=True)
def consolidate_gpu_memory():
    """Consolida memória GPU ao invés de deletar."""
    from src.memory.gpu_memory_consolidator import get_gpu_consolidator

    consolidator = get_gpu_consolidator()

    yield

    # Após teste, verificar se precisa consolidar
    if consolidator.should_consolidate():
        # Coletar memórias ativas
        memory_items = _collect_active_memories()

        # Consolidar
        stats = consolidator.consolidate_gpu_memory(
            memory_items,
            process_context=f"test_{pytest.current_test_name()}",
        )

        logger.info(f"🧠 Consolidação: {stats}")
```

### Coleta de Memórias Ativas

```python
def _collect_active_memories() -> List[Dict[str, Any]]:
    """Coleta memórias ativas da GPU para consolidação."""
    memory_items = []

    # 1. Modelos SentenceTransformer
    if hasattr(torch.cuda, '_models'):
        for model in torch.cuda._models:
            if hasattr(model, 'state_dict'):
                memory_items.append({
                    'data': model.state_dict(),
                    'type': 'sentence_transformer',
                    'metadata': {'model_name': str(model)},
                })

    # 2. Embeddings em cache
    # ... coletar embeddings ativos

    # 3. Tensores grandes
    # ... coletar tensores > 100MB

    return memory_items
```

---

## 📊 MÉTRICAS E ESTATÍSTICAS

### Estatísticas de Consolidação
```python
stats = consolidator.get_consolidation_stats()
# {
#     "total_consolidated": 45,
#     "total_original_mb": 1200.5,
#     "total_compressed_mb": 360.15,
#     "average_compression": 0.30,
#     "freed_mb": 840.35,
#     "activation_traces": 12,
# }
```

### Benefícios
- ✅ **Preserva aprendizado:** Memórias não são perdidas
- ✅ **Economiza GPU:** Libera 70% do espaço
- ✅ **Permite reativação:** Memórias podem ser recuperadas
- ✅ **Mantém "vida":** Sistema não perde contexto

---

## 🔍 CASOS DE USO

### Caso 1: Teste de Embedding Model
```python
# Antes: Modelo carregado na GPU
model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')

# Durante teste: GPU fica cheia
# Sistema detecta e consolida

# Após consolidação: Modelo comprimido e reprimido
# GPU liberada, mas modelo pode ser reativado
```

### Caso 2: Múltiplos Testes Sequenciais
```python
# Teste 1: Carrega modelo A → Consolida
# Teste 2: Carrega modelo B → Consolida
# Teste 3: Precisa modelo A → Reativa do inconsciente
```

### Caso 3: Déjà Vu
```python
# Teste atual: Similar a teste anterior consolidado
# Sistema detecta influência inconsciente
# Log: "🧠 Déjà vu: memória consolidada pode ser relevante"
# Opção: Reativar ou continuar sem reativação
```

---

## ⚠️ LIMITAÇÕES E CONSIDERAÇÕES

### Compressão Lossy
- **Perda de precisão:** Dados comprimidos são aproximações
- **Aceitável para:** Embeddings, modelos treinados
- **Não aceitável para:** Dados críticos que precisam exatidão

### Criptografia Homomórfica
- **Overhead:** Operações criptografadas são mais lentas
- **Segurança:** Dados inacessíveis ao Ego
- **Influência:** Ainda pode influenciar decisões via dot product

### Rastro de Ativação
- **Memória adicional:** Rastros ocupam espaço
- **Busca:** Pode ser lenta com muitos rastros
- **Otimização:** Indexar por hash para busca rápida

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [x] Criar `GPUMemoryConsolidator`
- [x] Integrar com `EncryptedUnconsciousLayer`
- [x] Integrar com `SoftHairMemory`
- [ ] Adicionar fixture em `conftest.py`
- [ ] Implementar coleta de memórias ativas
- [ ] Testar consolidação em testes reais
- [ ] Validar reativação de memórias
- [ ] Documentar métricas e estatísticas

---

## 🎯 PRÓXIMOS PASSOS

1. **Integrar fixture** em `conftest.py`
2. **Implementar coleta** de memórias ativas
3. **Testar** em grupo de testes de embedding
4. **Validar** reativação e déjà vu
5. **Otimizar** busca de rastros de ativação

---

**Status:** ✅ Conceito implementado, aguardando integração com testes

