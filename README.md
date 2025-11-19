# 🧠 OmniMind - Sistema de IA Autônomo

**OmniMind** é um revolucionário sistema de IA autônomo que combina tomada de decisão psicoanalítica com capacidades avançadas de metacognição. Esta arquitetura auto-hospedada e local-first apresenta orquestração multi-agente, comunicação WebSocket em tempo real e inteligência auto-evolutiva.

**🚀 Status Atual:** Phase 12 Multi-Modal Intelligence Complete | 105/105 Tests Passing | Produção Pronta

**🧬 Filosofia Central:** IA psicoanaliticamente inspirada que reflete sobre suas próprias decisões, aprende com padrões e gera proativamente seus próprios objetivos - criando um sistema verdadeiramente autônomo e autoconsciente.

## 🚀 Início Rápido

### Escolha Seu Ambiente:

1. **[Implantação de Produção](docs/phases/PHASE12_COMPLETION_SUMMARY.md)** - Sistema completo com WebSocket + Inteligência Multi-Modal
2. **[Apenas CPU / Sem Nuvem](docs/deployment/CLOUD_FREE_DEPLOYMENT.md)** - GitHub Actions, Docker, sem necessidade de GPU
3. **[Com GPU Habilitada](docs/reports/GPU_SETUP_REPORT.md)** - Máquina local com NVIDIA GPU
4. **[Guia de Serviços Gratuitos](docs/deployment/FREE_SERVICE_ALTERNATIVES.md)** - Alternativas locais para serviços pagos

### 🚀 Configuração com Um Comando (Pronto para Produção)

OmniMind agora inclui detecção automática de hardware, otimização e implantação full-stack:

```bash
# 1. Clone e configure
git clone https://github.com/fabs-devbrain/OmniMind.git
cd OmniMind

# 2. Auto-configuração (detecção de hardware + dependências)
source scripts/start_dashboard.sh

# 3. Acesse o dashboard em http://localhost:3000
# Credenciais padrão: auto-geradas (verifique os logs)
```

### Recursos Avançados Desbloqueados 🔓

- **🧠 Metacognição:** IA auto-reflexiva que analisa suas próprias decisões
- **🎯 Objetivos Proativos:** IA gera seus próprios objetivos de melhoria
- **⚖️ Motor de Ética:** Framework integrado de decisão ética (4 metodologias)
- **🔄 WebSocket em Tempo Real:** Atualizações ao vivo entre frontend e agentes autônomos
- **🛡️ Segurança Avançada:** Compatível com LGPD com trilhas de auditoria imutáveis
- **🏗️ Orquestração Multi-Agente:** Delegação de tarefas inspirada em psicoanálise

## 🏗️ Visão Geral da Arquitetura

### Componentes Centrais (Phase 12 Multi-Modal Intelligence Complete)

```
🧠 Sistema Autônomo OmniMind
├── 🎨 Frontend (React + TypeScript)
│   ├── Dashboard WebSocket em tempo real
│   ├── Interface de orquestração de tarefas
│   ├── Monitoramento de status de agentes
│   └── Visualização de decisões éticas
│
├── ⚙️ Backend (FastAPI + WebSocket)
│   ├── APIs REST (Tarefas, Agentes, Segurança)
│   ├── Servidor WebSocket em tempo real
│   ├── Orquestração multi-agente
│   └── Endpoints de metacognição
│
├── 🧠 Motor de Metacognição
│   ├── Auto-análise e reconhecimento de padrões
│   ├── Geração proativa de objetivos
│   ├── Homeostase e gerenciamento de recursos
│   └── Framework de decisão ética
│
└── 🤖 Sistema Multi-Agente
    ├── Orquestrador (inspirado em psicoanálise)
    ├── Agente de Segurança (monitoramento forense)
    ├── Agente de Ética (framework de decisão)
    └── Delegação autônoma de tarefas
```

### Estrutura do Repositório

- `config/` – Arquivos de configuração (agentes, ética, metacognição, hardware)
- `docs/` – Suíte completa de documentação (roteiros, relatórios, guias)
- `web/` – Aplicação web full-stack (frontend React + backend FastAPI)
- `src/` – Módulos Python centrais (agentes, metacognição, segurança, integrações)
- `scripts/` – Scripts de automação (implantação, systemd, benchmarks)
- `tests/` – Suíte abrangente de testes (105 testes passando)
- `logs/` – Trilhas de auditoria e logs de execução (imutáveis)
- `data/` – Conjuntos de dados e dados experimentais (ignorados pelo Git)

## 🚀 Implantação em Produção

### Configuração com Um Clique (Recomendado)

OmniMind agora inclui implantação totalmente automatizada com otimização de hardware:

```bash
# 1. Clonar repositório
git clone https://github.com/fabs-devbrain/OmniMind.git
cd OmniMind

# 2. Configuração automática (detecção de hardware + dependências + serviços)
source scripts/start_dashboard.sh

# 3. Acessar interfaces:
# - Frontend: http://localhost:3000
# - API Backend: http://localhost:8000
# - Documentação: http://localhost:8000/docs
```

