# 📊 ANÁLISE ARQUIVO ATUAL - sandbox.py

**Data:** 17 de dezembro de 2025
**Arquivo:** `src/autopoietic/sandbox.py` (321 linhas)
**Status:** Funcionando, mas SEM isolamento de namespaces e cgroups

---

## 🔍 O QUE EXISTE AGORA

### Proteções Atuais:

✅ **Resource Limits via `resource` module:**
- RLIMIT_CPU (tempo máximo)
- RLIMIT_AS (memória máxima)
- RLIMIT_FSIZE (tamanho arquivo máximo)

✅ **Security Validation:**
- Detecta `import os`, `subprocess.run`, `eval()`, etc.
- Verifica assinatura de segurança
- Verifica marca de gerado no sandbox

✅ **Execução em Subprocess:**
- Cria arquivo temporário
- Executa em subprocesso separado
- Captura stdout/stderr
- Timeout enforcement

✅ **Cleanup:**
- Remove arquivos temporários
- Context manager support

---

## ❌ O QUE NÃO EXISTE (Necessário)

❌ **Isolamento de Namespaces:**
- Sem `unshare --pid --ipc --uts --net`
- Componente pode ver processos do sistema
- Componente pode afetar IPC global

❌ **Isolamento de Cgroups:**
- Sem `systemd-run --slice=omnimind-sandbox.slice`
- Sem limite de RAM via cgroup (apenas resource.setrlimit)
- Sem CPU quota
- Sem OOM Kill coordenado

❌ **Escalação Privilegiada Controlada:**
- Sem `sudo unshare` para namespace isolation
- Sem integração com sudoers

❌ **Isolamento de Rede:**
- Componente pode se conectar à rede
- Sem `--net` namespace

---

## 📋 PLANO DE INTEGRAÇÃO

### Estrutura Nova (manter compatibilidade):

```python
class AutopoieticSandbox:

    def __init__(self, ...):
        # Existente - manter tudo
        self.max_memory_mb = ...
        self.temp_dir = ...
        # NOVO:
        self.use_systemd_run = True  # Feature flag
        self.use_namespaces = True   # Feature flag

    def execute_component(self, component_code, component_name):
        # NOVO: Estratégia em cascata
        result = self._try_execute_with_systemd_run(code, name)
        if result['isolation'] == 'failed':
            result = self._try_execute_with_unshare(code, name)
        if result['isolation'] == 'failed':
            result = self._try_execute_direct(code, name)  # Existente
        return result

    def _try_execute_with_systemd_run(self, code, name):
        """PRIMARY: systemd-run + unshare + cgroup"""
        # Nova função

    def _try_execute_with_unshare(self, code, name):
        """FALLBACK 1: unshare simples (namespaces)"""
        # Nova função

    def _execute_direct(self, code, name):
        """FALLBACK 2: Execução direta (já existe como execute_component)"""
        # Refatorar existente para usar como fallback

    def execution_context(self):
        # Existente - manter igual
```

---

## 🎯 MUDANÇAS ESPECÍFICAS

### Mudança 1: Importar módulos necessários

**Adicionar após imports existentes:**
```python
import shlex  # Para escapar argumentos de linha de comando
```

### Mudança 2: Adicionar métodos de isolamento

**Adicionar novos métodos ao final da classe:**

```python
def _try_execute_with_systemd_run(
    self, component_code: str, component_name: str
) -> Dict[str, Any]:
    """Execute with systemd-run + unshare (PRIMARY)."""
    # Implementação aqui

def _try_execute_with_unshare(
    self, component_code: str, component_name: str
) -> Dict[str, Any]:
    """Execute with unshare only (FALLBACK 1)."""
    # Implementação aqui
```

### Mudança 3: Refatorar execute_component()

**ANTES:**
```python
def execute_component(self, component_code, component_name):
    # ... execução direta com resource limits
    result = {...}
    return result
```

**DEPOIS:**
```python
def execute_component(self, component_code, component_name):
    if not self.validate_component(component_code):
        raise SandboxError("...")

    # Strategy 1: Systemd-run + unshare
    try:
        result = self._try_execute_with_systemd_run(component_code, component_name)
        if result.get('isolation') != 'failed':
            return result
    except Exception as e):
        self._logger.warning(f"systemd-run failed: {e}")

    # Strategy 2: Unshare
    try:
        result = self._try_execute_with_unshare(component_code, component_name)
        if result.get('isolation') != 'failed':
            return result
    except Exception as e:
        self._logger.warning(f"unshare failed: {e}")

    # Strategy 3: Direct (existing)
    self._logger.error("Isolation failed 2x, executing directly (RISK)")
    return self._execute_direct_unsafe(component_code, component_name)
```

---

## 📝 PSEUDOCÓDIGO IMPLEMENTATIONS

### Função 1: _try_execute_with_systemd_run()

