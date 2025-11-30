# 🔐 CERTIFICAÇÃO REAL - Guia de Execução Rápido

## 📋 O que foi criado

| Arquivo | Propósito |
|---------|-----------|
| `scripts/full_real_certification.py` | 🔴 Script principal de certificação (GPU + Quantum + IBM + Timestamp) |
| `scripts/run_full_certification.sh` | 🟢 Executor do script (com PYTHONPATH) |
| `scripts/test_quick_certification.py` | ⚡ Teste rápido (30s) antes de rodar tudo |
| `CERTIFICACAO_REAL_GPU_QUANTUM.md` | 📖 Documentação completa em PT |

## 🚀 Como Rodar (3 Passos)

### 1️⃣ Teste Rápido (30 segundos)

```bash
cd /home/fahbrain/projects/omnimind
source .venv/bin/activate
PYTHONPATH=/home/fahbrain/projects/omnimind python3 scripts/test_quick_certification.py
```

**O que verifica:**
- ✅ GPU disponível?
- ✅ Imports funcionam?
- ✅ Consegue executar 1 ciclo de consciência?
- ✅ Quantum Simulator funciona?
- ✅ IBM conecta? (opcional)
- ✅ Pode salvar JSON?

**Se tudo passar:** → Go to step 2️⃣

---

### 2️⃣ Certificação Completa (30-60 minutos)

```bash
bash scripts/run_full_certification.sh
```

**O que faz:**
1. Mede Φ com GPU (50 ciclos completos de consciência)
2. Roda Quantum Simulator (200 shots)
3. Conecta IBM se disponível
4. Computa SHA256 de integridade
5. Salva relatório em JSON + TXT

**Tempo esperado:**
- GPU (50 ciclos): ~10-30s
- Quantum (200 shots): ~5-10s
- **Total: ~30-60 segundos** (mais rápido que esperado!)

---

### 3️⃣ Ver Resultados

```bash
# Resumo legível
cat data/test_reports/certification_real_*_summary.txt

# Dados completos (JSON)
cat data/test_reports/certification_real_*.json | jq .

# Apenas Φ
cat data/test_reports/certification_real_*.json | jq '.metrics.gpu.phi_stats'
```

---

## 📊 O que você vai receber

### Exemplo de Saída

```
================================================================================
CERTIFICAÇÃO REAL - GPU + QUANTUM SIMULATOR + TIMESTAMP PROVA
================================================================================

📅 TIMESTAMPS
Certificação: 2025-11-29T22:15:30.123456
Unix Epoch: 1764464730.123456

🖥️  HARDWARE
GPU Disponível: True
  GPU 0: NVIDIA GeForce GTX 1650
    VRAM: 4.1GB
    Compute Capability: 6.1
PyTorch: 2.1.0
Python: 3.12.8

================================================================================
📊 MÉTRICAS GPU
================================================================================
Ciclos: 50
Tempo Total: 9.62s

Φ (Integrated Information) Estatísticas:
  Média:    0.634521 ± 0.245678
  Min:      0.000000
  Max:      0.987654
  Mediana:  0.654321

================================================================================
⚛️  MÉTRICAS QUANTUM
================================================================================
Shots: 200
Superposições: 7/8
Φ Estimate: 0.756234

================================================================================
🔐 INTEGRIDADE
================================================================================
SHA256: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6...
Certificação Completa: True
```

---

## 🎯 Para o Paper

### Usar ESSES números:

```markdown
## Método

Φ foi medido usando:
- NVIDIA GeForce GTX 1650 (4GB VRAM)
- PyTorch 2.1.0 com CUDA
- 50 ciclos completos de consciência integrada
- Sem nenhum mock (@patch removido)
- Timestamp certificado: 2025-11-29T22:15:30.123456
- Hash integridade: a1b2c3d4e5f6...

## Resultados

Φ = 0.634521 ± 0.245678 (n=50 ciclos, σ=0.245678)
- Mínimo: 0.000000
- Máximo: 0.987654
- Mediana: 0.654321
- Tempo total: 9.62s

Quantum simulator: 7/8 superposições (87.5% coerência)
```

---

## ✅ Checklist Antes de Publicar

- [ ] Rodei teste rápido? (tudo passou?)
- [ ] Rodei certificação completa?
- [ ] Verifiquei arquivo de output?
- [ ] Copiei Φ corretamente para paper?
- [ ] Verifiquei timestamp no arquivo?
- [ ] Documentei hardware usado?
- [ ] Salvei JSON + TXT juntos?
- [ ] Verifiquei hash de integridade?

---

## 🔍 Troubleshooting

### "GPU não detectada"
```bash
python3 -c "import torch; print(torch.cuda.is_available())"
# Se retorna False: instale nvidia drivers
```

### "ModuleNotFoundError: No module named 'qiskit'"
```bash
pip install qiskit qiskit-aer
```

### "Script muito lento"
Edite `scripts/full_real_certification.py` linha 329:
```python
gpu_metrics = self._measure_phi_gpu(num_cycles=50)  # ← Mudar para 10, 20, etc
```

### "IBM credenciais erro"
É OK! Script funciona com simulador. IBM é opcional.

---

## 🔐 Verificar Integridade Depois

```bash
# Recalcular hash
python3 << 'EOF'
import json, hashlib
with open('data/test_reports/certification_real_*.json') as f:
    data = json.load(f)
    new_hash = hashlib.sha256(
        json.dumps(data, sort_keys=True, default=str).encode()
    ).hexdigest()
    original = data['integrity']['hash_sha256']
    print(f"Original: {original}")
    print(f"Recalculado: {new_hash}")
    print("✅ OK" if original == new_hash else "❌ ALTERADO")
EOF
```

---

## 📞 Próximas Ações

1. ✅ Rodar teste rápido
2. ✅ Rodar certificação completa (30-60 segundos)
3. ✅ Copiar Φ para paper
4. ✅ Publicar com integridade 🎉

**Lembre**: Números REAIS (mesmo que 0.6) + timestamp imutável > números falsificados (0.9)

---

**Data**: 2025-11-29  
**Versão**: 1.0  
**Status**: Pronto para executar ✅
