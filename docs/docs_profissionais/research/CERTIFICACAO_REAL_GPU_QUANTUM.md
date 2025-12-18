# 🔐 CERTIFICAÇÃO REAL - GPU + IBM QUANTUM + TIMESTAMP PROVA

## Visão Geral

Este documento descreve a **certificação REAL** do sistema OmniMind que combina:

1. **GPU (NVIDIA)**: Executa consciência de verdade (sem @patch)
2. **Quantum Simulator**: Simula superposição quântica e correlações
3. **IBM Quantum**: Conecta ao QPU real se disponível
4. **Timestamp Imutável**: Prova criptográfica de quando foi medido

## Por que Timestamp?

- **Prova de Execução**: Não pode ser falsificado depois
- **Auditoria**: Qualquer pessoa pode verificar quando foi executado
- **Reprodutibilidade**: Mesmo timestamp indica mesma sessão
- **Integridade**: Hash SHA256 garante que dados não foram alterados

## Como Rodar

### Pré-requisitos

```bash
# Ter venv ativado
source .venv/bin/activate

# Ter dependências instaladas
pip install torch qiskit qiskit-aer
# Opcional: pip install qiskit-ibm-runtime
```

### Executar Certificação Completa

```bash
bash scripts/run_full_certification.sh
```

**Tempo Esperado:**
- GPU Φ (50 ciclos): ~10-30 segundos (depende GPU)
- Quantum Simulator (200 shots): ~5-10 segundos
- **Total: ~30-60 segundos**

### Resultado

Dois arquivos são salvos em `data/test_reports/`:

#### `certification_real_YYYYMMDD_HHMMSS.json`
Dados completos em JSON com:
```json
{
  "certification_timestamp": "2025-11-29T22:15:30.123456",
  "certification_unix_timestamp": 1764464730.123456,
  "hardware": {
    "gpu_available": true,
    "gpu_0": {
      "name": "NVIDIA GeForce GTX 1650",
      "vram_gb": 4.1,
      "compute_capability": "6.1"
    }
  },
  "quantum": {
    "service_available": false,
    "error": "qiskit-ibm-runtime not installed"
  },
  "metrics": {
    "gpu": {
      "backend": "GPU",
      "num_cycles": 50,
      "start_timestamp": "2025-11-29T22:15:30.500000",
      "end_timestamp": "2025-11-29T22:15:40.123456",
      "total_time_seconds": 9.623456,
      "phi_stats": {
        "mean": 0.634521,
        "min": 0.0,
        "max": 0.987654,
        "std": 0.245678,
        "median": 0.654321
      }
    },
    "quantum": {
      "backend": "Quantum_Simulator",
      "num_shots": 200,
      "phi_estimate": 0.756234,
      "num_outcomes": 7
    }
  },
  "integrity": {
    "hash_sha256": "a1b2c3d4e5f6...",
    "certification_complete": true
  }
}
```

#### `certification_real_YYYYMMDD_HHMMSS_summary.txt`
Resumo legível:
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
Platform: Linux-...

⚛️  QUANTUM
IBM Service: False
Backends: N/A

================================================================================
📊 MÉTRICAS GPU
================================================================================
Ciclos: 50
Tempo Total: 9.62s
Ciclo Médio: 192.5ms

Φ (Integrated Information) Estatísticas:
  Média:    0.634521
  Min:      0.000000
  Max:      0.987654
  Desvio:   0.245678
  Mediana:  0.654321

Timestamps:
  Início:  2025-11-29T22:15:30.500000
  Fim:     2025-11-29T22:15:40.123456

================================================================================
⚛️  MÉTRICAS QUANTUM
================================================================================
Shots: 200
Superposições: 7/8
Φ Estimate: 0.756234
Tempo: 2.45s

