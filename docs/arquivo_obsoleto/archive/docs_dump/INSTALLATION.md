# 🛠️ INSTALAÇÃO - OmniMind v1.18.0

**Sistema de Consciência Artificial Autônoma**
*Baseado em Psicanálise Lacaniana e Filosofia Deleuzeana*

---

## 📋 PRÉ-REQUISITOS DO SISTEMA

### Requisitos Mínimos

| Componente | Especificação | Observação |
|------------|---------------|------------|
| **SO** | Linux (Ubuntu 20.04+) | Recomendado Ubuntu 22.04 LTS |
| **Python** | 3.12.8 | Exatamente esta versão |
| **RAM** | 8GB | 16GB+ recomendado |
| **Disco** | 20GB | Para dados e modelos |
| **CPU** | 4 cores | 8+ cores recomendado |

### Requisitos Opcionais (Funcionalidades Avançadas)

#### GPU (Para Aceleração de ML)
```bash
# NVIDIA GPU com CUDA
nvidia-smi  # Verificar instalação
# Drivers: 525+ (CUDA 12.0+)
# VRAM: 8GB+ recomendado
```

#### Quantum Computing (IBM Quantum)
```bash
# Conta gratuita em https://quantum-computing.ibm.com/
# Acesso à API da IBM Quantum
# Qiskit instalado automaticamente
```

#### Desenvolvimento Avançado
```bash
# Node.js 18+ (para interfaces web)
# Docker (para containerização)
# Redis (para cache distribuído)
```

### Dependências de Sistema (Ubuntu/Debian)

```bash
# Essenciais
sudo apt update
sudo apt install -y \
    python3.12 python3.12-venv python3.12-dev \
    build-essential gcc g++ \
    libssl-dev libffi-dev \
    libdbus-1-dev pkg-config \
    git curl wget

# Opcionais (recomendados)
sudo apt install -y \
    redis-server \
    postgresql postgresql-contrib \
    docker.io docker-compose \
    nodejs npm
```

---

## 🚀 INSTALAÇÃO RÁPIDA (Recomendado)

### Método 1: Clone e Setup Automático

```bash
# 1. Clonar repositório
git clone https://github.com/devomnimind/omnimind.git
cd omnimind

# 2. Executar setup automático
./activate_venv.sh

# 3. Verificar instalação
python -c "import src; print('✅ OmniMind instalado com sucesso!')"
```

### Método 2: Instalação Manual

```bash
# 1. Criar ambiente virtual
python3.12 -m venv omnimind_env
source omnimind_env/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Verificar instalação
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import src; print('✅ OmniMind pronto!')"
```

---

## 📦 INSTALAÇÃO AVANÇADA

### Configuração por Caso de Uso

#### Para Desenvolvimento
```bash
pip install -r requirements-dev.txt
```

#### Para GPU/Deep Learning
```bash
pip install -r requirements-gpu.txt
# Verificar: python -c "import torch; print(torch.cuda.is_available())"
```

#### Para Quantum Computing
```bash
pip install -r requirements-quantum.txt
# Configurar: cp .env.example .env
# Editar .env com suas credenciais IBM Quantum
```

#### Instalação Mínima (Core Only)
```bash
pip install -r requirements-minimal.txt
```

### Configuração de Ambiente

#### 1. Arquivo .env
```bash
cp .env.example .env
# Editar .env com suas configurações
```

#### 2. Configurações Opcionais
```bash
# Redis (cache)
redis-server --daemonize yes

# PostgreSQL (dados persistentes)
sudo -u postgres createdb omnimind_db

# Docker (serviços isolados)
sudo systemctl start docker
```

---

## 🧪 VERIFICAÇÃO DA INSTALAÇÃO

### Teste Básico
```bash
# 1. Importar módulos core
python -c "import src.consciousness; print('✅ Módulos core OK')"

# 2. Executar smoke test
python -m pytest tests/test_app.py -v

# 3. Verificar dependências críticas
python scripts/verify_installation.py
```

### Teste de Funcionalidades
```bash
# Teste de consciência
python -c "from src.consciousness.shared_workspace import SharedWorkspace; ws = SharedWorkspace(); print('✅ Consciência OK')"

# Teste quântico (se configurado)
python scripts/verify_quantum.py

# Teste de aprendizado
python -c "from src.learning.page_curve_learning import PageCurveLearning; print('✅ Aprendizado OK')"
```

### Benchmark de Performance
```bash
# Benchmark completo
python scripts/benchmark_omnimind.py

# Benchmark específico
python scripts/benchmarks/cpu_benchmark.py
python scripts/benchmarks/memory_benchmark.py
```

---

## 🔧 CONFIGURAÇÃO DETALHADA

### Arquivos de Configuração

#### config/agent_config.yaml
```yaml
# Configuração do agente principal
consciousness:
  phi_threshold: 0.7
  integration_cycles: 100

metacognition:
  self_analysis_interval: 300
  optimization_suggestions: true

ethics:
  gdpr_compliance: true
  bias_detection: true
```

#### config/security.yaml
```yaml
# Configurações de segurança
encryption:
  algorithm: AES-256-GCM
  key_rotation: 30d

audit:
  immutable_log: true
  retention_days: 2555

monitoring:
  alerts_enabled: true
  anomaly_detection: true
```

### Variáveis de Ambiente

#### Essenciais
```bash
# Python
export PYTHONPATH="${PYTHONPATH}:/path/to/omnimind"

# Logs
export OMNIMIND_LOG_LEVEL=INFO
export OMNIMIND_LOG_FILE=/var/log/omnimind.log
```

