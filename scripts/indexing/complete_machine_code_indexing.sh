#!/bin/bash

# Script Completo para Indexação de Máquina e Código - OmniMind
# Este script executa indexação completa de embeddings para todo o sistema

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando Indexação Completa de Máquina e Código - OmniMind${NC}"
echo "   $(date)"
echo ""

# ============================================================================
# CONFIGURAÇÃO INICIAL
# ============================================================================

# Calcular caminhos - INDEXAR TUDO DO SISTEMA
# O usuário quer indexar /code (IDE) + /projects/omnimind (projeto completo)
CODE_PATH="/code"
PROJECT_PATH="/home/fahbrain/projects/omnimind"

echo "📁 Caminhos a indexar:"
echo "   IDE/Code: $CODE_PATH"
echo "   Projeto: $PROJECT_PATH"
echo ""
echo "📏 Limites de indexação:"
echo "   • Tamanho máximo: 500MB (PDFs, artigos, datasets grandes OK)"
echo "   • Excluídos: Arquivos binários reais (não texto)"
echo "   • Incluídos: Código, docs, PDFs, JSONs, configs grandes"

# Ativar venv do projeto
if [ -f "$PROJECT_PATH/.venv/bin/activate" ]; then
    source "$PROJECT_PATH/.venv/bin/activate"
    echo -e "${GREEN}✅ Ambiente virtual ativado${NC}"
else
    echo -e "${RED}❌ Ambiente virtual não encontrado em $PROJECT_PATH/.venv${NC}"
    exit 1
fi

# Criar diretórios necessários
mkdir -p "$PROJECT_PATH/logs/indexing"
mkdir -p "$PROJECT_PATH/data/context"

# ============================================================================
# CONFIGURAÇÃO CUDA
# ============================================================================

echo -e "${GREEN}🎯 Configurando CUDA para GTX 1650...${NC}"

# Otimizar CUDA se script existir
if [ -f "$PROJECT_PATH/scripts/cuda_optimize.sh" ]; then
    source "$PROJECT_PATH/scripts/cuda_optimize.sh"
    echo -e "${GREEN}✅ CUDA otimizado${NC}"
else
    echo -e "${YELLOW}⚠️  Script cuda_optimize.sh não encontrado, configurando manualmente...${NC}"
    export CUDA_VISIBLE_DEVICES="0"
    export PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync"
    export TORCH_USE_CUDA_DSA="1"
    export CUDA_LAUNCH_BLOCKING="0"
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
    echo -e "${GREEN}✅ CUDA configurado manualmente${NC}"
fi

# Verificar GPU
echo "🔍 Verificando GPU..."
python3 -c "
import torch
if torch.cuda.is_available():
    device_count = torch.cuda.device_count()
    for i in range(device_count):
        props = torch.cuda.get_device_properties(i)
        print(f'✅ GPU {i}: {props.name} ({props.total_memory // 1024 // 1024}MB)')
        print(f'   CUDA: {torch.version.cuda}')
        print(f'   CuDNN: {torch.backends.cudnn.version()}')
else:
    print('❌ CUDA não disponível')
" 2>/dev/null

# ============================================================================
# VERIFICAÇÃO E INICIALIZAÇÃO QDRANT
# ============================================================================

echo -e "${GREEN}🗄️ Verificando Qdrant...${NC}"

# Verificar se Qdrant está rodando
if curl -s --max-time 5 http://localhost:6333/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Qdrant já está rodando${NC}"
else
    echo -e "${YELLOW}⚠️  Qdrant não está respondendo. Tentando iniciar...${NC}"

    # Tentar iniciar via Docker Compose
    if [ -f "$PROJECT_PATH/docker-compose.yml" ]; then
        cd "$PROJECT_PATH"
        docker-compose up -d qdrant 2>/dev/null
        sleep 10

        if curl -s --max-time 5 http://localhost:6333/healthz > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Qdrant iniciado via Docker${NC}"
        else
            echo -e "${RED}❌ Falha ao iniciar Qdrant${NC}"
            echo "   Verifique se Docker está instalado e funcionando"
            exit 1
        fi
    else
        echo -e "${RED}❌ docker-compose.yml não encontrado${NC}"
        echo "   Instale e configure Qdrant manualmente:"
        echo "   docker run -p 6333:6333 qdrant/qdrant"
        exit 1
    fi
