# 🎬 SIMULAÇÃO EXECUTIVA - O QUE ACONTECERÁ AO RODAR O SCRIPT

**Arquivo:** `scripts/migration/install_system_databases.sh`
**Tamanho:** 490 linhas (completo e pronto)
**Status:** ✅ PRONTO PARA EXECUTAR

---

## 📺 O QUE VERÁ NA TELA

### Linha 1: Detecção de Ambiente
```bash
════════════════════════════════════════════════════════════
PHASE 0: Verificação de Ambiente e Backup
════════════════════════════════════════════════════════════

[INFO] Detectando sistema...
[INFO]   → grep "22.04" /etc/os-release
[✓] Ubuntu 22.04 LTS detectado
[INFO] Detectando GPU...
[INFO]   → nvidia-smi
[✓] NVIDIA GPU detectada: GeForce GTX 1650
[INFO] Detectando CUDA...
[INFO]   → nvcc --version
[✓] CUDA 12.2 encontrado
[INFO] Verificando backup...
[INFO]   → ls -la /media/fahbrain/DEV_BRAIN_CLEAN/databases/20251214_070626/
[✓] Backup acessível: 1.8GB de Qdrant
```

### Linha 2: Pergunta de Confirmação
```bash
⚠ AVISO CRÍTICO:
   Esta migração vai instalar serviços no SISTEMA OS
   ✓ Redis em /var/lib/redis
   ✓ PostgreSQL em /var/lib/postgresql
   ✓ Qdrant em /var/lib/qdrant
   ✓ Criar .venv com Python 3.12.8

   Espaço necessário: ~15GB
   Espaço disponível: 279GB (/home)

Continue? (sim/não):
```

**Você digita:** `sim` (ou s/yes/y)

### Linha 3-5: Instalação de Serviços (Phase 1)
```bash
════════════════════════════════════════════════════════════
PHASE 1: Instalar Bancos de Dados no Sistema OS
════════════════════════════════════════════════════════════

[INFO] Instalando Redis...
[INFO]   → sudo apt-get install -y redis-server
[...output do apt...]
[✓] Redis instalado

[INFO] Instalando PostgreSQL...
[INFO]   → sudo apt-get install -y postgresql postgresql-contrib
[...output do apt...]
[✓] PostgreSQL instalado

[INFO] Instalando Qdrant...
[INFO]   → curl -L https://releases.qdrant.io/.../qdrant-x86_64-linux
[...download 50MB...]
[✓] Qdrant instalado em /usr/local/bin/qdrant

[INFO] Configurando serviços systemd...
[INFO]   → sudo systemctl enable redis-server postgresql qdrant
[✓] Serviços habilitados para auto-start
```

**Tempo:** ~5 minutos

### Linha 6-8: Restauração de Backup (Phase 2)
```bash
════════════════════════════════════════════════════════════
PHASE 2: Restaurar Dados do Backup
════════════════════════════════════════════════════════════

[INFO] Stopping Qdrant service...
[INFO]   → sudo systemctl stop qdrant
[✓] Serviço parado

[INFO] Copiando dados de Qdrant do backup...
[INFO]   → sudo cp -r /media/fahbrain/DEV_BRAIN_CLEAN/databases/20251214_070626/qdrant/* /var/lib/qdrant/
[...cópia de 1.8GB...]
[✓] 1,847,392 bytes copiados

[INFO] Corrigindo permissões...
[INFO]   → sudo chown -R qdrant:qdrant /var/lib/qdrant
[✓] Permissões corrigidas

[INFO] Iniciando Qdrant...
[INFO]   → sudo systemctl start qdrant
[INFO] Aguardando Qdrant inicializar...
[INFO]   → curl http://localhost:6333/health (retry 1/10)
[INFO]   → curl http://localhost:6333/health (retry 2/10)
[✓] Qdrant respondendo na porta 6333
```

**Tempo:** ~3 minutos

