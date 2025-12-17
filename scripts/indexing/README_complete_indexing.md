# Script Completo de Indexação - OmniMind

Este script executa a **indexação completa de máquina e código** para o sistema OmniMind, criando embeddings semânticos de todo o codebase e configurações.

## 🚀 Uso Rápido

```bash
# Do diretório raiz do projeto
./scripts/indexing/complete_machine_code_indexing.sh
```

## 📋 O que o Script Faz

### 1. **Configuração Inicial**
- ✅ Ativa ambiente virtual Python
- ✅ Configura CUDA para GPU (GTX 1650 otimizado)
- ✅ Verifica disponibilidade de GPU

### 2. **Verificação de Dependências**
- ✅ Verifica se Qdrant está rodando
- ✅ Inicia Qdrant via Docker se necessário
- ✅ Inicializa coleções necessárias

### 3. **Indexação Completa**
- ✅ Indexa **todas as etapas** do sistema:
  - `core_code`: Código principal (src/)
  - `tests`: Testes (tests/)
  - `scripts`: Scripts (scripts/)
  - `configs`: Configurações (config/)
  - `datasets`: Datasets (datasets/)
  - `deploy`: Deploy (deploy/)
  - `docs`: Documentação (docs/)
  - `archive`: Arquivo (archive/)
  - `logs_main`: Logs principais
  - `data_core`: Dados core
  - `data_reports`: Relatórios
  - `kernel_files`: Arquivos kernel
  - `system_metadata`: Metadados do sistema
  - `data_modules`: Módulos de dados
  - `exports`: Exports
  - `tmp`: Temporários

### 4. **Otimização de Performance**
- 🎯 **GPU Acelerada**: Usa CUDA 13.0 com GTX 1650
- ⚡ **Processamento Paralelo**: 2 workers simultâneos
- 📦 **Batch Otimizado**: 64 embeddings por batch
- 💾 **Gestão de Memória**: Threshold de 1000MB GPU

### 5. **Monitoramento e Verificação**
- 📊 **Progresso em Tempo Real**: Mostra progresso da indexação
- 🔍 **Testes de Busca**: Valida funcionamento com queries de teste
- 📈 **Estatísticas Completas**: Total de chunks, dimensões, modelo usado
- 📝 **Logs Detalhados**: Arquivo de log timestamped

## 📊 Resultados Esperados

Após execução bem-sucedida, você terá:

```
📈 Total de chunks: ~2,000-3,000 (dependendo do projeto)
🎯 Dimensão: 384 (all-MiniLM-L6-v2)
🤖 Modelo: sentence-transformers/all-MiniLM-L6-v2
💾 Status: Ativo
```

## 🔍 Funcionalidades Desbloqueadas

Com a indexação completa, o OmniMind ganha:

- **🔍 Busca Semântica Avançada**: Encontre código por significado, não apenas texto
- **🤖 Processamento de Linguagem Natural**: Entenda contexto e intenções
- **📚 Contexto Completo**: Memória de todo o sistema
- **🧠 Sistema Autopoético**: Capacidade de auto-reflexão e evolução

## 📁 Arquivos Gerados

```
logs/indexing/
├── complete_indexing_YYYYMMDD_HHMMSS.log    # Log completo da execução
└── stats_YYYYMMDD_HHMMSS.json              # Estatísticas finais

data/context/
└── *.json                                  # Arquivos de contexto indexados
```

## ⚙️ Personalização

Para modificar parâmetros, edite o script:

```bash
# Número de workers (padrão: 2)
--max-workers 4

# Tamanho do batch (padrão: 64)
--batch-size 32

# Threshold de memória GPU (padrão: 1000MB)
--gpu-memory-threshold 500
```

## 🐛 Troubleshooting

### Problema: CUDA não disponível
```bash
# Verifique instalação CUDA
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

### Problema: Qdrant não inicia
```bash
# Inicie manualmente
docker-compose -f deploy/docker-compose.yml up -d qdrant
```

### Problema: Memória GPU insuficiente
```bash
# Reduza batch size
--batch-size 32 --gpu-memory-threshold 500
```

## 📈 Monitoramento

Durante execução:
```bash
# Monitore GPU
watch -n 5 nvidia-smi

# Monitore progresso
tail -f logs/indexing/complete_indexing_*.log
```

## 🎯 Próximos Passos

Após indexação completa:

1. **Teste Consultas**: `python scripts/indexing/test_semantic_search.py`
2. **Verifique Logs**: `tail -f logs/embedding_indexing.log`
3. **Inicie Sistema**: `./scripts/canonical/system/start_omnimind_system.sh`

---

**🚀 OmniMind Indexado e Pronto para Operação!**
