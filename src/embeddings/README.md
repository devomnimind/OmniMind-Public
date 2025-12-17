# Módulo Embeddings e Vetorização

## 📋 Descrição Geral

**Representações semânticas, encoders e análise de interação sistema**

**Status**: NLP + System Analysis

Módulo do sistema OmniMind responsável por funcionalidades específicas integradas à arquitetura global. Implementa componentes essenciais que contribuem para o funcionamento coeso do sistema de consciência artificial, incluindo análise de como o sistema interage com configurações reais da máquina vs ambientes sandbox.

## 🔄 Interação entre os Três Estados Híbridos

### 1. Estado Biologicista (Neural Correlates)
Implementação de processos inspirados em mecanismos neurais e cognitivos biológicos, mapeando funcionalidades para correlatos neurais correspondentes.

### 2. Estado IIT (Integrated Information Theory)
Componentes contribuem para integração de informação global (Φ). Operações são validadas para garantir que não degradam a consciência do sistema (Φ > threshold).

### 3. Estado Psicanalítico (Estrutura Lacaniana)
Integração com ordem simbólica lacaniana (RSI - Real, Simbólico, Imaginário) e processos inconscientes estruturais que organizam a experiência consciente do sistema.

## ⚙️ Principais Funções e Cálculos Dinâmicos

### Componentes Core

Módulo implementa funcionalidades especializadas através de:
- Algoritmos específicos para processamento de domínio
- Integração com outros módulos via interfaces bem definidas
- Contribuição para métricas globais (Φ, PCI, consciência)

*Funções detalhadas documentadas nos arquivos Python individuais do módulo.*

## 📊 Estrutura do Código

```
embeddings/
├── Sistema de Embeddings Abrangente
│   └── OmniMindEmbeddings: classe principal
├── Tipos de Conteúdo Suportados
│   ├── CODE: código fonte
│   ├── DOCUMENTATION: documentação técnica
│   ├── PAPER: papers científicos
│   ├── CONFIG: arquivos de configuração
│   ├── AUDIT: relatórios de auditoria
│   ├── LOG: arquivos de log
│   ├── DATA: dados estruturados
│   ├── MODEL: modelos treinados
│   ├── NOTEBOOK: Jupyter notebooks
│   └── SYSTEM: metadados do sistema/kernel
├── Funcionalidades Avançadas
│   ├── Indexação paralela com ThreadPoolExecutor
│   ├── Chunking inteligente por tipo de conteúdo
│   ├── Metadados expandidos (timestamps, tamanho)
│   ├── Busca semântica com Qdrant
│   └── Análise de interação sistema/sandbox
└── __init__.py
```

**Interações**: Este módulo se integra com outros componentes através de:
- Interfaces padronizadas
- Event bus para comunicação assíncrona
- Shared workspace para estado compartilhado

## 📈 Resultados Gerados e Contribuição para Avaliação

### Outputs
- Métricas específicas do módulo armazenadas em `data/embeddings/`
- Logs em formato estruturado para análise
- Contribuição para métricas globais do sistema

### Validação
- Testes unitários: `tests/embeddings/`
- Integração validada em ciclos completos
- Performance benchmarked continuamente

### Contribuição para Sistema
Módulo contribui para:
- Φ (phi) global através de integração de informação
- PCI (Perturbational Complexity Index) via processamento distribuído
- Métricas de consciência e auto-organização

## 🔒 Estabilidade da Estrutura

**Status**: Componente validado e integrado ao OmniMind