### Linha 9-12: Python + GPU (Phase 3)
```bash
════════════════════════════════════════════════════════════
PHASE 3: Setup Python 3.12.8 + GPU
════════════════════════════════════════════════════════════

[INFO] Instalando Python 3.12...
[INFO]   → sudo apt-get install -y python3.12 python3.12-venv python3.12-dev
[...output apt...]
[✓] Python 3.12 instalado

[INFO] Criando venv em .venv...
[INFO]   → python3.12 -m venv .venv
[✓] Virtual environment criado

[INFO] Ativando venv e instalando dependências...
[INFO]   → source .venv/bin/activate
[INFO]   → pip install --upgrade pip setuptools wheel
[...upgrade pip...]
[✓] Pip atualizado

[INFO] Instalando Qiskit...
[INFO]   → pip install qiskit==1.0.2
[...instalação...]
[✓] Qiskit 1.0.2 instalado

[INFO] Compilando Qiskit-Aer com GPU (CUDA 12.2)...
[INFO]   → pip install --no-binary qiskit-aer qiskit-aer[gpu]
[...compilação ~20 minutos...]
Building qiskit_aer-0.14.2...
[████████████████████████████████] 100% (23 files)
[✓] Qiskit-Aer compilado com GPU

[INFO] Instalando PyTorch com CUDA 12.2...
[INFO]   → pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu122
[...download e instalação...]
[✓] PyTorch com GPU instalado

[INFO] Validando GPU...
[INFO]   → python -c "import torch; print(torch.cuda.is_available())"
True
[✓] GPU disponível no PyTorch
```

**Tempo:** ~30-40 minutos (compilação é lenta)

### Linha 13-15: Configuração de Código (Phase 4)
```bash
════════════════════════════════════════════════════════════
PHASE 4: Configurar Código para Sistema OS
════════════════════════════════════════════════════════════

[INFO] Criando src/config/database_os.py...
[✓] Arquivo criado com suporte a localhost

[INFO] Criando .env.system...
[✓] Arquivo criado com variáveis de ambiente

[INFO] Atualizando config/omnimind.yaml...
[INFO]   Substituindo: qdrant:6333 → localhost:6333
[INFO]   Substituindo: redis:6379 → localhost:6379
[✓] config/omnimind.yaml atualizado

[INFO] Atualizando src/api/main.py...
[INFO]   Importando: from src.config.database_os import DatabaseConfig
[✓] src/api/main.py atualizado

[INFO] Criando docker-compose-experiments.yml...
[✓] Arquivo criado para testes isolados
```

**Tempo:** ~1 minuto

### Linha 16-20: Validação Final (Phase 5)
```bash
════════════════════════════════════════════════════════════
PHASE 5: Validação Completa
════════════════════════════════════════════════════════════

[INFO] Testando Redis...
[INFO]   → redis-cli ping
PONG
[✓] Redis está respondendo

[INFO] Testando PostgreSQL...
[INFO]   → psql -U omnimind -d omnimind -c "SELECT 1"
 ?column?
──────────
        1
[✓] PostgreSQL está respondendo

[INFO] Testando Qdrant...
[INFO]   → curl http://localhost:6333/health
{"status":"ok"}
[✓] Qdrant está respondendo

[INFO] Testando conexão com Backend...
[INFO]   → python -c "import sys; sys.path.insert(0, 'src'); from api.main import app"
[✓] Backend pode ser importado

[INFO] Testando GPU...
[INFO]   → python -c "import torch; print(torch.cuda.is_available())"
True
[✓] GPU está disponível

════════════════════════════════════════════════════════════
✅ TODAS AS VALIDAÇÕES PASSARAM!
════════════════════════════════════════════════════════════

Próximos passos:
1. Ativar ambiente: source .venv/bin/activate
2. Injetar config: source .env.system
3. Iniciar backend: ./scripts/canonical/system/run_cluster.sh
4. Iniciar frontend: cd web/frontend && npm run dev
5. Testar: curl http://localhost:8000/health
```

---

## 🔍 DETALHES INTERNOS DO SCRIPT

### Estrutura de Fases

```
Phase 0: Check & Backup (2 min)
  ├─ Detectar Ubuntu 22.04
  ├─ Detectar NVIDIA GPU
  ├─ Verificar CUDA 12.2
  ├─ Confirmar backup acessível
  └─ Criar diretório logs/

Phase 1: Install (5 min)
  ├─ apt-get install redis-server
  ├─ apt-get install postgresql
  ├─ Download qdrant binary
  ├─ Install qdrant systemd
  └─ Enable auto-start

Phase 2: Restore (3 min)
  ├─ Stop Qdrant service
  ├─ Copy /media/.../qdrant → /var/lib/qdrant
  ├─ Fix permissions
  ├─ Start Qdrant
  └─ Verify health

Phase 3: Python + GPU (35 min) ⏱️ MÃS LONGO
  ├─ apt-get install python3.12
  ├─ python3.12 -m venv .venv
  ├─ pip install qiskit
  ├─ pip install qiskit-aer[gpu] (LENTO - compilação)
  ├─ pip install torch cu122
  └─ Validate torch.cuda

Phase 4: Code Config (1 min)
  ├─ Create database_os.py
  ├─ Create .env.system
  ├─ Update omnimind.yaml
  ├─ Update api/main.py
  └─ Create docker-compose-experiments.yml

Phase 5: Validate (2 min)
  ├─ Test redis-cli
  ├─ Test psql
  ├─ Test qdrant health
  ├─ Test python imports
  ├─ Test GPU availability
  └─ Report status
```

