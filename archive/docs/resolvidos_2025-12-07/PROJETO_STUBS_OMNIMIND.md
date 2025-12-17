# 🔧 PROJETO STUBS OMNIMIND

**Data**: 2025-12-07 (última atualização)
**Autor**: Fabrício da Silva + assistência de IA
**Objetivo**: Criar stubs de tipos para bibliotecas externas sem suporte completo de mypy

> **📝 NOTA**: Este documento é atualizado conforme problemas de mypy são identificados durante o desenvolvimento. Problemas de bibliotecas sem suporte devem ser adicionados aqui para criação de stubs posteriormente.

---

## 📋 RESUMO EXECUTIVO

Este projeto visa criar stubs de tipos (`.pyi`) para bibliotecas externas usadas no OmniMind que não possuem suporte completo de tipos ou que geram erros de mypy. Os stubs serão criados como forks dos repositórios originais, adaptados às necessidades do OmniMind.

---

## 🎯 OBJETIVOS

1. **Identificar bibliotecas sem suporte de tipos**
2. **Documentar todas as bibliotecas que precisam de stubs**
3. **Criar plano de fork e desenvolvimento de stubs**
4. **Implementar stubs seguindo padrões do OmniMind**
5. **Integrar stubs no sistema de tipos do projeto**

---

## 📚 BIBLIOTECAS IDENTIFICADAS

### 🔴 CRÍTICAS (Erros de mypy frequentes)

1. **qdrant-client** ⚠️
   - **Problema**: `QdrantClient` não tem atributos reconhecidos pelo mypy
   - **Erros comuns**:
     - `"QdrantClient" has no attribute "search"`
     - `"QdrantClient" has no attribute "query_points"`
     - `"CollectionInfo" has no attribute "vectors_count"` (deve usar `indexed_vectors_count`)
     - `List item 0 has incompatible type "dict[str, object]"; expected "PointStruct"`
   - **Arquivos afetados**: 8 arquivos
     - `integrations/qdrant_integration.py`
     - `integrations/qdrant_adapter.py`
     - `embeddings/code_embeddings.py`
     - `memory/dataset_indexer.py`
     - `memory/semantic_cache.py`
     - `memory/hybrid_retrieval.py`
     - `memory/episodic_memory.py`
     - `memory/consciousness_metrics_indexer.py` (NOVO)
   - **Status**: ⏳ Documentado, aguardando stub
   - **Prioridade**: 🔴 ALTA
   - **Notas**: API tem múltiplas versões (query_points, search, search_points) - stub deve suportar todas

2. **sentence-transformers** ⚠️
   - **Problema**: Tipos incompletos em `SentenceTransformer`
   - **Erro comum**: `"SentenceTransformer" has no attribute "encode"`
   - **Arquivos afetados**: 7 arquivos
     - `autonomous/solution_lookup_engine.py`
     - `embeddings/code_embeddings.py`
     - `memory/semantic_memory_layer.py`
     - `memory/dataset_indexer.py`
     - `memory/semantic_cache.py`
     - `memory/hybrid_retrieval.py`
     - `memory/model_optimizer.py`
   - **Status**: ⏳ Documentado, aguardando stub
   - **Prioridade**: 🔴 ALTA

3. **datasets** (HuggingFace) ⚠️
   - **Problema**: `Module "datasets" has no attribute "load_from_disk"` e `"load_dataset"`
   - **Arquivos afetados**: 1 arquivo
     - `memory/dataset_indexer.py`
   - **Status**: ⏳ Documentado, aguardando stub
   - **Prioridade**: 🔴 ALTA

### 🟡 MÉDIA (Erros ocasionais)

4. **transformers** (HuggingFace)
   - **Problema**: Tipos complexos não totalmente cobertos
   - **Arquivos afetados**: 1 arquivo
     - `integrations/llm_router.py`
   - **Status**: ⏳ Documentado
   - **Prioridade**: 🟡 MÉDIA

5. **torch** (PyTorch)
   - **Problema**: Tipos dinâmicos em operações tensor
   - **Arquivos afetados**: 20 arquivos
   - **Status**: ⏳ Documentado
   - **Prioridade**: 🟡 MÉDIA

