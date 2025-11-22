#!/bin/bash
# scripts/upload_secrets.sh
# Script para carregar variáveis de um arquivo .env para o GitHub Secrets
# Requer GitHub CLI (gh) instalado e autenticado.

if ! command -v gh &> /dev/null; then
    echo "❌ Erro: GitHub CLI (gh) não está instalado."
    echo "Instale-o primeiro: https://cli.github.com/"
    exit 1
fi

ENV_FILE=$1
GITHUB_ENV=$2

if [ -z "$ENV_FILE" ]; then
    echo "Uso: ./scripts/upload_secrets.sh <arquivo_env> [nome_ambiente_github]"
    echo "Exemplo (Secrets Globais): ./scripts/upload_secrets.sh .env"
    echo "Exemplo (Staging):         ./scripts/upload_secrets.sh .env.staging staging"
    echo "Exemplo (Production):      ./scripts/upload_secrets.sh .env.production production"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Arquivo $ENV_FILE não encontrado!"
    exit 1
fi

echo "🔍 Lendo variáveis de $ENV_FILE..."

# Lê o arquivo linha por linha
while IFS='=' read -r key value || [ -n "$key" ]; do
    # Ignora comentários e linhas vazias
    [[ $key =~ ^#.*$ ]] && continue
    [[ -z $key ]] && continue
    
    # Remove espaços em branco extras
    key=$(echo $key | xargs)
    value=$(echo $value | xargs)

    # Se houver um ambiente especificado, usa --env
    if [ -n "$GITHUB_ENV" ]; then
        echo "📤 Enviando $key para o ambiente '$GITHUB_ENV'..."
        gh secret set "$key" --env "$GITHUB_ENV" --body "$value"
    else
        echo "📤 Enviando $key para Secrets do Repositório (Global)..."
        gh secret set "$key" --body "$value"
    fi

done < "$ENV_FILE"

echo "✅ Concluído! Segredos carregados."