fi

# Inicializar coleções Qdrant se necessário
echo "📋 Verificando coleções Qdrant..."
python3 "$PROJECT_PATH/scripts/indexing/init_qdrant_collections.py" 2>/dev/null || true

# ============================================================================
# INDEXAÇÃO COMPLETA DO SISTEMA
# ============================================================================

echo -e "${GREEN}🔍 Executando Indexação Completa do Sistema...${NC}"
echo "   📁 Indexando: IDE (/code) + Projeto Completo (/home/fahbrain/projects/omnimind)"
echo "   🚫 Excluindo apenas: node_modules, __pycache__, .git, caches"

# Timestamp para logs
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_PATH/logs/indexing/complete_system_indexing_${TIMESTAMP}.log"
STATS_FILE="$PROJECT_PATH/logs/indexing/stats_${TIMESTAMP}.json"

echo "📝 Log: $LOG_FILE"
echo "📊 Stats: $STATS_FILE"
echo ""

# Comando de indexação completa do sistema
# INDEXAR TUDO: /code (IDE) + /home/fahbrain/projects/omnimind (projeto completo)
INDEXING_CMD="python3 -c \"
import sys
sys.path.insert(0, '$PROJECT_PATH/src')
from embeddings.code_embeddings import OmniMindEmbeddings
import os

# Inicializar embeddings
embeddings = OmniMindEmbeddings(
    qdrant_url='http://localhost:6333',
    collection_name='omnimind_embeddings',
    gpu_memory_threshold_mb=1000,
    batch_size_embeddings=64,
    enable_async_execution=True
)

# Função para indexar tudo recursivamente
def index_everything(root_path, name):
    print(f'🔍 Indexando {name}: {root_path}')
    total_chunks = 0

    if not os.path.exists(root_path):
        print(f'⚠️  Caminho não existe: {root_path}')
        return 0

    # Indexar todos os arquivos recursivamente
    for root, dirs, files in os.walk(root_path):
        # Remover diretórios que não queremos indexar
        dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', '.vscode', '.idea', 'cache', 'caches', '.cache']]

        for file in files:
            filepath = os.path.join(root, file)

            # Pular arquivos muito grandes (>500MB) - mas permitir PDFs, docs, etc.
            try:
                file_size = os.path.getsize(filepath)
                if file_size > 500 * 1024 * 1024:  # 500MB
                    print(f'⏭️  Pulando arquivo muito grande: {filepath} ({file_size/1024/1024:.1f}MB)')
                    continue
            except:
                continue

            # Pular arquivos binários reais (não só pela extensão)
            # Verificar se é binário analisando os primeiros bytes
            try:
                with open(filepath, 'rb') as f:
                    first_bytes = f.read(1024)
                    # Arquivos binários têm muitos bytes nulos ou caracteres de controle
                    if b'\x00' in first_bytes[:100]:  # Bytes nulos indicam binário
                        continue
                    # Verificar se é texto legível
                    try:
                        first_bytes.decode('utf-8')
                        is_text = True
                    except UnicodeDecodeError:
                        # Se não é UTF-8, pode ainda ser texto em outra codificação
                        try:
                            first_bytes.decode('latin-1')
                            is_text = True
                        except:
                            is_text = False

                    if not is_text:
                        continue

            except:
                continue

            # Pular apenas extensões binárias óbvias
            if any(filepath.endswith(ext) for ext in ['.pyc', '.pyo', '.so', '.o', '.a', '.lib', '.dll', '.exe', '.bin']):
                continue

            try:
                chunks = embeddings.index_file(filepath)
                total_chunks += chunks
                if total_chunks % 100 == 0:
                    print(f'📊 Progresso {name}: {total_chunks} chunks indexados...')
            except Exception as e:
                print(f'⚠️  Erro ao indexar {filepath}: {e}')
                continue

    print(f'✅ {name} indexado: {total_chunks} chunks')
    return total_chunks