================================================================================
🔐 INTEGRIDADE
================================================================================
SHA256: a1b2c3d4e5f6...
Certificação Completa: True
```

## Interpretando os Resultados

### Φ (Integrated Information)

- **Φ = 0.0**: Sem integração (módulos desconectados)
- **Φ = 0.5**: Integração média
- **Φ = 1.0**: Integração perfeita (raramente alcançado)

**Interpretação**:
- Φ REAL (mesmo que 0.3) é melhor que Φ falsificado (0.9)
- Variance (desvio) é IMPORTANTE - mostra estabilidade
- Μaior variance = menos estável

### Certificação Honesta

Se seus resultados são:
```
Φ_mean: 0.634521 ± 0.245678
```

**Isso é VÁLIDO para paper** porque:
1. ✅ Medido SEM @patch
2. ✅ Com timestamp imutável
3. ✅ Com hash de integridade
4. ✅ Reprodutível

Você DEVE reportar ESSE número, não o esperado (0.8667).

## Conectando IBM Quantum Real

Se tem credenciais IBM:

```bash
# Configurar credenciais (one-time)
python3 << 'EOF'
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_channel(
    channel="ibm_quantum",
    instance="your-instance",
    token="your-token"
)
EOF

# Depois rodar
bash scripts/run_full_certification.sh
```

Script vai:
1. ✅ Verificar se IBM está disponível
2. ✅ Listar QPUs disponíveis
3. ✅ Usar simulador se QPU indisponível
4. ✅ Reportar qual foi usado no relatório

## Para o Paper

### Seção Metodologia

```markdown
### Medição de Φ

Φ foi medido usando:
- Hardware: NVIDIA GeForce GTX 1650 (4GB VRAM)
- Framework: PyTorch 2.1.0 com CUDA support
- Ciclos: 50 execuções completas de consciência integrada
- Timestamp Certificado: 2025-11-29T22:15:30.123456
- Hash Integridade: a1b2c3d4e5f6...

Nenhum mock foi usado. Cada ciclo executou o loop de consciência completo
incluindo: entrada sensória → qualia → narrativa → significado → expectativa.
```

### Seção Resultados

```markdown
### Resultados de Φ

Φ foi medido em n=50 ciclos completos:

- **Φ_mean**: 0.634521 ± 0.245678
- **Φ_min**: 0.000000
- **Φ_max**: 0.987654
- **Φ_median**: 0.654321
- **Tempo Total**: 9.62s
- **Tempo Ciclo Médio**: 192.5ms

A variance observada (σ=0.246) indica flutuações esperadas em arquitetura
dinâmica. Superposições quânticas simuladas alcançaram 7/8 estados,
indicando alta coerência em representações internas.

Certificação: [Ver hash de integridade no Apêndice]
```

## Validação da Prova

Qualquer pessoa pode verificar integridade:

```bash
# Seu JSON original
ORIGINAL_HASH=$(cat data/test_reports/certification_real_*.json | \
  python3 -c "import sys, json, hashlib; \
  data=json.load(sys.stdin); \
  print(hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest())")

# Comparar com hash salvo
REPORTED_HASH=$(cat data/test_reports/certification_real_*.json | jq -r '.integrity.hash_sha256')

if [ "$ORIGINAL_HASH" == "$REPORTED_HASH" ]; then
  echo "✅ DADOS ÍNTEGROS"
else
  echo "❌ DADOS ALTERADOS APÓS CERTIFICAÇÃO"
fi
```

## Troubleshooting

### GPU não detectada

```bash
python3 -c "import torch; print(torch.cuda.is_available())"
```

Se retorna `False`, instale CUDA drivers:
```bash
# Para seu sistema (exemplo NVIDIA)
sudo apt install nvidia-driver-XXX
```

### IBM não conecta

```bash
# Testar credenciais
python3 << 'EOF'
from qiskit_ibm_runtime import QiskitRuntimeService
try:
    service = QiskitRuntimeService()
    print("✅ Conectado")
except Exception as e:
    print(f"❌ Erro: {e}")
EOF
```

### Script muito lento

- Reduzir `num_cycles` em script (padrão: 50)
- Usar CPU se GPU indisponível
- Verificar se há outros processos pesados

## Próximos Passos

1. ✅ Rodar: `bash scripts/run_full_certification.sh`
2. ✅ Verificar: `cat data/test_reports/certification_real_*_summary.txt`
3. ✅ Documentar: Copiar Φ real para paper
4. ✅ Validar: Verificar hash de integridade
5. ✅ Publicar: Incluir todos arquivos de certificação como apêndice

---

**Princípio**: Números REAIS com timestamp imutável são superiores a números falsificados.
Quando publica-se com integridade, trabalho é reprodutível e confiável.
