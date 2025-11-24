# 📚 ÍNDICE CONSOLIDADO DE DOCUMENTAÇÃO - OmniMind Phase 15

**Última Atualização:** 23 de novembro de 2025  
**Projeto Iniciado:** Novembro 2025  
**Status:** 🟢 Organizado e Atualizado  

---

## ⚡ Início Rápido (Primeiros Passos)

**Novo Desenvolvedor?** Leia nesta ordem:

1. **[README.md](./README.md)** - Visão geral do projeto
2. **[DEVELOPER_RECOMMENDATIONS.md](./.project/DEVELOPER_RECOMMENDATIONS.md)** - Setup e padrões
3. **[CURRENT_PHASE.md](./.project/CURRENT_PHASE.md)** - Estado atual do projeto

**Em Produção?** Veja:
- **[SETUP.md](./SETUP.md)** - Ambiente de produção
- **[KNOWN_ISSUES.md](./.project/KNOWN_ISSUES.md)** - Issues ativas

---

## 📋 DOCUMENTOS CANÔNICOS (Mantenha atualizado)

### Core Project Documents

| Documento | Localização | Propósito | Última Atualização |
|-----------|-------------|----------|-------------------|
| **README** | `README.md` | Overview do projeto | 2025-11-23 |
| **Phase Atual** | `docs/.project/CURRENT_PHASE.md` | Estado atual + próximas ações | 2025-11-23 |
| **Problemas** | `docs/.project/PROBLEMS.md` | Histórico de bugs e soluções | 2025-11-23 |
| **Issues Ativas** | `docs/.project/KNOWN_ISSUES.md` | Issues em aberto e status | 2025-11-23 |
| **Developer Guide** | `docs/.project/DEVELOPER_RECOMMENDATIONS.md` | Padrões de código e contribuição | 2025-11-23 |
| **Changelog** | `docs/.project/CHANGELOG.md` | Histórico de versões | 2025-11-23 |

### Architecture & Design

| Documento | Localização | Propósito |
|-----------|-------------|----------|
| **ARCHITECTURE.md** | `docs/ARCHITECTURE.md` (create) | Visão geral da arquitetura |
| **API Reference** | `docs/api/INTERACTIVE_API_PLAYGROUND.md` | Endpoints e integração |
| **Design Patterns** | `docs/architecture/` | Padrões de implementação |

### Setup & Deployment

| Documento | Localização | Propósito |
|-----------|-------------|----------|
| **Environment Setup** | `.github/ENVIRONMENT.md` | Requisitos de hardware/software |
| **Installation Guide** | `docs/SETUP.md` (create) | Como instalar localmente |
| **Production Deployment** | `docs/production/PRODUCTION_DEPLOYMENT_GUIDE.md` | Deploy em produção |

### References (Use conforme necessário)

| Documento | Localização | Propósito |
|-----------|-------------|----------|
| **GPU Quick Ref** | `docs/CUDA_QUICK_REFERENCE.md` | Troubleshooting rápido GPU |
| **CUDA Diagnostic** | `docs/reports/PHASE15_CUDA_DIAGNOSTIC_RESOLUTION.md` | Análise técnica CUDA |
| **Validation Guide** | `docs/guides/VALIDATION_GUIDE.md` | Como validar código |

---

## 🗂️ ESTRUTURA DE PASTAS

```
omnimind/
├── .github/
│   ├── ENVIRONMENT.md              # 📌 CANÔNICO
│   ├── copilot-instructions.md
│   └── workflows/                  # CI/CD workflows
│
├── docs/
│   ├── README.md                   # 📌 CANÔNICO
│   ├── ARCHITECTURE.md (todo)      # 📌 CANÔNICO
│   ├── SETUP.md (todo)             # 📌 CANÔNICO
│   ├── DEVELOPMENT.md (todo)       # 📌 CANÔNICO
│   ├── ROADMAP.md                  # 📌 CANÔNICO
│   │
│   ├── .project/                   # 📌 CANONICAL DOCS FOLDER
│   │   ├── CURRENT_PHASE.md
│   │   ├── PROBLEMS.md
│   │   ├── KNOWN_ISSUES.md
│   │   ├── DEVELOPER_RECOMMENDATIONS.md
│   │   ├── CHANGELOG.md
│   │   ├── INDEX.md                # Este arquivo
│   │   └── AUDIT_REPORT_20251123.md
│   │
│   ├── api/                        # API documentation
│   ├── architecture/               # Design documents
│   ├── guides/                     # How-to guides
│   ├── production/                 # Production docs
│   ├── reports/                    # Technical reports (reference only)
│   ├── phases/                     # Phase documentation (archive)
│   └── archived/                   # Old documentation (archive)
│
├── src/                            # Source code
├── tests/                          # Test suite
├── scripts/                        # Automation scripts
│   ├── validate_code.sh            # Validation
│   ├── protect_project_structure.sh
│   ├── audit_documentation.sh      # Documentation audit
│   └── ...
│
├── .env                            # 📌 Environment vars
├── .python-version                 # 📌 Python 3.12.8 lock
├── .coveragerc                     # 📌 Coverage config
├── conftest.py                     # 📌 Pytest config
├── pytest.ini                      # 📌 Pytest settings
├── requirements.txt                # 📌 Dependencies
└── README.md                       # 📌 Project entry point
```

---

