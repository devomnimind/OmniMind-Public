# Configuração de Ambiente Python - OmniMind

## Estado Atual

✅ **Python:** 3.12.8 (STRICT)
✅ **VEnv:** Único (.venv do projeto)
✅ **Interpretador:** ${workspaceFolder}/.venv/bin/python
✅ **Cache:** Limpo e otimizado

## Arquivos de Configuração

### settings.json
- Define o interpretador Python padrão
- Força uso do .venv local
- Configura ferramentas (Black, Flake8, MyPy, Pylint)
- Define PYTHONPATH para src/

### launch.json
- Configurações de debug Python
- Pytest runner pré-configurado
- Variáveis de ambiente otimizadas

### cleanup_venv.sh
Script para manter ambiente limpo:
```bash
bash .vscode/cleanup_venv.sh
```

Remove:
- Cache Python (__pycache__, *.pyc)
- Cache de interpreters do VS Code
- Cache Pylance

## Verificações

### Verificar interpretador ativo
```bash
python --version  # Deve ser 3.12.8
which python      # Deve ser .venv/bin/python
```

### Verificar venv único
```bash
find ~ -maxdepth 3 -type d -name ".venv"  # Deve retornar 1 resultado
```

## Se VS Code ainda mostrar múltiplos interpreters

1. Execute: `bash .vscode/cleanup_venv.sh`
2. Recarregue VS Code: Ctrl+Shift+P > "Developer: Reload Window"
3. Abra nova terminal para reativar o venv

## Status

- ✅ VEnv único confirmado
- ✅ Cache limpo
- ✅ Configurações otimizadas
- ✅ Pronto para produção

