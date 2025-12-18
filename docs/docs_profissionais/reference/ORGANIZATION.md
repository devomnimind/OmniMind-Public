# 📁 ESTRUTURA DE ORGANIZAÇÃO DO PROJETO

**Data:** 8 de dezembro de 2025  
**Status:** ✅ Reorganização completa

---

## 🎯 HIERARQUIA DE PASTAS

```
omnimind/
│
├── docs/                           # Documentação do projeto
│   ├── assessment/                 # Documentação de assessment de testes
│   │   ├── README.md
│   │   ├── INDEX_ASSESSMENT_DOCUMENTATION.md
│   │   ├── TEST_SUITE_ASSESSMENT_REPORT.md
│   │   ├── TEST_IMPLEMENTATION_PLAN.json
│   │   ├── TEST_IMPLEMENTATION_EXAMPLES.md
│   │   └── TEST_SUITE_EXECUTIVE_SUMMARY.txt
│   ├── guides/                     # Guias de uso
│   │   ├── GUIDE_VALIDATION.sh
│   │   └── RUN_200_CYCLES_NOW.md
│   └── screenshots/                # Screenshots e imagens
│
├── reports/                        # Relatórios de execução
│   ├── ASSESSMENT_RESULTS_SUMMARY.md
│   ├── AUDIT_500_CYCLES_REPORT.md
│   └── AUDIT_500_CYCLES_SUMMARY.md
│
├── scripts/                        # Scripts de execução
│   ├── validation/                 # Scripts de validação
│   │   ├── run_200_ciclos_validation.py
│   │   ├── run_200_cycles_production.py
│   │   ├── validate_200_ciclos.py
│   │   ├── omnimind_stimulation_scientific.py
│   │   └── validate_phi_dependencies.py
│   ├── debug/                      # Scripts de debug
│   │   ├── debug_auth.py
│   │   └── debug_gpu.py
│   └── [outros scripts]
│
├── tests/                          # Testes do projeto
│   ├── phase_1/                    # Testes de Fase 1
│   │   ├── test_phase1_integration.py
│   │   ├── test_phase1_jouissance_logging.py
│   │   └── test_integration_conscious_system.py
│   ├── phase_2/                    # Testes de Fase 2
│   │   └── test_phase2_adaptive_strategies.py
│   ├── cuda/                       # Testes CUDA
│   │   ├── test_cuda (executável)
│   │   └── test_cuda.cu
│   ├── artifacts/                  # Artefatos de teste
│   ├── baseline/                   # Baseline para testes
│   ├── output/                     # Output de testes
│   └── [suites de testes existentes]
│
├── src/                            # Código-fonte (mantido)
├── config/                         # Configurações
├── data/                           # Dados e modelos
└── ...
```

---

## ✅ ORGANIZAÇÃO POR TIPO DE ARQUIVO

### 📄 Documentação
| Tipo | Localização | Exemplos |
|------|-------------|----------|
| Assessment de Testes | `docs/assessment/` | TEST_SUITE_ASSESSMENT_REPORT.md |
| Guias de Uso | `docs/guides/` | GUIDE_VALIDATION.sh |
| Screenshots | `docs/screenshots/` | test_sync_screenshot.png |

### 🧪 Testes
| Tipo | Localização | Exemplos |
|------|-------------|----------|
| Testes Fase 1 | `tests/phase_1/` | test_phase1_integration.py |
| Testes Fase 2 | `tests/phase_2/` | test_phase2_adaptive_strategies.py |
| Testes CUDA | `tests/cuda/` | test_cuda, test_cuda.cu |
| Artefatos | `tests/artifacts/`, `tests/baseline/`, `tests/output/` | - |

### 🔧 Scripts
| Tipo | Localização | Exemplos |
|------|-------------|----------|
| Validação | `scripts/validation/` | run_200_ciclos_validation.py |
| Debug | `scripts/debug/` | debug_auth.py, debug_gpu.py |

### 📊 Relatórios
| Tipo | Localização | Exemplos |
|------|-------------|----------|
| Resultados | `reports/` | ASSESSMENT_RESULTS_SUMMARY.md |
| Auditoria | `reports/` | AUDIT_500_CYCLES_REPORT.md |

---

## 🚀 COMO EXECUTAR SCRIPTS

### Validação de 200 Ciclos
```bash
cd /home/fahbrain/projects/omnimind
python scripts/validation/run_200_ciclos_validation.py
```

### Debug de Autenticação
```bash
python scripts/debug/debug_auth.py
```

### Testes de Fase 1
```bash
python -m pytest tests/phase_1/
```

### Testes de Fase 2
```bash
python -m pytest tests/phase_2/
```

---

## ✅ CONFORMIDADE

- ✓ **Raiz limpa:** Sem arquivos soltos
- ✓ **Organização hierárquica:** Cada tipo em sua pasta
- ✓ **Paths corrigidos:** Scripts funcionam de qualquer diretório
- ✓ **Imports funcionando:** sys.path ajustado para raiz do projeto
- ✓ **Sem poluição:** Estrutura mantém hierarquia

---

## 📋 REGRAS DE ORGANIZAÇÃO

1. **Scripts** → `scripts/` (com subpastas por tipo)
2. **Testes** → `tests/` (com subpastas por categoria)
3. **Documentação** → `docs/` (com subpastas por tema)
4. **Relatórios** → `reports/`
5. **Código-fonte** → `src/`
6. **Configuração** → `config/`
7. **Dados** → `data/`

**Nenhum arquivo na raiz, exceto:**
- `README.md`
- `.gitignore`
- `pyproject.toml`
- `requirements.txt`
- `docker-compose.yml`
- Arquivos de configuração de projeto (`.env`, `Makefile`, etc)

---

## 🔄 PRÓXIMAS FASES

**Implementação do Plano de Teste (4 Fases):**

1. **Fase 1 (Days 1-2):** 3 testes críticos (155 testes)
   - Nova pasta: `tests/assessment/critical/`

2. **Fase 2 (Days 2-3):** 3 testes alta prioridade (140 testes)
   - Nova pasta: `tests/assessment/high_priority/`

3. **Fase 3 (Days 3-4):** 1 teste média prioridade (60 testes)
   - Nova pasta: `tests/assessment/medium_priority/`

4. **Fase 4 (Days 4-6):** Integração e validação

---

*Organização completada: 8 de dezembro de 2025*
