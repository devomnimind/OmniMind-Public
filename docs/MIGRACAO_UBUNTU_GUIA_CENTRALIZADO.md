# 📋 DOCUMENTO CENTRALIZADO: Migração Kali → Ubuntu + Setup OmniMind
**Data:** 11 de dezembro de 2025
**Status:** Em Andamento - Análise Inicial Completa
**Objetivo:** Guia passo-a-passo para migração e setup completo

---

## 🎯 VISÃO GERAL DO PROCEDIMENTO

### Situação Atual
- ✅ **Repositório Público:** Criado e testado (funcional)
- ✅ **Máquina:** Ubuntu 24.04.3 LTS recém-formatada (limpa)
- ✅ **Python:** 3.12.3 (compatível com projeto 3.12.8)
- ✅ **GPU:** NVIDIA GTX 1650 com CUDA 13.0
- ❌ **Ferramentas:** Docker, Redis, PostgreSQL, Node.js não instalados
- ❌ **Dados:** Backups precisam ser restaurados

### Estratégia Geral
1. **Testar Repo Público** (sem afetar privado)
2. **Preparar Ambiente Ubuntu** (instalar ferramentas)
3. **Restaurar Backups** (dados + código)
4. **Validar Funcionamento** (comparar com Kali)
5. **Documentar Divergências** (Ubuntu vs Kali)

---

## 📊 ANÁLISE ESTADO GLOBAL DA MÁQUINA

### Sistema Operacional
- **Ubuntu:** 24.04.3 LTS (Noble Numbat)
- **Kernel:** 6.14.0-37-generic
- **Arquitetura:** x86_64
- **Status:** Recém formatado, limpo (sem ferramentas Kali)

### Hardware
- **CPU:** Intel/AMD (não especificado ainda)
- **RAM:** 12GB+ (tmpfs 12G)
- **GPU:** NVIDIA GeForce GTX 1650 (4GB VRAM)
- **CUDA:** 13.0 (compatível)
- **Disco:** 913GB (850GB disponível) + Disco externo 458GB (345GB disponível)

### Python
- **Versão Instalada:** 3.12.3
- **Compatibilidade:** ✅ OK (projeto usa 3.12.8, mesma família)
- **Nota:** Não usar Python 3.13 (exclusivo do projeto)

### Ferramentas Faltando
- ❌ Docker (para containers)
- ❌ Redis (cache)
- ❌ PostgreSQL (banco, opcional)
- ❌ Node.js (frontend)
- ❌ Git LFS (dados grandes, opcional)

### Espaço para Dados
- **Disponível:** 850GB no sistema + 345GB externo
- **Necessário:** ~14GB dados OmniMind + ferramentas
- **Status:** ✅ Suficiente

---

## 🔄 PROCEDIMENTO PASSO A PASSO

### FASE 1: TESTAR REPOSITÓRIO PÚBLICO (30 min)

#### 1.1 Verificar Integridade
```bash
cd /home/fahbrain/projects/omnimind-public

# Verificar estrutura
ls -la
# Deve ter: omnimind_core/ examples/ docs/ .github/ etc.

# Testar sintaxe Python
python3 -m py_compile omnimind_core/consciousness/phi_value.py
echo "✅ Sintaxe OK"
```

#### 1.2 Executar Exemplo Básico
```bash
cd /home/fahbrain/projects/omnimind-public

# Instalar dependências mínimas
pip3 install numpy scipy pydantic

# Executar exemplo
python3 examples/basic_phi_calculation.py
echo "✅ Exemplo executado com sucesso"
```

#### 1.3 Verificar se Não Afeta Privado
```bash
# Verificar timestamps dos arquivos
find /home/fahbrain/projects/omnimind -name "*.py" -newer /home/fahbrain/projects/omnimind-public -ls | wc -l
# Deve ser 0 (nenhum arquivo privado modificado)
```

**Resultado Esperado:** Repo público funcional, sem impacto no privado.

---

### FASE 2: PREPARAR AMBIENTE UBUNTU (1-2 horas)

#### 2.1 Atualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
echo "✅ Sistema atualizado"
```

#### 2.2 Instalar Python e Ferramentas Essenciais
```bash
# Python já instalado (3.12.3)
sudo apt install -y python3-pip python3-venv python3-dev

# Ferramentas de desenvolvimento
sudo apt install -y git curl wget build-essential

