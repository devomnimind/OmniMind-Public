# MCP Servers: Valores Reais vs Hardcoded

**Data**: 2025-12-08
**Autor**: Fabrício da Silva + assistência de IA

## 📋 Visão Geral

Este documento documenta quais métodos dos servidores MCP retornam **valores reais do sistema** versus valores **hardcoded** ou **mockados**. Isso é crítico para entender o comportamento dos testes e evitar falhas quando valores esperados não correspondem à realidade do sistema.

## 🔍 PythonMCPServer (`src/integrations/mcp_python_server.py`)

### ✅ Valores Reais do Sistema

| Método | Retorna | Fonte |
|--------|---------|-------|
| `get_python_info()` | Informações do Python | `sys.version`, `sys.version_info`, `sys.executable`, `platform.platform()` |
| `list_packages()` | Lista de pacotes instalados | `pip list` via subprocess ou `pkg_resources.working_set` |
| `execute_code()` | Resultado da execução | Subprocess executando código Python real |
| `lint_code()` | Issues de linting | `flake8` via subprocess (valores reais do código) |
| `type_check()` | Erros de tipo | `mypy` via subprocess (valores reais do código) |
| `format_code()` | Código formatado | `black` via subprocess (formatação real) |
| `run_tests()` | Resultados de testes | `pytest` via subprocess (resultados reais) |

**Observações**:
- `format_code()` sempre formata código usando black, então código formatado **não será igual** ao original
- `run_tests()` retorna resultados reais de pytest, que podem ser "passed", "failed" ou "error" dependendo do path
- Todos os métodos retornam valores baseados no estado real do sistema/ambiente

### ⚠️ Valores Hardcoded/Mockados

Nenhum método deste servidor retorna valores hardcoded. Todos usam valores reais do sistema.

---

## 🔍 SystemInfoMCPServer (`src/integrations/mcp_system_info_server.py`)

### ✅ Valores Reais do Sistema

| Método | Retorna | Fonte |
|--------|---------|-------|
| `get_gpu_info()` | Informações da GPU | `nvidia-smi` via subprocess ou `torch.cuda` |
| `get_cpu_info()` | Informações da CPU | `platform.processor()`, `psutil.cpu_count()`, `psutil.cpu_freq()`, `psutil.cpu_percent()` |
| `get_memory_info()` | Informações de memória RAM | `psutil.virtual_memory()`, `psutil.swap_memory()` |
| `get_disk_info()` | Informações de disco | `psutil.disk_usage()` no path do projeto |
| `get_temperature()` | Temperaturas | `psutil.sensors_temperatures()` ou `nvidia-smi` (pode retornar `None` se não disponível) |

**Observações Críticas**:
- **Todos os valores são REAIS** e variam conforme o sistema
- CPU: Modelo, número de cores, frequência variam por hardware
- Memória: Total e disponível variam por sistema
- Disco: Espaço total e livre variam por sistema
- Temperatura: Pode ser `None` se sensores não disponíveis, ou valores que variam constantemente
- GPU: Nome e VRAM variam por hardware

**Campos Retornados**:
- `get_cpu_info()` retorna `cores_physical` e `cores_logical`, **não** `cores`
- `get_memory_info()` retorna valores em GB como `float` (não `int`)
- `get_temperature()` pode retornar `None` para `cpu_c` e `gpu_c` se sensores não disponíveis

### ⚠️ Valores Hardcoded/Mockados

Nenhum método deste servidor retorna valores hardcoded. Todos usam valores reais do sistema.

---

## 🔍 LoggingMCPServer (`src/integrations/mcp_logging_server.py`)

### ✅ Valores Reais do Sistema

| Método | Retorna | Fonte |
|--------|---------|-------|
| `search_logs()` | Logs encontrados | Arquivos de log reais (`logs/omnimind.log`, etc.) |
| `get_recent_logs()` | Logs recentes | Arquivos de log reais (últimas N linhas) |
| `get_audit_logs()` | Logs de auditoria | `ImmutableAuditSystem` (dados reais) |

**Observações**:
- Retorna lista vazia se arquivos não existirem ou não houver logs
- Valores dependem do conteúdo real dos arquivos de log

### ⚠️ Valores Hardcoded/Mockados

Nenhum método retorna valores hardcoded. Todos usam dados reais dos arquivos de log.

---

## 🧪 Implicações para Testes

### ❌ Testes Incorretos (ANTES da Correção)

**Problema**: Testes esperavam valores hardcoded específicos que não correspondem à realidade do sistema.

**Exemplos de Testes Incorretos**:
```python
# ❌ INCORRETO - Espera valor hardcoded
assert result["model"] == "Intel Core i5"
assert result["cores"] == 4
assert result["total_gb"] == 24
assert result["cpu_c"] == 45.0

# ❌ INCORRETO - Espera código original após formatação
assert result["formatted_code"] == code  # Black formata código!
```

### ✅ Testes Corretos (APÓS a Correção)

**Solução**: Testes verificam estrutura, tipos e consistência, não valores específicos.

**Exemplos de Testes Corretos**:
```python
# ✅ CORRETO - Verifica estrutura e tipos
assert isinstance(result["model"], str)
assert isinstance(result["cores_physical"], int)
assert result["cores_physical"] > 0

# ✅ CORRETO - Verifica que código foi formatado (não compara valores)
assert isinstance(result["formatted_code"], str)
assert len(result["formatted_code"]) > 0

# ✅ CORRETO - Verifica consistência (não valores absolutos)
assert result["available_gb"] <= result["total_gb"]
assert result["free_gb"] >= 0
```

---

## 📝 Regras para Novos Testes

### ✅ SEMPRE Fazer

1. **Verificar estrutura**: Campos esperados existem?
2. **Verificar tipos**: Valores têm tipos corretos?
3. **Verificar consistência**: Relações entre valores fazem sentido?
4. **Documentar origem**: Adicionar docstring indicando se valores são reais ou mockados

### ❌ NUNCA Fazer

1. **Comparar valores hardcoded** para métodos que retornam valores reais
2. **Assumir valores específicos** de hardware/software
3. **Esperar valores estáticos** quando sistema retorna valores dinâmicos
4. **Ignorar casos None** quando valores podem não estar disponíveis

---

## 🔧 Correções Aplicadas (2025-12-08)

### PythonMCPServer

1. ✅ `test_format_code_basic`: Corrigido para verificar estrutura, não código original
2. ✅ `test_get_python_info_basic`: Corrigido para verificar estrutura completa
3. ✅ `test_run_tests_different_paths`: Corrigido para aceitar "passed", "failed" ou "error"

### SystemInfoMCPServer

1. ✅ `test_get_gpu_info_basic`: Corrigido para verificar estrutura, não valores específicos
2. ✅ `test_get_cpu_info_basic`: Corrigido para usar `cores_physical` e `cores_logical`
3. ✅ `test_get_memory_info_basic`: Corrigido para verificar tipos e consistência
4. ✅ `test_get_disk_info_basic`: Corrigido para verificar tipos e consistência
5. ✅ `test_get_temperature_basic`: Corrigido para aceitar `None` se sensores não disponíveis

### ReactAgent

1. ✅ Melhorado tratamento de CUDA OOM no catch-all final de `_init_embedding_model()`

---

## 📚 Referências

- `src/integrations/mcp_python_server.py`
- `src/integrations/mcp_system_info_server.py`
- `src/integrations/mcp_logging_server.py`
- `src/agents/react_agent.py`
- `tests/integrations/test_mcp_python_server.py`
- `tests/integrations/test_mcp_system_info_server.py`

---

**Última Atualização**: 2025-12-08

