# 🔧 CORREÇÃO: Monitor Não Mata Processos Uvicorn Existentes

**Data**: 2025-12-08
**Autor**: Fabrício da Silva + assistência de IA
**Status**: ✅ CORRIGIDO

---

## 🐛 PROBLEMA IDENTIFICADO

**Sintoma**:
- CPU dispara e depois despenca durante execução de testes
- Monitor estava matando processos uvicorn que já estavam rodando
- Processos eram mortos e reiniciados repetidamente, causando sobrecarga

**Causa Raiz**:
- Linhas 542-546 do `pytest_server_monitor.py` usavam `pkill -f uvicorn`
- Isso matava TODOS os processos uvicorn, incluindo os que já estavam rodando
- Não verificava se servidor já estava rodando antes de tentar iniciar

---

## ✅ CORREÇÕES APLICADAS

### 1. Verificação Antes de Iniciar Servidor

**Arquivo**: `tests/plugins/pytest_server_monitor.py` - Método `_start_server()`

**Mudança**:
```python
def _start_server(self):
    """
    Inicia servidor via scripts/start_omnimind_system_sudo.sh com elevação automática.

    IMPORTANTE: Verifica se servidor já está rodando antes de tentar iniciar.
    Não mata processos uvicorn existentes - apenas verifica se servidor responde.
    """
    # Verificar se servidor já está rodando antes de tentar iniciar
    if self._is_server_healthy():
        logger.info("✅ Servidor já está rodando e respondendo - não precisa iniciar")
        print("✅ Servidor já está rodando - usando servidor existente")
        state_manager = get_server_state_manager()
        state_manager.mark_running()
        return
```

**Benefício**: Se servidor já está rodando, não tenta iniciar novamente.

---

### 2. Removido pkill de Processos Uvicorn

**Arquivo**: `tests/plugins/pytest_server_monitor.py` - Linhas 542-546

**Antes**:
```python
# Mata processos antigos para garantir limpeza
subprocess.run(["pkill", "-f", "uvicorn"], stderr=subprocess.DEVNULL)
subprocess.run(
    ["pkill", "-f", "python web/backend/main.py"], stderr=subprocess.DEVNULL
)
```

**Depois**:
```python
# IMPORTANTE: NÃO matar processos uvicorn existentes
# Se servidor já está rodando (iniciado manualmente ou por outro processo),
# não devemos matá-lo. Apenas mata processos que o plugin iniciou.
# Verificar se plugin iniciou o processo antes de matar
if self.server_process is not None:
    try:
        # Apenas mata processo que plugin iniciou
        if self.server_process.poll() is None:
            # Processo ainda está rodando
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
    except Exception as e:
        logger.debug(f"Erro ao terminar processo do plugin: {e}")

# NÃO usar pkill - pode matar processos uvicorn que não foram iniciados pelo plugin
# subprocess.run(["pkill", "-f", "uvicorn"], stderr=subprocess.DEVNULL)  # REMOVIDO
# subprocess.run(["pkill", "-f", "python web/backend/main.py"], stderr=subprocess.DEVNULL)  # REMOVIDO
```

**Benefício**: Apenas mata processos que o plugin iniciou, não processos existentes.

---

### 3. Verificação em _start_python_server()

**Arquivo**: `tests/plugins/pytest_server_monitor.py` - Método `_start_python_server()`

**Mudança**:
```python
def _start_python_server(self):
    """
    Inicia servidor via python -m uvicorn.

    IMPORTANTE: Verifica se servidor já está rodando antes de tentar iniciar.
    Não mata processos uvicorn existentes - apenas verifica se servidor responde.
    """
    # Verificar se servidor já está rodando antes de tentar iniciar
    if self._is_server_healthy():
        logger.info("✅ Servidor já está rodando e respondendo - não precisa iniciar")
        print("✅ Servidor já está rodando - usando servidor existente")
        state_manager = get_server_state_manager()
        state_manager.mark_running()
        return
```

**Benefício**: Consistência - ambos os métodos verificam antes de iniciar.

---

## 📊 IMPACTO

### Antes da Correção

- Monitor matava TODOS os processos uvicorn (incluindo existentes)
- CPU disparava por matar/reiniciar processos repetidamente
- Processos eram mortos mesmo quando servidor já estava rodando
- Sobrecarga desnecessária

### Após a Correção

- Monitor verifica se servidor já está rodando antes de iniciar
- Apenas mata processos que o plugin iniciou
- Respeita processos uvicorn existentes
- CPU não dispara mais por matar/reiniciar processos

---

## 🎯 COMPORTAMENTO ESPERADO

1. **Servidor já está rodando**:
   - Monitor verifica se servidor responde
   - Se sim, usa servidor existente (não tenta iniciar)
   - Não mata processos existentes

2. **Servidor não está rodando**:
   - Monitor tenta iniciar servidor
   - Se timeout, apenas mata processo que plugin iniciou
   - Não mata processos que não foram iniciados pelo plugin

3. **Sobrecarga de CPU**:
   - Não deve mais ocorrer
   - Monitor não mata/reinicia processos desnecessariamente

---

## ⚠️ NOTAS

**Processos Uvicorn Existentes**:
- Se servidor já está rodando (iniciado manualmente ou por outro processo), monitor não interfere
- Monitor apenas verifica se servidor responde e usa servidor existente

**Processos Iniciados pelo Plugin**:
- Se plugin iniciou processo e precisa reiniciar, apenas termina processo que iniciou
- Não usa `pkill` que mataria todos os processos uvicorn

**Sobrecarga de CPU**:
- É normal para o projeto e máquina atual durante execução de testes
- Monitor não deve causar sobrecarga adicional por matar/reiniciar processos

---

**Status**: ✅ **CORRIGIDO - Monitor não mata processos uvicorn existentes e verifica se servidor já está rodando antes de iniciar**