6. **numpy** ⚠️
   - **Problema**: Tipos de array dinâmicos e incompatibilidades com `float()`
   - **Erros específicos identificados** (2025-12-07):
     - `Argument 1 to "float" has incompatible type "SupportsDunderLT[Any] | SupportsDunderGT[Any]"; expected "str | Buffer | SupportsFloat | SupportsIndex"` [arg-type]
     - Ocorre em operações como `float(np.clip(...))`, `float(np.linalg.norm(...))`, `float(np.var(...))`
     - MyPy não reconhece que numpy retorna tipos compatíveis com `float()`
   - **Arquivos afetados**: 3 arquivos críticos + 30 arquivos com uso geral
     - `consciousness/gozo_calculator.py` (linha 189: `float(np.clip(novelty, 0.0, 1.0))`)
     - `consciousness/delta_calculator.py` (linha 166: `float(trauma_level)`)
     - `consciousness/cycle_result_builder.py` (linha 139: `float(activation)`)
     - Outros arquivos com operações numpy similares
   - **Operações problemáticas**:
     - `np.clip()` → retorno não reconhecido como `SupportsFloat`
     - `np.linalg.norm()` → retorno não reconhecido como `SupportsFloat`
     - `np.var()` → retorno não reconhecido como `SupportsFloat`
     - `np.mean()` → retorno não reconhecido como `SupportsFloat`
     - Operações aritméticas com arrays numpy → tipos incompatíveis
   - **Workaround atual**: `# type: ignore[arg-type,assignment]` (não ideal)
   - **Status**: ⏳ Documentado, aguardando stub
   - **Prioridade**: 🔴 ALTA (erros frequentes em cálculos de consciência)
   - **Notas**: Stub deve definir tipos de retorno corretos para funções numpy comuns

7. **qiskit** / **qiskit-aer**
   - **Problema**: Tipos não disponíveis
   - **Arquivos afetados**: Múltiplos arquivos em `quantum_consciousness/`
   - **Status**: ⏳ Documentado (já usa `type: ignore[import-untyped]`)
   - **Prioridade**: 🟡 MÉDIA

8. **dbus**
   - **Problema**: Sem stubs disponíveis
   - **Arquivos afetados**: `integrations/dbus_controller.py`
   - **Status**: ⏳ Documentado (já usa `type: ignore`)
   - **Prioridade**: 🟡 MÉDIA

### 🟢 BAIXA (Erros raros ou bem tipados)

9. **pydantic**
   - **Status**: ✅ Geralmente bem tipado
   - **Arquivos afetados**: 1 arquivo
   - **Prioridade**: 🟢 BAIXA

10. **fastapi**
    - **Status**: ✅ Geralmente bem tipado
    - **Arquivos afetados**: 6 arquivos
    - **Prioridade**: 🟢 BAIXA

11. **supabase**
    - **Status**: ⏳ Pode precisar de stubs
    - **Arquivos afetados**: 1 arquivo
    - **Prioridade**: 🟢 BAIXA

12. **redis**
    - **Status**: ⏳ Pode precisar de stubs
    - **Arquivos afetados**: 1 arquivo
    - **Prioridade**: 🟢 BAIXA

---

## 🏗️ ARQUITETURA DO PROJETO STUBS

### Estrutura Proposta

```
omnimind-stubs/
├── README.md
├── setup.py
├── pyproject.toml
├── stubs/
│   ├── qdrant_client/
│   │   └── __init__.pyi
│   ├── sentence_transformers/
│   │   └── __init__.pyi
│   ├── transformers/
│   │   └── __init__.pyi
│   └── ...
└── docs/
    └── DEVELOPMENT.md
```

### Padrão de Stub

```python
# stubs/qdrant_client/__init__.pyi
from typing import Any, List, Optional, Dict
from typing_extensions import Protocol

class QdrantClient:
    def __init__(self, url: str = ..., **kwargs: Any) -> None: ...

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = ...,
        score_threshold: Optional[float] = ...,
        with_payload: bool = ...,
        **kwargs: Any
    ) -> List[Any]: ...

    def get_collection(self, collection_name: str) -> Any: ...

    def create_collection(
        self,
        collection_name: str,
        vectors_config: Any,
        **kwargs: Any
    ) -> None: ...
```

---

## 📝 PLANO DE IMPLEMENTAÇÃO

### FASE 1: Documentação e Mapeamento (Semana 1)

**Objetivos**:
- [x] Identificar todas as bibliotecas sem suporte de tipos
- [x] Documentar erros de mypy por biblioteca
- [ ] Criar lista priorizada
- [ ] Definir padrões de stub

