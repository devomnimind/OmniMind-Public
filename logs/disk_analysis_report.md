# RELATÓRIO DE USO DE DISCO - OMNIMIND

## Disco Total
- **Total**: 891GB
- **Usado**: 219GB (26%)
- **Disponível**: 627GB (74%)

## Diretórios Grandes Encontrados

### 1. `/home/fahbrain/.cache` - **24GB** (NORMAL)
- **HuggingFace**: 15GB (modelos de IA baixados)
- **Pip**: 5GB (cache de pacotes Python)
- **Playwright**: 1.6GB (navegadores para testes)
- **Mozilla**: 1.1GB (cache do navegador)

### 2. `/home/fahbrain/.pyenv` - **7.3GB** (NORMAL)
- **Versions**: 7.2GB (múltiplas versões do Python instaladas)
- Outros: 100MB (plugins, shims, etc.)

### 3. `/home/fahbrain/projects/omnimind/.venv` - **9.7GB** (NORMAL)
- Ambiente virtual Python com todas as dependências
- Inclui bibliotecas de IA, ML, etc.

### 4. `/home/fahbrain/projects` - **12GB** (NORMAL)
- Todo o projeto OmniMind: 12GB
- Dados: 536MB
- Deploy: 258MB
- Web: 146MB
- Logs: 32MB

## Análise de Segurança

✅ **NENHUM DIRETÓRIO SUSPEITO ENCONTRADO**

Todos os diretórios grandes são legítimos:
- **Cache de IA**: Modelos HuggingFace para desenvolvimento
- **Ambientes Python**: Pyenv e venv necessários para desenvolvimento
- **Projeto**: Código fonte e dados do OmniMind

## Recomendações

### Limpeza Opcional (se necessário espaço)
```bash
# Limpar cache pip
pip cache purge

# Limpar cache HuggingFace (cuidado - pode deletar modelos)
rm -rf ~/.cache/huggingface/hub/models--*

# Limpar versões antigas do pyenv
pyenv versions  # ver quais versões
pyenv uninstall <versao_antiga>
```

### Monitoramento Contínuo
O sistema de monitoramento está ativo e irá alertar sobre:
- Aumento anormal de uso de disco
- Novos diretórios grandes suspeitos
- Mudanças no padrão de uso

## Conclusão
Os diretórios de ~50GB são caches e ambientes de desenvolvimento normais. Não há indicação de atividade maliciosa ou vazamento de dados.