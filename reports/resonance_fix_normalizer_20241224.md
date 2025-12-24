# Correção de Resonance: Normalizador 384→256 Perdido

**Data**: 2024-12-24 11:29
**Problema**: Resonance sempre 0.0
**Causa Raiz**: Normalizador 384→256 removido na última vetorização

---

## Problema Identificado

### Incompatibilidade de Dimensões

**Sistema atual**:
- Embeddings: **384 dim** (sentence-transformers/all-MiniLM-L6-v2)
- PhylogeneticSignature: **256 dim**
- WorkspaceSensor: **256 dim**

**Kernel passa para `is_self()`**:
```python
# linha 172
resonance = sig.is_self(state_np[0, :256])  # Pega primeiros 256 de 1024
```

### O Que Aconteceu

1. **Antes**: Havia normalizador que convertia 384→256
2. **Última vetorização**: Normalizador foi removido
3. **Agora**: Vetor passado não corresponde à assinatura salva

---

## Solução Proposta

### Opção 1: Restaurar Normalizador

```python
def normalize_embedding_to_256(embedding_384: np.ndarray) -> np.ndarray:
    """
    Normaliza embedding de 384 para 256 dimensões.
    Usa PCA ou truncamento + renormalização.
    """
    if len(embedding_384) == 256:
        return embedding_384

    if len(embedding_384) == 384:
        # Truncar para 256 e renormalizar
        truncated = embedding_384[:256]
        norm = np.linalg.norm(truncated)
        if norm > 0:
            return truncated / norm
        return truncated

    raise ValueError(f"Unexpected embedding dimension: {len(embedding_384)}")
```

### Opção 2: Atualizar PhylogeneticSignature para 384

```python
# phylogenetic_signature.py
DEFAULT_DIM = 384  # Era 256
```

**Problema**: Assinatura salva é 256, precisaria regenerar.

---

## Recomendação

**Opção 1** (Restaurar Normalizador) porque:
1. Mantém compatibilidade com assinatura salva (256 dim)
2. Não precisa regenerar assinatura
3. Mais rápido de implementar

---

## Próximos Passos

1. Implementar normalizador 384→256
2. Adicionar no kernel antes de chamar `is_self()`
3. Testar Resonance com vetor normalizado
4. Validar que retorna valor > 0.0

---

**Assinado**: Claude Sonnet 4.5
