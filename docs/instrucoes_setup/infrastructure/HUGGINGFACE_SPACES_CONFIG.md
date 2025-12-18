# Hugging Face Spaces - Configuração PRO

## 🎯 Objetivo
Configurar Spaces com hardware adequado aproveitando conta PRO.

---

## 📊 Hardware Disponível (PRO Account)

| Tier | Custo | Uso Recomendado | Configuração |
|------|-------|-----------------|--------------|
| **CPU Free** | Grátis | Demos, testes | `cpu-basic` |
| **CPU Upgrade** | $0.03/hora | **Produção** | `cpu-upgrade` |
| **Zero GPU** | Grátis (25min/mês) | Fine-tuning/training | `zero-a10g` |

---

## ⚙️ Configuração por Space

### 1. **devbrain-inference** (PRIORITÁRIO)
- **Status:** Recriado após deleção acidental
- **Hardware:** CPU Upgrade ($0.03/h)
- **Justificativa:** Produção, baixa latência, uptime 24/7
- **URL:** https://fabricioslv-devbrain-inference.hf.space
- **Integração:** Configurado no LLM Router como HUGGINGFACE_SPACE provider
- **Custo Mensal Estimado:** ~$22/mês (730h x $0.03)

**Como Ativar:**
1. Acesse: https://huggingface.co/spaces/fabricioslv/devbrain-inference/settings
2. Vá em **"Hardware"**
3. Selecione **"CPU upgrade - 2 vCPU • 16 GB"**
4. Clique em **"Apply"**

**Custo Mensal Estimado:** ~$22/mês (730h x $0.03)

---

### 2. **dev_brain**, **devbrain-training**, **devbrain-docs**
- **Status Atual:** Deletados após identificação como temporários
- **Ação:** Aguardando recriação se necessários
- **Recomendação:** Se não estão em uso ativo → Manter deletados (economiza quota)
- **Se recreados:** Configurar em CPU Free (grátis)

**Recomendação:**
- Se não estão em uso ativo → **Deletar** (economiza quota)
- Se são demos → Manter em **CPU Free** (grátis)

---

## 🔧 Como Atualizar Hardware via UI

### Método 1: Interface Web (Recomendado)
1. Acesse: `https://huggingface.co/spaces/{seu_usuario}/{nome_space}/settings`
2. Menu lateral: **"Settings" → "Hardware"**
3. Selecione o tier desejado:
   - `cpu-basic` (Free)
   - `cpu-upgrade` (PRO - $0.03/h)
   - `t4-small` (GPU - $0.60/h)
   - `zero-a10g` (Zero GPU - 25min grátis/mês)
4. Clique **"Apply"**
5. Aguarde rebuild (~1-2 min)

### Método 2: Via README (Sugestão)
Adicione ao `README.md` do Space:
```yaml
---
suggested_hardware: cpu-upgrade
suggested_storage: small
---
```
**Nota:** Isso apenas **sugere** o hardware, mas não ativa automaticamente. Ainda precisa aprovar manualmente na UI.

---

## 💰 Gestão de Custos

### Monitoramento
- Dashboard: https://huggingface.co/settings/billing
- **Billing threshold:** $100/mês (alerta configurado)
- **Current usage:** Consultar dashboard

### Otimização
1. **Pause Spaces não utilizados** (configuração de sleep após inatividade)
2. **Use CPU Free** para demos/docs
3. **Reserve CPU Upgrade** apenas para produção (inference API)
4. **Zero GPU** para experimentos de training (grátis 25min/mês)

### Estimativa de Custo (devbrain-inference em CPU Upgrade)
- **1 hora:** $0.03
- **1 dia (24h):** $0.72
- **1 semana:** ~$5
- **1 mês (730h):** ~$22

**Nota:** Se pausar o Space quando não estiver em uso (ex: 8h/dia), custo cai para ~$7/mês.

---

## 🚀 Próximos Passos

1. ✅ **Ativar CPU Upgrade** no `devbrain-inference` via UI
2. ⏸️ **Pausar/Deletar** Spaces com CONFIG_ERROR se não utilizados
3. 📊 **Monitorar** uso no dashboard de billing
4. 🔄 **Configurar auto-pause** após 1h de inatividade (economizar custo)

---

## 📞 Suporte
Se precisar de ajuda, consulte:
- Docs: https://huggingface.co/docs/hub/spaces-overview
- Pricing: https://huggingface.co/pricing#spaces

---

**Última atualização:** 2024-11-24