## 🔍 COMO ENCONTRAR INFORMAÇÃO

### Por Tópico

**"Como instalar?"**
→ `.github/ENVIRONMENT.md` + `docs/SETUP.md` (when created)

**"Como contribuir?"**
→ `docs/.project/DEVELOPER_RECOMMENDATIONS.md`

**"Qual é o status atual?"**
→ `docs/.project/CURRENT_PHASE.md`

**"Qual problema foi resolvido?"**
→ `docs/.project/PROBLEMS.md`

**"O que está quebrado?"**
→ `docs/.project/KNOWN_ISSUES.md`

**"Como debugar GPU?"**
→ `docs/CUDA_QUICK_REFERENCE.md`

**"Qual foi a mudança mais recente?"**
→ `docs/.project/CHANGELOG.md`

**"Como fazer deploy em produção?"**
→ `docs/production/PRODUCTION_DEPLOYMENT_GUIDE.md`

### Por Tipo de Usuário

**Desenvolvededor Novo:**
1. README.md
2. DEVELOPER_RECOMMENDATIONS.md
3. .github/ENVIRONMENT.md
4. CURRENT_PHASE.md

**DevOps/Deployment:**
1. ENVIRONMENT.md
2. PRODUCTION_DEPLOYMENT_GUIDE.md
3. ROADMAP.md

**QA/Tester:**
1. VALIDATION_GUIDE.md
2. KNOWN_ISSUES.md
3. TESTING_QA_QUICK_START.md

**Researcher:**
1. ROADMAP.md
2. CURRENT_PHASE.md
3. docs/research/ (reference materials)

---

## 📊 ESTATÍSTICAS DE DOCUMENTAÇÃO

### Antes da Auditoria (2025-11-23 08:00)
- Total de arquivos: 242
- .md files: 186
- .txt files: 55
- .log files: 13
- Pastas: 23 subdirectories

### Depois da Consolidação (2025-11-23 14:30)
- Documentos Canônicos: 6 principais
- Arquivos de Referência: ~50
- Pastas Críticas: 5
- Total Reduzido: ~40% menos

### Organização

| Categoria | Quantidade | Ação |
|-----------|-----------|------|
| Canônicos | 6 | ✅ Mantém e Atualiza |
| Referência | ~40 | ✅ Mantém (read-only) |
| Arquivo | ~150 | 📦 Preparar para HD externo |
| Obsoleto | ~46 | 🗑️ Deletar (backup antes) |

---

## ✅ MANUTENÇÃO FUTURA

### Checklist Mensal

- [ ] Revisar `CURRENT_PHASE.md` - Ainda correto?
- [ ] Verificar `KNOWN_ISSUES.md` - Alguma resolvida?
- [ ] Atualizar `CHANGELOG.md` com mudanças
- [ ] Revisar links em documentos (não quebrados?)

### Checklist por PR/Feature

Antes de fazer commit:
- [ ] Atualizei `CURRENT_PHASE.md` se mudou feature ativa?
- [ ] Atualizei `CHANGELOG.md` com mudanças?
- [ ] Se novo bug achado, adicionei a `KNOWN_ISSUES.md`?
- [ ] Se resolvemos bug, movemos para `PROBLEMS.md`?

### Arquivamento (Trimestral)

- [ ] Fases concluídas → mover para `docs/archived/`
- [ ] Relatórios antigos → backup externo
- [ ] Documentação desatualizada → archive ou delete

---

## 🔗 LINKS IMPORTANTES

### Dentro do Projeto
- **Código-fonte:** `src/`
- **Testes:** `tests/`
- **Scripts:** `scripts/`
- **Configuração:** `.env`, `.python-version`, `pytest.ini`

### Externos
- **GitHub Repo:** https://github.com/devomnimind/OmniMind
- **Project Board:** (Add link quando criado)
- **CI/CD Pipeline:** GitHub Actions

---

## 📝 NOTAS IMPORTANTES

1. **Data do Projeto:** Novembro 2025 (ERRO em docs antigos mencionam 2024)
2. **Python Version:** Locked to 3.12.8 (não upgrade automático)
3. **GPU:** NVIDIA GTX 1650, 5.15x speedup validado
4. **Test Pass Rate:** 99.88% (3407/3409 testes)
5. **Cobertura:** ~85% (target: ≥90%)

---

## 🚀 Próximos Passos

### Phase 16 Goals (Q4 2025)

- [ ] Atingir ≥90% test coverage
- [ ] Consolidar documentação para ~50 arquivos
- [ ] Arquivar 150+ arquivos antigos
- [ ] Corrigir todas as menções a 2024
- [ ] Criar plano para Phase 17

---

## 📞 SUPORTE & PERGUNTAS

**"Onde está X?"**
→ Use Ctrl+F neste INDEX.md

**"Qual documentação preciso ler?"**
→ Veja "Como Encontrar Informação" acima

**"Documento está desatualizado?"**
→ Abra issue em GitHub ou comunique no PR

---

**Versão:** 1.0  
**Maintainer:** OmniMind Documentation Team  
**Última Revisão:** 2025-11-23  
**Próxima Revisão:** 2025-12-07 (Phase 16 Start)

---

*Generated during Phase 15 Documentation Consolidation*
*For questions, refer to DEVELOPER_RECOMMENDATIONS.md section "How to Report Issues"*