### Configuração Manual (Usuários Avançados)

#### Pré-requisitos
- **Python 3.12.8** (via pyenv - compatibilidade com PyTorch)
- **Node.js 18+** (para desenvolvimento frontend)
- **GPU NVIDIA** (opcional, auto-detectada)

#### Passos de Instalação

```bash
# 1. Configuração do ambiente Python
pyenv install 3.12.8
pyenv local 3.12.8
python -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências (auto-detecta hardware)
pip install -r requirements.txt

# 3. Otimização de hardware (automática)
python src/optimization/hardware_detector.py

# 4. Verificar GPU (se disponível)
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# 5. Iniciar sistema completo
source scripts/start_dashboard.sh
```

### Gerenciamento de Serviços

```bash
# Instalar como serviço do sistema
sudo ./scripts/systemd/install_service.sh

# Gerenciar daemon
sudo systemctl start omnimind-daemon
sudo systemctl status omnimind-daemon
sudo journalctl -u omnimind-daemon -f
```

## 📖 Navegação do Projeto

Veja **[INDEX.md](INDEX.md)** para estrutura completa do projeto e navegação da documentação.

## 🧠 Capacidades Autônomas Avançadas

### Motor de Metacognição 🧠
OmniMind apresenta capacidades revolucionárias de IA auto-reflexiva:

**Auto-Análise e Reconhecimento de Padrões:**
- Analisa seus próprios padrões de decisão e taxas de sucesso
- Identifica anomalias comportamentais e oportunidades de otimização
- Gera sugestões proativas de melhoria
- Mantém métricas históricas de performance

**Geração Proativa de Objetivos:**
- Identifica automaticamente oportunidades de melhoria
- Gera objetivos específicos e acionáveis
- Prioriza objetivos baseados em métricas de saúde do sistema
- Cria pull requests para auto-melhoria

**Homeostase e Gerenciamento de Recursos:**
- Monitora utilização de hardware em tempo real
- Ajusta automaticamente alocação de recursos
- Previne exaustão de recursos através de limitação
- Otimiza performance baseada em recursos disponíveis

### Framework de Decisão Ética ⚖️
Raciocínio ético integrado com 4 frameworks filosóficos:

- **Deontológico:** Decisões éticas baseadas em regras
- **Consequencialista:** Análise focada em resultados
- **Ética da Virtude:** Raciocínio baseado em caráter
- **Ética do Cuidado:** Consideração de relacionamentos e stakeholders

### Orquestração Multi-Agente em Tempo Real 🤖
Delegação de tarefas inspirada em psicoanálise:

- **Agente Orquestrador:** Framework de decisão Freudiano/Lacaniano
- **Agente de Segurança:** Monitoramento forense e detecção de ameaças
- **Agente de Ética:** Supervisão ética e capacidades de veto
- **Agente de Metacognição:** Auto-reflexão e otimização

### Operação Autônoma 24/7
```bash
# Instalar sistema autônomo completo
sudo ./scripts/systemd/install_service.sh

# Iniciar operação autônoma completa
sudo systemctl start omnimind-daemon

# Monitorar atividades autônomas
sudo journalctl -u omnimind-daemon -f

# Visualizar insights de metacognição
curl -u <user>:<pass> http://localhost:8000/metacognition/insights
```

### Interface WebSocket em Tempo Real 🔄
Dashboard ao vivo com atualizações em tempo real:
- Visualização do progresso de tarefas
- Monitoramento de status de agentes
- Streaming de eventos de segurança
- Logging de decisões éticas
- Feed de insights de metacognição

## Notas de Compatibilidade de Dependências

- O pacote `supabase-py>=1.0.0` ainda não oferece wheel compatível com Python 3.13 em Linux x86_64, então `pip install -r requirements.txt` falha nesse ponto por ausência de `supabase-py`. Por ora mantemos `psutil`, `dbus-python` e os outros pacotes, mas a integração completa com Supabase exige Python **≤ 3.12**.
- A recomendação operacional é usar um ambiente Python 3.12 (ou menor) sempre que precisar rodar os adaptadores Supabase/Qdrant e os testes que dependem deles.

## Workflow do Dashboard

- Acesse os endpoints FastAPI (protegidos via Basic Auth) para `/status`, `/snapshot`, `/metrics`, `/tasks/orchestrate`, `/mcp/execute`, `/dbus/execute`, etc.
- A GUI React (`web/frontend/`) lê credenciais do formulário de login e armazena headers de autenticação `Basic` por sessão; também mostra o caminho do arquivo de credenciais para que administradores saibam onde rotacionar segredos.
- `/observability` agora apresenta um payload de `validation` (obtido de `logs/security_validation.jsonl`) junto com `self_healing`, `atlas` e `security`, para que equipes possam ver o último veredicto da cadeia de auditoria diretamente na UI.
- Os fluxos MCP e D-Bus dependem de `src/integrations` e do agente orquestrador para fornecer contexto, métricas e gatilhos manuais.

