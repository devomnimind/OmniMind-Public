#!/bin/bash
set -e

echo "=== CRIANDO CHAVE GPG PARA OMNIMIND ==="
echo "Quando solicitado, forneça uma passphrase segura:"
echo ""

# Criar chave com configuração interativa
gpg --full-generate-key --expert << EOGPG
1
4096
2y
Y
OmniMind Autonomous Agent
omnimind@devbrain.systems
OmniMind Production Key
Production key for OmniMind autonomous agent system
O
EOGPG

echo ""
echo "=== CHAVE CRIADA COM SUCESSO ==="
echo "Listando chaves:"
gpg --list-keys --keyid-format SHORT

echo ""
echo "=== EXPORTANDO CHAVES ==="
KEY_ID=$(gpg --list-keys --keyid-format SHORT | grep 'OmniMind' -A1 | tail -1 | awk '{print $1}')

echo "Key ID identificado: $KEY_ID"
echo "Exportando chave pública..."
gpg --armor --export $KEY_ID > .omnimind/pgp/public.key

echo "Exportando chave privada (forneça a passphrase quando solicitado)..."
gpg --armor --export-secret-keys $KEY_ID > .omnimind/pgp/private.key

echo ""
echo "=== VERIFICAÇÃO ==="
ls -la .omnimind/pgp/
echo ""
echo "=== CHAVES CRIADAS COM SUCESSO! ==="
echo "Key ID: $KEY_ID"
echo "Arquivos salvos em .omnimind/pgp/"
