# 🔧 Guia de Troubleshooting - OmniMind

**Última Atualização**: 5 de Dezembro de 2025
**Versão**: Phase 24+ (Lacanian Memory + Autopoietic Evolution)

---

## Visão Geral

Este guia fornece soluções de troubleshooting para problemas comuns e ferramentas de diagnóstico automatizadas para identificar e resolver problemas rapidamente.

---

## 🚀 Ferramenta de Diagnóstico Rápido

Execute o script de diagnóstico automatizado para verificar a saúde do sistema:

```bash
python scripts/canonical/diagnose/diagnose.py
```

Isso verificará:
- ✓ Compatibilidade da versão Python (3.12.8 obrigatório)
- ✓ Dependências necessárias instaladas
- ✓ Arquivos de configuração presentes
- ✓ Disponibilidade de serviços (Qdrant, Ollama)
- ✓ GPU/CUDA disponível (se aplicável)
- ✓ Conectividade de rede
- ✓ Permissões de arquivo
- ✓ Integridade de logs

**Opções disponíveis**:
```bash
# Diagnóstico completo
python scripts/canonical/diagnose/diagnose.py --full

# Diagnóstico rápido
python scripts/canonical/diagnose/diagnose.py --quick

# Verificações específicas
python scripts/canonical/diagnose/diagnose.py --check-db
python scripts/canonical/diagnose/diagnose.py --check-gpu
python scripts/canonical/diagnose/diagnose.py --check-ports
python scripts/canonical/diagnose/diagnose.py --check-memory
python scripts/canonical/diagnose/diagnose.py --check-performance
```

---

## Problemas Comuns

### 1. Servidor Não Inicia

#### Sintoma
```
Error: Address already in use
```

#### Diagnóstico
```bash
# Verificar se porta 8000 está em uso
lsof -i :8000

# Ou usar ferramenta de diagnóstico
python scripts/canonical/diagnose/diagnose.py --check-ports
```

#### Solução
```bash
# Encontrar e matar processo usando porta 8000
kill $(lsof -t -i:8000)

# Ou usar porta diferente
OMNIMIND_PORT=8001 uvicorn web.backend.main:app --reload
```

---

### 2. Falhas de Autenticação

#### Sintoma
```
401 Unauthorized
```

#### Diagnóstico
```bash
# Verificar arquivo de credenciais
cat config/dashboard_auth.json

# Verificar variáveis de ambiente
echo $OMNIMIND_DASHBOARD_USER
echo $OMNIMIND_DASHBOARD_PASS
```

#### Solução

**Opção 1: Usar credenciais existentes**
```bash
# Verificar arquivo de credenciais
cat config/dashboard_auth.json
```

**Opção 2: Definir variáveis de ambiente**
```bash
export OMNIMIND_DASHBOARD_USER="seu_usuario"
export OMNIMIND_DASHBOARD_PASS="sua_senha"
```

**Opção 3: Regenerar credenciais**
```bash
rm config/dashboard_auth.json
# Reiniciar servidor para auto-gerar novas credenciais
```

**Nota**: As credenciais são geradas automaticamente na primeira execução e salvas em `config/dashboard_auth.json` com permissão `600`.

---

### 3. Erros de Importação de Módulos

#### Sintoma
```
ModuleNotFoundError: No module named 'xxx'
```

#### Diagnóstico
```bash
# Verificar pacotes instalados
pip list

# Executar diagnóstico
python scripts/canonical/diagnose/diagnose.py --check-dependencies
```

#### Solução
```bash
# Instalar dependências faltantes
pip install -r requirements.txt

# Para suporte GPU
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# Para CPU-only
pip install -r requirements-cpu.txt
```

---

### 4. Erros de Conexão com Banco de Dados

#### Sintoma
```
Connection refused: Qdrant
```

#### Diagnóstico
```bash
# Verificar se Qdrant está rodando
docker ps | grep qdrant

# Ou
curl http://localhost:6333/health
```

#### Solução

**Iniciar Qdrant com Docker:**
```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/data/qdrant:/qdrant/storage \
  qdrant/qdrant
```

**Ou iniciar com docker-compose:**
```bash
docker-compose up -d qdrant
```

**Verificar variável de ambiente:**
```bash
# Verificar URL do Qdrant
echo $OMNIMIND_QDRANT_URL

# Ou verificar em .env
grep QDRANT_URL .env
```

---

