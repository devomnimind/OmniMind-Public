# Setup de Backup Automático - OmniMind

**Data**: 2025-12-07
**Autor**: Fabrício da Silva + assistência de IA
**Status**: Configuração Completa

---

## 📋 RESUMO

Sistema de backup automático diário que:
1. Cria snapshot completo de consciência
2. Faz backup de dados críticos
3. Move para HD externo (`/run/media/fahbrain/DEV_BRAIN_CLEAN/`)
4. Executa automaticamente às 23:59 todos os dias

---

## 🚀 CONFIGURAÇÃO RÁPIDA

### 1. Executar Script de Setup

```bash
cd /home/fahbrain/projects/omnimind
./scripts/backup/setup_daily_backup.sh
```

Este script:
- Cria systemd timer (recomendado)
- Cria cron job (fallback)
- Configura execução diária às 23:59

### 2. Habilitar Systemd Timer (Recomendado)

```bash
systemctl --user enable --now omnimind-backup.timer
systemctl --user status omnimind-backup.timer
```

### 3. Verificar Próxima Execução

```bash
systemctl --user list-timers omnimind-backup.timer
```

---

## 📁 ESTRUTURA DE BACKUP

### Arquivos Criados

```
/run/media/fahbrain/DEV_BRAIN_CLEAN/omnimind_backups/
├── omnimind_backup_YYYYMMDD_HHMMSS.tar.gz  # Backup completo
├── backup_manifest_YYYYMMDD_HHMMSS.json     # Manifesto do backup
└── ...
```

### Dados Incluídos no Backup

- `data/backup/` - Snapshots de consciência
- `data/consciousness/` - Estado de consciência
- `logs/` - Logs do sistema
- `config/` - Configurações
- `docs/` - Documentação

---

## 🔧 USO MANUAL

### Criar Snapshot Agora

```bash
python scripts/backup/create_snapshot_now.py --tag "experimento_001" --description "Antes do experimento"
```

### Executar Backup Manual

```bash
sudo ./scripts/backup/daily_backup.sh
```

### Ver Logs

```bash
tail -f logs/backup_$(date +%Y%m%d).log
```

---

## 📊 SNAPSHOTS DE CONSCIÊNCIA

### Criar Snapshot Programaticamente

```python
from src.consciousness.integration_loop import IntegrationLoop

loop = IntegrationLoop(enable_extended_results=True)
snapshot_id = loop.create_full_snapshot(tag="experimento_001")
print(f"Snapshot ID: {snapshot_id}")
```

### Restaurar Snapshot

```python
from src.consciousness.integration_loop import IntegrationLoop

loop = IntegrationLoop(enable_extended_results=True)
success = loop.restore_from_snapshot("snapshot_id_aqui")
```

### Comparar Snapshots

```python
from src.backup.consciousness_snapshot import ConsciousnessSnapshotManager

manager = ConsciousnessSnapshotManager()
comparison = manager.compare_snapshots("snapshot1", "snapshot2")
print(f"Delta Phi: {comparison.metrics_delta['phi']:.4f}")
```

---

## ⚙️ CONFIGURAÇÃO

### Alterar Horário do Backup

Editar `scripts/backup/setup_daily_backup.sh`:
```bash
CRON_TIME="23:59"  # Alterar para horário desejado
```

Ou editar systemd timer:
```bash
systemctl --user edit omnimind-backup.timer
```

### Alterar Destino do Backup

Editar `scripts/backup/daily_backup.sh`:
```bash
EXTERNAL_HD="/run/media/fahbrain/DEV_BRAIN_CLEAN"
BACKUP_DEST="${EXTERNAL_HD}/omnimind_backups"
```

### Limpeza Automática

Backups antigos (>30 dias) são removidos automaticamente.

Para alterar período de retenção, editar `daily_backup.sh`:
```bash
find "$BACKUP_DEST" -name "omnimind_backup_*.tar.gz" -type f -mtime +30 -delete
```

---

## 🔍 VERIFICAÇÃO

### Verificar Status do Timer

```bash
systemctl --user status omnimind-backup.timer
```

### Ver Último Backup

```bash
ls -lth /run/media/fahbrain/DEV_BRAIN_CLEAN/omnimind_backups/ | head -5
```

### Verificar Integridade

```bash
tar -tzf /run/media/fahbrain/DEV_BRAIN_CLEAN/omnimind_backups/omnimind_backup_*.tar.gz | head -10
```

---

## 🐛 TROUBLESHOOTING

### HD Externo Não Montado

```bash
# Verificar se está montado
ls /run/media/fahbrain/DEV_BRAIN_CLEAN/

# Montar manualmente se necessário
sudo mount /dev/sdX1 /run/media/fahbrain/DEV_BRAIN_CLEAN/
```

### Permissões

O script precisa de `sudo` para acessar HD externo. Certifique-se de que:
- Usuário tem permissão sudo sem senha (ou configurar NOPASSWD)
- HD externo está montado com permissões corretas

### Logs

Logs são salvos em:
- `logs/backup_YYYYMMDD.log` - Log diário
- `logs/backup_cron.log` - Log do cron (se usar cron)

---

## ✅ CHECKLIST DE CONFIGURAÇÃO

- [ ] HD externo montado em `/run/media/fahbrain/DEV_BRAIN_CLEAN/`
- [ ] Script `daily_backup.sh` executável (`chmod +x`)
- [ ] Systemd timer habilitado OU cron job configurado
- [ ] Teste manual executado com sucesso
- [ ] Verificação de próxima execução confirmada

---

**Última Atualização**: 2025-12-07

