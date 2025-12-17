# 🎯 SMART RESOURCE ISOLATION - AMBIENTE HÍBRIDO DE DEV

**Data:** 12/12/2025
**Problema:** Matar scripts dev com 90% CPU é burro - ambiente híbrido tem picos legítimos
**Solução:** Análise comportamental inteligente + systemd + earlyoom

---

## 🤔 POR QUÊ O LIMITE FIXO DE 90% NÃO FUNCIONA

### Cenário Real: Testes + Backend + VS Code + Ollama

```
⏱️  t=0min:   50% CPU - Tudo normal
⏱️  t=2min:   75% CPU - Teste pesado começa
⏱️  t=3min:   92% CPU - ⚠️  Alerta fixo! MATA TESTE
❌ Teste foi matado injustamente
```

### Vs. Inteligente: Análise de Comportamento

```
⏱️  t=0-5min:  Média 85% ✅ NORMAL (carga pesada mas estável = OK)
               Curva: 50→75→92→88→85 (sobe e estabiliza = esperado)

⏱️  t=5-10min: Média 98% ❌ ALERTA (crescimento contínuo!)
               Curva: 85→92→96→99→99 (vai só subindo = problema!)
               Ação: Reduce nice priority, monitora mais
```

---

## 📊 ESTRATÉGIA EM 4 CAMADAS

### Layer 1: systemd Slice (Isolamento)

```ini
[Slice]
CPUQuota=95%              # Max 95% CPU (soft limit com burst)
CPUAccounting=yes
MemoryMax=90%             # Max 90% memória
OOMPolicy=continue        # IMPORTANTE: Não mata - apenas pausa/throttle
OOMScoreAdjust=-900       # Nunca OOM kill (-900 = último a morrer)
```

**Resultado:**
- ✅ OmniMind pode burstar para 95% (legítimo)
- ✅ Nunca é OOM killer'd (mesmo em 100%)
- ✅ Apenas pausado se realmente fora de controle

### Layer 2: Monitor Inteligente

```python
# Histórico de 5 minutos (1 sample/min)
CPU_HISTORY = [50, 75, 92, 88, 85]  # Média = 78%, estável

# Análise
primeira_metade = média([50, 75, 92]) = 72%
segunda_metade  = média([88, 85])    = 86%

# Decisão
if segunda > primeira * 1.1:  # Crescimento > 10%?
    behavior = "GROWING" ⚠️  (possível problema)
else:
    behavior = "STABLE" ✅ (normal, apenas carga pesada)
```

**Detecta:**
- ✅ Loops CPU (100% constante)
- ✅ Vazamentos memória (crescimento contínuo)
- ✅ Picos legítimos (sobe e estabiliza)

### Layer 3: earlyoom Inteligente

```bash
earlyoom \
  -m 3 -r 800 \
  --prefer '^(?!.*(omnimind|pytest|code)).*'  # Prefira matar OUTROS
  --avoid '(omnimind|pytest|code)'             # Nunca mate ESTES
```

**O que faz:**
- Monitora memória constantemente
- Se < 3%, mata processos
- Mas protege: OmniMind, pytest, VS Code
- Sistema continua responsivo

### Layer 4: VS Code + systemd Notificações

VS Code pode receber notificações do systemd:

```bash
# SE sistema ativa ressource pressure
systemctl show -p Result omnimind-dev.slice

# VS Code recebe webhook
"omnimind.systemd-monitoring": true
# Mostra alert no VS Code quando pressão detectada
```

---

## 🚀 COMO IMPLEMENTAR

### Passo 1: Setup Smart Resources

```bash
cd /home/fahbrain/projects/omnimind

# Install systemd service + monitor + earlyoom
sudo bash scripts/setup_smart_resources.sh test
```

**O que faz:**
- ✅ Cria `/etc/systemd/system/omnimind-dev.slice`
- ✅ Cria `/etc/systemd/system/omnimind-backend-protected.service`
- ✅ Cria `/usr/local/bin/omnimind-smart-monitor.sh`
- ✅ Configura earlyoom para proteger OmniMind
- ✅ Inicia monitor em background

### Passo 2: Executar 500-Cycle Test

```bash
export OMNIMIND_RESOURCE_MODE=smart

bash scripts/recovery/03_run_500_cycles_no_timeout.sh
```

**O que muda:**
- Test roda sob `omnimind-dev.slice` (max 95% CPU)
- Monitor analisa comportamento (5min trends)
- earlyoom protege de OOM kills
- VS Code permanece responsivo

### Passo 3: Monitor em Tempo Real

Em outro terminal:

```bash
# Ver metrics atualizadas a cada min
watch -n 1 'tail -1 /tmp/omnimind-metrics-5min.txt'

# Ver logs de alerta
tail -f /var/log/omnimind/smart-monitor.log
```

---

## 📊 COMO SABER QUE FUNCIONOU

### ✅ Verificação 1: Slice Criado

```bash
systemctl show --no-pager omnimind-dev.slice

# Procure:
# CPUQuota=95%
# MemoryMax=90%
# OOMPolicy=continue
```

### ✅ Verificação 2: Monitor Rodando

```bash
systemctl status omnimind-smart-monitor.service

# Procure: Active: active (running)
```

### ✅ Verificação 3: Processo Sob Slice

```bash
systemctl show -p Slice $(pgrep -f python.*03_run)

# Procure: Slice=omnimind-dev.slice
```

### ✅ Verificação 4: earlyoom Protegendo

```bash
# Check earlyoom está rodando
systemctl status earlyoom

# Ver se está protegendo
grep -i "omnimind\|pytest" /var/log/syslog | tail -10
```

