# Indexação de Embeddings OmniMind

Este script executa a indexação completa ou incremental dos embeddings do projeto OmniMind.

## Pré-requisitos

- Python 3.8+
- Qdrant rodando (docker run -p 6333:6333 qdrant/qdrant)
- Ambiente virtual ativado

## Uso

### Indexação Completa (recomendado na primeira vez)
```bash
python run_indexing.py
```

### Indexação Incremental (só arquivos modificados)
```bash
python run_indexing.py --incremental
```

### Opções Avançadas
```bash
# Paralelização máxima
python run_indexing.py --max-workers 8

# Qdrant em URL diferente
python run_indexing.py --qdrant-url http://localhost:6334

# Coleção customizada
python run_indexing.py --collection minha_colecao
```

## O que é indexado

- **Código fonte**: `src/`, `tests/`, `scripts/`
- **Documentação**: `docs/`, `papers/`, `audit/`
- **Dados**: `data/`, `logs/`, `models/`, `exports/`
- **Sistema**: metadados do kernel, hardware, processos
- **Configurações**: arquivos de config do projeto

## Funcionalidades

- ✅ **Indexação incremental**: só processa arquivos modificados
- ✅ **Paralelização**: múltiplos workers simultâneos
- ✅ **Tipos inteligentes**: chunking otimizado por tipo de conteúdo
- ✅ **Busca semântica**: Qdrant para consultas eficientes
- ✅ **Metadados do sistema**: análise de interação real vs sandbox

## Logs

Os logs são salvos em `logs/embedding_indexing.log` para auditoria.

## Exemplo de Busca

Após indexação, você pode buscar semanticamente:

```python
from src.embeddings.code_embeddings import OmniMindEmbeddings

embeddings = OmniMindEmbeddings()
results = embeddings.search("função de processamento de dados", top_k=5)
for result in results:
    print(f"{result['file_path']}: {result['content'][:100]}...")
```