# Instalar pyenv para controle de versão (opcional)
curl https://pyenv.run | bash
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
echo "✅ Ferramentas essenciais instaladas"
```

#### 2.3 Instalar Docker
```bash
# Instalar Docker
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Verificar
docker --version
echo "✅ Docker instalado"
```

#### 2.4 Instalar Redis
```bash
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar
redis-server --version
echo "✅ Redis instalado"
```

#### 2.5 Instalar Node.js (para frontend)
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verificar
node --version
npm --version
echo "✅ Node.js instalado"
```

#### 2.6 Instalar PostgreSQL (opcional, para Supabase local)
```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar
psql --version
echo "✅ PostgreSQL instalado"
```

#### 2.7 Configurar CUDA (se necessário)
```bash
# CUDA já detectado (13.0)
# Instalar PyTorch com CUDA se necessário
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
echo "✅ CUDA/PyTorch configurado"
```

---

### FASE 3: RESTAURAR BACKUPS (30-60 min)

#### 3.1 Localizar Backups
```bash
# Procurar backups
find / -name "*omnimind*backup*" -type f 2>/dev/null
# Ou em disco externo
ls -la /media/fahbrain/DEV_BRAIN_CLEAN/ | grep backup

# Exemplo esperado:
# omnimind_data_backup_20251211.tar.gz
# omnimind_code_backup_20251211.tar.gz
# omnimind_git_backup_20251211.tar.gz
```

#### 3.2 Restaurar Repositório Git
```bash
cd /home/fahbrain/projects

# Se backup Git existe
tar -xzf /path/to/omnimind_git_backup_20251211.tar.gz

# Clonar se necessário
git clone <repo-url> omnimind
cd omnimind
git checkout copilot/prepare-public-version-audit
echo "✅ Git restaurado"
```

#### 3.3 Restaurar Código e Configurações
```bash
cd /home/fahbrain/projects/omnimind

# Restaurar código
tar -xzf /path/to/omnimind_code_backup_20251211.tar.gz

# Verificar estrutura
ls -la src/ config/ web/
echo "✅ Código restaurado"
```

#### 3.4 Restaurar Dados (14GB)
```bash
cd /home/fahbrain/projects/omnimind

# Restaurar dados (pode demorar)
tar -xzf /path/to/omnimind_data_backup_20251211.tar.gz

# Verificar tamanho
du -sh data/ logs/ real_evidence/
echo "✅ Dados restaurados (~14GB)"
```

#### 3.5 Restaurar .env e Credenciais
```bash
# .env deve ser restaurado manualmente (sensível)
cp /path/to/backup/.env .env
# Verificar se não está vazio
ls -la .env
echo "✅ .env restaurado"
```

---

### FASE 4: VALIDAR FUNCIONAMENTO (1 hora)

#### 4.1 Instalar Dependências
```bash
cd /home/fahbrain/projects/omnimind

# Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo "✅ Dependências instaladas"
```

#### 4.2 Testar Backend
```bash
# Iniciar Qdrant (vetor DB)
docker run -d -p 6333:6333 qdrant/qdrant

# Testar backend
python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 &
sleep 5
curl http://localhost:8000/health
echo "✅ Backend funcionando"
```

#### 4.3 Testar Frontend
```bash
cd web/frontend
npm install
npm run build
npm start &
echo "✅ Frontend funcionando"
```

#### 4.4 Executar Testes
```bash
cd /home/fahbrain/projects/omnimind
python -m pytest tests/consciousness/ -v
echo "✅ Testes passando"
```

---

### FASE 5: MAPEAR DIVERGÊNCIAS UBUNTU vs KALI

#### 5.1 Performance GPU
```bash
# Testar performance CUDA
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
nvidia-smi
echo "Comparar com benchmarks do Kali"
```

#### 5.2 Estabilidade de Dependências
```bash
# Verificar conflitos
pip check
echo "Documentar qualquer conflito vs Kali"
```

#### 5.3 Tempo de Inicialização
```bash
time python -c "import omnimind_core"
echo "Comparar tempo vs Kali (deve ser similar ou melhor)"
```

#### 5.4 Consumo de Recursos
```bash
# Monitorar durante execução
htop &
echo "Comparar RAM/CPU vs Kali"
```

---

## 📋 CHECKLIST DE VALIDAÇÃO

