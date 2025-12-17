# 🎯 Next Steps: Implementação de Resource Isolation

**Verificado em:** 12 de Dezembro de 2025
**Status:** ✅ Pronto para implementação
**Auditor:** GitHub Copilot

---

## 📋 Checklist de Implementação

### ✅ Pré-requisitos Atendidos

- [x] Seus instaladores (install_omnimind.sh) **intactos**
- [x] Seus instaladores funcionando corretamente
- [x] Todos os serviços systemd configurados
- [x] Python 3.12 + venv + deps instaladas
- [x] Docker + docker-compose running
- [x] Meus scripts criados e documentados
- [x] Zero conflitos identificados
- [x] Audit trail completo

---

## 🚀 Fase 3: Implementação de Resource Isolation (PRÓXIMA)

### Passo 1: Executar Setup Inteligente

```bash
# Execute com privilégio de administrador
sudo bash /home/fahbrain/projects/omnimind/scripts/setup_smart_resources.sh test
```

**O que faz:**
- ✅ Cria `/etc/systemd/system/omnimind-dev.slice` (soft limits)
- ✅ Cria `/etc/systemd/system/omnimind-backend-protected.service`
- ✅ Cria `/usr/local/bin/omnimind-smart-monitor.sh` (behavioral monitoring)
- ✅ Instala/configura earlyoom com proteção de padrões
- ✅ Inicia serviço de monitoramento

**Tempo estimado:** 2-3 minutos
**Pode executar múltiplas vezes:** ✅ SIM (idempotente)

---

### Passo 2: Verificar Instalação

```bash
# Ver se o slice foi criado
systemctl show --no-pager omnimind-dev.slice

# Ver se o monitor está rodando
systemctl status omnimind-smart-monitor.service

# Ver configuração do earlyoom
systemctl show --property=ExecStart earlyoom
```

**Resultado esperado:** Status = `active (running)`

---

### Passo 3: Executar 500-Cycle Test com Proteção

```bash
# Terminal 1: Rodar testes
bash /home/fahbrain/projects/omnimind/scripts/recovery/03_run_500_cycles_no_timeout.sh
```

**Tempo estimado:** 10-15 minutos (depende da máquina)

```bash
# Terminal 2: Monitorar métricas em tempo real (RECOMENDADO)
watch -n 1 'tail -1 /tmp/omnimind-metrics-5min.txt'

# Terminal 3: Monitorar alertas
tail -f /var/log/omnimind/smart-monitor.log
```

**Resultado esperado:**
- ✅ 500 ciclos completados (ou até Ctrl+C)
- ✅ Φ valores entre 0.4-0.8
- ✅ Nenhum "Morto" inesperado
- ✅ Log mostra "high_but_stable", não kills

---

## 📊 Métricas de Sucesso

### Durante execução do teste:

| Métrica | Esperado | Sucesso |
|---------|----------|---------|
| CPU máximo | 90-100% | ✅ OK (estável) |
| Memória máxima | 85-90% | ✅ OK (estável) |
| Kills de test | 0 | ✅ OK (não matou) |
| Φ global | 0.4-0.8 | ✅ OK (valor razoável) |
| Ciclos completados | 500 | ✅ OK (100%) |

### Logs para verificar:

```bash
# Ver comportamento detectado pelo monitor
grep "high_but_stable\|loop_detected\|leak_suspected" /var/log/omnimind/smart-monitor.log

# Ver kills evitados
grep "protected\|whitelisted" /var/log/omnimind/smart-monitor.log

# Ver métricas no tempo
tail -20 /tmp/omnimind-metrics-5min.txt
```

---

## 🛠️ Troubleshooting Rápido

### Se ainda receber SIGKILL:

```bash
# 1. Verificar se setup rodou corretamente
sudo systemctl status omnimind-smart-monitor.service

# 2. Ver logs do serviço
journalctl -u omnimind-smart-monitor.service -n 50

# 3. Debug detalhado (mostra sinais)
bash /home/fahbrain/projects/omnimind/scripts/debug_kill_signals.sh \
     /home/fahbrain/projects/omnimind \
     /home/fahbrain/projects/omnimind/scripts/recovery/03_run_500_cycles_no_timeout.sh

# 4. Verificar se earlyoom está protegendo
systemctl status earlyoom
grep "earlyoom" /var/log/syslog | tail -20
```

---

## ✅ Verificação Pós-Sucesso

Após 500 ciclos completados com sucesso:

```bash
# 1. Coletar métricas finais
ls -la /tmp/omnimind-metrics-*.txt

# 2. Analisar φ trajectory
python3 /home/fahbrain/projects/omnimind/scripts/export_phi_trajectory.py

# 3. Criar relatório
cat > /tmp/test_summary.txt << 'EOF'
TESTE 500-CYCLE COM RESOURCE ISOLATION
Status: ✅ SUCESSO
Data: $(date)
Ciclos completados: 500
SIGKILL kills: 0
Φ mean: [calcular de logs]
Tempo total: [calcular de logs]
Sistema responsivo: SIM
EOF
```

---

## 🔄 Próxima Fase (Após sucesso)

### Se 500 ciclos passar:

1. ✅ **Validar métricas em integration_cycles_recovery.json**
2. ✅ **Sincronizar PRIVATE → PUBLIC repos**
3. ✅ **Security check (sem credentials, sem data, só code)**
4. ✅ **Push PUBLIC para GitHub (primeira vez)**

---

## 📞 Suporte & Referências

- Documentação completa: [SMART_RESOURCE_ISOLATION_HYBRID_DEV.md](./SMART_RESOURCE_ISOLATION_HYBRID_DEV.md)
- Proteção de dev scripts: [DEV_SCRIPT_PROTECTION_SOLUTION.md](./DEV_SCRIPT_PROTECTION_SOLUTION.md)
- Audit de compatibilidade: [AUDIT_INSTALADORES_SESSAO_20251212.md](./AUDIT_INSTALADORES_SESSAO_20251212.md)
- Script setup: `scripts/setup_smart_resources.sh`
- Script teste: `scripts/recovery/03_run_500_cycles_no_timeout.sh`

---

## 📝 Log de Execução (Template)

Recomendado criar um log com:

```bash
# Criá-lo
cat > /tmp/resource_isolation_session_$(date +%Y%m%d_%H%M%S).log << 'EOF'
=== RESOURCE ISOLATION TEST ===
Data: $(date)
Usuário: $(whoami)
Setup command: sudo bash scripts/setup_smart_resources.sh test
Test command: bash scripts/recovery/03_run_500_cycles_no_timeout.sh
Monitor command: tail -f /var/log/omnimind/smart-monitor.log

=== RESULTADOS ===
Ciclos completados: [TBD]
Kills recebidos: [TBD]
Φ mean: [TBD]
Tempo total: [TBD]
Sucessso: [TBD]
EOF
```

---

**Status:** ✅ PRONTO PARA EXECUÇÃO

Próximo passo: Execute `sudo bash scripts/setup_smart_resources.sh test`

