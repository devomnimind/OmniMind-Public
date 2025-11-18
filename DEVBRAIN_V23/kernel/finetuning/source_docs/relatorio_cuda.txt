# Relatório: Instalação de Drivers NVIDIA e CUDA Toolkit
**Data:** 17 de novembro de 2025  
**Status:** ✓ INSTALAÇÃO CONCLUÍDA - REBOOT NECESSÁRIO

---

## 1. Pacotes Instalados

### Drivers NVIDIA
- **nvidia-driver:** 550.163.01-3
- **nvidia-driver-bin:** 550.163.01-3  
- **nvidia-driver-libs:** 550.163.01-3
- **nvidia-kernel-dkms:** 550.163.01-3 (módulo kernel)
- **nvidia-kernel-support:** 550.163.01-3
- **firmware-nvidia-gsp:** 550.163.01-3

### CUDA Toolkit
- **nvidia-cuda-toolkit:** 12.4.131~12.4.1-4+b1
- **nvidia-cuda-dev:** 12.4.127~12.4.1-4+b1
- **nvidia-cuda-gdb:** 12.4.127~12.4.1-4+b1 (debugger)
- **libcuda1:** 550.163.01-3 (biblioteca principal)
- **libcudart12:** 12.4.127 (runtime)

### Bibliotecas CUDA
- **libcublas12:** 12.4.5.8 (álgebra linear)
- **libcublaslt12:** 12.4.5.8
- **libcufft11:** 11.2.1.3 (FFT)
- **libcurand10:** 11.1.1 (números aleatórios)
- **libcusparse12:** 12.3.1.170 (matrizes esparsas)
- **libcusolver11:** 11.6.1.9 (solucionador)
- **libnpp*:** 12.2.5.30 (processamento de imagem)
- **libcupti12:** 12.4.127 (profiling)

### Ferramentas de Desenvolvimento
- **nsight-compute:** 2024.1.1.4 (profiler GPU)
- **nsight-systems:** 2023.4.4.54 (análise de sistema)
- **nvidia-visual-profiler:** 12.4.127
- **nvidia-cuda-gdb:** 12.4.127

### Utilitários
- **nvidia-smi:** 550.163.01-3 ✓ (monitoramento GPU)
- **nvidia-settings:** 550.163.01-1 (configuração)
- **nvidia-persistenced:** 550.163.01-1

### Suporte OpenCL
- **nvidia-opencl-icd:** 550.163.01-3
- **nvidia-opencl-dev:** 12.4.127
- **ocl-icd-opencl-dev:** 2.3.4-1

### Compiladores
- **gcc-13:** 13.4.0-4
- **g++-13:** 13.4.0-4
- **cpp-13:** 13.4.0-4

---

## 2. Resumo da Instalação

**Total de pacotes instalados:** 138  
**Tamanho de download:** 2.770 MB  
**Espaço em disco usado:** 7.509 MB