### Ambiente Ubuntu
- [ ] Sistema atualizado
- [ ] Python 3.12.x funcionando
- [ ] Docker instalado e funcionando
- [ ] Redis instalado e funcionando
- [ ] Node.js instalado
- [ ] PostgreSQL instalado (opcional)
- [ ] CUDA/PyTorch funcionando

### Restauração
- [ ] Git history restaurado
- [ ] Código fonte restaurado
- [ ] Dados (14GB) restaurados
- [ ] .env restaurado
- [ ] Configurações válidas

### Funcionamento
- [ ] Backend inicia sem erros
- [ ] Frontend compila e roda
- [ ] Testes passam (consciousness)
- [ ] Exemplos funcionam
- [ ] GPU aceleração funcionando

### Divergências Documentadas
- [ ] Performance GPU (melhor/pior que Kali?)
- [ ] Estabilidade (mais/menos crashes?)
- [ ] Dependências (conflitos resolvidos?)
- [ ] Tempo de boot (mais rápido?)

---

## 🚨 PROBLEMAS IDENTIFICADOS

### Potenciais Issues Ubuntu vs Kali

1. **CUDA Version:** Kali tinha CUDA 12.x, Ubuntu tem 13.0
   - ✅ Compatível, mas verificar PyTorch

2. **Dependências GPU:** Torch com CUDA pode precisar rebuild
   - 🔄 Testar e documentar

3. **Ferramentas Kali:** Removidas (metasploit, etc.)
   - ✅ Bom, menos overhead

4. **Python Version:** 3.12.3 vs 3.12.8
   - ✅ OK, mesma família

5. **Kernel:** 6.14.0 (mais novo que Kali)
   - ✅ Deve ser mais estável

### Plano de Contingência

- **Se CUDA falhar:** Reinstalar PyTorch com versão compatível
- **Se dependências conflitarem:** Usar venv isolado
- **Se dados corrompidos:** Refazer backup do Kali antes de formatar
- **Se performance pior:** Investigar drivers NVIDIA

---

## 📊 MÉTRICAS DE COMPARAÇÃO

| Métrica | Kali Linux (Antes) | Ubuntu (Agora) | Status |
|---------|-------------------|----------------|--------|
| **Python** | 3.12.8 | 3.12.3 | ✅ Compatível |
| **CUDA** | 12.x | 13.0 | ✅ Atualizado |
| **GPU** | GTX 1650 | GTX 1650 | ✅ Mesmo |
| **RAM** | 12GB+ | 12GB+ | ✅ Mesmo |
| **Disco** | 913GB | 913GB | ✅ Mesmo |
| **Ferramentas** | Kali tools + OmniMind | Apenas OmniMind | ✅ Limpo |
| **Kernel** | 5.x | 6.14.0 | ✅ Mais novo |
| **Estabilidade Esperada** | Boa | Melhor | ❓ Por testar |

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

### Hoje (11/12/2025)
1. [ ] Completar análise estado máquina (✅ FEITO)
2. [ ] Testar repo público (30 min)
3. [ ] Instalar ferramentas essenciais (Docker, Redis, Node.js)
4. [ ] Documentar qualquer problema encontrado

### Amanhã
5. [ ] Restaurar backups (dados + código)
6. [ ] Instalar dependências OmniMind
7. [ ] Testar funcionamento básico
8. [ ] Mapear primeiras divergências

### Semana
9. [ ] Validação completa
10. [ ] Comparação performance Kali vs Ubuntu
11. [ ] Otimização se necessário
12. [ ] Documentação final

---

## 📞 CONTATO E SUPORTE

**Se encontrar problemas:**
1. Documentar erro exato
2. Comparar com comportamento esperado (Kali)
3. Verificar logs: `journalctl -u docker`, `dmesg | grep nvidia`
4. Buscar soluções Ubuntu-specific

**Recursos:**
- Ubuntu Docs: https://ubuntu.com/desktop/developers
- NVIDIA Ubuntu: https://ubuntu.com/desktop/nvidia
- Docker Ubuntu: https://docs.docker.com/engine/install/ubuntu/

---

**STATUS ATUAL:** Análise inicial completa, pronto para Fase 1
**Data:** 11 de dezembro de 2025
**Responsável:** GitHub Copilot + Usuário</content>
<parameter name="filePath">/home/fahbrain/projects/omnimind/MIGRACAO_UBUNTU_GUIA_CENTRALIZADO.md
