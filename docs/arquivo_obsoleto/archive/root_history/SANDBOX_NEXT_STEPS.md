# 🎯 PRÓXIMOS PASSOS - Sandbox Implementation

**Data:** 17 de dezembro de 2025
**Status:** ✅ **Infraestrutura pronta, pronto para integração**

---

## 📋 O QUE JÁ FOI FEITO

✅ **Auditoria Global:** 50+ subprocess calls identificadas
✅ **3-Layer Architecture:** Namespaces + Cgroups + Sudoers
✅ **Slice Configurado:** `/etc/systemd/system/omnimind-sandbox.slice`
✅ **Sudoers Seguro:** `/etc/sudoers.d/omnimind` (protege user processes)
✅ **Documentação:** 4 arquivos .md criados
✅ **Verificação:** Tudo funcionando, sem limite em omnimind.service

---

## 🔧 O QUE FALTA

### TAREFA 1: Atualizar `src/autopoietic/sandbox.py`

**Objetivo:** Integrar `systemd-run --slice=omnimind-sandbox.slice` como primary strategy

**Localização:** `/home/fahbrain/projects/omnimind/src/autopoietic/sandbox.py`

**O que fazer:**

```python
# Função execute_component() precisa de:

def execute_component(self, code: str, class_name: str) -> dict:
    """
    Estratégia em cascata:
    1. PRIMARY: systemd-run + unshare + slice (cgroup limits)
    2. FALLBACK 1: unshare simples (namespaces, sem limits)
    3. FALLBACK 2: Execução direta (no limits, risky)
    """

    # Strategy 1: With systemd-run + slice + cgroup limits
    try:
        return self._execute_with_systemd_run(code, class_name)
        # Command: sudo systemd-run --scope --slice=omnimind-sandbox.slice \
        #         --setenv=PYTHONPATH=/path/to/src \
        #         unshare --pid --ipc --uts --net -- \
        #         python3 component.py
    except Exception as e1:
        self.logger.warning(f"systemd-run failed: {e1}")

    # Strategy 2: Simple unshare (namespaces only, no cgroup)
    try:
        return self._execute_with_unshare(code, class_name)
        # Command: sudo unshare --pid --ipc --uts --net -- \
        #         python3 component.py
    except Exception as e2:
        self.logger.warning(f"unshare failed: {e2}")

    # Strategy 3: Direct execution (LAST RESORT - risky)
    self.logger.error("Sandbox isolation failed 2x, executing directly (RISK)")
    return self._execute_direct(code, class_name)
```

**Arquivo de referência:** `AUDITORIA_ISOLAMENTO_GLOBAL.md` (Seção 7 - Integração)

---

### TAREFA 2: Testar Sandbox com Todos os Casos

**Criar arquivo:** `test_sandbox_integration.py`

```python
import pytest
from src.autopoietic.sandbox import AutopoieticSandbox

class TestSandboxIntegration:
    """Testes de integração do sandbox com isolamento"""

    @pytest.fixture
    def sandbox(self):
        return AutopoieticSandbox()

    def test_basic_execution(self, sandbox):
        """✅ Componente seguro executa com sucesso"""
        code = '''
class SafeComponent:
    _security_signature="safe"
    _generated_in_sandbox=True
    def run(self):
        return "OK"
'''
        result = sandbox.execute_component(code, 'SafeComponent')
        assert result['success']
        assert result['isolation'] != 'none'

    def test_memory_limit(self, sandbox):
        """✅ Componente respeta limite de 1GB RAM"""
        code = '''
class MemoryComponent:
    _security_signature="memory_test"
    _generated_in_sandbox=True
    def run(self):
        # Tenta alocar 100MB (deve funcionar)
        x = bytearray(100 * 1024 * 1024)
        return "OK"
'''
        result = sandbox.execute_component(code, 'MemoryComponent')
        assert result['success']  # 100MB < 1GB

    def test_oom_kill(self, sandbox):
        """✅ Componente que usa >8GB é morto por OOM"""
        code = '''
class OOMComponent:
    _security_signature="oom_test"
    _generated_in_sandbox=True
    def run(self):
        # Tenta alocar 10GB (deve falhar)
        x = bytearray(10 * 1024 * 1024 * 1024)
        return "SHOULD NOT REACH HERE"
'''
        result = sandbox.execute_component(code, 'OOMComponent')
        assert not result['success']  # Deve falhar
        assert 'memory' in result.get('error', '').lower() or \
               'killed' in result.get('error', '').lower()

    def test_namespace_isolation(self, sandbox):
        """✅ Componente é isolado via namespaces"""
        code = '''
import os
class IsolationComponent:
    _security_signature="isolation_test"
    _generated_in_sandbox=True
    def run(self):
        # Em namespace, deve ser PID 1
        pid = os.getpid()
        return f"PID={pid}"
'''
        result = sandbox.execute_component(code, 'IsolationComponent')
        assert result['success']
        assert 'PID=' in str(result.get('output', ''))

    def test_isolation_method_detection(self, sandbox):
        """✅ Sistema detecta qual método de isolamento foi usado"""
        code = '''
class TestComponent:
    _security_signature="test"
    _generated_in_sandbox=True
    def run(self):
        return "OK"
'''
        result = sandbox.execute_component(code, 'TestComponent')
        assert result['isolation'] in ['systemd_run', 'unshare', 'direct']
        # Esperado: systemd_run (primary)
        assert result['isolation'] == 'systemd_run'
```