**Tempo de instalação:** ~15-20 minutos  
**Repositório:** Kali Rolling (http://kali.download/kali)

---

## 3. Configuração do Hardware

### GPU Detectada
```
Modelo: NVIDIA GeForce GTX 1650 Mobile / Max-Q
ID PCI: 01:00.0
Arquitetura: Turing (TU117M)
CUDA Compute: 7.5
VRAM: 4GB GDDR6
```

### Especificações CUDA para GTX 1650
- **Arquitetura CUDA:** 61 (sm_61)
- **CUDA Cores:** 1024
- **Tensor Cores:** Não disponível (só RTX)
- **RT Cores:** Não disponível (só RTX)
- **Memory Bandwidth:** 128 GB/s
- **TDP:** 35-50W (Mobile/Max-Q)

---

## 4. Configurações Otimizadas para GTX 1650 (4GB VRAM)

### Parâmetros Recomendados (config/agent_config.yaml)

```yaml
gpu:
  device: "cuda:0"
  gpu_layers: 20          # 16-20 ideal para 4GB
  offload_ratio: 0.95     # Máximo GPU
  
model:
  quantization: "Q4_K_M"  # 4-5GB modelo
  context_window: 2048    # Conservador para VRAM
  batch_size: 1           # Produção low-latency
  
llama_cpp:
  n_gpu_layers: 20
  n_ctx: 2048
  n_batch: 512
  use_mmap: true          # Evita picos RAM
  use_mlock: false
  
cuda:
  compute_capability: "7.5"
  architecture: "sm_61"
  max_threads_per_block: 1024
```

### Variáveis de Ambiente CUDA

```bash
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
export CUDA_VISIBLE_DEVICES=0
```

---

## 5. Verificação Pós-Reboot

Após reiniciar, execute os seguintes comandos:

### 5.1 Verificar Driver NVIDIA
```bash
nvidia-smi
```
**Output esperado:**
```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.163.01             Driver Version: 550.163.01     CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                  TCC/WDDM  | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce GTX 1650...  Off  | 00000000:01:00.0  Off |                  N/A |
| N/A   XXC    P8              XXW /  N/A |      XXMiB /  4096MiB |      X%      Default |
+-----------------------------------------+------------------------+----------------------+
```

### 5.2 Verificar CUDA
```bash
nvcc --version
```
**Output esperado:**
```
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2024 NVIDIA Corporation
Built on ...
Cuda compilation tools, release 12.4, V12.4.127
```

### 5.3 Teste de CUDA
```bash
cd /usr/local/cuda/samples/1_Utilities/deviceQuery
sudo make
./deviceQuery
```

### 5.4 Verificar Bibliotecas
```bash
ldconfig -p | grep cuda | head -10
```

---

## 6. Compilação do llama.cpp com CUDA

Após reboot, compilar llama.cpp:

```bash
cd ~
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp

# Limpar build anterior (se existir)
rm -rf build

# Configurar com CUDA
cmake -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_CUDA=ON \
  -DLLAMA_BUILD_SERVER=ON \
  -DCMAKE_CUDA_ARCHITECTURES=61 \
  -DCMAKE_INSTALL_PREFIX=/usr/local/llama.cpp

# Compilar (10-20 minutos)
cmake --build build --config Release -j $(nproc)

# Instalar
sudo cmake --install build

# Verificar
/usr/local/llama.cpp/bin/llama-cli --version
```

---

## 7. Instalação do Ollama

```bash
# Download e instalação
curl https://ollama.ai/install.sh | sh

# Verificar instalação
ollama --version

# Configurar como serviço systemd
sudo tee /etc/systemd/system/ollama.service << 'EOF'
[Unit]
Description=Ollama LLM Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=5
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_CUDA_VISIBLE_DEVICES=0"

[Install]
WantedBy=multi-user.target
EOF

# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

# Verificar status
systemctl status ollama
```

---

## 8. Download de Modelos

### Modelo Principal: Qwen2-7B-Instruct Q4_K_M

```bash
# Via Ollama (mais fácil)
ollama pull qwen2:7b-instruct

# Verificar
ollama list

# Testar
time ollama run qwen2:7b-instruct "Olá, como você está?"
```

**Performance esperada:**
- Primeira execução: ~10-15 segundos (carregamento)
- Inferência: 3-6 tokens/segundo
- VRAM usada: ~3.8-4.0GB

### Modelo Alternativo: Deepseek-Coder

```bash
ollama pull deepseek-coder:6.7b-instruct-q4_K_M
```

---

## 9. Próximas Fases de Desenvolvimento

### Fase 3: Instalação de Dependências Python ✓ PRONTO
```bash
cd ~/projects/omnimind
source venv/bin/activate
pip install -r requirements.txt
```

### Fase 4: Configuração do Qdrant (Vector Database)
```bash
# Via Docker
docker run -d -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  --name qdrant_omnimind \
  qdrant/qdrant

# Verificar
curl http://localhost:6333/healthz
```

### Fase 5: Implementar Agentes ReAct
- Criar `src/agents/react_agent.py`
- Implementar loop Think→Act→Observe
- Integrar com sistema de auditoria
- Testes unitários

### Fase 6: Sistema de Memória Episódica
- Implementar `src/memory/episodic_memory.py`
- Integração com Qdrant
- Consolidação automática

### Fase 7: Integração MCP + D-Bus
- MCP server para filesystem
- D-Bus controllers
- Testes de integração

---

## 10. Otimizações de Performance

### 10.1 Configurações do Sistema

```bash
# Persistência GPU (reduz latência de inicialização)
sudo nvidia-persistenced --user $USER

# Governor de CPU para performance
sudo cpupower frequency-set -g performance

# Desabilitar CPU idle states (opcional, mais calor)
# sudo cpupower idle-set -D 0
```

### 10.2 Monitoramento Contínuo

```bash
# Terminal 1: Monitor GPU
watch -n 1 nvidia-smi

# Terminal 2: Monitor temperatura
watch -n 1 "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader"

# Terminal 3: Logs do Ollama
journalctl -u ollama -f
```

### 10.3 Benchmarks de Referência

Após setup completo, executar benchmarks:

```bash
cd ~/projects/omnimind
source venv/bin/activate

python3 << 'EOF'
import time
from src.audit import log_action

# Teste de inferência
start = time.time()
# ... código de teste
duration = time.time() - start

log_action(
    'gpu_benchmark_completed',
    {
        'duration_seconds': duration,
        'tokens_per_second': tokens / duration,
        'vram_used_mb': vram_used,
        'gpu_utilization': utilization
    },
    'system'
)
EOF
```

---

## 11. Troubleshooting Comum

### Problema: nvidia-smi não funciona após reboot
**Solução:**
```bash
sudo dkms status
sudo dkms install nvidia/550.163.01
sudo modprobe nvidia
```

### Problema: CUDA out of memory
**Solução:**
- Reduzir `gpu_layers` de 20 → 16
- Usar `context_window: 2048`
- Verificar processos: `nvidia-smi`

### Problema: Baixa performance (<2 tokens/s)
**Solução:**
- Verificar GPU está sendo usada: `nvidia-smi` (deve mostrar processo)
- Verificar `gpu_layers` está configurado
- Recompilar llama.cpp com `-DGGML_CUDA=ON`

---

## 12. Checklist de Verificação

### Pré-Reboot
- [x] Drivers NVIDIA instalados
- [x] CUDA Toolkit instalado
- [x] nvidia-smi presente
- [x] Módulo kernel DKMS configurado
- [x] Registrado no sistema de auditoria

### Pós-Reboot (a fazer)
- [ ] nvidia-smi funcionando
- [ ] CUDA detectando GPU
- [ ] llama.cpp compilado com CUDA
- [ ] Ollama instalado e rodando
- [ ] Modelo Qwen2 baixado
- [ ] Teste de inferência (3-6 tokens/s)
- [ ] Qdrant rodando
- [ ] Agentes implementados

---

## 13. Registro de Auditoria

**Evento registrado:**
```json
{
  "action": "nvidia_drivers_installed",
  "category": "system",
  "details": {
    "driver_version": "550.163.01-3",
    "cuda_version": "12.4.127",
    "toolkit_version": "12.4.131",
    "gpu_model": "GTX 1650 Mobile",
    "reboot_required": true,
    "status": "installed_pending_reboot"
  },
  "timestamp": "2025-11-17T..."
}
```

---

## 14. Conclusão

✅ **INSTALAÇÃO DOS DRIVERS NVIDIA E CUDA CONCLUÍDA COM SUCESSO**

**Próxima ação OBRIGATÓRIA:**
```bash
sudo reboot
```

Após reiniciar:
1. Verificar nvidia-smi
2. Compilar llama.cpp com CUDA
3. Instalar e configurar Ollama
4. Baixar modelo Qwen2-7B
5. Testar inferência
6. Continuar implementação dos agentes

**Tempo estimado para próximas fases:** 2-3 horas

---

**Data:** 2025-11-17  
**Sistema:** OmniMind v0.1.0-alpha  
**Status:** Drivers instalados - REBOOT NECESSÁRIO
