# 📊 ANÁLISE DE PROCESSOS - 405 Total

## 🔴 DISTRIBUIÇÃO ATUAL

```
250 root       (61.7%) - Sistema + Docker + Serviços
111 fahbrain   (27.4%) - Desenvolvimento + Testes
 31 mysql      (7.6%)  - Banco de dados
  3 dhcpcd     (0.7%)  - Network
  2 ollama     (0.5%)  - LLM Local
  8 outros     (2.0%)  - Systemd, NVIDIA, etc
```

## ✅ CANDIDATOS A DESATIVAÇÃO

### 1. **MYSQL (31 processos) - ⚠️ CRÍTICO PARA ANÁLISE**
```bash
ps aux | grep mysql | grep -v grep | head -3
```
**Status**: Rodando (provavelmente Supabase local ou test db)
**Ação recomendada**:
- ✅ MANTER se OmniMind usa para dados reais
- ❌ DESATIVAR se apenas teste (usa 200-400MB RAM)

### 2. **Ollama (2 processos) - ANÁLISE**
```bash
ps aux | grep ollama | grep -v grep
```
**Status**: LLM local (Meta Llama)
**Ação recomendada**:
- ✅ MANTER se usando para IA local
- ❌ DESATIVAR se apenas teste (usa 4-8GB VRAM quando ativo)

### 3. **Docker Proxy + Containerd (24 processos) - NECESSÁRIO**
```
12 x /usr/sbin/docker-proxy
12 x /usr/bin/containerd-shim-runc-v2
```
**Status**: Docker containers rodando (provavelmente MCP servers)
**Ação**: ✅ MANTER (necessário para testes)

### 4. **Serviços Systemd (root) - ANÁLISE**
```
- NetworkManager       → Rede (✅ MANTER)
- ModemManager        → Modem (❌ DESATIVAR se sem modem)
- wpa_supplicant      → WiFi (❌ DESATIVAR se Ethernet)
- smartd              → Monitoramento disco (❌ DESATIVAR)
- haveged             → Entropia (❌ DESATIVAR)
- lightdm             → X11 Display (❌ DESATIVAR se headless)
- Xorg                → Display server (❌ DESATIVAR se headless)
- upowerd             → Power (❌ DESATIVAR)
- udisks2             → Storage (❌ DESATIVAR)
- accounts-daemon     → Auth (✅ MANTER)
```

## 🎯 RECOMENDAÇÃO FINAL

### **Cenário 1: Servidor de Testes (Mínimo de recursos)**
```bash
# Desativar:
sudo systemctl stop mysql
sudo systemctl stop ollama
sudo systemctl stop smartd
sudo systemctl stop haveged
sudo systemctl stop lightdm
sudo systemctl stop wpa_supplicant
sudo systemctl stop ModemManager
sudo systemctl stop upowerd
sudo systemctl stop udisks2

# Economiza: ~600MB RAM + reduz processo em ~150
```

### **Cenário 2: Dev Machine (Atual - OK)**
```
Manter tudo rodando (flexibilidade)
Apenas verificar MySQL/Ollama se consumindo demais
```

## 📈 IMPACTO ESPERADO

| Ação | Processos ↓ | RAM Liberada | CPU ↓ |
|------|-------------|--------------|-------|
| Parar MySQL | -31 | ~250MB | ~5% |
| Parar Ollama | -2 | ~4GB* | ~30%* |
| Parar Serviços X11 | -20 | ~100MB | ~3% |
| Parar tudo acima | -53 | ~4.5GB | ~40% |

*Ollama: só consome se modelo ativo

## ✅ CONCLUSÃO

**Seus 405 processos estão normais:**
- ✅ Sem ferramentas Kali realmente rodando
- ✅ Docker + Containerd = necessário
- ✅ OmniMind processes = saudáveis
- ⚠️ MySQL/Ollama = verificar se necessários
- ⚠️ Serviços GUI = desnecessários se headless

**Próxima ação:** Responda qual é seu setup:
1. Servidor de testes apenas?
2. Dev machine com GUI?
3. Precisa de MySQL/Ollama?
