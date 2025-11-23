# Modo Desenvolvimento - Validações Otimizadas

## Visão Geral

O modo desenvolvimento (`DEV_MODE`) permite acelerar o ciclo de desenvolvimento reduzindo o tempo de validações durante commits, mantendo a segurança e qualidade do código.

## Como Usar

### Ativar Modo Desenvolvimento

```bash
# Para uma sessão
export OMNIMIND_DEV_MODE=true

# Para commits específicos
OMNIMIND_DEV_MODE=true git commit -m "mensagem"

# Para desenvolvimento contínuo (adicionar ao ~/.bashrc ou ~/.zshrc)
echo 'export OMNIMIND_DEV_MODE=true' >> ~/.bashrc
```

### Desativar Modo Desenvolvimento

```bash
# Remover variável
unset OMNIMIND_DEV_MODE

# Ou definir como false
export OMNIMIND_DEV_MODE=false
```

## Diferenças entre Modos

### Modo Produção (Padrão)
- ✅ Testes completos (todos os ~1000+ testes)
- ✅ Validações de código completas (black, flake8, mypy)
- ✅ Verificações de segurança
- ✅ Análise de dependências completa
- ⏱️ Tempo: ~1+ hora

### Modo Desenvolvimento
- ✅ Testes críticos apenas (~50 testes principais)
- ✅ Validações básicas de código
- ✅ Verificações essenciais de segurança
- ✅ Análise rápida de dependências
- ⏱️ Tempo: ~5-10 minutos

## Quando Usar

### ✅ Use DEV_MODE para:
- Desenvolvimento iterativo rápido
- Testes de funcionalidades novas
- Refatoração incremental
- Debugging e troubleshooting
- Commits frequentes durante desenvolvimento

### ❌ Não use DEV_MODE para:
- Commits para produção/main branch
- Releases e deploys
- Pull requests críticos
- Mudanças que afetam segurança
- Quando testes completos são necessários

## Validações por Nível

O script automaticamente detecta o tipo de mudança e aplica validações apropriadas:

| Tipo de Mudança | Produção | Desenvolvimento |
|----------------|----------|----------------|
| Arquivos Core | Completo | Completo |
| Código Python | Completo | Básico |
| Testes | Todos | Críticos |
| Documentação | Básico | Básico |
| Configuração | Completo | Completo |

## Testes Executados no Modo Dev

No modo desenvolvimento, apenas estes testes críticos são executados:

- `tests/test_agents_core_integration.py` - Integração core dos agentes
- `tests/test_config_validator.py` - Validação de configurações
- `tests/test_audit.py` - Sistema de auditoria

## Monitoramento

O relatório final indica claramente qual modo foi usado:

```
📊 Resumo da validação:
   • Nível: FULL
   • Modo: DESENVOLVIMENTO (validações reduzidas)
   • Arquivos analisados: 45
   • Arquivos modificados: 3
   • Testes executados: 50 passed, 0 skipped, 0 warnings
   • Tempo total: 245s
```

## Segurança

- Mesmo no modo dev, validações críticas de segurança são mantidas
- Dependências são sempre verificadas
- Arquivos core são sempre validados
- Baseline de testes é respeitado

## Recomendações

1. **Use DEV_MODE durante desenvolvimento ativo**
2. **Desative DEV_MODE antes de PRs e releases**
3. **Execute testes completos periodicamente** (sem DEV_MODE)
4. **Monitore regressões** através dos baselines

## Troubleshooting

### Problemas Comuns

**Testes críticos falhando no modo dev:**
- Corrija os testes antes de continuar
- Verifique se mudanças afetam funcionalidades core

**Validações lentas mesmo com DEV_MODE:**
- Verifique se a variável está definida corretamente
- Confirme que mudanças não acionaram validações completas

**Commits rejeitados:**
- DEV_MODE não afeta rejeições de commit
- Verifique conflitos ou problemas de merge