# 🛠️ Tasks do VS Code - OmniMind Development

Este arquivo documenta todas as tasks disponíveis no VS Code para facilitar o desenvolvimento seguro e eficiente do OmniMind.

## 🚀 Como Usar as Tasks

### Acesso Rápido
- **Terminal → Run Task** ou **Ctrl+Shift+P → "Tasks: Run Task"**
- **Terminal → Run Build Task** ou **Ctrl+Shift+P → "Tasks: Run Build Task"**
- **Terminal → Run Test Task** ou **Ctrl+Shift+P → "Tasks: Run Test Task"**
- **Scripts diretos**: `./scripts/run_tests_parallel.sh [modo]`

### Atalhos de Teclado Sugeridos
```json
// Adicione ao keybindings.json
[
    {
        "key": "ctrl+shift+t",
        "command": "workbench.action.tasks.runTask",
        "args": "⚡ Testes Rápidos Paralelos"
    },
    {
        "key": "ctrl+shift+c",
        "command": "workbench.action.tasks.runTask",
        "args": "✅ Validação Manual de Código"
    }
]
```

## 📋 Categorias de Tasks

### 🔒 **SEGURANÇA (4 tasks)**
- **🔍 Validação Completa de Segurança** - Monitoramento anti-AI maliciosa
- **📋 Checklist de Segurança Pré-Commit** - Verificação obrigatória antes de commits
- **🚨 Detectar Arquivos Suspeitos** - Busca por artefatos ROO Code e similares
- **🧹 Limpeza Profunda de Artefatos** - Remoção de arquivos suspeitos

### ✅ **QUALIDADE DE CÓDIGO (6 tasks)**
- **✅ Validação Manual de Código** - Black, Flake8, MyPy completos
- **🔧 Correção Automática de Código** - Formatação e imports automáticos
- **🔍 Verificar Tipos (MyPy)** - Validação de tipos estáticos
- **🎨 Verificar Linting (Flake8)** - Qualidade de código
- **⚡ Verificar Formatação (Black)** - Conformidade Black
- **🔧 Corrigir Imports Automáticos** - Ordenação de imports

### 🧪 **TESTES PARALELIZADOS (5 tasks)**
- **🧪 Executar Todos os Testes** - Suite completa com paralelização e cobertura
- **⚡ Testes Rápidos Paralelos** - Testes rápidos em paralelo (sem cobertura)
- **📊 Testes com Cobertura Detalhada** - Cobertura completa com relatório HTML
- **🚨 Testes Críticos (Smoke Test)** - Apenas testes críticos de segurança e core
- **🔄 Testes Seriais (Sem Paralelização)** - Testes que requerem execução serial

### 🏗️ **DESENVOLVIMENTO (6 tasks)**
- **📦 Instalar/Atualizar Dependências** - Setup completo do ambiente
- **🚀 Iniciar Ambiente de Desenvolvimento** - Dashboard e serviços
- **🐳 Verificar Status Docker** - Containers e serviços
- **🧠 Verificar Status do OmniMind** - Serviços da aplicação
- **📈 Verificar Métricas do Sistema** - Recursos e performance
- **🔧 Verificar Configurações do Ambiente** - Versões das ferramentas

### 🔄 **GIT & VERSIONAMENTO (5 tasks)**
- **🔄 Git Status Seguro** - Verificação segura do repositório
- **🌿 Criar Branch de Desenvolvimento Seguro** - Branch com timestamp
- **🔄 Sincronizar com Branch Principal** - Rebase seguro
- **🔍 Auditoria de Commits Recentes** - Análise de histórico
- **🔄 Reset para Estado Limpo** - Reset forçado (⚠️ cuidado)

### 🧹 **MANUTENÇÃO (3 tasks)**
- **🧹 Limpeza de Cache** - Remove __pycache__, *.pyc, caches
- **📦 Verificar Dependências Desatualizadas** - Pacotes para atualizar
- **🧠 Verificar Integridade de Arquivos** - Compilação Python

### 💾 **BACKUP & DEBUG (4 tasks)**
- **💾 Criar Backup de Segurança** - Backup completo do projeto
- **🔙 Restaurar de Backup** - Lista backups disponíveis
- **🐛 Debug com Logs Detalhados** - Execução com debug completo
- **📊 Analisar Performance** - Profiling com cProfile

### 📊 **RELATÓRIOS (1 task)**
- **📝 Gerar Relatório de Desenvolvimento** - Status automático do projeto

## ⚡ **TESTES PARALELIZADOS - CONFIGURAÇÃO AVANÇADA**

### Modos de Execução
```bash
# Modo rápido (desenvolvimento)
./scripts/run_tests_parallel.sh fast

# Modo completo (CI/CD)
./scripts/run_tests_parallel.sh full

# Cobertura detalhada
./scripts/run_tests_parallel.sh coverage

# Apenas testes críticos
./scripts/run_tests_parallel.sh smoke

# Testes que precisam ser seriais
./scripts/run_tests_parallel.sh serial
```

### Configurações de Workers
- **auto**: Detecta automaticamente (recomendado)
- **4, 8, 16**: Número específico de workers
- **Limitação**: Máximo 8 workers para evitar sobrecarga

### Estratégias de Distribuição
- **worksteal**: Workers roubam trabalho quando terminam (padrão)
- **load**: Balanceia baseado em testes anteriores
- **each**: Um teste por worker

### Filtros Avançados
```bash
# Apenas testes de segurança
./scripts/run_tests_parallel.sh fast -k security

# Apenas testes lentos
./scripts/run_tests_parallel.sh full -m slow

# Testes específicos
./scripts/run_tests_parallel.sh fast -k "test_critical or test_core"
```

