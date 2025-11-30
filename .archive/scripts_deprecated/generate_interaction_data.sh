#!/bin/bash
# Script para Geração Automática de Dados de Interação com OmniMind
# Simula usuários interagindo com o sistema para gerar dados reais

set -e

echo "🤖 Iniciando geração automática de dados de interação..."

# Verificar se estamos na raiz do projeto
if [[ ! -d "/home/fahbrain/projects/omnimind" ]]; then
    echo "❌ Erro: Execute este script da raiz do projeto OmniMind"
    exit 1
fi

cd /home/fahbrain/projects/omnimind

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar se o serviço OmniMind está rodando
if ! curl -s http://localhost:8000/health >/dev/null; then
    echo "❌ OmniMind API não está rodando. Inicie com: sudo systemctl start omnimind.service"
    exit 1
fi

echo "✅ OmniMind API detectado em localhost:8000"

# Lista de perguntas simuladas (baseadas nas interações reais)
PERGUNTAS=(
    "Qual é o status atual do projeto OmniMind?"
    "Explique como funciona a consciência artificial no sistema"
    "Quais são as métricas de performance atuais?"
    "Como otimizar o uso de memória do PyTorch?"
    "Qual é o roadmap para as próximas fases?"
    "Explique o cálculo de Φ (phi) na teoria da informação integrada"
    "Como funciona o sistema de coevolução entre agentes?"
    "Quais são os principais desafios técnicos atuais?"
    "Como o sistema lida com aprendizado contínuo?"
    "Explique a arquitetura de swarm intelligence"
    "Quais são as integrações com bancos de dados?"
    "Como funciona o sistema de ética e governança?"
    "Explique o processamento quântico implementado"
    "Quais são os endpoints da API disponíveis?"
    "Como monitorar o sistema em produção?"
    "Explique o sistema de feedback bidirecional"
    "Quais são as estratégias de deployment?"
    "Como funciona a detecção de anomalias?"
    "Explique o sistema de metacognição"
    "Quais são os requisitos de hardware?"
)

# Função para fazer pergunta e salvar resposta
fazer_pergunta() {
    local pergunta="$1"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local output_file="data/interaction_data/${timestamp}_interaction.json"

    echo "🤔 Fazendo pergunta: ${pergunta:0:50}..."

    # Fazer a pergunta via API
    response=$(curl -s -X POST http://localhost:8000/chat \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$pergunta\", \"user_id\": \"data_generator_${timestamp}\"}")

    # Verificar se a resposta foi bem-sucedida
    if [[ $? -eq 0 ]] && echo "$response" | jq -e '.response' >/dev/null 2>&1; then
        # Salvar dados da interação
        cat > "$output_file" << EOF
{
    "timestamp": "$timestamp",
    "question": "$pergunta",
    "response": $(echo "$response" | jq '.response'),
    "metadata": {
        "user_id": "data_generator_${timestamp}",
        "session_type": "automated_data_generation",
        "api_endpoint": "/chat",
        "response_time_ms": $(echo "$response" | jq -r '.processing_time // 0')
    }
}
EOF
        echo "✅ Interação salva em: $output_file"
    else
        echo "❌ Erro na resposta da API para: ${pergunta:0:30}..."
        echo "Resposta: $response" >> data/interaction_data/errors.log
    fi

    # Pequena pausa para não sobrecarregar
    sleep 2
}

# Criar diretório para dados
mkdir -p data/interaction_data

echo "📊 Iniciando geração de $((${#PERGUNTAS[@]})) interações..."

# Executar todas as perguntas
for pergunta in "${PERGUNTAS[@]}"; do
    fazer_pergunta "$pergunta"
done

echo "🎉 Geração de dados concluída!"

# Estatísticas finais
total_arquivos=$(ls data/interaction_data/*.json 2>/dev/null | wc -l)
echo "📈 Total de interações geradas: $total_arquivos"

# Calcular estatísticas básicas
if [[ $total_arquivos -gt 0 ]]; then
    echo "📊 Estatísticas das interações:"
    ls data/interaction_data/*.json | head -5 | xargs jq -r '"\(.question[:50])... -> \(.metadata.response_time_ms)ms"' 2>/dev/null || echo "Erro ao calcular estatísticas"
fi

echo "💾 Dados salvos em: data/interaction_data/"
echo "🔄 Execute novamente para gerar mais dados ou modifique PERGUNTAS para variar"</content>
<parameter name="filePath">/home/fahbrain/projects/omnimind/generate_interaction_data.sh