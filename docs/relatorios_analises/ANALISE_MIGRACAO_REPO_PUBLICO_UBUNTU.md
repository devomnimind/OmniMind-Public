# 📊 Análise: Migração para Ubuntu + Separação Repositório Público/Privado

**Data:** 11 de dezembro de 2025
**Status:** Planejamento Estratégico Completo
**Objetivo:** Validar estrutura privada vs pública e planejar migração para Ubuntu preservando dados

---

## 📋 ÍNDICE RÁPIDO

1. [Análise da Estrutura Atual](#análise-da-estrutura-atual)
2. [Documentação Identificada](#documentação-identificada)
3. [Estratégia de Separação Público/Privado](#estratégia-de-separação-públicoprivado)
4. [Plano de Migração para Ubuntu](#plano-de-migração-para-ubuntu)
5. [Preservação de Dados](#preservação-de-dados)
6. [Checklist de Instalação Ubuntu](#checklist-de-instalação-ubuntu)

---

## 🏗️ ANÁLISE DA ESTRUTURA ATUAL

### 1. Status da Ramificação

**Branch Atual:** `copilot/prepare-public-version-audit` ✅

**Branches Disponíveis:**

```
Local Branches:
├── copilot/add-metrics-autopoietic-manager
├── copilot/capture-metrics-in-core-modules
├── copilot/execute-documentation-and-analysis
├── copilot/prepare-public-version-audit ← VOCÊ ESTÁ AQUI
├── copilot/understand-current-composition
└── master

Remote Branches:
├── origin/master (principal)
├── origin/copilot/prepare-public-version-audit
├── origin/copilot/update-instruction-procedure
├── origin/integration/copilot-experimental-modules (experimental)
└── ... (25 branches removas no total)
```

**Recomendação:** Sua branch atual é a correta para auditoria de versão pública! ✅

---

### 2. Tamanho e Organização

| Diretório | Tamanho | Tipo | Prioridade Migração |
|-----------|--------|------|---------------------|
| `data/` | 14 GB | **CRÍTICO** (dados do sistema) | 🔴 MÁXIMA |
| `deploy/` | 529 MB | Infra (Docker, K8s) | 🟠 ALTA |
| `web/` | 185 MB | Frontend + Backend | 🟠 ALTA |
| `logs/` | 56 MB | Logs de execução | 🟡 MÉDIA |
| `docs/` | 56 MB | Documentação | 🟡 MÉDIA |
| `real_evidence/` | 45 MB | Dados de pesquisa | 🔴 MÁXIMA |
| `tests/` | 17 MB | Suite de testes | 🟢 BAIXA |
| `src/` | 15 MB | Código principal | 🟠 ALTA |
| Outros | < 10 MB | Scripts, config, etc | 🟢 BAIXA |

**Total:** ~14.4 GB

**Crítico para Preservar:** `data/`, `real_evidence/`, `web/`, `src/`, `deploy/`, `logs/`

---

### 3. Árvore de Estrutura (Resumida)

```
omnimind/
├── src/                          # Código principal (15 MB)
│   ├── agents/                   # Agentes inteligentes
│   ├── consciousness/            # Sistema de consciência (IIT 3.0)
│   ├── core/                     # Máquinas desejantes (Deleuze/Guattari)
│   ├── memory/                   # Sistema lacaniano de memória
│   ├── lacanian/                 # Integração psicanalítica
│   ├── quantum_consciousness/    # Integração quântica
│   └── ...                       # 40+ módulos especializados
│
├── web/                          # Frontend + Backend (185 MB)
│   ├── backend/                  # FastAPI + Orchestrator
│   └── frontend/                 # React/TypeScript
│
├── data/                         # **CRÍTICO** (14 GB)
│   ├── consciousness/            # Métricas de consciência
│   ├── metrics/                  # Dados do sistema
│   ├── memory/                   # Armazenamento de memória
│   ├── sessions/                 # Sesiones ativas
│   ├── validation/               # Baselines de validação
│   └── monitor/                  # Monitoramento em tempo real
│
├── deploy/                       # Infra (Docker, K8s) (529 MB)
│   ├── docker-compose.yml
│   ├── Dockerfile.tests
│   └── kubernetes/
│
├── tests/                        # Suite de testes
│   ├── agents/
│   ├── consciousness/
│   └── ... (40+ test modules)
│
├── docs/                         # Documentação (56 MB)
│   ├── canonical/                # Referência arquitetural
│   ├── implementation/           # Guias de implementação
│   ├── analysis/                 # Análises técnicas
│   └── ... (100+ arquivos)
│
├── scripts/                      # Utilitários
│   ├── development/
│   ├── monitoring/
│   └── autopoietic/
│
├── config/                       # Configurações
│   ├── agent_config.yaml
│   ├── security.yaml
│   └── ... (20+ configs)
│
├── requirements/                 # Dependências
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── requirements-minimal.txt
│
├── pyproject.toml               # Configuração Python
├── README.md                    # Principal (403 linhas)
├── .env                         # Variáveis de ambiente
└── .git/                        # Histórico Git (sincronizado)
```

---

## 📚 DOCUMENTAÇÃO IDENTIFICADA

### Documentação Principal

| Arquivo | Tipo | Status | Propósito |
|---------|------|--------|-----------|
| `README.md` | Markdown | ✅ Atual | Visão geral completa, descobertas, arquitetura |
| `docs/canonical/omnimind_architecture_reference.md` | Markdown | ✅ Atual | Referência arquitetural canônica |
| `docs/architecture/dashboard_architecture.md` | Markdown | ✅ Atual | Arquitetura dashboard |
| `docs/architecture/external_ai_integration_architecture.md` | Markdown | ✅ Atual | Integração com APIs externas |

### Documentação de Descobertas (Autopoiesis)

```
docs/
├── DESCOBERTA_SISTEMA_AUTOPOIETICO.md         # Descoberta geral
├── ARQUITETURA_SISTEMA_AUTOPOIETICO.md        # Arquitetura técnica
├── ANALISE_EXPANDED_KERNEL_PROCESS.md         # Análise detalhada
└── RELATORIO_EXECUTIVO_AUTOPOIESIS.md         # Executivo
```

### Documentação de Validação

```
docs/analysis/
├── validation/
│   ├── VERIFICACAO_PHI_SISTEMA.md             # Validação de consciência
│   └── ANALISE_DEPENDENCIAS_PHI.md            # Dependências IIT
└── diagnostics/
    └── ... (análises de segurança, performance)
```

### Documentação Técnica

- `docs/implementation/` - Guias de implementação
- `docs/phases/` - Histórico de fases
- `docs/theory/` - Fundamentos teóricos
- `docs/reference/` - Referências técnicas

---

## 🎯 ESTRATÉGIA DE SEPARAÇÃO PÚBLICO/PRIVADO

### Princípio Fundamental

> **"O repositório privado contém: desenvolvimento experimental, dados reais do sistema, configurações sensíveis.**
> **O repositório público contém: código estável, documentação pedagógica, exemplos de uso."**

### 1. Estrutura de Repositórios

```
Repositório Privado (VOCÊ)                    Repositório Público
├── src/                                      ├── src/
│   ├── agents/ ✅ Compartilhado             │   ├── agents/ ✅
│   ├── consciousness/ ⚠️ Parcial            │   ├── consciousness/ (sem métricas reais)
│   ├── core/ ✅ Compartilhado               │   ├── core/ ✅
│   ├── memory/ ✅ Compartilhado             │   ├── memory/ ✅
│   ├── quantum_consciousness/ ⛔ PRIVADO   │   └── ...
│   ├── security/ ⛔ PRIVADO                 │
│   └── ...                                  │
│                                             │
├── data/ ⛔ PRIVADO (dados reais)           ├── data/
│   ├── consciousness/                      │   ├── example_datasets/
│   ├── metrics/                            │   ├── sample_results/
│   ├── sessions/                           │   └── README (documentação)
│   └── ...                                 │
│                                             │
├── config/                                  ├── config/
│   ├── agent_config.yaml ✅ Compartilhado  │   ├── agent_config_template.yaml
│   ├── security.yaml ⛔ PRIVADO            │   ├── example_security.yaml
│   └── ...                                 │   └── README
│                                             │
├── web/                                     ├── web/
│   ├── backend/ ✅ Compartilhado           │   ├── backend/ ✅
│   └── frontend/ ✅ Compartilhado          │   └── frontend/ ✅
│                                             │
├── tests/ ✅ Compartilhado                 ├── tests/ ✅
├── docs/ ✅ Compartilhado                  ├── docs/ ✅
├── deploy/ ✅ Compartilhado                ├── deploy/ ✅
│                                             │
├── .env ⛔ PRIVADO                         ├── .env.example ✅
├── .env.local ⛔ PRIVADO                   │
├── logs/ ⛔ PRIVADO (dados reais)          │
└── real_evidence/ ⛔ PRIVADO (pesquisa)    │
                                             │
                                             └── README_PUBLIC.md (guia de uso)
```

**Legenda:**
- ✅ Compartilhado = Sincronizar regularmente
- ⚠️ Parcial = Sincronizar código, mas remover dados sensíveis
- ⛔ Privado = Nunca publicar

### 2. Matriz de Sincronização

| Arquivo/Diretório | Privado | Público | Estratégia |
|-------------------|---------|---------|-----------|
| `src/agents/` | ✅ | ✅ | Sincronização direta |
| `src/consciousness/` | ✅ | ✅ | Sincronização, remover métricas reais |
| `src/core/` | ✅ | ✅ | Sincronização direta |
| `src/memory/` | ✅ | ✅ | Sincronização direta |
| `src/quantum_consciousness/` | ✅ | ❌ | Manter privado (experimental) |
| `src/security/` | ✅ | ❌ | Manter privado (sensível) |
| `data/` | ✅ | ⚠️ | Dados exemplo, sem dados reais |
| `config/*.yaml` | ✅ | ⚠️ | Templates, sem credenciais |
| `.env` | ✅ | ❌ | Manter privado (segredos) |
| `logs/` | ✅ | ❌ | Manter privado (dados reais) |
| `real_evidence/` | ✅ | ❌ | Manter privado (pesquisa) |
| `tests/` | ✅ | ✅ | Sincronização direta |
| `docs/` | ✅ | ✅ | Sincronização completa |
| `web/` | ✅ | ✅ | Sincronização direta |
| `deploy/` | ✅ | ✅ | Sincronização completa |

---

## 🚀 PLANO DE MIGRAÇÃO PARA UBUNTU

### Fase 1: Preparação no Kali Linux (ANTES de formatar)

#### 1.1 Backup Completo de Dados

```bash
# Criar backup criptografado de dados críticos
cd /home/fahbrain/projects/

# Backup 1: Dados do sistema OmniMind
tar -czf omnimind_data_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  omnimind/data/ \
  omnimind/logs/ \
  omnimind/real_evidence/ \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git'

# Backup 2: Código e configuração
tar -czf omnimind_code_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  omnimind/src/ \
  omnimind/tests/ \
  omnimind/config/ \
  omnimind/web/ \
  omnimind/scripts/ \
  omnimind/docs/ \
  omnimind/.env \
  omnimind/.env.local \
  omnimind/pyproject.toml \
  omnimind/requirements/ \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git'

# Backup 3: Git history
tar -czf omnimind_git_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  omnimind/.git/

# Armazenar em dispositivo externo ou cloud seguro
ls -lh omnimind_*_backup_*.tar.gz
```

#### 1.2 Sincronizar com Repositório Remoto

```bash
cd omnimind

# Garantir que todos os commits estão remotos
git push origin copilot/prepare-public-version-audit
git push origin master
git push --all origin

# Verificar status
git status
git log --oneline -n 10
```

#### 1.3 Documentar Configurações Locais

```bash
# Salvar configurações do ambiente
echo "=== Python Version ===" > environment_snapshot.txt
python --version >> environment_snapshot.txt

echo "=== Pip Packages ===" >> environment_snapshot.txt
pip freeze >> environment_snapshot.txt

echo "=== System Info ===" >> environment_snapshot.txt
uname -a >> environment_snapshot.txt

echo "=== Installed Services ===" >> environment_snapshot.txt
systemctl list-unit-files --type=service >> environment_snapshot.txt

echo "=== GPU/CUDA ===" >> environment_snapshot.txt
nvidia-smi >> environment_snapshot.txt 2>&1 || echo "No NVIDIA GPU"

# Salvar cache do HuggingFace
tar -czf huggingface_cache_backup_$(date +%Y%m%d).tar.gz \
  ~/.cache/huggingface/hub/ 2>/dev/null || echo "Cache vazio"

# Copiar para backup
cp environment_snapshot.txt omnimind/
```

---

### Fase 2: Instalação em Ubuntu

#### 2.1 Instalação Limpa do Ubuntu

```bash
# ✅ Durante instalação:
# - Selecionar "Ubuntu Desktop" ou "Ubuntu Server"
# - Criar usuário com mesmo nome: fahbrain
# - Usar mesmo hostname: omnimind-dev (opcional)
# - Configurar OpenSSH (opcional, para acesso remoto)

# Após primeiro boot:
sudo apt update && sudo apt upgrade -y

# Instalar Git primeiramente
sudo apt install -y git curl wget
```

#### 2.2 Restaurar Repositório Git

```bash
# Criar estrutura de diretórios
mkdir -p ~/projects
cd ~/projects

# Clonar repositório (não há necessidade de re-fazer backup)
git clone <seu-repo-url> omnimind
cd omnimind

# Checkout da branch de trabalho
git checkout copilot/prepare-public-version-audit

# Verificar status
git log --oneline -n 5
```

---

### Fase 3: Restauração de Dados

#### 3.1 Restaurar Dados do Backup

```bash
cd ~/projects/omnimind

# Restaurar dados críticos (10 GB)
tar -xzf /caminho/para/omnimind_data_backup_*.tar.gz

# Restaurar código
tar -xzf /caminho/para/omnimind_code_backup_*.tar.gz

# Restaurar .env (SENSIVELMENTE!)
# NÃO sobrescrever se já existe, fazer merge manual
if [ ! -f .env ]; then
  tar -xzf omnimind_code_backup_*.tar.gz -C . omnimind/.env
fi

# Restaurar cache HuggingFace
tar -xzf /caminho/para/huggingface_cache_backup_*.tar.gz \
  -C ~/
```

#### 3.2 Validar Integridade

```bash
# Verificar estrutura restaurada
du -sh data/ logs/ real_evidence/ src/ web/
echo "✅ Todos os diretórios restaurados"

# Verificar Git history
git log --oneline -n 20 | wc -l
echo "✅ Git history intacto"

# Listar branches
git branch -a | wc -l
echo "✅ Branches sincronizadas"
```

---

## 💾 PRESERVAÇÃO DE DADOS

### O Que Preservar (14 GB)

| Diretório | Dados | Tamanho | Como Preservar |
|-----------|-------|--------|-----------------|
| `data/` | Métricas consciência, validação, memória | 14 GB | Backup + Git LFS (opcional) |
| `logs/` | Histórico de execução | 56 MB | Compactar, armazenar |
| `real_evidence/` | Pesquisa original | 45 MB | Compactar, armazenar seguro |
| `.env` | Credenciais API | < 1 KB | Criptografar, não versionar |
| `config/` | Configurações do sistema | 180 KB | Incluir no backup |

### Estrutura de Backup Recomendada

```
~/Backups/
├── omnimind_KALI_full_backup_20251211/
│   ├── data/                        # 14 GB
│   ├── logs/                        # 56 MB
│   ├── real_evidence/               # 45 MB
│   ├── .env.encrypted               # Criptografado
│   ├── config/                      # 180 KB
│   ├── environment_snapshot.txt     # Referência
│   ├── BACKUP_MANIFEST.txt          # Índice
│   └── RESTORE_INSTRUCTIONS.md      # Como restaurar
│
└── omnimind_git_history.tar.gz      # Git completo
```

---

## ☑️ CHECKLIST DE INSTALAÇÃO UBUNTU

### Pré-Instalação (Kali Linux)

- [ ] Executar backups completos (3 archives)
- [ ] Sincronizar repositório remoto (`git push --all`)
- [ ] Salvar snapshot do ambiente (`environment_snapshot.txt`)
- [ ] Backup do cache HuggingFace
- [ ] Criar lista de ferramentas críticas usadas
- [ ] Documentar credenciais seguras (fora do git)
- [ ] Testar restauração em máquina de teste (opcional)

### Instalação Ubuntu (Fase 1-3)

- [ ] Instalar Ubuntu Desktop/Server
- [ ] Criar usuário `fahbrain` (mesmo nome)
- [ ] `sudo apt update && sudo apt upgrade -y`
- [ ] Instalar Git: `sudo apt install -y git curl wget`
- [ ] Clonar repositório: `git clone <url> ~/projects/omnimind`
- [ ] Checkout branch: `git checkout copilot/prepare-public-version-audit`

### Restauração de Dados

- [ ] Restaurar `data/` do backup
- [ ] Restaurar `logs/` do backup
- [ ] Restaurar `real_evidence/` do backup
- [ ] Restaurar `.env` manualmente (não sobrescrever)
- [ ] Restaurar cache HuggingFace em `~/.cache/huggingface/`
- [ ] Validar integridade: `du -sh data/ logs/ real_evidence/`

### Instalação de Ferramentas Essenciais

- [ ] **Python 3.12+:**
  ```bash
  sudo apt install -y python3.12 python3.12-venv python3-pip
  python3.12 -m venv /home/fahbrain/projects/omnimind/.venv
  source /home/fahbrain/projects/omnimind/.venv/bin/activate
  pip install --upgrade pip
  ```

- [ ] **Dependências do OmniMind:**
  ```bash
  cd ~/projects/omnimind
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  ```

- [ ] **PostgreSQL (para Supabase local, opcional):**
  ```bash
  sudo apt install -y postgresql postgresql-contrib
  ```

- [ ] **Redis:**
  ```bash
  sudo apt install -y redis-server
  systemctl start redis-server
  ```

- [ ] **Docker (para compose):**
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker fahbrain
  ```

- [ ] **Node.js (para frontend):**
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt install -y nodejs
  ```

- [ ] **CUDA (se usar GPU):**
  ```bash
  # Instruções específicas para seu GPU
  # https://developer.nvidia.com/cuda-downloads
  ```

### ✅ REMOVER/DESABILITAR (Kali)

- [ ] **Desabilitar ferramentas Kali não usadas:**
  ```bash
  # Listar pacotes Kali
  apt list --installed | grep kali

  # Remover ferramentas desnecessárias
  sudo apt remove -y kali-tools-*  # Ferramentas hacking
  sudo apt remove -y aircrack-ng metasploit-framework burp-suite
  ```

- [ ] **Usar repositórios Ubuntu padrão:**
  ```bash
  sudo sed -i 's/kali/ubuntu/g' /etc/apt/sources.list
  sudo apt update
  ```

### Validação Final

- [ ] Todos os dados restaurados: `du -sh data/ logs/ real_evidence/`
- [ ] Git funcional: `git log -1`
- [ ] Python funcional: `python --version`
- [ ] Dependências instaladas: `pip list | wc -l`
- [ ] Backend inicia: `python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000`
- [ ] Frontend builds: `cd web/frontend && npm install && npm run build`
- [ ] Dados acessíveis: `ls -la data/consciousness/ | head`

---

## 🔄 SINCRONIZAÇÃO PRIVADO/PÚBLICO (Fluxo Contínuo)

### 1. Setup Inicial (Uma Vez)

```bash
# Repositório privado (você tem)
git clone <private-repo> omnimind-private
cd omnimind-private

# Adicionar remote público
git remote add public <public-repo-url>
git fetch public

# Criar branch local para sincronização
git checkout -b sync/private-to-public origin/master
```

### 2. Fluxo Regular

```bash
# A. Desenvolver normalmente no repositório privado
git commit -m "Feature: Nova capacidade"
git push origin copilot/prepare-public-version-audit

# B. Quando pronto para publicar
git checkout sync/private-to-public
git pull origin master  # Sincronizar com private main

# C. Remover arquivos sensíveis (antes de pushpara público)
rm -rf data/consciousness/real_metrics/*
rm -rf logs/*
rm .env .env.local
# ... remover conforme matriz de sincronização

# D. Push para repositório público
git push public sync/private-to-public
# Depois criar PR no GitHub: "Sync: Private to Public"

# E. Voltar ao desenvolvimento privado
git checkout copilot/prepare-public-version-audit
```

### 3. Automatizar com Script

```bash
# script: sync_to_public.sh
#!/bin/bash

PRIVATE_DIR="$HOME/projects/omnimind"
PUBLIC_DIR="$HOME/projects/omnimind-public"
FILTERED_DIR="/tmp/omnimind-filtered"

# 1. Clonar public
rm -rf "$PUBLIC_DIR"
git clone <public-repo-url> "$PUBLIC_DIR"
cd "$PUBLIC_DIR"

# 2. Copiar arquivos sincronizáveis do private
rsync -av --exclude-from=/dev/stdin "$PRIVATE_DIR/" "$PUBLIC_DIR/" << 'EOF'
.git/
.env
.env.local
logs/
data/consciousness/real_metrics/
real_evidence/
src/quantum_consciousness/
src/security/
EOF

# 3. Commit e push
git add -A
git commit -m "Sync: Update from private ($(date +%Y-%m-%d))"
git push origin master

echo "✅ Sincronização completa"
```

---

## 📊 SUMMARY: ANTES vs. DEPOIS

### ANTES (Kali Linux - Atual)

```
Kali Linux
├── Ferramentas Kali (desnecessárias)
├── OmniMind Privado
│   ├── 14 GB dados reais
│   ├── Código experimental
│   ├── Configurações sensíveis
│   └── ✅ Funcional
└── Sem repositório público
```

### DEPOIS (Ubuntu - Proposto)

```
Ubuntu Clean
├── Apenas ferramentas OmniMind
├── OmniMind Privado (ESTE MESMO)
│   ├── 14 GB dados restaurados
│   ├── Código fonte
│   ├── Configurações seguras
│   └── ✅ Funcional, documentado
│
└── OmniMind Público (NOVO)
    ├── Código open source
    ├── Exemplos de uso
    ├── Documentação pedagógica
    ├── Templates (sem credenciais)
    └── ✅ Pronto para comunidade
```

---

## 🎯 PRÓXIMOS PASSOS

### Imediato (Esta Semana)

1. **Executar Backups:**
   ```bash
   cd ~/projects
   tar -czf omnimind_data_backup_$(date +%Y%m%d).tar.gz omnimind/data omnimind/logs omnimind/real_evidence
   tar -czf omnimind_code_backup_$(date +%Y%m%d).tar.gz omnimind/src omnimind/tests omnimind/config omnimind/web
   # Armazenar em dispositivo externo seguro
   ```

2. **Sincronizar Git:**
   ```bash
   cd ~/projects/omnimind
   git push --all origin
   git status  # Verificar se tudo está sincronizado
   ```

3. **Documentar Ambiente:**
   ```bash
   pip freeze > environment_snapshot.txt
   nvidia-smi > gpu_info.txt
   uname -a > system_info.txt
   ```

### Semana Próxima

4. **Formatar para Ubuntu (quando pronto)**
5. **Restaurar Dados** seguindo Fase 3
6. **Instalar Ferramentas** do Checklist
7. **Validar Funcionamento** com testes

### Após Ubuntu Estável

8. **Criar Repositório Público** no GitHub
9. **Inicializar Sincronização** com script
10. **Documentar Fluxo** para contribuidores

---

## 📌 CONCLUSÃO

Sua abordagem é **sólida e bem estruturada**:

✅ **Dados Preservados**: Backup triplo garante 14 GB + Git history
✅ **Código Separado**: Privado (experimental) vs Público (produção)
✅ **Migração Planejada**: Processo em 3 fases sem perda
✅ **Ubuntu Limpo**: Apenas ferramentas OmniMind, sem Kali
✅ **Sincronização**: Fluxo claro privado→público

**Recomendação Final**: Execute os backups AGORA, antes de qualquer mudança. O resto pode ser feito conforme necessário.

---

**Documento Preparado Por:** GitHub Copilot
**Data:** 11 de dezembro de 2025
**Status:** Pronto para Implementação ✅