**Deliverables**:
- Este documento (PROJETO_STUBS_OMNIMIND.md)
- Lista completa de bibliotecas
- Padrões de código para stubs

### FASE 2: Setup do Projeto (Semana 1-2)

**Objetivos**:
- [ ] Criar repositório `omnimind-stubs`
- [ ] Configurar estrutura de diretórios
- [ ] Configurar `pyproject.toml` e `setup.py`
- [ ] Criar documentação de desenvolvimento

**Deliverables**:
- Repositório criado
- Estrutura de diretórios
- Configuração de build

### FASE 3: Desenvolvimento de Stubs (Semana 2-4)

**Prioridade 1 - Qdrant Client**:
- [ ] Analisar API completa do QdrantClient
- [ ] Criar stub completo
- [ ] Testar com mypy
- [ ] Documentar

**Prioridade 2 - Sentence Transformers**:
- [ ] Analisar API completa do SentenceTransformer
- [ ] Criar stub completo
- [ ] Testar com mypy
- [ ] Documentar

**Prioridade 3 - Outras bibliotecas**:
- [ ] Implementar conforme necessidade

### FASE 4: Integração (Semana 4-5)

**Objetivos**:
- [ ] Integrar stubs no OmniMind
- [ ] Configurar mypy para usar stubs
- [ ] Validar redução de erros
- [ ] Documentar uso

---

## 🔍 VARREURA DE BIBLIOTECAS

### Processo de Identificação

1. **Análise de Imports**: Buscar todos os imports em `src/`
2. **Análise de Erros MyPy**: Identificar erros relacionados a bibliotecas externas
3. **Verificação de Stubs Existentes**: Verificar se há stubs públicos disponíveis
4. **Priorização**: Classificar por frequência de erro e impacto

### Resultados da Varredura

**Última atualização**: 2025-12-07

#### Erros MyPy Identificados por Biblioteca

**numpy** (2 erros críticos):
- `src/consciousness/gozo_calculator.py:189`: `float(np.clip(...))` - tipo incompatível
- `src/consciousness/cycle_result_builder.py:139`: `float(activation)` - tipo incompatível
- **Padrão**: Operações numpy retornam tipos que mypy não reconhece como compatíveis com `float()`
- **Solução proposta**: Stub deve definir `np.clip()`, `np.linalg.norm()`, etc. como retornando `SupportsFloat`

**qdrant-client** (múltiplos erros):
- Atributos não reconhecidos: `search`, `query_points`, `get_collection`
- Tipos de retorno incompatíveis: `PointStruct` vs `dict[str, object]`

**sentence-transformers** (múltiplos erros):
- Atributo `encode` não reconhecido em `SentenceTransformer`
- Tipos de retorno de embeddings não definidos

---

## 📊 MODELO DE CÓDIGO PARA STUBS

### Stub Numpy (Exemplo - Prioridade Alta)

```python
"""
Stub para numpy - OmniMind.

Este stub corrige problemas de tipagem com operações numpy comuns,
especialmente conversões para float() que mypy não reconhece.

Versão numpy suportada: >=1.20.0
Criado em: 2025-12-07
"""

from typing import Any, SupportsFloat, Union, overload
from typing_extensions import Protocol

# Protocolo para tipos compatíveis com float()
class SupportsFloatConversion(Protocol):
    """Protocolo para tipos que podem ser convertidos para float."""
    def __float__(self) -> float: ...

# Overloads para np.clip
@overload
def clip(
    a: SupportsFloatConversion,
    a_min: float,
    a_max: float,
    out: None = ...,
    **kwargs: Any
) -> float: ...

@overload
def clip(
    a: Any,
    a_min: float,
    a_max: float,
    out: None = ...,
    **kwargs: Any
) -> Any: ...

# Overloads para np.linalg.norm
@overload
def norm(x: SupportsFloatConversion, ord: Any = ..., axis: None = ...) -> float: ...

@overload
def norm(x: Any, ord: Any = ..., axis: Any = ...) -> Any: ...

# Overloads para np.var
@overload
def var(a: SupportsFloatConversion, axis: None = ..., **kwargs: Any) -> float: ...

@overload
def var(a: Any, axis: Any = ..., **kwargs: Any) -> Any: ...

# Overloads para np.mean
@overload
def mean(a: SupportsFloatConversion, axis: None = ..., **kwargs: Any) -> float: ...

@overload
def mean(a: Any, axis: Any = ..., **kwargs: Any) -> Any: ...

# Módulo linalg
class linalg:
    norm = norm  # type: ignore[assignment]
    # ... outros métodos

# Módulo principal
class ndarray:
    """Array numpy."""
    def __float__(self) -> float: ...
    # ... outros métodos

# Exports
__all__ = ["ndarray", "clip", "linalg", "var", "mean"]
```