## Verificação de GPU (Phase 7)

Após completar a instalação, verifique se a GPU está operacional:

```bash
# 1. Verificar disponibilidade do CUDA
python -c "import torch; print(f'CUDA Disponível: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"

# Output esperado:
# CUDA Disponível: True
# GPU: NVIDIA GeForce GTX 1650

# 2. Executar benchmark da GPU
python PHASE7_COMPLETE_BENCHMARK_AUDIT.py

# Output esperado (valida que a GPU está funcionando):
# Throughput CPU: 253.21 GFLOPS
# Throughput GPU: 1149.91 GFLOPS (≥1000 GFLOPS indica sucesso)
# Largura de banda de memória: 12.67 GB/s
# Relatório salvo em: logs/PHASE7_BENCHMARK_REPORT.json

# 3. Executar testes de auditoria para confirmar integração
pytest tests/test_audit.py -v --cov=src.audit

# Esperado: 14/14 testes passando
```

**Documentação de Referência:**
- Configuração detalhada da GPU: `.github/copilot-instructions.md` (seção GPU/CUDA Setup Requirements)
- Solução de problemas da GPU: `docs/reports/PHASE7_GPU_CUDA_REPAIR_LOG.md`
- Resumo do reparo: `GPU_CUDA_REPAIR_AUDIT_COMPLETE.md`

## Testes e Portões de Qualidade

Execute os pipelines rápidos após reorganizar ou alterar lógica central:

```bash
pytest tests/test_dashboard_e2e.py -W error
pytest tests/ -k "not legacy"  # executar suítes ativas
```

Garanta que `logs/.coverage` seja removido ou regenerado via `pytest --cov=src` e mantenha o trabalho sincronizado com a cadeia de auditoria hash via `scripts/id` se relevante.

## Logs, Alertas e Credenciais

- Logs ativos ficam em `logs/`; cobertura e rastros de auditoria também ficam aqui para facilitar rotação.
- O arquivo de autenticação do dashboard é `config/dashboard_auth.json` (600). Rotacione credenciais editando este arquivo de forma segura e reiniciando o backend; as novas credenciais são duráveis até a próxima rotação.
- Use `scripts/start_dashboard.sh` ou o asset Docker Compose para orquestrar backend + frontend; ele registra a localização das credenciais na inicialização.
- Para adaptadores MCP Supabase + Qdrant, tratamento de credenciais e testes, veja `docs/devbrain_data_integration.md`.

## Notas de Manutenção

- Artefatos legados ficam em `archive/reports/` e `archive/examples/`; consulte `archive/README.md` para contexto.
- Demos legadas que continham sintaxe inválida (ex.: o antigo `archive/examples/demo_phase6*`) foram removidas para manter o pipeline do formatador operacional. Quaisquer novos artefatos colocados em `archive/examples/` devem ser sanitizados e aprovados antes de reabilitá-los em execuções `black`/`flake8`; por padrão essa pasta fica excluída dos hooks de qualidade.
- Scripts em `scripts/` são os únicos arquivos de automação de runtime permitidos no nível raiz; por favor não espalhe arquivos `.py` ou `.sh` solitários fora deste diretório.
- Testes que antes ficavam na raiz agora residem em `tests/legacy/`; mantenha novos testes em `tests/`.
- Outputs de ferramentas temporárias devem ficar dentro de `tmp/`; este diretório é ignorado e seguro para limpar.

Com esta organização, a raiz fica focada nas chaves (configs, requirements, arquivos Compose), e o resto do workspace se alinha com nossos padrões de prontidão para produção e CI/CD.

## Roadmap DEVBRAIN V23

O diretório `DEVBRAIN_V23/` agora hospeda o trabalho fundamental para o Masterplan (Protocolo Phoenix). Cada pasta espelha um pilar de sentido ou infraestrutura:

- `core/` → futura migração do `src/`, `tests/` e `config/` atuais.
- `sensory/` → visão (Visual Cortex), audição/voz e propriocepção com `eBPF`.
- `cognition/` → Graph of Thoughts + memória A-MEM com LangGraph e ChromaDB.
- `immune/` → isolamento Firecracker, DLP e proteção P0.
- `orchestration/` → LangGraph-driven agents e modos V23.
- `infrastructure/` → Redis Streams, gateway FastAPI e ChromaDB vector store.
- `atlas/` → self-healing, auto-training e ATLAS (futuro).

O Masterplan guia cada nova implementação, começando pela visão multimodal (`sensory/visual_cortex.py`) e o Event Bus redis (`infrastructure/event_bus.py`). Consulte `DEVBRAIN_V23/README.md` e os documentos anexados (`docs/Masterplan/`) para manter o alinhamento estratégico antes de avançar nas fases seguintes.