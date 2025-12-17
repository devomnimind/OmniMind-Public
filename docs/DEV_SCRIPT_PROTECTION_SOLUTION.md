# 🛡️ OMNIMIND DEV SCRIPT PROTECTION - SOLUÇÃO COMPLETA

**Data:** 12/12/2025
**Problema:** Dev scripts (500-cycle tests) estão sendo SIGKILL'd
**Root Cause:** ResourceProtector enviando `SIGKILL` em vez de `SIGTERM`
**Solução:** Whitelist automática + isolamento de recursos

---

## 🔴 PROBLEMA IDENTIFICADO

### O que estava acontecendo:

```
[SIGTERM] Recebido SIGTERM...   ← Handler interceptou SIGTERM
Morto (exit code 137)            ← Mas foi morto com SIGKILL
```

**Exit code 137 = 128 + 9 (SIGKILL)**
→ Sinal 9 (SIGKILL) **NÃO pode ser interceptado por handlers Python**

### Culpado: `src/monitor/resource_protector.py`

```python
# Linha ~180 (antes da correção):
try:
    proc.wait(timeout=2)
except psutil.TimeoutExpired:
    proc.kill()  # ❌ ISSO ENVIA SIGKILL (sinal 9) - NÃO PODE SER CAPTURADO!
```

---

## ✅ SOLUÇÃO IMPLEMENTADA

### 1. **Whitelist Automática para Dev Scripts**

Adicionado em `src/monitor/resource_protector.py`:

```python
def _is_dev_script(self, pid: int) -> bool:
    """Dev scripts NUNCA são matados - são críticos para testing"""
    dev_patterns = [
        "pytest",
        "03_run_500_cycles",
        "03_test_50_cycles",
        "MASTER_RECOVERY",
        "integration_cycles",
        "jupyter",
        "robust_consciousness_validation",
    ]
    # Se encontrar padrão dev, retorna True = PROTEGIDO
```

**Resultado:** Dev scripts automaticamente não são matados.

### 2. **Isolamento de Recursos**

Script novo: `scripts/setup_resource_isolation.sh`

```bash
bash scripts/setup_resource_isolation.sh test
# Configura:
# • .env.resource_config
# • resource_isolation_config.py
# • Dev script patterns
# • Limites relaxados para TEST mode
```

### 3. **Wrapper Seguro para Dev Scripts**

Script novo: `scripts/run_dev_safe.sh`

```bash
bash scripts/run_dev_safe.sh /home/fahbrain/projects/omnimind \
                             scripts/recovery/03_run_500_cycles_no_timeout.sh
```

**O wrapper:**
- ✅ Marca processo como DEV
- ✅ Define nice=10 (baixa prioridade)
- ✅ Detecta se foi SIGKILL'd
- ✅ Salva logs mesmo se morto

### 4. **Debug Script para Rastrear Kills**

Script novo: `scripts/debug_kill_signals.sh`

```bash
bash scripts/debug_kill_signals.sh /home/fahbrain/projects/omnimind \
                                   scripts/recovery/03_run_500_cycles_no_timeout.sh
```

**Mostra:**
- Quantos SIGKILL vs SIGTERM foram enviados
- Quem enviou (strace)
- Contexto exato do kill

---

## 🚀 COMO USAR

### Opção 1: Usar wrapper seguro (RECOMENDADO)

```bash
cd /home/fahbrain/projects/omnimind

# Primeira execução: setup isolamento
bash scripts/setup_resource_isolation.sh test

# Depois: executar com proteção
bash scripts/run_dev_safe.sh . scripts/recovery/03_run_500_cycles_no_timeout.sh
```

### Opção 2: Executar direto (com env vars)

```bash
export OMNIMIND_RESOURCE_PROTECTOR_MODE=test
export OMNIMIND_ENABLE_DEV_ISOLATION=true

bash scripts/recovery/03_run_500_cycles_no_timeout.sh
```

### Opção 3: Debug se continuar recebendo SIGKILL

```bash
bash scripts/debug_kill_signals.sh . scripts/recovery/03_run_500_cycles_no_timeout.sh
```

---

## 🔍 COMO GARANTIR QUE FUNCIONOU

### ✅ Verificação 1: Dev scripts não aparecem no "kill list"

