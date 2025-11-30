# 🚀 OmniMind Autostart Configuration Guide

**Data**: 30 Novembro 2025  
**Status**: ✅ Configurado

---

## 📋 O que foi configurado

O OmniMind Dashboard agora inicia **automaticamente com o sistema** através do systemd.

### Componentes Ativados:

```
✅ Backend (FastAPI) - Porta 8000
✅ Frontend (Vite)   - Porta 3000
✅ Serviço Systemd   - omnimind.service
```

---

## 🔧 Informações Técnicas

### Arquivo de Serviço:
```
/etc/systemd/system/omnimind.service
```

### Script Principal:
```
/home/fahbrain/projects/omnimind/start_all_servers.sh
```

### Comportamento:
- Inicia ao fazer boot do sistema
- Reinicia automaticamente se falhar
- Logs via systemd journal

---

## 📖 Comandos Úteis

### Iniciar Serviço (Manual)
```bash
sudo systemctl start omnimind.service
```

### Parar Serviço
```bash
sudo systemctl stop omnimind.service
```

### Restart Serviço
```bash
sudo systemctl restart omnimind.service
```

### Ver Status
```bash
sudo systemctl status omnimind.service
```

### Ver Logs em Tempo Real
```bash
sudo journalctl -u omnimind.service -f
```

### Ver Últimos 100 Logs
```bash
sudo journalctl -u omnimind.service -n 100
```

### Desabilitar Autostart (não inicia mais no boot)
```bash
sudo systemctl disable omnimind.service
```

### Reabilitar Autostart
```bash
sudo systemctl enable omnimind.service
```

### Verificar se está ativo no boot
```bash
sudo systemctl is-enabled omnimind.service
```

---

## 🧪 Teste Rápido

```bash
# 1. Reiniciar o serviço
sudo systemctl restart omnimind.service

# 2. Aguardar 10 segundos
sleep 10

# 3. Verificar status
sudo systemctl status omnimind.service

# 4. Testar conectividade
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## 📊 Monitoramento

### Ver processo do OmniMind
```bash
ps aux | grep -E "uvicorn|vite" | grep -v grep
```

### Ver portas em uso
```bash
netstat -tulpn | grep -E "3000|8000"
```

### Ver logs detalhados
```bash
# Últimas 50 linhas
tail -50 /tmp/backend.log
tail -50 /tmp/frontend.log

# Follow em tempo real
tail -f /tmp/backend.log
tail -f /tmp/frontend.log
```

---

## 🔐 Credenciais

```
Usuário: admin
Senha:   omnimind2025!
```

---

## 🌐 URLs de Acesso

| Serviço | URL | Descrição |
|---------|-----|-----------|
| Frontend | http://127.0.0.1:3000 | Dashboard React |
| Backend | http://localhost:8000 | API FastAPI |
| Health | http://localhost:8000/health | Status do Backend |

---

## ⚙️ Arquitetura do Serviço

```
┌─────────────────────────────────────────┐
│  systemd (systemctl)                     │
├─────────────────────────────────────────┤
│  omnimind.service                        │
│  └─ Executa: start_all_servers.sh        │
│     ├─ Backend (uvicorn) port 8000       │
│     └─ Frontend (vite) port 3000         │
└─────────────────────────────────────────┘
```

### Sequência de Inicialização:

1. **Boot do Sistema** → systemd processa unidades
2. **Após Network Online** → Inicia omnimind.service
3. **Script Executa**:
   - Limpa processos antigos
   - Ativa venv
   - Inicia Backend (FastAPI)
   - Aguarda Backend responder
   - Inicia Frontend (Vite)
   - Aguarda Frontend responder
4. **Serviço Ativo** → Dashboard disponível

---

## 🐛 Troubleshooting

### Serviço não inicia?

```bash
# Ver erro
sudo systemctl status omnimind.service
sudo journalctl -u omnimind.service -n 50
```

### Porta já em uso?

```bash
# Ver processos usando porta 8000
lsof -i :8000

# Ver processos usando porta 3000
lsof -i :3000

# Matar processo específico
sudo kill -9 <PID>
```

### Venv não encontrado?

```bash
cd /home/fahbrain/projects/omnimind
source activate_venv.sh
```

### Backend não responde?

```bash
# Ver log backend
tail -100 /tmp/backend.log

# Reiniciar manualmente
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate
python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000
```

---

## 📝 Notas Importantes

1. **Primeiro Boot**: Pode levar 10-15 segundos para tudo estar pronto
2. **Logs**: Verifique `/tmp/backend.log` e `/tmp/frontend.log` se houver problemas
3. **Reinicialização**: O serviço tenta reiniciar automaticamente 3x se falhar
4. **Permissões**: Serviço roda como root (necessário para bindar portas)
5. **Variáveis de Ambiente**: Carregadas do `.env`

---

## ✅ Verificação Pós-Instalação

```bash
# 1. Verificar arquivo de serviço existe
ls -l /etc/systemd/system/omnimind.service

# 2. Verificar que está ativo no boot
sudo systemctl is-enabled omnimind.service
# Deve retornar: enabled

# 3. Ver status
sudo systemctl status omnimind.service

# 4. Fazer reboot para testar
sudo reboot

# 5. Após reboot, verificar se está rodando
sudo systemctl status omnimind.service
curl http://localhost:8000/health
```

---

## 🚀 Resumo

✅ **Serviço Systemd**: `/etc/systemd/system/omnimind.service`  
✅ **Autostart**: Habilitado (inicia com o sistema)  
✅ **Script Principal**: `/home/fahbrain/projects/omnimind/start_all_servers.sh`  
✅ **Reinicialização Automática**: Habilitada (se falhar)  
✅ **Logs**: Via `systemctl` e `/tmp/`  

**O OmniMind Dashboard agora inicia automaticamente ao ligar a máquina!** 🎉

---

Generated: 2025-11-30 02:55:00 UTC