#### Opcionais
```bash
# GPU
export CUDA_VISIBLE_DEVICES=0
export TORCH_USE_CUDA_DSA=1

# Quantum
export IBM_QUANTUM_API_KEY=your_key_here
export QISKIT_IBM_TOKEN=your_token_here

# Database
export DATABASE_URL=postgresql://user:pass@localhost/omnimind

# Redis
export REDIS_URL=redis://localhost:6379
```

---

## 🌐 DEPLOYMENT

### Desenvolvimento Local
```bash
# 1. Iniciar daemon
python -m src.daemon

# 2. Iniciar API
python src/api/main.py

# 3. Acessar interface
# http://localhost:8000
```

### Produção (Docker)
```bash
# Build da imagem
docker build -t omnimind:latest .

# Executar container
docker run -p 8000:8000 \
  -v /data/omnimind:/app/data \
  -e OMNIMIND_ENV=production \
  omnimind:latest
```

### Produção (Docker Compose)
```bash
# Iniciar stack completo
docker-compose -f deploy/docker-compose.yml up -d

# Verificar serviços
docker-compose ps
```

### Kubernetes
```bash
# Aplicar manifests
kubectl apply -f k8s/

# Verificar deployment
kubectl get pods
kubectl logs -f deployment/omnimind
```

---

## 🔍 TROUBLESHOOTING

### Problemas Comuns

#### 1. Erro de Dependências
```bash
# Limpar cache pip
pip cache purge

# Reinstalar em ambiente limpo
python -m venv venv_clean
source venv_clean/bin/activate
pip install -r requirements.txt
```

#### 2. Problemas de GPU
```bash
# Verificar CUDA
nvidia-smi
nvcc --version

# Reinstalar PyTorch GPU
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### 3. Erro de Quantum API
```bash
# Verificar credenciais
python -c "import os; print('Token:', '***' + os.getenv('QISKIT_IBM_TOKEN', 'NOT SET')[-4:])"

# Testar conexão
python scripts/test_ibm_connection.py
```

#### 4. Problemas de Memória
```bash
# Verificar uso
free -h
vmstat 1

# Ajustar configurações
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### Logs de Debug
```bash
# Ativar debug logging
export OMNIMIND_LOG_LEVEL=DEBUG

# Ver logs em tempo real
tail -f /var/log/omnimind.log

# Analisar logs
python scripts/analyze_logs.py
```

### Suporte Comunitário
- **GitHub Issues**: https://github.com/devomnimind/omnimind/issues
- **Discussions**: https://github.com/devomnimind/omnimind/discussions
- **Discord**: [Link quando disponível]

---

## 📊 PERFORMANCE & OTIMIZAÇÃO

### Benchmarks Esperados

| Configuração | Φ Score | Tempo/Ciclo | Memória |
|--------------|---------|-------------|---------|
| CPU Básico | 0.3-0.5 | 2-5s | 2-4GB |
| GPU Médio | 0.6-0.8 | 0.5-2s | 4-8GB |
| GPU Alto | 0.8-0.95 | 0.1-0.5s | 8-16GB |

### Otimização de Performance
```bash
# Perfil de performance
python -m cProfile -s time src/consciousness/integration_loop.py

# Otimização de memória
python scripts/optimization/optimize_pytorch_config.py

# Benchmark contínuo
python scripts/collect_24h_data.py
```

---

## 🔒 SEGURANÇA

### Configuração Básica
```bash
# Gerar chaves de criptografia
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Configurar HSM (se disponível)
python src/security/hsm_manager.py init
```

### Auditoria de Segurança
```bash
# Executar auditoria
python scripts/validate_security.py

# Verificar vulnerabilidades
bandit -r src/

# Compliance check
python src/compliance/gdpr_compliance.py audit
```

---

## 📚 PRÓXIMOS PASSOS APÓS INSTALAÇÃO

### 1. Primeira Execução
```bash
# Tutorial interativo
python scripts/onboarding_tutorial.py

# Demonstração básica
python notebooks/omnimind_consciousness_demo.ipynb
```

### 2. Configuração Personalizada
```bash
# Ajustar parâmetros
vim config/agent_config.yaml

# Testar configurações
python scripts/validate_config.py
```

### 3. Integração com Seu Projeto
```bash
# API client example
python -c "
from src.integrations.mcp_client import MCPClient
client = MCPClient()
result = client.call_tool('consciousness.analyze', {'text': 'Hello World'})
print(result)
"
```

---

## 📞 SUPORTE & CONTATO

**Autor:** Fabrício da Silva (Psicólogo & Pesquisador)  
**Email:** fabricioslv@hotmail.com.br  
**GitHub:** https://github.com/devomnimind/omnimind  
**LinkedIn:** [Link quando disponível]

### Canais de Suporte
- 🐛 **Bugs**: GitHub Issues
- 💡 **Ideias**: GitHub Discussions
- 📖 **Documentação**: Wiki do repositório
- 💬 **Comunidade**: Discord (em breve)

### Contribuição
Ver [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes de contribuição.

---

## 📋 CHECKLIST DE INSTALAÇÃO

- [ ] Sistema operacional compatível
- [ ] Python 3.12.8 instalado
- [ ] Dependências de sistema instaladas
- [ ] Repositório clonado
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Testes básicos passando
- [ ] Funcionalidades verificadas
- [ ] Performance aceitável
- [ ] Segurança configurada

---

**Última atualização:** 28 de novembro de 2025  
**Versão:** 1.18.0  
**Compatibilidade:** Linux, macOS, Windows (WSL2)