```python
def _try_execute_with_systemd_run(self, component_code, component_name):
    """
    Execute in systemd slice with:
    - 1GB RAM limit
    - 7GB Swap limit
    - 50% CPU quota
    - PID/IPC/UTS/NET isolation
    """

    # 1. Criar arquivo temporário
    component_file = ...
    write component_code to file

    # 2. Build command
    cmd = [
        'sudo', 'systemd-run',
        '--scope',
        '--slice=omnimind-sandbox.slice',
        '--setenv=PYTHONPATH=/path/to/src',
        '--setenv=CUDA_*=...',
        'unshare', '--pid', '--ipc', '--uts', '--net',
        '--', 'python3', str(component_file)
    ]

    # 3. Execute via subprocess
    try:
        process = subprocess.Popen(cmd, ...)
        stdout, stderr = process.communicate(timeout=30)

        if process.returncode == 0:
            return {
                'success': True,
                'isolation': 'systemd_run',  # Success indicator
                'output': stdout,
                ...
            }
        else:
            return {
                'success': False,
                'isolation': 'failed',
                'error': stderr,
                ...
            }
    except Exception as e:
        return {
            'success': False,
            'isolation': 'failed',
            'error': str(e),
            ...
        }
```

### Função 2: _try_execute_with_unshare()

```python
def _try_execute_with_unshare(self, component_code, component_name):
    """
    Execute with unshare only:
    - PID/IPC/UTS/NET isolation
    - NO cgroup limits
    - Falls back from _try_execute_with_systemd_run
    """

    # Praticamente igual, mas sem systemd-run:
    cmd = [
        'sudo', 'unshare',
        '--pid', '--ipc', '--uts', '--net',
        '--', 'python3', str(component_file)
    ]

    # ... execution same as above
    # isolação = 'unshare' if success
```

### Função 3: _execute_direct_unsafe()

```python
def _execute_direct_unsafe(self, component_code, component_name):
    """
    Direct execution (existing execute_component logic)
    ONLY if unshare also fails
    """

    # Pegar lógica ATUAL de execute_component()
    # Passar para aqui
    # isolation = 'none'
```

---

## ✅ GARANTIAS DE COMPATIBILIDADE

### Sem quebrar:

✅ `AutopoieticSandbox()` - construtor compatível
✅ `execute_component(code, name)` - interface compatível
✅ Validação de componente - mantida igual
✅ Cleanup - mantido igual
✅ Context manager - mantido igual
✅ `create_secure_sandbox()` - factory mantida

### Com enhancements:

✅ Result dict com novo campo `isolation`
✅ Fallback automático se isolamento falhar
✅ Logging detalhado de cada estratégia
✅ Sudoers checks (avisa se sudo não funciona)

---

## 🔐 SEGURANÇA VERIFICADA

### Antes:
- Resource limits (CPU, memory, file size)
- Validação de código
- Subprocess separado

### Depois:
- Resource limits (CPU, memory, file size) ✅ MANTIDO
- Validação de código ✅ MANTIDO
- Subprocess separado ✅ MANTIDO
- **+ Namespace isolation (PID/IPC/UTS/NET)** 🆕
- **+ Cgroup limits (RAM/Swap/CPU)** 🆕
- **+ Sudoers protection** 🆕

---

## 🧪 TESTES NECESSÁRIOS

### Unit tests a criar:

```python
def test_execute_with_systemd_run():
    # Verifica que retorna isolation='systemd_run'

def test_execute_with_unshare_fallback():
    # Simula falha systemd-run
    # Verifica que tenta unshare

def test_execute_direct_fallback():
    # Simula falha unshare
    # Verifica que executa direto (risky)

def test_isolation_field():
    # Verifica que sempre tem 'isolation' no result

def test_cascade_on_failure():
    # Verifica que realmente tenta 3x antes de falhar
```

---

## 📊 COMPARAÇÃO

| Aspecto | Atual | Novo |
|---------|-------|------|
| **Execução** | Subprocess + resource | Subprocess + resource |
| **Isolamento PID** | Não | Sim (namespace) |
| **Isolamento IPC** | Não | Sim (namespace) |
| **Isolamento UTS** | Não | Sim (namespace) |
| **Isolamento NET** | Não | Sim (namespace) |
| **Limite RAM** | resource.RLIMIT_AS | + cgroup MemoryMax |
| **Limite Swap** | Não | Sim (cgroup) |
| **CPU Quota** | Não | Sim (cgroup) |
| **OOM Kill** | Timeout kill | Cgroup OOM Kill |
| **Fallback** | Não | Sim (3 estratégias) |
| **Compatibilidade** | N/A | 100% compatível |

---

## 🚀 PRÓXIMO PASSO

**Quer proceder com implementação seguindo procedimento seguro?**

1. ✅ Criar branch: `feature/sandbox-systemd-integration`
2. ✅ Estudar código atual (feito)
3. ⏳ Implementar funções novas
4. ⏳ Testar
5. ⏳ Quality checks
6. ⏳ Gracefull restart
7. ⏳ Monitor
8. ⏳ Liberar

Confirma que começo com Branch + Implementação?