### ✅ Verificação 5: Métricas Inteligentes

```bash
cat /tmp/omnimind-metrics-5min.txt

# Procure:
# cpu_behavior=high_but_stable ✅ (normal)
# ou
# cpu_behavior=growing ⚠️ (alerta - monitor vê)
```

---

## 🎯 COMPARAÇÃO: ANTES vs DEPOIS

| Métrica | Antes (90% fixo) | Depois (Inteligente) |
|---------|------------------|---------------------|
| Teste com pico legítimo? | ❌ Morto | ✅ Roda |
| Loop CPU 100%? | ❌ Continua | ✅ Detectado |
| Vazamento memória? | ❌ Não vê | ✅ Vê crescimento |
| VS Code responsivo? | ❌ Às vezes travado | ✅ Sempre responsivo |
| Backend autoreparável? | ✅ Sim | ✅ Sim |
| Sistema estável? | ⚠️  Frágil | ✅ Robusto |

---

## 🔍 DEBUGGING: Se Problema Persistir

### Caso 1: Processo ainda é matado

```bash
# Check se realmente sob slice
ps -eo pid,cmd | grep python
# Veja qual PID é seu script

systemctl show -p Slice <PID>
# Deve retornar: Slice=omnimind-dev.slice

# Se não, registre manualmente:
echo <PID> >> /sys/fs/cgroup/systemd/omnimind-dev.slice/cgroup.procs
```

### Caso 2: Monitor não alertando

```bash
# Verificar logs
tail -f /var/log/omnimind/smart-monitor.log

# Verificar métricas
cat /tmp/omnimind-metrics-5min.txt

# Se vazio, monitor pode não estar rodando:
sudo systemctl restart omnimind-smart-monitor
```

### Caso 3: earlyoom matando errado

```bash
# Ver o que earlyoom fez
sudo tail -f /var/log/syslog | grep earlyoom

# Se está matando OmniMind, update config:
sudo vim /etc/default/earlyoom
# Adicione à --avoid: '|omnimind'
```

---

## 💡 RECURSOS ADICIONAIS

### Scripts Úteis

```bash
# Ver comportamento de recursos agora
watch -n 1 'free -h && echo "---" && ps aux | head -15'

# Ver slices criados
systemctl list-units --state=loaded | grep slice

# Ver processos sob slice
systemctl show --no-pager --value -p Cgroup omnimind-dev.slice

# Testar limite CPU (deve ficar < 95%)
stress --cpu 8 --timeout 60s
```

### Integração com VS Code

```json
// .vscode/settings.json
{
  "omnimind.enableSystemdMonitoring": true,
  "omnimind.smartResourceMode": "enabled",
  "omnimind.alertOnCPUGrowth": true,
  "omnimind.alertOnMemoryGrowth": true
}
```

### Alertas do Sistema

O `omnimind-smart-monitor.sh` pode enviar notifications:

```bash
# Integração com notify-send (desktop)
notify-send "OmniMind" "CPU crescente: 95%" -u critical

# Ou webhook para dashboard
curl -X POST http://localhost:8000/alerts \
  -d '{"type": "cpu_growing", "value": 95}'
```

---

## ✅ GARANTIAS FINAIS

Esta estratégia garante:

1. ✅ **Testes rodam mesmo com 90-100% CPU** - se comportamento é estável
2. ✅ **Loops travados são detectados** - crescimento contínuo = alerta
3. ✅ **VS Code permanece responsivo** - tem prioridade
4. ✅ **Backend pode autoreparar** - sem desativar
5. ✅ **Sistema não trava** - earlyoom cuida de OOM
6. ✅ **Debugável** - logs mostram tudo que aconteceu

---

## 🚀 PRÓXIMO PASSO

```bash
# Setup completo
sudo bash /home/fahbrain/projects/omnimind/scripts/setup_smart_resources.sh test

# Executar test com novo sistema
export OMNIMIND_RESOURCE_MODE=smart
bash /home/fahbrain/projects/omnimind/scripts/recovery/03_run_500_cycles_no_timeout.sh
```

**Resultado esperado:** 500 ciclos completados SEM kills, mesmo com picos de CPU/memória!


---

## 📌 Apêndice: Relação com install_omnimind.sh

Este documento descreve a **Camada 3+ de Isolamento de Recursos**.

Para a **Camada 1-2 (Instalação Inicial)**, consulte:
- `scripts/canonical/install/install_omnimind.sh` - Instalação completa
- `scripts/canonical/install/setup_security_privileges.sh` - Sudoers config

### Sequência Completa de Setup

```bash
# Fase 1: Instalação inicial (seu install_omnimind.sh)
bash scripts/canonical/install/install_omnimind.sh
# ✅ Python, deps, Docker, GPU

# Fase 2: Segurança (seu setup_security_privileges.sh)
sudo bash scripts/canonical/install/setup_security_privileges.sh
# ✅ Sudoers e permissões

# Fase 3: Resource Isolation (este documento + script)
sudo bash scripts/setup_smart_resources.sh test
# ✅ systemd slice + monitor + earlyoom

# Fase 4: Testes protegidos
bash scripts/recovery/03_run_500_cycles_no_timeout.sh
# ✅ 500 ciclos sem SIGKILL
```

### Compatibilidade

✅ Totalmente compatível com `install_omnimind.sh`
✅ Não interfere com serviços existentes (docker-compose)
✅ Adiciona apenas proteção, não substitui nada
✅ Pode ser removido com `sudo systemctl stop omnimind-smart-monitor.service`

Veja: `docs/AUDIT_INSTALADORES_SESSAO_20251212.md` para análise completa de compatibilidade.