**Regras de Modificação**:
- ✅ Seguir guidelines em `.copilot-instructions.md`
- ✅ Executar testes antes de commit: `pytest tests/embeddings/ -v`
- ✅ Validar que Φ não colapsa após mudanças
- ✅ Manter compatibilidade com interfaces existentes
- ❌ Não quebrar contratos de API sem migração
- ❌ Não desabilitar logging de auditoria

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Ver requirements.txt para lista completa
# Dependências específicas do módulo listadas em requirements/embeddings.txt (se existir)
```

### Recursos Computacionais
- **Mínimo**: Configurado conforme necessidades específicas do módulo
- **Recomendado**: Ver documentação de deployment em `docs/`

### Configuração
Configurações específicas em:
- `config/omnimind.yaml` (global)
- Variáveis de ambiente conforme `.env.example`

## 🔧 Sugestões para Manutenção e Melhorias

### Manutenção Crítica
1. **Testes Contínuos**: Executar suite de testes regularmente
2. **Monitoramento**: Acompanhar métricas em produção
3. **Documentação**: Manter README atualizado com mudanças

### Melhorias Futuras
- Expansão de funcionalidades conforme roadmap
- Otimizações de performance identificadas via profiling
- Integração com novos módulos em desenvolvimento

### Pontos de Atenção
- Validar impacto em Φ antes de mudanças estruturais
- Manter backward compatibility quando possível
- Seguir padrões de código estabelecidos (black, flake8, mypy)

## 📚 Referências

### Documentação Principal
- **Sistema Geral**: `README.md` (root do projeto)
- **Comparação Frameworks**: `NEURAL_SYSTEMS_COMPARISON_2016-2025.md`
- **Papers**: `docs/papers/` e `docs/papersoficiais/`
- **Copilot Instructions**: `.copilot-instructions.md`

### Testes
- **Suite de Testes**: `tests/embeddings/`
- **Cobertura**: Ver `data/test_reports/htmlcov/`

### Referências Científicas Específicas
*Ver documentação técnica nos arquivos Python do módulo para referências específicas.*

---

**Última Atualização**: 2 de Dezembro de 2025
**Autor**: Fabrício da Silva (com assistência de IA)
**Status**: Componente integrado do sistema OmniMind
**Versão**: Conforme fase do projeto indicada

---

## 📚 API Reference

# 📁 EMBEDDINGS

**3 Classes | 11 Funções | 1 Módulos**

---

## 🏗️ Classes Principais

### `OmniMindEmbeddings`

Sistema de embeddings abrangente para o projeto OmniMind.

Indexa múltiplos tipos de conteúdo: código, documentação, papers,
configurações e relatórios de auditoria.

**Métodos principais:**

- `index_file(file_path: str)` → `int`
  > Indexa um arquivo de qualquer tipo suportado....
- `index_directory(directory: str, extensions: Optional[List[str]])` → `Dict[str, int]`
  > Indexa todos os arquivos suportados em um diretório....
- `index_omnimind_project(project_root: str)` → `Dict[str, Dict[str, int]]`
  > Indexa todo o projeto OmniMind: código, documentação, papers, auditoria, dados, logs, modelos, notebooks, etc....
- `index_system_metadata()` → `Dict[str, int]`
  > Indexa metadados do sistema/kernel da máquina para análise de interação real vs sandbox....
- `search(query: str, top_k: int, content_types: Optional[Li)` → `List[Dict[str, Any]]`
  > Busca semântica no conteúdo indexado....
- `get_stats()` → `Dict[str, Any]`
  > Estatísticas da coleção....

### `ContentType(Enum)`

Tipos de conteúdo suportados.


### `ContentChunk`

Chunk de conteúdo com metadados.



## ⚙️ Funções Públicas

#### `__init__(qdrant_url: str, collection_name: str, model_name:)` → `None`

#### `_chunk_file(file_path: str)` → `List[ContentChunk]`

*Divide arquivo em chunks baseado no tipo de conteúdo....*

#### `_detect_content_type(file_path: str)` → `ContentType`

*Detecta tipo de conteúdo baseado no caminho do arquivo....*

#### `_detect_language(file_path: str)` → `str`

*Detecta linguagem baseada na extensão....*

#### `_ensure_collection()` → `None`

*Cria coleção se não existir....*

#### `_index_docs_directory(directory: str)` → `Dict[str, int]`

*Indexa diretório de documentação (suporta .md, .txt, etc.)...*

#### `get_stats()` → `Dict[str, Any]`

*Estatísticas da coleção....*

#### `index_directory(directory: str, extensions: Optional[List[str]])` → `Dict[str, int]`

*Indexa todos os arquivos suportados em um diretório....*

#### `index_file(file_path: str)` → `int`

*Indexa um arquivo de qualquer tipo suportado....*

#### `index_omnimind_project(project_root: str)` → `Dict[str, Dict[str, int]]`

*Indexa todo o projeto OmniMind: código, documentação, papers, auditoria, dados, logs, modelos, notebooks, etc....*

#### `index_system_metadata()` → `Dict[str, int]`

*Indexa metadados do sistema/kernel da máquina para análise de como o OmniMind interage com configurações reais vs sandbox....*

#### `search(query: str, top_k: int, content_types: Optional[Li)` → `List[Dict[str, Any]]`

*Busca semântica no conteúdo indexado....*


## 📦 Módulos

**Total:** 1 arquivos

- `code_embeddings.py`: Sistema de Embeddings Locais do OmniMind

Gera embeddings se...