**Como rodar:**
```bash
pytest test_sandbox_integration.py -v
```

---

### TAREFA 3: Integrar com AutopoieticManager

**Objetivo:** Garantir que TODOS os componentes executados passam pelo sandbox

**Arquivo:** `src/autopoietic/autopoietic_manager.py`

**Mudança esperada:**
```python
# Antes (inseguro):
result = exec(component_code)

# Depois (seguro):
from src.autopoietic.sandbox import AutopoieticSandbox
sandbox = AutopoieticSandbox()
result = sandbox.execute_component(component_code, component_name)
```

---

### TAREFA 4: Documentar no README

**Arquivo:** `/home/fahbrain/projects/omnimind/README.md`

**Adicionar seção:**
```markdown
## 🛡️ Security - Sandbox Isolation

OmniMind uses 3-layer sandbox isolation for dynamically generated components:

1. **Namespace Isolation** (via unshare)
   - PID, IPC, UTS, NET namespaces
   - Generated code runs in isolated environment

2. **Resource Limits** (via systemd cgroups)
   - RAM: 1GB max
   - Swap: 7GB max
   - CPU: 50% quota
   - OOM Kill enforced

3. **Permission Control** (via sudoers)
   - Only sandbox operations allowed
   - User processes protected
   - Generic kill operations blocked

See [SANDBOX_ARQUITETURA_FINAL.md](SANDBOX_ARQUITETURA_FINAL.md) for details.
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Antes de considerar completo, verificar:

- [ ] `sandbox.py` atualizado com systemd-run + cascade strategy
- [ ] `test_sandbox_integration.py` criado e todos os testes passando
- [ ] `AutopoieticManager` integrado com sandbox
- [ ] README.md documentado
- [ ] Full test suite rodando com sandbox ativo
- [ ] Memory limits validados (não existe processo >8GB)
- [ ] OmniMind.service com 16GB + 4GB GPU intacto
- [ ] Sudoers protegendo user processes
- [ ] Documentação atualizada

---

## 🎯 PRIORIDADE

### CRITICAL (Esta semana):
1. ✅ Infraestrutura sandbox (FEITO)
2. ⏳ Atualizar sandbox.py (systemd-run integration)
3. ⏳ Test sandbox integration

### HIGH (Próximas 2 semanas):
4. ⏳ Integrar com AutopoieticManager
5. ⏳ Full test suite com sandbox
6. ⏳ Validate memory limits

### MEDIUM (Próximas 3 semanas):
7. ⏳ Deploy em staging
8. ⏳ Production deployment
9. ⏳ Community documentation

---

## 📚 REFERÊNCIAS

**Documentos criados nesta sessão:**
- `AUDITORIA_ISOLAMENTO_GLOBAL.md` - Audit completo
- `SANDBOX_PRODUCAO_COMPLETO.md` - Operação completa
- `SANDBOX_ARQUITETURA_FINAL.md` - Arquitetura (quick ref)
- `SANDBOX_AUDIT_FINAL_REPORT.md` - Relatório final

**Verificar:**
```bash
ls -la SANDBOX_*.md AUDITORIA_*.md
```

---

## 🚀 COMO COMEÇAR

**Passo 1: Entender a arquitetura**
```bash
cat SANDBOX_ARQUITETURA_FINAL.md
```

**Passo 2: Ver arquivo atual do sandbox**
```bash
cat src/autopoietic/sandbox.py | head -50
```

**Passo 3: Integrar com systemd-run**
```python
# Em execute_component():
# 1. Try: systemd-run --slice=omnimind-sandbox.slice + unshare
# 2. Fallback: unshare simples
# 3. Fallback: direto
```

**Passo 4: Testar**
```bash
pytest test_sandbox_integration.py -v
```

---

## 💡 DICAS

1. **systemd-run sintaxe:**
   ```bash
   sudo systemd-run --scope \
     --slice=omnimind-sandbox.slice \
     --setenv=PYTHONPATH=/path/to/src \
     unshare --pid --ipc --uts --net -- \
     python3 component.py
   ```

2. **Verificar limits durante execução:**
   ```bash
   watch 'systemctl show omnimind-sandbox.slice | grep Memory'
   ```

3. **Logs do sandbox:**
   ```bash
   journalctl -u omnimind-sandbox.slice -f
   ```

4. **Matar componente preso:**
   ```bash
   sudo pkill -9 --cgroup omnimind/sandbox
   ```

---

## 📞 PERGUNTAS?

**Q: Posso rodar componentes sem sandbox?**
A: Sim, via fallback direto, mas não recomendado.

**Q: E se component precisa de mais de 8GB?**
A: Design arquitetural - componentes devem ser leves. Se precisa >8GB, deve ser refatorado.

**Q: Como faço debug de componente no sandbox?**
A: Adicionar logs via `print()` ou logging module. Output capturado em result['output'].

**Q: Qual o overhead de isolamento?**
A: ~50-200ms por execução (namespace + cgroup setup). Aceitável para componentes < 1 minuto.

---

**Status:** ✅ Infraestrutura pronta. Aguardando integração com sandbox.py.

**Próximo milestone:** Ter `systemd-run + unshare + cgroup limits` rodando com teste verde.
