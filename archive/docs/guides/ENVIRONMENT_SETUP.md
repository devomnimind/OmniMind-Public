# 🔧 Guia de Configuração de Ambiente - OmniMind

**Última Atualização**: 5 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)

---

## 📋 Pré-requisitos do Sistema

### Hardware Mínimo Recomendado

- **CPU**: 4 cores (Intel i5/Ryzen 5 ou superior)
- **RAM**: 8GB (16GB recomendado)
- **GPU**: NVIDIA GTX 1650 ou superior (4GB VRAM) - **Opcional mas recomendado**
- **Armazenamento**: 50GB SSD disponível
- **SO**: Linux Ubuntu 20.04+ ou similar (Kali Linux 6.16.8+ validado)

### Software Obrigatório

- **Python**: 3.12.8 (obrigatório, outras versões podem causar problemas)
- **Ollama**: Instalado e rodando com modelo `phi:latest`
- **CUDA**: 12.4+ (se GPU disponível)
- **Git**: Para controle de versão
- **Docker & Docker Compose**: Opcional, para containerização

---

## 🚀 Instalação Passo a Passo

### 1. Clone do Repositório

```bash
cd /home/fahbrain/projects
git clone <repository-url> omnimind
cd omnimind
```

### 2. Criação do Ambiente Virtual

```bash
# Criar ambiente virtual com Python 3.12.8
python3.12 -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar Python
python --version  # Deve ser 3.12.8
```

### 3. Instalação de Dependências

```bash
# Instalar dependências principais
pip install -r requirements.txt

# Ou instalar por categoria (recomendado)
pip install -r requirements/requirements-core.txt
pip install -r requirements/requirements-dev.txt

# Se GPU disponível
pip install -r requirements/requirements-gpu.txt
```

### 4. Configuração do Ollama

```bash
# Verificar se Ollama está instalado
ollama --version

# Se não estiver, instalar (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Baixar modelo phi:latest (modelo padrão)
ollama pull phi:latest

# Verificar modelos disponíveis
ollama list
# Deve mostrar: phi:latest
```

### 5. Configuração de Variáveis de Ambiente

Criar arquivo `.env` na raiz do projeto:

```bash
# Modelo LLM
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi:latest

# GPU
CUDA_VISIBLE_DEVICES=0
OMNIMIND_GPU=true
OMNIMIND_FORCE_GPU=true

# Modo
OMNIMIND_MODE=development
OMNIMIND_DEV=true
OMNIMIND_DEBUG=true

# Qdrant (opcional)
OMNIMIND_QDRANT_URL=http://localhost:6333
OMNIMIND_QDRANT_API_KEY=

# Supabase (opcional)
OMNIMIND_SUPABASE_URL=
OMNIMIND_SUPABASE_ANON_KEY=

# Dashboard Auth (gerado automaticamente)
# Ver: config/dashboard_auth.json após primeira execução
```

### 6. Verificação de GPU (Opcional)

```bash
# Verificar CUDA
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'CUDA Device Count: {torch.cuda.device_count()}')"

# Verificar driver NVIDIA
nvidia-smi

# Output esperado:
# NVIDIA Driver Version: 550.163.01  CUDA Version: 12.4
```

### 7. Configuração do Qdrant (Opcional)

Para testes completos que requerem Qdrant:

```bash
# Via Docker
docker run -p 6333:6333 qdrant/qdrant

# Ou via docker-compose
cd deploy
docker-compose up -d qdrant
```

Verificar se está rodando:
```bash
curl http://localhost:6333/health
# Deve retornar: {"status":"ok"}
```

---

## 🔧 Configuração Avançada

### Configuração do Modelo LLM

**Arquivo**: `config/agent_config.yaml`

```yaml
model:
  name: "phi:latest"           # Modelo primário (Microsoft Phi)
  provider: "ollama"
  base_url: "http://localhost:11434"
  fallback_model: "qwen2:7b-instruct"  # Fallback se phi não disponível
```

**Verificar configuração**:
```bash
python -c "
import yaml
with open('config/agent_config.yaml') as f:
    config = yaml.safe_load(f)
    print(f\"Modelo: {config['model']['name']}\")
    print(f\"Provider: {config['model']['provider']}\")
"
```

### Configuração de Sudo (Para Scripts que Requerem)

**Script**: `scripts/configure_sudo_omnimind.sh`

```bash
# Executar UMA VEZ para configurar sudo sem senha
bash scripts/configure_sudo_omnimind.sh
```

**O que faz**:
- Cria arquivo `/etc/sudoers.d/omnimind-automation`
- Adiciona permissões NOPASSWD para comandos específicos
- Permite execução de scripts sem prompt de senha

---

## ✅ Verificação Final

### Checklist de Validação

```bash
# 1. Python correto
python --version  # Deve ser 3.12.8

# 2. Ambiente virtual ativado
which python  # Deve apontar para .venv/bin/python

# 3. Dependências instaladas
python -c "import torch; import numpy; print('✅ Dependências OK')"

# 4. Ollama rodando
curl http://localhost:11434/api/tags  # Deve retornar JSON

# 5. Modelo phi disponível
ollama list | grep phi  # Deve mostrar: phi:latest

# 6. GPU (se disponível)
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"

# 7. Qdrant (se necessário)
curl http://localhost:6333/health  # Deve retornar: {"status":"ok"}
```

### Teste Rápido

```bash
# Executar teste simples
python -c "
from src.boot import check_hardware
profile = check_hardware()
print(f'✅ Hardware Profile: {profile}')
"
```

---

## 🚨 Troubleshooting

### Python 3.12.8 não encontrado

```bash
# Instalar Python 3.12.8 via pyenv (recomendado)
pyenv install 3.12.8
pyenv local 3.12.8

# Ou via sistema
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
```

### Ollama não responde

```bash
# Verificar se Ollama está rodando
ps aux | grep ollama

# Se não estiver, iniciar
ollama serve

# Verificar logs
journalctl -u ollama -f  # Se instalado como serviço
```

### Modelo phi:latest não encontrado

```bash
# Baixar modelo
ollama pull phi:latest

# Verificar
ollama list
```

### Erros de GPU/CUDA

```bash
# Verificar variáveis de ambiente
echo $CUDA_VISIBLE_DEVICES
echo $CUDA_HOME

# Verificar PyTorch
python -c "import torch; print(torch.__version__)"
python -c "import torch; print(torch.cuda.is_available())"

# Se CUDA não detectado mas GPU presente
export CUDA_VISIBLE_DEVICES=0
export OMNIMIND_FORCE_GPU=true
```

### Qdrant não acessível

```bash
# Verificar se está rodando
docker ps | grep qdrant

# Se não estiver, iniciar
docker run -d -p 6333:6333 qdrant/qdrant

# Verificar health
curl http://localhost:6333/health
```

---

## 📚 Próximos Passos

Após configuração bem-sucedida:

1. **Leia o Quick Start**: `docs/canonical/QUICK_START.md`
2. **Execute testes**: `./scripts/run_tests_fast.sh`
3. **Inicie o sistema**: `./scripts/canonical/system/start_omnimind_system.sh`
4. **Consulte a documentação**: `docs/DOCUMENTATION_INDEX.md`

---

## 🔗 Referências

- **Quick Start**: `docs/canonical/QUICK_START.md`
- **Technical Checklist**: `docs/canonical/TECHNICAL_CHECKLIST.md`
- **Safe Commands**: `docs/canonical/SAFE_COMMANDS.md`
- **System Initialization**: `docs/canonical/omnimind_system_initialization.md`

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