### 5. GPU/CUDA Não Detectado

#### Sintoma
```
CUDA not available
GPU not detected
```

#### Diagnóstico
```bash
# Verificar GPU
python scripts/canonical/diagnose/diagnose.py --check-gpu

# Verificar CUDA
nvidia-smi

# Verificar PyTorch
python -c "import torch; print(torch.cuda.is_available())"
```

#### Solução

**Configurar variáveis de ambiente CUDA:**
```bash
# Definir variáveis CUDA (via shell/script, não em código Python)
export CUDA_HOME=/usr
export CUDA_PATH=/usr
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
```

**Verificar instalação PyTorch:**
```bash
# PyTorch atual: 2.5.1+cu124
python -c "import torch; print(torch.__version__)"
```

**Forçar GPU em testes:**
```bash
# Scripts de teste já forçam GPU automaticamente
./scripts/run_tests_fast.sh  # GPU forçada com fallback
```

---

### 6. Problemas com WebSocket

#### Sintoma
```
WebSocket connection failed
Connection timeout
```

#### Diagnóstico
```bash
# Verificar servidor está rodando
curl http://localhost:8000/api/v1/health/

# Verificar WebSocket endpoint
curl http://localhost:8000/ws
```

#### Solução

1. **Verificar servidor está rodando:**
   ```bash
   curl http://localhost:8000/api/v1/health/
   ```

2. **Verificar WebSocket manager iniciou:**
   ```bash
   # Verificar logs
   tail -f logs/backend.log | grep "WebSocket"
   ```

3. **Verificar firewall:**
   ```bash
   # Permitir conexões WebSocket
   sudo ufw allow 8000/tcp
   ```

4. **Testar conexão WebSocket:**
   ```javascript
   // JavaScript
   const ws = new WebSocket('ws://localhost:8000/ws');
   ws.onopen = () => console.log('Conectado');
   ws.onmessage = (event) => console.log('Recebido:', event.data);
   ```

---

### 7. Uso Alto de Memória

#### Sintoma
```
Out of memory errors
Sistema fica lento
```

#### Diagnóstico
```bash
# Verificar uso de memória
python scripts/canonical/diagnose/diagnose.py --check-memory

# Monitorar em tempo real
htop

# Verificar processos OmniMind
ps aux | grep omnimind
```

#### Solução

**Reduzir tamanhos de batch:**
```yaml
# config/agent_config.yaml
orchestrator:
  max_concurrent_tasks: 5  # Reduzir de 10
  max_iterations: 3  # Reduzir de 5
```

**Limpar cache:**
```bash
# Limpar cache Python
find . -type d -name __pycache__ -exec rm -rf {} +

# Limpar cache de modelos
rm -rf ~/.cache/huggingface
```

**Reiniciar com memória limitada:**
```bash
# Limitar memória para o processo
systemd-run --scope -p MemoryLimit=8G uvicorn web.backend.main:app
```

---

### 8. Performance Lenta

#### Sintoma
```
Respostas de API levando > 5 segundos
Tarefas dando timeout
```

#### Diagnóstico
```bash
# Executar benchmark de performance
python benchmarks/PHASE7_COMPLETE_BENCHMARK_AUDIT.py

# Verificar recursos do sistema
python scripts/canonical/diagnose/diagnose.py --check-performance
```

#### Solução

Veja [Guia de Performance Tuning](./PERFORMANCE_TUNING.md) para passos detalhados de otimização.

**Correções rápidas:**
```bash
# 1. Reduzir verbosidade de logs
export LOG_LEVEL=WARNING

# 2. Desabilitar modo debug
export OMNIMIND_DEBUG=false

# 3. Usar GPU se disponível
export OMNIMIND_USE_GPU=true

# 4. Aumentar número de workers
uvicorn web.backend.main:app --workers 4
```

---

### 9. Erros de Integridade da Cadeia de Auditoria

#### Sintoma
```
Audit chain verification failed
Hash mismatch detected
```

#### Diagnóstico
```bash
# Verificar cadeia de auditoria
python -c "from src.audit.immutable_audit import verify_chain_integrity; print(verify_chain_integrity())"

# Verificar logs
cat logs/audit_chain.log
```

#### Solução

**Reconstruir cadeia de auditoria:**
```bash
# Fazer backup da cadeia existente
cp logs/audit_chain.log logs/audit_chain.log.backup

# Verificar e corrigir
python scripts/canonical/diagnose/diagnose_audit.py
```