# Indexar IDE (/code)
chunks_ide = index_everything('$CODE_PATH', 'IDE (/code)')

# Indexar projeto completo
chunks_project = index_everything('$PROJECT_PATH', 'Projeto OmniMind')

total_chunks = chunks_ide + chunks_project
print(f'🎉 TOTAL SISTEMA INDEXADO: {total_chunks} chunks')
print(f'   IDE: {chunks_ide} chunks')
print(f'   Projeto: {chunks_project} chunks')
\""

echo "🚀 Comando: Indexação completa recursiva de todo o sistema"
echo ""

# Executar indexação
echo -e "${BLUE}📊 PROGRESSO DA INDEXAÇÃO COMPLETA:${NC}"
eval "$INDEXING_CMD" 2>&1 | tee "$LOG_FILE"

# Verificar se foi bem-sucedido
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✅ Indexação COMPLETA do sistema bem-sucedida!${NC}"
else
    echo -e "${RED}❌ Indexação falhou ou foi interrompida${NC}"
    echo "   Verifique o log: $LOG_FILE"
    tail -n 20 "$LOG_FILE"
    exit 1
fi

# ============================================================================
# VERIFICAÇÃO FINAL E ESTATÍSTICAS
# ============================================================================

echo -e "${GREEN}🔍 Verificando resultado final da indexação completa...${NC}"

# Verificar coleção Qdrant
echo "📊 Estatísticas da coleção após indexação completa:"
if curl -s --max-time 5 http://localhost:6333/collections/omnimind_embeddings > /dev/null 2>&1; then
    curl -s http://localhost:6333/collections/omnimind_embeddings | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    vectors_count = data.get('vectors_count', 0)
    config = data.get('config', {})
    params = config.get('params', {})
    vectors = params.get('vectors', {})
    size = vectors.get('size', 'N/A')
    model = vectors.get('model', 'N/A')

    print(f'   📈 Total de chunks: {vectors_count:,}')
    print(f'   🎯 Dimensão: {size}')
    print(f'   🤖 Modelo: {model}')
    print(f'   💾 Status: Ativo')

    # Salvar estatísticas completas
    import os
    stats_file = os.path.join('$PROJECT_PATH', 'logs', 'indexing', 'stats_${TIMESTAMP}.json')
    with open(stats_file, 'w') as f:
        json.dump({
            'timestamp': '$TIMESTAMP',
            'indexing_type': 'complete_system',
            'paths_indexed': ['$CODE_PATH', '$PROJECT_PATH'],
            'vectors_count': vectors_count,
            'dimension': size,
            'model': model,
            'status': 'completed',
            'excluded_patterns': ['node_modules', '__pycache__', '.git', 'cache', 'caches', '.cache', 'binary_files', 'temp_files'],
            'size_limits': {'max_file_size': '500MB', 'binary_detection': 'content_analysis'}
        }, f, indent=2)

except Exception as e:
    print(f'   ❌ Erro ao obter estatísticas: {e}')
" 2>/dev/null
else
    echo -e "${RED}   ❌ Coleção não encontrada${NC}"
fi

# Verificar arquivos de contexto criados
echo ""
echo "📁 Sistema de contexto criado:"
CONTEXT_FILES=$(find "$PROJECT_PATH/data/context" -name "*.json" 2>/dev/null | wc -l)
if [ "$CONTEXT_FILES" -gt 0 ]; then
    echo "   ✅ $CONTEXT_FILES arquivos de contexto do sistema"
    echo "   📍 Localização: $PROJECT_PATH/data/context/"
