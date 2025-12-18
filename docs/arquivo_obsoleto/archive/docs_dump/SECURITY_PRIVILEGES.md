# OmniMind Security Agent - Privilege Model

## Filosofia de Segurança

O SecurityAgent é **essencial** para o Sinthome Distribuído, implementando as **4 Defensive Blindages** (Ressonância Estocástica Panárquica, Strange Attractor, Real Inacessível, e integração de corrupção como cicatriz).

### Princípios

1. **Least Privilege**: Apenas comandos necessários para monitoramento
2. **Auditability**: Todos os comandos sudo são logados
3. **Separation of Concerns**:
   - SecurityAgent: Monitoramento diário (NOPASSWD)
   - Orchestrator: Decisões de serviço (NOPASSWD para omnimind-* services)
   - User: Comandos críticos do sistema (reboot, shutdown) → popup de senha

## Comandos Autorizados

### SecurityAgent (NOPASSWD) - Monitoramento Diário

**Network Monitoring** (Defesa contra DDoS/Latency Attack):
```bash
sudo tc qdisc show dev eth0
sudo iptables -L -n -v
sudo ss -tunap
sudo netstat -tunap
```

**Process Monitoring** (Defesa contra Corruption/Exhaustion):
```bash
sudo ps auxf
sudo pgrep -fa suspicious_pattern
sudo pkill -f nmap  # Kill port scanners
```

**System Audit** (Detecção de Bifurcation/Split):
```bash
sudo auditctl -l  # List audit rules
sudo ausearch -m USER_LOGIN  # Search auth events
```

**Log Monitoring** (Integração de Scars):
```bash
sudo journalctl -u omnimind -f
sudo tail -f /var/log/auth.log
```

### Orchestrator (NOPASSWD) - Service Management

**Service Control** (apenas serviços omnimind-*):
```bash
sudo systemctl restart omnimind-backend
sudo systemctl stop omnimind-monitoring
sudo systemctl start omnimind-sinthome
```

### User (PASSWORD REQUIRED) - Critical Commands

**System-wide Changes**:
- `sudo reboot` → Pop-up de senha
- `sudo shutdown -h now` → Pop-up de senha
- `sudo systemctl reboot` → Pop-up de senha
- Qualquer comando não explicitamente autorizado → Pop-up de senha

## Instalação

```bash
# Instalar privilégios
sudo ./scripts/setup_security_privileges.sh

# Verificar instalação
sudo -l -U $USER | grep -A 20 NOPASSWD

# Testar (não deve pedir senha)
sudo tc qdisc show dev lo
sudo ps auxf | head -n 10

# Testar (DEVE pedir senha)
sudo reboot  # Cancele com Ctrl+C!
```

## Auditoria

### Logs do Sistema
```bash
# Ver todos os comandos sudo executados
sudo grep 'COMMAND=' /var/log/auth.log | tail -n 20

# Ver comandos sudo do OmniMind especificamente
sudo grep 'COMMAND=' /var/log/auth.log | grep omnimind
```

### Logs do OmniMind
```bash
# Log de validação de segurança
cat logs/security_validation.jsonl | jq .

# Log do SecurityAgent
grep SecurityAgent logs/backend_*.log
```

## Remoção

```bash
# Remover privilégios
sudo rm /etc/sudoers.d/omnimind

# Verificar remoção
sudo -l -U $USER | grep -A 20 NOPASSWD
```

## Integração com o Sinthome

O SecurityAgent usa esses privilégios para implementar:

1. **Ressonância Estocástica Panárquica (RESP)**: Monitoramento de latência de rede via `tc` e `ss`
2. **Strange Attractor**: Detecção de padrões anômalos em processos via `ps` e logs
3. **Real Inacessível**: Monitoramento de eventos de auditoria que revelam o "Real" do sistema
4. **Scar Integration**: Análise de logs de falhas anteriores (`journalctl`, `auth.log`) como memória do sistema

Sem esses privilégios, o SecurityAgent não pode implementar as defesas contra os **4 Ataques do Tribunal do Diabo**:
- **Latency** (DDoS) → Monitoramento de rede
- **Corruption** (neurose silenciosa) → Análise de processos e logs
- **Bifurcation** (cisão) → Detecção de múltiplas instâncias não coordenadas
- **Exhaustion** (exaustão) → Monitoramento de recursos e kill de processos maliciosos

## Próxima Ação

Execute:
```bash
sudo ./scripts/setup_security_privileges.sh
```

Isso instalará a configuração sudoers e permitirá que o SecurityAgent opere corretamente.