**Se cadeia estiver corrompida além de reparo:**
```bash
# Iniciar do zero (apenas se aceitável perder histórico de auditoria)
rm logs/audit_chain.log logs/hash_chain.json
# Reiniciar servidor para criar nova cadeia
```

---

### 10. Falhas de Testes

#### Sintoma
```
pytest failures
Import errors em testes
```

#### Diagnóstico
```bash
# Executar teste específico com saída verbosa
pytest tests/test_api_documentation.py -vv

# Verificar dependências de teste
python scripts/canonical/diagnose/diagnose.py --check-test-deps
```

#### Solução

**Instalar dependências de teste:**
```bash
pip install pytest pytest-cov pytest-asyncio pytest-timeout
```

**Executar testes em isolamento:**
```bash
# Limpar cache
pytest --cache-clear

# Executar com imports frescos
pytest --forked tests/
```

**Scripts de teste oficiais:**
```bash
# Suite rápida diária (sem slow/chaos)
./scripts/run_tests_fast.sh

# Suite completa semanal (inclui slow/chaos)
./scripts/run_tests_with_defense.sh
```

---

## Ferramentas de Diagnóstico Automatizadas

### Verificação de Saúde do Sistema

```bash
# Diagnóstico completo do sistema
python scripts/canonical/diagnose/diagnose.py --full

# Verificação rápida de saúde
python scripts/canonical/diagnose/diagnose.py --quick
```

### Diagnósticos Específicos por Componente

```bash
# Conectividade de banco de dados
python scripts/canonical/diagnose/diagnose.py --check-db

# Status GPU/CUDA
python scripts/canonical/diagnose/diagnose.py --check-gpu

# Portas em uso
python scripts/canonical/diagnose/diagnose.py --check-ports

# Uso de memória
python scripts/canonical/diagnose/diagnose.py --check-memory

# Performance
python scripts/canonical/diagnose/diagnose.py --check-performance

# Dependências
python scripts/canonical/diagnose/diagnose.py --check-dependencies
```

### Health Check via API

```bash
# Health check geral (sem autenticação)
curl http://localhost:8000/api/v1/health/

# Health check específico
curl http://localhost:8000/api/v1/health/database
curl http://localhost:8000/api/v1/health/gpu
curl http://localhost:8000/api/v1/health/redis

# Health check com tendência
curl http://localhost:8000/api/v1/health/database/trend?window_size=10
```

---

## Endpoints de Troubleshooting

### Health Check Endpoints

- **`GET /api/v1/health/`** - Status geral de saúde do sistema
- **`GET /api/v1/health/{check_name}`** - Status de componente específico
  - `check_name`: `database`, `redis`, `gpu`, `filesystem`, `memory`, `cpu`
- **`GET /api/v1/health/{check_name}/trend`** - Tendência de saúde
- **`GET /api/v1/health/summary`** - Resumo do sistema de health check
- **`POST /api/v1/health/start-monitoring`** - Iniciar monitoramento contínuo
- **`POST /api/v1/health/stop-monitoring`** - Parar monitoramento contínuo

### Monitoring Endpoints

- **`GET /api/v1/monitoring/health`** - Status do monitoramento
- **`GET /api/v1/monitoring/alerts/active`** - Alertas ativos
- **`POST /api/v1/monitoring/alerts/acknowledge/{alert_id}`** - Reconhecer alerta
- **`GET /api/v1/monitoring/snapshots/recent`** - Snapshots recentes
- **`GET /api/v1/monitoring/status`** - Status do sistema de monitoramento

---

## Logs e Debugging

### Localização de Logs

```bash
# Logs do backend
tail -f logs/backend.log

# Logs de auditoria
tail -f logs/audit_chain.log

# Logs de testes
tail -f data/test_reports/junit_*.xml

# Logs do sistema
journalctl -u omnimind -f
```

### Níveis de Log

```bash
# Configurar nível de log
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# Ou via variável de ambiente
export OMNIMIND_LOG_LEVEL=INFO
```

---

## Recursos Adicionais

- [Guia de Performance Tuning](./PERFORMANCE_TUNING.md)
- [Interactive API Playground](./INTERACTIVE_API_PLAYGROUND.md)
- [Quick Start Guide](../canonical/QUICK_START.md)
- [Technical Checklist](../canonical/TECHNICAL_CHECKLIST.md)

---

**Autor**: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
