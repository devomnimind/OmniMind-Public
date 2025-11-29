# 🎯 QUICK REFERENCE - Correção de Loop Infinito em Testes

## O Problema
```
❌ test_loop_produces_improving_phi TIMEOUT (30s+)
❌ 29.098 linhas de output (vs 9k esperado)
❌ Cross-prediction logging infinito
```

## A Solução
```bash
1. Reduzir ciclos de teste:        20 → 5 ciclos
2. Adicionar timeout global:       pytest.ini --timeout=30
3. Marcar testes lentos:           @pytest.mark.slow
4. Instalar plugin:                pip install pytest-timeout
```

## Como Usar

### Testes Rápidos (Padrão)
```bash
pytest tests/consciousness/ --timeout=30
# Resultado: 97 testes em < 30 segundos
```

### Testes Completos (Inclui Slow)
```bash
pytest tests/consciousness/ --timeout=30 -m "not slow"
# Resultado: 103 testes (sem slow)
```

### Apenas Testes Lentos
```bash
pytest tests/consciousness/ -m "slow"
# Resultado: 3 testes para validação completa
```

## Arquivos Alterados
| Arquivo | Mudança |
|---------|---------|
| pytest.ini | +`--timeout=30` |
| test_integration_loop.py | 20 → 5 ciclos |
| test_contrafactual.py | 15 → 5 ciclos |
| test_integration_loss.py | Ciclos + @slow |

## Resultados
✅ Tempo: 10.65s (vs 30+ timeout)  
✅ Output: -69% (29k → 9k linhas)  
✅ Testes: 297/300 passando  
✅ Timeout: 0 (vs 5+ antes)

## Versão
v1.17.8 - 29 Nov 2025  
Commit: f3d68915

