# 🔄 CHECKLIST: Reinício Seguro do Sistema (12 Dez 2025)

**Data:** 12 de Dezembro de 2025
**Sistema:** Ubuntu 24.04.3 LTS
**Status Atual:** ✅ Diagnóstico completo realizado

---

## 📊 Status do Sistema

### Recurso
| Item | Valor | Status |
|------|-------|--------|
| CPU Cores | 8 | ✅ OK |
| RAM Total | 23GB | ✅ OK |
| RAM Disponível | 13GB | ✅ OK |
| RAM Usada | 9.4GB (41%) | ✅ OK |
| Uptime | 21 minutos | ✅ OK |
| Load Average | 2.38, 3.41, 3.12 | ✅ OK |

### Serviços
- ✅ 2 serviços OmniMind ativos (esperado)
- ✅ Serviços respondendo

### Problemas Identificados
- ⚠️ Desculpe (VSCode) reportou erro interno na screenshot
- ⚠️ Pode estar relacionado a plugins ou IDE

---

## 🛑 ANTES DE REINICIAR

### ✅ Checklist Pré-Reinício

```bash
# 1. Parar todos os serviços graciosamente
sudo systemctl stop omnimind-backend omnimind-frontend omnimind-monitor 2>/dev/null || true

# 2. Parar containers Docker
docker stop $(docker ps -q) 2>/dev/null || true

# 3. Sincronizar buffers
sync
sudo sync

# 4. Verificar que tudo parou
systemctl list-units --type=service --state=active | grep omnimind || echo "✅ Serviços parados"

# 5. Logs finais (backup antes de reiniciar)
tar -czf /tmp/logs_antes_reboot_$(date +%Y%m%d_%H%M%S).tar.gz logs/ 2>/dev/null || true
```

---

## 🔄 MÉTODO DE REINÍCIO RECOMENDADO

### Opção A: Reinício Completo (Recomendado)

```bash
# Parar serviços
echo "Parando serviços..."
sudo systemctl stop omnimind-* 2>/dev/null || true
docker stop $(docker ps -q) 2>/dev/null || true
sleep 2

# Sincronizar
sync

# Reiniciar sistema
echo "Reiniciando em 10 segundos..."
sudo shutdown -r +10
```

**Tempo esperado:** 2-3 minutos
**Resultado:** Sistema limpo, tudo reinicias

---

### Opção B: Reboot Imediato

```bash
sudo reboot
```

**Aviso:** Forçará parada de tudo imediatamente

---

### Opção C: Shutdown Gracioso (Se não vai usar agora)

```bash
sudo shutdown -h +10  # Desliga em 10 minutos
```

---

## ⏱️ Sequência Recomendada

### Fase 1: Parar Tudo (2 minutos)

```bash
# 1. Terminal 1: Parar backend
docker-compose -f deploy/docker-compose.yml down 2>/dev/null || true

# 2. Terminal 2: Parar systemd services
sudo systemctl stop omnimind-dev.slice 2>/dev/null || true

# 3. Sincronizar
sync && sleep 2

# 4. Verificar
ps aux | grep -E 'python|uvicorn|docker' | grep -v grep
```

**Esperado:** Nenhum processo OmniMind rodando

---

### Fase 2: Verificar Estado (1 minuto)

```bash
# Verificar que tudo parou
systemctl list-units --type=service --state=active | wc -l
docker ps | wc -l
ps aux | grep python | grep -v grep | wc -l
```

**Esperado:**
- Poucos serviços systemd ativos (sistema)
- 0 containers Docker
- 0-1 processos Python

---

### Fase 3: Sincronizar e Desligar (1 minuto)

```bash
# Sync final
echo "Sincronizando..."
sync
sudo sync

# Aguardar 5 segundos
sleep 5

# Reiniciar
echo "Reiniciando sistema..."
sudo reboot
```

**Tempo total esperado:** 5-10 minutos

---

## 📋 Pós-Reinício: Verificação

Após reiniciar, em novo terminal:

```bash
# Aguardar boot (2-3 min)
echo "Aguardando boot..."
sleep 180

# 1. Verificar sistema
uname -a
uptime

# 2. Ativar venv
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

# 3. Verificar que tudo está limpo
ps aux | grep python | grep -v grep | wc -l

# 4. Iniciar serviços manualmente
bash scripts/canonical/system/start_omnimind_system_robust.sh
```

---

## 🆘 Se Houver Problemas Pós-Reinício

### Serviços não sobem

```bash
# 1. Verificar logs
journalctl -u omnimind-backend -n 50

# 2. Iniciar manualmente
export PYTHONPATH=/home/fahbrain/projects/omnimind/src
cd /home/fahbrain/projects/omnimind
python src/main.py --debug
```

### Containers Docker não descem

```bash
# Force stop
docker kill $(docker ps -q) 2>/dev/null || true

# Remove containers
docker container prune -f

# Restart daemon
sudo systemctl restart docker
```

### Memória cheia após boot

```bash
# Limpar caches
sudo sync
sudo sysctl -w vm.drop_caches=3

# Reiniciar
free -h
```

---

## 📝 Log de Reinício (Template)

```bash
# Criar log antes de reiniciar
cat > /tmp/reboot_log_$(date +%Y%m%d_%H%M%S).txt << 'EOF'
=== PRÉ-REINÍCIO ===
Data: $(date)
Uptime: $(uptime)
Serviços ativos: $(systemctl list-units --type=service --state=active | grep -c omnimind)
Memória: $(free -h | grep Mem)

=== MOTIVO ===
Diagnóstico completo + verificação de serviços + otimização

=== PÓS-REINÍCIO (preencher depois) ===
Boot OK: [ ]
Serviços iniciaram: [ ]
Testes rodando: [ ]
Sistema responsivo: [ ]
EOF

cat /tmp/reboot_log_*.txt
```

---

## ✅ Checklist Final

- [ ] Todos os logs foram coletados
- [ ] Todos os serviços foram parados
- [ ] Buffers foram sincronizados
- [ ] Sistema pronto para reiniciar
- [ ] Backup de dados realizado (se necessário)
- [ ] Procedure documentada
- [ ] Ninguém mais usando sistema

---

## 🚀 Comando Direto (SEGURO)

Se tudo está OK, execute:

```bash
echo "Parando serviços..." && \
sudo systemctl stop omnimind-* 2>/dev/null || true && \
docker stop $(docker ps -q) 2>/dev/null || true && \
sleep 2 && \
sync && \
echo "Sistema pronto para reiniciar" && \
echo "Execute: sudo reboot"
```

---

## 📞 Suporte

Se houver problemas:

1. **Não forçar desligamento** - aguardar gracioso
2. **Verificar logs** - `journalctl -p err -n 20`
3. **Conferir disco** - `df -h`
4. **Backup antes** - `tar -czf backup.tar.gz .`

---

**Status:** ✅ Pronto para reinício
**Recomendação:** Execute quando não tiver testes em execução
**Tempo estimado:** 5-10 minutos (total)
**Risco:** Mínimo (todos os serviços parados graciosamente)

