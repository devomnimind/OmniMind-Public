# 📋 Scripts de Teste e Markers Pytest - Referência Técnica

**Última Atualização**: 08 de Dezembro de 2025  
**Status**: ✅ Documentação Ativa  
**Objetivo**: Referência técnica consolidada para scripts de teste e markers pytest

---

## 🎯 Scripts de Teste Ativos

### Scripts Principais

| Script | Localização | Escopo | Tempo Estimado | GPU | Servidor | Markers Incluídos |
|--------|------------|--------|----------------|-----|----------|-------------------|
| `run_tests_fast.sh` | `scripts/run_tests_fast.sh` | 3996 testes | 10-15 min | ✅ Forçada | ❌ Não | Unitários + `@real` (sem `@chaos`) |
| `run_tests_with_defense.sh` | `scripts/run_tests_with_defense.sh` | 4004 testes | 45-90 min | ✅ Forçada | ❌ Não | Todos (inclui `@chaos`) |
| `quick_test.sh` | `scripts/quick_test.sh` | 4004 testes | 30-45 min | ✅ Forçada | ✅ Sim | Todos (inclui `@chaos`) |

**Nota**: Todos os scripts forçam GPU via `CUDA_VISIBLE_DEVICES=0` e `OMNIMIND_FORCE_GPU=true`.

---

## 🏷️ Markers Pytest Registrados

**Arquivo de Configuração**: `config/pytest.ini` e `pyproject.toml`

### Markers Padrão

| Marker | Descrição | Uso |
|--------|-----------|-----|
| `@pytest.mark.asyncio` | Testes assíncronos | Marca testes com `async/await` |
| `@pytest.mark.slow` | Testes longos | Testes com timeout >30s (excluídos de `run_tests_fast.sh`) |
| `@pytest.mark.security` | Testes de segurança | Suites focadas em segurança |
| `@pytest.mark.parallel` | Testes paralelos | Testes que podem rodar em paralelo |
| `@pytest.mark.serial` | Testes seriais | Testes que devem rodar sequencialmente |
| `@pytest.mark.mock` | Testes mockados | Testes com `@patch` decorators |
| `@pytest.mark.semi_real` | Testes semi-reais | Sem `@patch` mas sem integração LLM completa |
| `@pytest.mark.real` | Testes reais | GPU+LLM+Network integration (mede métricas reais) |
| `@pytest.mark.chaos` | Chaos engineering | Testes que destroem servidor intencionalmente |

### Comportamento por Script

| Script | `@pytest.mark.slow` | `@pytest.mark.real` | `@pytest.mark.chaos` | `@pytest.mark.real + @chaos` |
|--------|---------------------|---------------------|---------------------|------------------------------|
| `run_tests_fast.sh` | ❌ Excluído | ✅ Incluído (sem `@chaos`) | ❌ Excluído | ❌ Excluído |
| `run_tests_with_defense.sh` | ❌ Excluído | ✅ Incluído | ✅ Incluído | ✅ Incluído |
| `quick_test.sh` | ❌ Excluído | ✅ Incluído | ✅ Incluído | ✅ Incluído |

---

## ⏱️ Configuração de Timeout

**Arquivo**: `config/pytest.ini`

- **Timeout por teste**: 800 segundos (13.3 minutos máximo por teste individual)
- **Método**: Thread-based (interrupção segura)
- **Sem timeout de sessão**: Cada teste recebe alocação completa de 800s

**Override de timeout específico**:
```python
@pytest.mark.slow
@pytest.mark.timeout(60)  # Override: este teste específico tem max 60s
async def test_long_operation():
    await some_operation()
```

---

## 📊 Estrutura de Testes

### Categorias de Testes

1. **Unitários/Integração Mockados** (sem markers)
   - Testes rápidos com mocks
   - Incluídos em todos os scripts
   - ~3900+ testes

2. **Testes Reais (`@pytest.mark.real` sem `@chaos`)**
   - GPU+LLM+Network integration
   - Não destrutivos
   - ~11 testes
   - Incluídos em `run_tests_fast.sh`

3. **Testes de Chaos Engineering (`@pytest.mark.real + @pytest.mark.chaos`)**
   - Destroem servidor intencionalmente
   - Validam resiliência de Φ após crashes
   - ~8 testes
   - Apenas em `run_tests_with_defense.sh` e `quick_test.sh`

---

## 🔧 Referências Técnicas

- **Configuração Pytest**: `config/pytest.ini`
- **Markers Registrados**: `pyproject.toml`
- **Server State Manager**: `tests/server_state_manager.py`
- **Documentação Completa**: `docs/canonical/TESTING_QUICK_START.md`

---

## ✅ Status de Consolidação

- ✅ Markers registrados em `pytest.ini` e `pyproject.toml`
- ✅ Scripts ativos documentados e validados
- ✅ Nenhuma referência a scripts obsoletos
- ✅ Comportamento de markers consistente entre scripts
- ✅ Timeout configurado corretamente

---

**Última Validação**: 2025-12-08  
**Status**: ✅ Documentação Atualizada e Consolidada