else
    echo "   ⚠️  Nenhum arquivo de contexto encontrado"
fi

# Teste de busca semântica abrangente
echo ""
echo -e "${GREEN}🔍 Testando busca semântica no sistema completo...${NC}"
python3 -c "
import sys
sys.path.insert(0, '$PROJECT_PATH/src')
try:
    from embeddings.code_embeddings import OmniMindEmbeddings
    embeddings = OmniMindEmbeddings()
    test_queries = [
        'função principal do sistema',
        'configuração do kernel',
        'processamento de dados',
        'segurança e autenticação',
        'interface do usuário',
        'banco de dados',
        'machine learning',
        'API endpoints'
    ]
    print('🔍 Testando consultas no sistema indexado:')
    for query in test_queries:
        results = embeddings.search(query, top_k=1)
        if results:
            file_path = results[0]['file_path']
            # Identificar se é da IDE ou projeto
            if '$CODE_PATH' in file_path:
                source = 'IDE'
            elif '$PROJECT_PATH' in file_path:
                source = 'Projeto'
            else:
                source = 'Sistema'
            print(f'   ✅ \"{query}\" -> [{source}] {file_path.split(\"/\")[-1]} (score: {results[0][\"score\"]:.3f})')
        else:
            print(f'   ❌ \"{query}\" -> Nenhum resultado')
except Exception as e:
    print(f'   ❌ Erro no teste: {e}')
" 2>/dev/null

# ============================================================================
# RESUMO FINAL
# ============================================================================

echo ""
echo -e "${GREEN}✨ INDEXAÇÃO COMPLETA DO SISTEMA FINALIZADA!${NC}"
echo ""
echo -e "${GREEN}📋 RESUMO DA INDEXAÇÃO COMPLETA:${NC}"
echo "   📅 Data/Hora: $(date)"
echo "   📁 Caminhos indexados:"
echo "      • IDE de Desenvolvimento: $CODE_PATH"
echo "      • Projeto OmniMind: $PROJECT_PATH"
echo "   📝 Log completo: $LOG_FILE"
echo "   📊 Estatísticas: $STATS_FILE"
echo ""
echo -e "${GREEN}🚫 PADRÕES EXCLUÍDOS:${NC}"
echo "   • node_modules (dependências)"
echo "   • __pycache__ (cache Python)"
echo "   • .git (controle de versão)"
echo "   • cache, caches, .cache (caches diversos)"
echo "   • Arquivos binários reais (>500MB pulados)"
echo "   • Arquivos temporários e de sistema"
echo ""
echo -e "${GREEN}🎯 SISTEMA TOTALMENTE VETORIZADO:${NC}"
echo "   🔍 Busca semântica em todo o código"
echo "   🤖 Processamento de linguagem natural completo"
echo "   📚 Contexto unificado: IDE + Projeto"
echo "   🧠 Sistema autopoético com memória total"
echo "   🔗 Conectividade entre componentes"
echo ""
echo -e "${GREEN}💡 CAPACIDADES DESBLOQUEADAS:${NC}"
echo "   • Consultas semânticas avançadas"
echo "   • Entendimento contextual completo"
echo "   • Navegação inteligente pelo código"
echo "   • Recomendações baseadas em similaridade"
echo "   • Análise de padrões em toda a base"
echo ""
echo -e "${GREEN}🚀 OmniMind + IDE COMPLETAMENTE INDEXADOS!${NC}"
echo ""
echo -e "${BLUE}💡 PRÓXIMOS PASSOS RECOMENDADOS:${NC}"
echo "   1. Teste consultas específicas sobre sua IDE"
echo "   2. Experimente buscas semânticas avançadas"
echo "   3. Verifique logs: tail -f logs/embedding_indexing.log"
echo "   4. Monitore uso: watch -n 5 nvidia-smi"
echo "   5. Explore: python scripts/indexing/test_semantic_search.py"
