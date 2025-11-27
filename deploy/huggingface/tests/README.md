---
title: OmniMind Tests
emoji: 🧪
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
suggested_hardware: t4-small
suggested_storage: small
---

# OmniMind Test Suite 🧪

Este Space executa a suite de testes do OmniMind em um ambiente isolado.

## 🚀 Como usar

O container executa automaticamente os testes ao iniciar. Verifique os logs do Space para ver o resultado.

### Configuração de Secrets (OBRIGATÓRIO)

Antes de executar, configure os seguintes secrets nas **Settings > Secrets** do Space:

- `HUGGING_FACE_HUB_TOKEN`: Seu token do Hugging Face (hf_...)
- `GITHUB_TOKEN`: Token do GitHub para acesso a repositórios
- `HF_SPACE_URL`: URL do Space (opcional)

### Configuração

- **Python:** 3.12.8
- **Framework:** Pytest
- **Hardware:** T4 GPU (Recomendado para testes de ML/Quantum) ou CPU Upgrade
- **Cobertura:** Relatório completo com HTML

## 📊 Status

Verifique a aba "Logs" para ver a saída do `pytest` com cobertura.

## 🔧 Configuração PRO

Para usuários PRO, o Space automaticamente detecta e usa GPU se disponível, caso contrário usa CPU upgrade.
