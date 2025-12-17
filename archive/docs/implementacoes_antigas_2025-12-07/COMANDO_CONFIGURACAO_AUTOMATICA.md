# 🔧 Comando para Configuração Automática - OmniMind

**Data**: 2025-01-XX
**Autor**: Fabrício da Silva + assistência de IA

---

## ✅ Status Atual

Os seguintes serviços já estão **HABILITADOS** para inicialização automática:

- ✅ `omnimind.service` - Serviço principal (Backend + Orchestrator)
- ✅ `omnimind-mcp.service` - MCP Orchestrator
- ✅ `omnimind-daemon.service` - Daemon
- ✅ `omnimind-frontend.service` - Frontend
- ✅ `omnimind-qdrant.service` - Qdrant

---

## 🚀 Comando para Configuração Definitiva

Execute este comando para garantir que todos os serviços estejam configurados corretamente:

```bash
sudo bash /home/fahbrain/projects/omnimind/scripts/canonical/system/configurar_inicializacao_automatica.sh
```

Este script irá:
1. Verificar todos os serviços instalados
2. Habilitar serviços que ainda não estão habilitados
3. Recarregar o daemon systemd
4. Mostrar status final de todos os serviços

---

## 📋 Comandos Manuais (Alternativa)

Se preferir executar manualmente:

```bash
# 1. Habilitar serviço principal
sudo systemctl enable omnimind.service

# 2. Habilitar MCP Orchestrator
sudo systemctl enable omnimind-mcp.service

# 3. Habilitar Daemon
sudo systemctl enable omnimind-daemon.service

# 4. Habilitar Frontend
sudo systemctl enable omnimind-frontend.service

# 5. Habilitar Qdrant
sudo systemctl enable omnimind-qdrant.service

# 6. Recarregar systemd
sudo systemctl daemon-reload

# 7. Verificar status
systemctl list-unit-files | grep omnimind
```

---

## ✅ Verificação

Após executar, verifique se os serviços estão habilitados:

```bash
systemctl is-enabled omnimind.service omnimind-mcp.service omnimind-daemon.service omnimind-frontend.service
```

Todos devem retornar: `enabled`

---

## 🔄 Iniciar Serviços Agora (Sem Reiniciar)

Para iniciar os serviços imediatamente (sem esperar o próximo boot):

```bash
sudo systemctl start omnimind.service
sudo systemctl start omnimind-mcp.service
sudo systemctl start omnimind-daemon.service
sudo systemctl start omnimind-frontend.service
```

---

## 📊 Verificar Status

```bash
# Status de todos os serviços
systemctl status omnimind.service
systemctl status omnimind-mcp.service

# Logs em tempo real
sudo journalctl -u omnimind.service -f
sudo journalctl -u omnimind-mcp.service -f
```

---

## ⚠️ Importante

- Os serviços iniciarão **automaticamente** no próximo boot da máquina
- Para iniciar agora (sem reiniciar), use `systemctl start`
- Para desabilitar: `sudo systemctl disable <serviço>`

