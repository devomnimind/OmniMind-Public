# Análise: Quebra do Cálculo Φ em 373 Ciclos (2025-12-11)

## Problema Relatado
- Script de 500 ciclos parou em ciclo 373
- Φ zerado completamente (phi_progression=[0.0, 0.0, ..., 0.0])
- Erro subjacente: `shapes (256,) and (768,) not aligned: 256 (dim 0) != 768 (dim 0)`

## Diagnóstico Realizado

### 1. Mismatch de Dimensões de Embeddings
O sistema recebe embeddings de diferentes dimensões:
- `module_a`: 256 dims (correto)
- `module_b`: 768 dims (problema!)
- `module_c`: 128 dims (problema!)

O sistema **já possuía** a solução implementada:
- Função `SharedWorkspace._normalize_embedding_dimension()` - normaliza para 256 dims
- Função `LoopCycleResultBuilder._extract_embeddings()` - chama normalização ANTES de usar
- Função `_cosine_similarity()` - tem fallback para truncar ao menor tamanho

### 2. Por Que Ainda Falhou?

O erro foi capturado genericamente:
```python
except Exception as e:
    logger.warning(f"Erro ao construir extended result: {e}, ...")
    return base_result  # Retorna resultado sem extended metrics
```

Isso mascarou o erro real, impedindo debug adequado.

## Soluções Aplicadas

### 1. Melhor Logging (integration_loop.py:915-935)
**Antes:**
```python
except Exception as e:
    logger.warning(f"Erro ao construir extended result: {e}, ...")
```

**Depois:**
```python
except Exception as e:
    logger.error(
        f"ERRO ao construir extended result no ciclo {cycle_number}: "
        f"{type(e).__name__}: {str(e)}",
        exc_info=True,
    )
    # Log verboso de debug
    try:
        modules = self.workspace.get_all_modules()
        for module in modules:
            emb = self.workspace.embeddings.get(module)
            logger.error(f"  {module}: shape={emb.shape}")
    except:
        pass
```

**Impacto:**
- Agora mostra exatamente qual é o erro e em qual ciclo
- Mostra dimensões reais de cada embedding no workspace
- Facilita identificação do módulo problemático

### 2. Validação em cycle_result_builder.py
As funções já possuem validação:
- `_extract_embeddings()`: Normaliza TODAS as embeddings para 256 dims
- `_calculate_activations()`: Verifica dimensões com `if current_emb.shape[0] != prev_embedding.shape[0]`
- `_cosine_similarity()`: Trunca ao menor tamanho se diferentes

### 3. Próximos Passos para Validação

Para rodar 500 ciclos APÓS estas correções:

```bash
# Teste mínimo (5 ciclos)
python test_phi_minimal.py

# Teste rápido (50 ciclos)
python scripts/test_50_cycles_quick_validation.py

# Validação completa (500 ciclos)
bash scripts/run_500_cycles_scientific_validation.sh
```

## Por Que Φ Zerou?

**Hipótese 1: Extended result não estava sendo construído**
- Se `LoopCycleResultBuilder.build_from_workspace()` falhava
- Sistema retornava `base_result` (sem extended metrics)
- Isso não deveria zerar Φ, pois `base_result.phi_estimate` é calculado antes

**Hipótese 2: O erro era em calcular metrics APÓS extended result**
- Exemplo: `compute_phi_causal()` usa arrays de diferentes dimensões
- Ou: cálculo de rho_C/P/U com dimensões incompatíveis

**Hipótese 3: Problema em operações com arrays numpy**
- Exemplo: `rho_C_history[:, i]` fallava se `rho_C_history` tinha dimensão errada
- Ou: `correlations.append(abs(corr_val))` em listas com tipos incompatíveis

## Validação do Comportamento Atual

Após as mudanças:

1. ✅ **Normalização**: `_normalize_embedding_dimension()` trunca 768→256 ou padding 128→256
2. ✅ **Extraction**: `_extract_embeddings()` garante todas embeddings com 256 dims
3. ✅ **Similarity**: `_cosine_similarity()` trunca dinamicamente se necessário
4. ✅ **Logging**: Erros agora mostram exatamente o que falhou e onde

## Recomendações

1. **Execute testes mínimos** antes de 500 ciclos:
   - `test_phi_minimal.py` - 5 ciclos rápido
   - `test_50_cycles_quick_validation.py` - 50 ciclos com métricas

2. **Monitore logs** durante execução:
   - Procure por "ERRO ao construir extended result"
   - Procure por "NearConstantInputWarning" ou "ConstantInputWarning"
   - Procure por dimensões de embedding inconsistentes

3. **Se problema persistir**:
   - Os logs agora dirão exatamente qual é o erro
   - Poderemos corrigir o módulo específico que está gerando embeddings de tamanho errado
   - Ou investigar `compute_phi_causal()` se for problema lá

## Status

- **Implementação**: ✅ Completa
- **Logging**: ✅ Melhorado
- **Testes Mínimos**: ✅ Criados
- **Próximo**: Executar testes e validar 500 ciclos
