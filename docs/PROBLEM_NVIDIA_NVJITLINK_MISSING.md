# 🚨 PROBLEMA CRÍTICO: Biblioteca NVIDIA nvjitlink Faltando

**Data:** 2025-12-14
**Status:** INVESTIGAÇÃO - Bloqueador

---

## ❌ Erro Atual

```
ImportError: /home/fahbrain/projects/omnimind/.venv/lib/python3.12/site-packages/torch/lib/../../nvidia/cusparse/lib/libcusparse.so.12:
undefined symbol: __nvJitLinkComplete_12_4, version libnvJitLink.so.12
```

**Significado:** Torch 2.5.1+cu124 precisa da biblioteca `libnvjitlink.so.12` (nvidia-nvjitlink-cu12) que NÃO está instalada.

---

## 🔍 Diagnóstico

### Localização Esperada:
- `.venv/lib/python3.12/site-packages/nvidia/nvjitlink/lib/libnvjitlink.so.12`
- `/usr/local/cuda-12.4/lib64/libnvjitlink.so.12`

### Verificação:
```bash
$ find .venv -name "libnvjitlink*"
# Resultado: NADA (venv não tem)

$ find /usr/local/cuda-12* -name "libnvjitlink*"
# Resultado: NADA (sistema não tem)

$ pip list | grep nvjitlink
nvidia-nvjitlink-cu12    12.4.127  # Pip diz que ESTÁ instalado!
```

### Problema:
Pip acha que o pacote está instalado MAS a biblioteca não está em lugar nenhum!

---

## ✅ SOLUÇÕES (Tentar nessa ordem)

### Solução 1: Reinstalar nvidia-nvjitlink com --force-reinstall
```bash
source .venv/bin/activate
pip install --force-reinstall --no-cache-dir nvidia-nvjitlink-cu12==12.4.127
python -c "import torch; print('✅ OK')"
```

### Solução 2: Se não funcionar - reinstalar TODOS os NVIDIA libs
```bash
source .venv/bin/activate
pip install --force-reinstall --no-cache-dir \
  nvidia-cuda-runtime-cu12==12.4.127 \
  nvidia-nvjitlink-cu12==12.4.127 \
  nvidia-cusparse-cu12==12.3.1.170 \
  nvidia-cusolver-cu12==11.6.1.9 \
  nvidia-cublas-cu12==12.4.5.8
python -c "import torch; print('✅ OK')"
```

### Solução 3: Usar Conda ao invés de pip (melhor gerenciamento de libs)
```bash
conda create -n omnimind python=3.12.3
conda activate omnimind
conda install pytorch::pytorch pytorch::pytorch-cuda=12.4 -c pytorch -c nvidia
conda install qiskit qiskit-aer-gpu -c conda-forge
```

### Solução 4: Usar Docker (isolado, sem problemas de libs do sistema)
```bash
docker build -f deploy/Dockerfile.development-gpu -t omnimind:dev-gpu .
docker run --gpus all -it omnimind:dev-gpu bash
python final_check.py  # ✅ Should work
```

---

## 🎯 RECOMENDAÇÃO

**Solução 3 (Conda) é a MAIS CONFIÁVEL** para máquinas locais com GPU, pois:
- ✅ Gerencia libs NVIDIA automaticamente
- ✅ Evita conflitos entre múltiplas versões
- ✅ Funciona com GPU sem problemas
- ✅ Reprodutível entre máquinas

**Solução 4 (Docker) é a MELHOR** para CI/CD e produção, pois:
- ✅ Ambiente isolado & reproducível
- ✅ Sem conflitos de libs do sistema
- ✅ Fácil deploy em qualquer servidor
- ✅ Control total sobre versões

---

## 📝 Próximo Passo

Escolha uma das soluções acima e execute. Recomendo **Solução 1 primeiro** (mais rápida), depois **Solução 3 (Conda)** se não funcionar.