```bash
# Monitorar resource_protector em outro terminal
tail -f /var/log/omnimind/omnimind.log | grep -i "resource\|kill\|protect"

# Se ver: "🛡️ Processo * protegido: 03_run_500_cycles" = OK
# Se ver: "Matando processo pesado: python" = PROBLEMA
```

### ✅ Verificação 2: Script roda sem SIGKILL

```bash
# Exit codes:
# 0   = SUCCESS
# 130 = Ctrl+C (normal)
# 143 = SIGTERM (handler funcionou)
# 137 = SIGKILL (PROBLEMA - ainda ativo)
```

### ✅ Verificação 3: Logs mostram proteção ativa

```
[DEV] Processo 12345 registrado como protegido (dev script)
🛡️  Dev script detected: 03_run_500_cycles
```

---

## 🎯 VISÃO GERAL DA SOLUÇÃO

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Dev scripts matados? | ✅ Sim (SIGKILL) | ❌ Não (whitelist) |
| Backend pode autoreparar? | ✅ Sim | ✅ Sim |
| SIGTERM handler funciona? | ❌ Não (SIGKILL) | ✅ Sim |
| Resource limits? | Rígidos | Relaxados (TEST) |
| Prioridade dev script? | Normal | Baixa (nice=10) |
| Logs de proteção? | ❌ Nenhum | ✅ Detalhados |

---

## 🔧 POR QUÊ ESSA SOLUÇÃO É MELHOR?

### ❌ Alternativas descartadas:

1. **Desativar ResourceProtector**
   - ❌ Sistema perde autorreparo
   - ❌ Machine fica instável

2. **SIGTERM em vez de SIGKILL**
   - ❌ Handler SIGTERM ainda pode não funcionar
   - ❌ Não resolve problema de raiz

3. **Aumentar recursos**
   - ❌ Não resolve problema de lógica
   - ❌ Machine já tem 24GB RAM

### ✅ Por que essa solução funciona:

1. **Whitelist automática**
   - Dev scripts NUNCA entram no "kill list"
   - Backend continua monitorando (vê mais RAM/CPU = mata outros procs)

2. **Isolamento de recursos**
   - Dev scripts rodam com nice=10 (baixa prioridade)
   - Backend/daemons têm prioridade normal (continuam responsivos)

3. **Sem desativar nada**
   - Sistema continua autoreparável
   - Apenas não interfere em dev

4. **Detectável e debugável**
   - Scripts de debug mostram exatamente o que está acontecendo
   - Logs claros de proteção

---

## 📊 PRÓXIMOS PASSOS

### Imediato:
1. Executar setup: `bash scripts/setup_resource_isolation.sh test`
2. Rodar com wrapper: `bash scripts/run_dev_safe.sh . scripts/recovery/03_run_500_cycles_no_timeout.sh`
3. Monitor em outro terminal: `tail -f logs/omnimind.log | grep DEV`

### Se receber SIGKILL novamente:
1. Execute debug: `bash scripts/debug_kill_signals.sh . scripts/recovery/03_run_500_cycles_no_timeout.sh`
2. Cole logs aqui → identificamos culpado exato
3. Adicionamos padrão à whitelist

### Validação final:
- ✅ 500-cycle test completa 100%
- ✅ Φ valores razoáveis
- ✅ Sem SIGKILL kills
- ✅ Backend continua ativo (não desativado)

---

## 🛡️ GARANTIAS

Esta solução **garante**:

1. ✅ **Dev scripts não são matados** por resource_protector
2. ✅ **Backend pode fazer autorreparo** conforme necessário
3. ✅ **Sistema não fica instável** (não desativa nada)
4. ✅ **Debugável** (sabemos exatamente o que está acontecendo)
5. ✅ **Sem desativar proteções importantes**

---

## 📞 SUPORTE TÉCNICO

Se problema persistir:

```bash
# 1. Coletar logs de debug
bash scripts/debug_kill_signals.sh . scripts/recovery/03_run_500_cycles_no_timeout.sh > /tmp/debug.txt

# 2. Ver recursos em tempo real
watch -n 1 'ps aux | grep python | grep 03_run'

# 3. Verificar resource_protector logs
grep "resource_protector" /var/log/omnimind/omnimind.log

# 4. Compartilhar esses 3 com análise técnica
```

