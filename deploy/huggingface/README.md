# Hugging Face Test Deployment

Scripts para deploy e monitoramento de testes no Hugging Face Spaces.

## 🚀 Deploy

Para fazer deploy da suite de testes no Hugging Face Spaces:

```bash
python scripts/deploy_huggingface.py
```

Este script:
- Carrega variáveis de ambiente do `.env`
- Cria/atualiza o Space `fabricioslv/omnimind-tests`
- Faz upload dos arquivos de configuração (Dockerfile, README.md)

## 🔐 Configuração de Secrets (CRÍTICO)

**IMPORTANTE:** Após o deploy, você DEVE configurar os secrets no Space:

1. Acesse: https://huggingface.co/spaces/fabricioslv/omnimind-tests/settings
2. Vá para a aba **"Secrets"**
3. Adicione os seguintes secrets:

| Secret Name | Value | Descrição |
|-------------|-------|-----------|
| `HUGGING_FACE_HUB_TOKEN` | `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` | Token do Hugging Face |
| `GITHUB_TOKEN` | `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` | Token do GitHub |
| `HF_SPACE_URL` | `https://fabricioslv-devbrain-inference.hf.space` | URL do Space (opcional) |

4. Clique **"Save"** e **reinicialize o Space**

## 📊 Download de Resultados

Para baixar os resultados dos testes executados no Space:

```bash
python scripts/download_hf_results.py
```

Este script baixa:
- `coverage.json` - Relatório de cobertura em JSON
- `htmlcov/index.html` - Relatório HTML de cobertura

## 🔧 Configuração

### Space Configuration
- **Nome:** `fabricioslv/omnimind-tests`
- **Hardware:** T4 GPU (recomendado) ou CPU Upgrade
- **SDK:** Docker
- **Python:** 3.12.8

### Recursos PRO
O Space automaticamente detecta conta PRO e usa:
- GPU T4 se disponível
- CPU upgrade (até 0.03) se GPU não disponível
- Fallback para tier gratuito

## 📈 Monitoramento

1. Acesse: https://huggingface.co/spaces/fabricioslv/omnimind-tests
2. Verifique a aba "Logs" para ver execução dos testes
3. Use `download_hf_results.py` para baixar métricas detalhadas

## 🧪 Testes Executados

O container executa:
```bash
pytest tests/ -v --tb=short --cov=src --cov-report=term-missing --cov-report=json:data/test_reports/coverage.json --cov-report=html:data/test_reports/htmlcov --maxfail=999 --durations=20 -W ignore::DeprecationWarning
```

Com:
- Cobertura completa de código
- Relatórios detalhados
- Tratamento de warnings
- Máximo de falhas configurável