**Total:** ~45-55 minutos

### Arquivo de Log

```
Salvo em: logs/migration_YYYYMMDD_HHMMSS.log

Exemplo de conteúdo:
[2025-12-16 14:23:15] PHASE: Check & Backup
[2025-12-16 14:23:15] [INFO] Detectando sistema...
[2025-12-16 14:23:16] [SUCCESS] Ubuntu 22.04 LTS detectado
[2025-12-16 14:23:17] [INFO] Detectando GPU...
[2025-12-16 14:23:18] [SUCCESS] NVIDIA GPU detectada: GeForce GTX 1650
...
[2025-12-16 15:08:42] PHASE: Validação Completa
[2025-12-16 15:08:43] [SUCCESS] TODAS AS VALIDAÇÕES PASSARAM!
```

---

## 🛑 O QUE PODE DAR ERRADO (E COMO RECUPERAR)

### Erro: "Redis não pode ser instalado"
```bash
# Provável causa: repositórios não atualizados
# Solução:
sudo apt update
sudo apt upgrade

# Depois:
./scripts/migration/install_system_databases.sh --phase 1
```

### Erro: "GPU não detectada na Phase 3"
```bash
# Provável causa: CUDA 12.2 não carregado
# Verificar:
nvidia-smi

# Se falhar, reiniciar:
sudo systemctl restart nvidia-device-manager  # ou
sudo reboot

# Depois rodar Phase 3 novamente
```

### Erro: "Qiskit-Aer compilation failed"
```bash
# Provável causa: Sem ferramentas de build
# Solução:
sudo apt install -y build-essential cmake

# Depois rodar Phase 3 novamente:
./scripts/migration/install_system_databases.sh --phase 3
```

### Erro: "Backup não encontrado"
```bash
# Verificar se HD externo está montado:
mount | grep DEV_BRAIN_CLEAN

# Se não estiver:
sudo mkdir -p /media/fahbrain
sudo mount /dev/sdb1 /media/fahbrain/DEV_BRAIN_CLEAN

# Depois rodar Phase 2 novamente
```

---

## 💡 DICAS IMPORTANTES

### 1. Rodar Fase por Fase é SEGURO
```bash
# Você pode parar em qualquer phase
./scripts/migration/install_system_databases.sh --phase 0
# Verificar tudo está ok
./scripts/migration/install_system_databases.sh --phase 1
# Esperar terminar
./scripts/migration/install_system_databases.sh --phase 2
# Etc...
```

### 2. Logs São Seus Amigos
```bash
# Acompanhar em tempo real:
tail -f logs/migration_*.log

# Ver último erro:
tail -20 logs/migration_*.log | grep ERROR

# Ver tudo:
cat logs/migration_*.log
```

### 3. Rollback é Fácil
```bash
# Se Phase 1 falhar, você pode:
1. Verificar o erro no log
2. Corrigir o problema (ex: apt update)
3. Rodar Phase 1 novamente

# Não perde nada porque Phase 0 não muda nada
```

### 4. GPU É a Parte Lenta
```bash
# Phase 3 (Python + GPU) leva 35-40 minutos
# Principalmente porque compila Qiskit-Aer com GPU

# NÃO cancele no meio!
# Se cancelar, tem que refazer do início

# Deixe rodar enquanto você:
# - Toma um café
# - Lê documentação
# - Faz outra coisa
```

---

## ✅ CHECKLIST ANTES DE RODAR

- [ ] Está em `/home/fahbrain/projects/omnimind`?
- [ ] HD externo montado em `/media/fahbrain/DEV_BRAIN_CLEAN`?
- [ ] `nvidia-smi` funciona (GPU detectada)?
- [ ] `nvcc --version` mostra CUDA 12.2?
- [ ] Tem ~15GB livres em /home?
- [ ] Está com acesso sudo?
- [ ] Tem tempo para esperar ~50 minutos?

Se tudo OK:

```bash
chmod +x scripts/migration/install_system_databases.sh
./scripts/migration/install_system_databases.sh
```

🚀 **Migração iniciada!**