### Template Base

```python
"""
Stub para [NOME_BIBLIOTECA].

Este stub foi criado para o projeto OmniMind para fornecer
suporte completo de tipos para mypy.

Baseado em: [VERSÃO_ORIGINAL]
Criado em: [DATA]
"""

from typing import Any, List, Optional, Dict, Union, Protocol
from typing_extensions import TypedDict

# Tipos auxiliares
class SomeConfig(TypedDict, total=False):
    """Configuração opcional."""
    key: str
    value: Any

# Classes principais
class MainClass:
    """Classe principal da biblioteca."""

    def __init__(self, param: str = ..., **kwargs: Any) -> None:
        """Inicializa a classe."""
        ...

    def method(self, arg: str) -> Any:
        """Método da classe."""
        ...

# Exports
__all__ = ["MainClass", "SomeConfig"]
```

### Padrões de Nomenclatura

- **Stubs**: `[biblioteca]/__init__.pyi`
- **Tipos auxiliares**: PascalCase (ex: `QdrantConfig`)
- **Métodos**: snake_case (ex: `get_collection`)
- **Atributos**: snake_case (ex: `collection_name`)

### Boas Práticas

1. **Usar `...` para valores padrão**: `def method(self, param: str = ...) -> Any:`
2. **Tipar retornos quando possível**: Preferir tipos específicos a `Any`
3. **Documentar tipos complexos**: Usar `TypedDict` para estruturas de dados
4. **Manter compatibilidade**: Seguir API original da biblioteca
5. **Versionar stubs**: Incluir versão da biblioteca suportada

---

## 🧪 TESTES E VALIDAÇÃO

### Processo de Validação

1. **Teste com MyPy**: Verificar que stubs resolvem erros
2. **Teste de Import**: Verificar que stubs não quebram imports
3. **Teste de Runtime**: Verificar que código funciona em runtime
4. **Validação de Cobertura**: Verificar que todos os métodos usados estão tipados

### Scripts de Validação

```bash
# Validar stub com mypy
mypy --config-file mypy.ini src/ --show-error-codes

# Validar imports
python -c "import [biblioteca]"

# Validar runtime
pytest tests/ -v
```

---

## 📚 REFERÊNCIAS

### Documentação de Stubs

- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [PEP 561 - Distributing and Packaging Type Information](https://www.python.org/dev/peps/pep-0561/)
- [typeshed](https://github.com/python/typeshed) - Stubs oficiais do Python

### Ferramentas

- `mypy` - Type checker
- `pyright` - Type checker alternativo
- `stubgen` - Gerador automático de stubs (base)

---

## 🎯 PRÓXIMOS PASSOS

1. **Completar varredura** de bibliotecas (em andamento)
2. **Priorizar bibliotecas** por impacto
3. **Criar repositório** `omnimind-stubs`
4. **Implementar primeiro stub** (Qdrant Client)
5. **Integrar no OmniMind**

---

**Última Atualização**: 2025-12-07
**Status**: 🟡 EM DESENVOLVIMENTO - Fase 1 (Documentação)

---

## 📝 ATUALIZAÇÕES RECENTES

### [2025-12-07] - Documentação de Problemas MyPy com Numpy

**Problemas identificados**:
- ✅ Erros específicos de mypy com numpy documentados
- ✅ Arquivos críticos identificados (3 arquivos com erros ativos)
- ✅ Operações problemáticas mapeadas (`np.clip`, `np.linalg.norm`, `np.var`, `np.mean`)
- ✅ Workaround atual documentado (`type: ignore[arg-type,assignment]`)

**Próximos passos**:
- [ ] Criar stub para numpy com tipos de retorno corretos
- [ ] Definir protocolos para operações numpy comuns
- [ ] Testar stub com arquivos críticos identificados
- [ ] Integrar stub no projeto OmniMind

**Impacto esperado**:
- Redução de 2 erros críticos de mypy
- Melhoria na tipagem de 30+ arquivos que usam numpy
- Eliminação de workarounds `type: ignore` em cálculos de consciência

