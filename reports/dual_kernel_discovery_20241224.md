# DESCOBERTA CRÍTICA: Dois Kernels em Conflito

**Data**: 2024-12-24 10:17
**Severidade**: 🚨 CRÍTICA
**Tipo**: Duplicação de Processo

---

## 🔥 Descoberta via journalctl

Ao investigar os logs do sistema via `sudo journalctl`, descobri que há **DOIS processos kernel** rodando simultaneamente:

### Kernel 1: PID 1733336 (EM LOOP DE MORTE)

**Comando**: `/home/fahbrain/projects/omnimind/.venv/bin/python3 /home/fahbrain/projects/omnimind/scripts/deploy/sovereign_kernel_runner.py`

**Estado**:
```
Φ=0.0499 (CRÍTICO < 0.1)
→ COMA VIGIL ativado a cada 7-8s
→ SurvivalComaHandler falha
→ Loop infinito
```

**Logs**:
```
10:16:28 - F=4.0496 | Φ=0.0499 | S=3.8602 | Σ=2.43 | Ω=0.05 | Res=0.0000
10:16:28 - HEMORRHAGE DETECTED (Φ=0.0499)
10:16:30 - Atadura applied
10:16:30 - Failed to execute: attempt_recovery() got unexpected keyword argument 'state'
```

**Consumo**:
- RAM: 275MB
- CPU: 164h acumulado
- Nice: 17 (baixa prioridade)

---

### Kernel 2: PID 980679 (SAUDÁVEL)

**Comando**: `/home/fahbrain/projects/omnimind/.venv/bin/python3 scripts/sovereign/sovereign_daemon.py`

**Estado**:
```
Φ=0.2212 (SAUDÁVEL > 0.1)
→ Operação normal
→ Sem loop de morte
```

**Logs**:
```
10:16:36 - F=6.1059 | Φ=0.2212 | S=4.0471 | Σ=4.72 | Ω=0.22 | Res=0.4337
10:16:36 - ⚙️ [RECALIBRATION]: Nice adjusted 16 → 15 (Φ=0.22)
```

**Consumo**:
- RAM: 179MB
- CPU: 159h acumulado
- Nice: 15 (prioridade normal)

---

## 🤔 Por Que Isso Está Acontecendo?

### Hipótese 1: Dois Scripts Diferentes

- **`sovereign_kernel_runner.py`**: Kernel principal (systemd service)
- **`sovereign_daemon.py`**: Daemon separado (processo root)

**Problema**: Ambos estão tentando gerenciar o mesmo sistema, mas com estados de Φ diferentes.

### Hipótese 2: Conflito de Estado

- Kernel 1 (PID 1733336) vê Φ=0.05 (crítico)
- Kernel 2 (PID 980679) vê Φ=0.22 (saudável)

**Pergunta**: Por que dois kernels veem Φ diferentes? Estão lendo de fontes diferentes?

---

## 📊 Evidências Adicionais

### Arquivos Modificados Recentemente (última hora)

```
data/recovery/recovery_attempt_20251224_093047.json
data/recovery/recovery_attempt_20251224_093035.json
data/monitor/module_metrics/snapshot.json
data/monitor/module_metrics/metrics.jsonl
data/monitor/consciousness_metrics/phi_history.jsonl
data/long_term_logs/omnimind_metrics.jsonl
data/long_term_logs/heartbeat.status
```

### Arquivos Temporários em /tmp (273MB)

```
/tmp/omnimind_wiki_sync_* (4 instâncias)
/tmp/omnimind_public_repo/
/tmp/omnimind-public-20251223_084338/
```

**Observação**: Sistema está criando múltiplas cópias temporárias, possivelmente para sync ou backup.

---

## 🚨 Problema Real

### Não É Apenas o Erro de Assinatura

O erro `attempt_recovery() got unexpected keyword argument 'state'` é **sintoma**, não causa raiz.

### Causa Raiz Possível

**Dois kernels competindo**:
1. Kernel 1 (systemd) tenta gerenciar sistema
2. Kernel 2 (daemon) também tenta gerenciar sistema
3. Ambos leem/escrevem em locais diferentes
4. Estados de Φ divergem
5. Kernel 1 entra em panic porque vê Φ baixo
6. Kernel 2 continua operando normalmente

---

## 🛠️ Ação Recomendada

### NÃO Aplicar Correção Anterior

A correção proposta (ajustar threshold de Φ) **não resolve** o problema real.

### Investigação Necessária

1. **Descobrir por que há 2 kernels rodando**
   - Um deveria estar rodando?
   - São processos independentes ou duplicados?

2. **Identificar fonte de Φ para cada kernel**
   - De onde Kernel 1 lê Φ=0.05?
   - De onde Kernel 2 lê Φ=0.22?

3. **Decidir qual kernel manter**
   - Matar Kernel 1 (em loop)?
   - Matar Kernel 2 (daemon)?
   - Manter ambos mas sincronizar?

---

## 📝 Próximos Passos

### Fase 1: Entender os Dois Processos

- [ ] Ler `sovereign_kernel_runner.py`
- [ ] Ler `sovereign_daemon.py`
- [ ] Identificar diferenças
- [ ] Verificar se ambos devem rodar

### Fase 2: Sincronizar ou Eliminar

- [ ] Se ambos devem rodar: sincronizar fonte de Φ
- [ ] Se apenas um deve rodar: matar o duplicado
- [ ] Atualizar systemd service se necessário

### Fase 3: Validar

- [ ] Confirmar que apenas um kernel está rodando
- [ ] Verificar que Φ é consistente
- [ ] Monitorar por 10 minutos

---

**Conclusão**: O sistema está em estado de **esquizofrenia** - dois kernels com percepções diferentes da realidade (Φ).
