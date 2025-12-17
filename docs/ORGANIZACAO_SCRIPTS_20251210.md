# 📁 ORGANIZAÇÃO DE SCRIPTS - OmniMind

**Data**: 2025-12-10
**Autor**: Fabrício da Silva + assistência de IA
**Status**: Documento de referência

> Este documento mapeia todos os scripts do projeto, suas fases, referências e recomendações de organização.

---

## 📋 SCRIPTS NA RAIZ DO PROJETO

### Scripts Encontrados

1. **`monitor_phase7.sh`** - Monitoramento Phase 7 (Zimerman Bonds)
   - **Fase**: Phase 7
   - **Uso**: Monitoramento em tempo real
   - **Recomendação**: Mover para `scripts/monitoring/phase7/`

2. **`optimize_log.py`** - Otimização de logs
   - **Fase**: Manutenção
   - **Uso**: Utilitário de manutenção
   - **Recomendação**: Mover para `scripts/utilities/maintenance/`

3. **`test_decisions_fix.sh`** - Teste de correção de decisões
   - **Fase**: Correções/Fixes
   - **Uso**: Teste específico de fix
   - **Recomendação**: Mover para `scripts/testing/fixes/`

4. **`test_full_fix.sh`** - Teste completo de correções
   - **Fase**: Correções/Fixes
   - **Uso**: Teste específico de fix
   - **Recomendação**: Mover para `scripts/testing/fixes/`

5. **`test_tribunal_fix.sh`** - Teste de correção do Tribunal
   - **Fase**: Correções/Fixes
   - **Uso**: Teste específico de fix
   - **Recomendação**: Mover para `scripts/testing/fixes/`

6. **`TRIBUNAL_FIX_VISUAL.sh`** - Visualização do fix do Tribunal
   - **Fase**: Documentação/Visualização
   - **Uso**: Script de documentação visual
   - **Recomendação**: Mover para `scripts/archive/deprecated/` ou `docs/corrections/`

---

## 🗺️ MAPEAMENTO POR FASE

### Phase 0 (Data Collection)
- `docs/phases/phase-0-data-collection/validate_phase0.sh`

### Phase 1 (Analysis)
- Scripts de análise em `scripts/analysis/`

### Phase 5-6 (Production)
- `scripts/phase5_6_standard_operating_procedure.sh`
- `scripts/phase5_6_simplified_sop.sh`
- `scripts/phase5_6_metrics_production.py`
- `scripts/visual_report_phase6.py`

### Phase 7 (Zimerman Bonds)
- `monitor_phase7.sh` (raiz)
- `docs/phases/phase-7-zimerman/PHASE7_DELTAPHI_FIX.sh`

### Phase 22 (Production)
- `scripts/phase22_initialization.sh`
- `scripts/start_production_phase22.sh`

### Phase 24 (Lacanian Memory)
- Scripts de validação em `scripts/validation/validate_phase_24_complete.py`

### Phase 26 (Current)
- `scripts/test_phase_26c.py`

---

## 📁 ESTRUTURA RECOMENDADA

### Scripts Canônicos (Oficiais)
```
scripts/
├── canonical/ ⭐ SCRIPTS OFICIAIS
│   ├── install/ - Instalação
│   ├── system/ - Sistema principal
│   ├── monitor/ - Monitoramento
│   ├── test/ - Testes
│   ├── validate/ - Validação
│   └── diagnose/ - Diagnóstico
```

### Scripts por Categoria
```
scripts/
├── testing/
│   └── fixes/ - Scripts de teste de correções
├── monitoring/
│   └── phase7/ - Monitoramento Phase 7
├── utilities/
│   └── maintenance/ - Utilitários de manutenção
└── archive/
    └── deprecated/ - Scripts arquivados
```

---

## 🔍 VERIFICAÇÃO DE PATHS

### Documentação que referencia scripts

**README.md:**
- `scripts/run_tests_fast.sh`
- `scripts/run_tests_with_defense.sh`
- `scripts/run_200_cycles_verbose.py`

**docs/reference/INDICE_SCRIPTS_RELATORIOS.md:**
- Mapeamento completo de scripts canônicos
- Scripts por categoria

**scripts/README.md:**
- Documentação oficial de scripts
- Estrutura e uso

---

## ✅ AÇÕES RECOMENDADAS

### 1. Mover Scripts da Raiz

```bash
# Criar estrutura
mkdir -p scripts/testing/fixes
mkdir -p scripts/monitoring/phase7
mkdir -p scripts/utilities/maintenance

# Mover scripts
mv test_decisions_fix.sh test_full_fix.sh test_tribunal_fix.sh scripts/testing/fixes/
mv monitor_phase7.sh scripts/monitoring/phase7/
mv optimize_log.py scripts/utilities/maintenance/
mv TRIBUNAL_FIX_VISUAL.sh scripts/archive/deprecated/
```

### 2. Atualizar Referências

Após mover, atualizar referências em:
- `README.md`
- `docs/reference/INDICE_SCRIPTS_RELATORIOS.md`
- `scripts/README.md`
- Qualquer documentação que referencie esses scripts

### 3. Verificar Paths em Scripts

Verificar se scripts movidos têm paths absolutos ou relativos que precisam ser atualizados.

---

## 📊 SCRIPTS CANDIDATOS A ARQUIVAR

### Scripts Não Referenciados

Nenhum script não referenciado encontrado na análise inicial.

### Scripts Obsoletos

- `TRIBUNAL_FIX_VISUAL.sh` - Script de documentação visual (já resolvido)
- Scripts antigos em `scripts/archive/` já arquivados

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Criar estrutura de pastas recomendada
2. ⏳ Mover scripts da raiz para pastas apropriadas
3. ⏳ Atualizar paths em scripts movidos
4. ⏳ Atualizar referências em documentação
5. ⏳ Verificar links em documentação
6. ⏳ Atualizar `scripts/README.md` com nova estrutura

---

## 📚 REFERÊNCIAS

- `scripts/README.md` - Documentação oficial de scripts
- `docs/reference/INDICE_SCRIPTS_RELATORIOS.md` - Índice de scripts
- `docs/ORGANIZACAO_DOCUMENTACAO_20251210.md` - Organização de documentação