## 🎯 **Workflow Recomendado**

### Desenvolvimento Rápido
1. **⚡ Testes Rápidos Paralelos** (validação contínua)
2. **✅ Validação Manual de Código** (qualidade)
3. **🔧 Correção Automática** (formatação)

### Antes de Commit
1. **📋 Checklist de Segurança Pré-Commit** (segurança)
2. **🧪 Executar Todos os Testes** (funcionalidade completa)
3. **📊 Testes com Cobertura Detalhada** (métricas)

### CI/CD Pipeline
1. **🚨 Testes Críticos (Smoke Test)** (verificação rápida)
2. **📊 Testes com Cobertura Detalhada** (relatório completo)
3. **🔒 Verificar Segurança de Dependências** (auditoria)

### Manutenção Semanal
1. **🧹 Limpeza Profunda de Artefatos** (limpeza)
2. **📦 Verificar Dependências Desatualizadas** (atualização)
3. **📝 Gerar Relatório de Desenvolvimento** (status)

## ⚠️ **Avisos Importantes**

- **🔄 Reset para Estado Limpo**: Remove mudanças não commitadas
- **🧹 Limpeza Profunda**: Remove logs antigos (7+ dias)
- **💾 Backup**: Exclui caches automaticamente
- **🔍 Segurança**: Sempre execute validações antes de commits
- **⚡ Paralelização**: Limitada a 8 workers para estabilidade

## 🎨 **Dicas de Performance**

- **Desenvolvimento**: Use "⚡ Testes Rápidos Paralelos"
- **CI/CD**: Use "📊 Testes com Cobertura Detalhada"
- **Debug**: Use "🔄 Testes Seriais" para isolamento
- **Monitoramento**: Scripts salvam logs em `debug_*.log` e `perf_*.txt`

## 🔧 **Configuração Personalizada**

### Adicionar Novas Tasks
```json
{
    "label": "Minha Task Personalizada",
    "type": "shell",
    "command": "./scripts/run_tests_parallel.sh fast -k 'minha_feature'",
    "group": "test",
    "detail": "Testes da minha feature específica"
}
```

### Configurar pytest-xdist
Edite `pytest.ini` para ajustar:
- Número de workers: `-n auto`
- Estratégia: `--dist worksteal`
- Máximo de falhas: `--maxfail=5`

---

**📅 Última atualização:** $(date)
**⚡ Performance:** Testes até 8x mais rápidos com paralelização
**🔒 Ambiente Protegido:** Tasks incluem verificações de segurança automáticas

### 💾 **BACKUP E RECUPERAÇÃO**
- **💾 Criar Backup de Segurança** - Backup completo do projeto
- **🔙 Restaurar de Backup** - Lista backups disponíveis

### 🐛 **DEBUGGING E PERFORMANCE**
- **🐛 Debug: Executar com Logs Detalhados** - Execução com debug completo
- **📊 Analisar Performance** - Análise com cProfile
- **🧠 Verificar Integridade de Arquivos** - Verifica compilação Python

### 📊 **RELATÓRIOS**
- **📝 Gerar Relatório de Desenvolvimento** - Relatório automático do status

## 🎯 **Workflow Recomendado**

### Antes de Começar a Trabalhar
1. **🔍 Validação Completa de Segurança** - Verificar integridade
2. **📋 Checklist de Segurança Pré-Commit** - Confirmar ambiente seguro
3. **📦 Instalar/Atualizar Dependências** - Garantir dependências atualizadas

### Durante o Desenvolvimento
1. **✅ Validação Manual de Código** - Verificar qualidade frequente
2. **🧪 Testes Rápidos (Sem Cobertura)** - Validar mudanças rapidamente
3. **🔧 Correção Automática de Código** - Manter formatação consistente

### Antes de Commitar
1. **📋 Checklist de Segurança Pré-Commit** - Verificação final
2. **✅ Validação Manual de Código** - Garantir qualidade
3. **🧪 Executar Todos os Testes** - Validar funcionalidade

### Manutenção Semanal
1. **🧹 Limpeza Profunda de Artefatos** - Limpeza geral
2. **📦 Verificar Dependências Desatualizadas** - Atualizar pacotes
3. **📊 Gerar Relatório de Desenvolvimento** - Status do projeto

## ⚠️ **Avisos Importantes**

- **🔄 Reset para Estado Limpo**: Remove todas as mudanças não commitadas
- **🧹 Limpeza Profunda**: Remove logs antigos (7+ dias)
- **💾 Backup**: Exclui caches e arquivos temporários automaticamente
- **🔍 Segurança**: Sempre execute validações de segurança antes de commits

## 🎨 **Dicas de Uso**

- Use **Ctrl+Shift+P → "Tasks: Run Task"** para acesso rápido
- Tasks de **build** são executadas com **Ctrl+Shift+B**
- Tasks de **test** são executadas com **Ctrl+Shift+T**
- Configure keybindings personalizadas no `keybindings.json` se desejar

## 🔧 **Configuração Personalizada**

Para adicionar novas tasks, edite `.vscode/tasks.json`. Exemplo:

```json
{
    "label": "Minha Task Personalizada",
    "type": "shell",
    "command": "echo 'Comando personalizado'",
    "group": "build",
    "detail": "Descrição da task"
}
```

---

**📅 Última atualização:** $(date)
**🔒 Ambiente Protegido:** Tasks incluem verificações de segurança automáticas