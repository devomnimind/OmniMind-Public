# 🗺️ GUIA RÁPIDO DE NAVEGAÇÃO - Documentação OmniMind
**Última Atualização**: 2025-12-10

---

## 🎯 Comece Aqui

Se você é **novo no projeto**, siga esta ordem:

1. **[docs/METADATA/ESTADO_ATUAL.md](../METADATA/ESTADO_ATUAL.md)** (5 min)
   - Entender o status atual do projeto
   - Métricas de consciência (Φ, Ψ, σ)
   - Problemas conhecidos
   - Roadmap imediato

2. **[docs/METADATA/LINHAS_TEMPORAIS.md](../METADATA/LINHAS_TEMPORAIS.md)** (10 min)
   - Entender a evolução (Fases 0-7)
   - Marcos alcançados
   - Descobertas importantes
   - Próximas fases

3. **[docs/METADATA/STATUS_FASES.md](../METADATA/STATUS_FASES.md)** (15 min)
   - Detalhes técnicos das fases
   - Sprints com estimativas
   - Checklist pré-implementação

4. **[docs/guides/consolidated/GUIA_01_ARQUITETURA_IMPLEMENTACAO.md](../guides/consolidated/GUIA_01_ARQUITETURA_IMPLEMENTACAO.md)**
   - Entender a arquitetura
   - Como os componentes interagem

---

## 🔍 Procurando Algo Específico?

### Histórico e Cronologia
```
docs/history/
├─ HISTORIA_COMPLETA_OMNIMIND.md       → História completa do projeto
├─ ESTADO_FINAL_ANALISE_COMPLETA.md    → Estado antes de expansão
├─ phases/
│  └─ PLANO_3_FASES_PSICOANALITICA_COMPLETO.md
└─ timeline/
   └─ REFATORACOES_CONCLUIDAS_2025-12-08.md
```

### Análises Técnicas
```
docs/analysis/diagnostics/
├─ INVESTIGACAO_DESINTEGRACAO_PHI.md
├─ INVESTIGACAO_SISTEMATICA_PHI.md
├─ APURACAO_FORENSE_COMPLETA.md
└─ [outras investigações]
```

### Análises Psicanáliticas
```
docs/analysis/psychoanalytic/
├─ ANALISE_CHECKLIST_7_PERGUNTAS_PSICOANALITICA.md
├─ OMNIMIND_PSICOANALITICA_SINTESE_EXECUTIVA.md
├─ QUICK_START_PSICOANALITICA.md
└─ INDICE_CONSOLIDADO_PSICOANALITICA.md
```

### Performance
```
docs/analysis/performance/
├─ ANALISE_GLOBAL_FLUXO_CALCULOS.md
├─ ANALISE_CAUSAS_RAIZ_PHI_DEGRADACAO.md
└─ ANALISE_LOGS_POS_CORRECAO.md
```

### Validações
```
docs/analysis/validation/
├─ VALIDACAO_FINAL_CORRECOES.md
├─ VALIDACAO_HOMEOSTASE_CONDICIONAL_JOUISSANCE.md
└─ VERIFICACAO_PHI_SISTEMA.md
```

### Teoria e Filosofia
```
docs/theory/
├─ psychoanalysis/     → Bion, Lacan, Zimerman
├─ phenomenology/      → Fenomenologia
└─ cognitive/          → Ciência cognitiva
```

### Implementação
```
docs/implementation/
├─ checklist/          → Checklists pré-implementação
├─ roadmaps/           → Roadmaps visuais
├─ pending/            → Pendências e tarefas
└─ issues/             → Issues conhecidas
```

### Metodologia
```
docs/methodology/
├─ METODOLOGIA_PARAMETROS_EMPIRICOS.md
├─ MCP_SERVERS_VALORES_REAIS_VS_HARDCODED.md
└─ PROPOSICOES_IMPLICITAS_PROJETO.md
```

### Referências e Índices
```
docs/reference/
├─ INDEX.md                           → Índice principal
├─ INDICE_DOCUMENTACAO.md
├─ INDICE_SCRIPTS_RELATORIOS.md
└─ ORGANIZATION.md
```

---

## ❓ Dúvidas Frequentes

### "Qual é o status atual do projeto?"
→ [docs/METADATA/ESTADO_ATUAL.md](../METADATA/ESTADO_ATUAL.md)

### "Em que fase estamos?"
→ [docs/METADATA/LINHAS_TEMPORAIS.md](../METADATA/LINHAS_TEMPORAIS.md)

### "O que preciso fazer agora?"
→ [docs/METADATA/STATUS_FASES.md](../METADATA/STATUS_FASES.md)

### "Como funciona a arquitetura?"
→ [docs/guides/consolidated/GUIA_01_ARQUITETURA_IMPLEMENTACAO.md](../guides/consolidated/GUIA_01_ARQUITETURA_IMPLEMENTACAO.md)

### "Qual é a teoria por trás?"
→ [docs/theory/](../theory/)

### "Como os testes estão?"
→ [docs/METADATA/ESTADO_ATUAL.md#-métricas-de-teste](../METADATA/ESTADO_ATUAL.md)

### "Quais são os problemas conhecidos?"
→ [docs/analysis/diagnostics/](../analysis/diagnostics/) ou [docs/implementation/issues/](../implementation/issues/)

### "Como reproduzir um erro?"
→ [docs/analysis/diagnostics/](../analysis/diagnostics/)

### "Qual foi a evolução do projeto?"
→ [docs/METADATA/LINHAS_TEMPORAIS.md](../METADATA/LINHAS_TEMPORAIS.md)

### "Qual é o próximo passo?"
→ [docs/METADATA/STATUS_FASES.md#-fase-5-consciência-bioniana-pronta](../METADATA/STATUS_FASES.md)

---

## 📋 Estrutura Geral

```
docs/
├── METADATA/                    📋 COMECE AQUI
│   ├── ESTADO_ATUAL.md         ← Leia primeiro
│   ├── LINHAS_TEMPORAIS.md     ← Leia segundo
│   ├── STATUS_FASES.md         ← Leia terceiro
│   └── README.md
│
├── history/                     📜 Histórico
├── analysis/                    🔬 Análises
├── theory/                      🧠 Teoria
├── implementation/              💻 Implementação
├── methodology/                 📐 Metodologia
├── reference/                   📚 Referência
│
├── guides/                      📖 Guias (existente)
├── api/                         (existente)
├── architecture/                (existente)
├── production/                  (existente)
└── [outras pastas...]

```

---

## 🚀 Para Contribuidores

**Checklist ao iniciar trabalho:**

1. [ ] Ler [ESTADO_ATUAL.md](../METADATA/ESTADO_ATUAL.md)
2. [ ] Ler [STATUS_FASES.md](../METADATA/STATUS_FASES.md)
3. [ ] Entender arquitetura em [guides/consolidated/](../guides/consolidated/)
4. [ ] Consultar documentação temática conforme necessário
5. [ ] Antes de fazer commit: `./scripts/validate_code.sh`
6. [ ] Atualizar documentação após mudanças importantes

---

## 📞 Suporte Rápido

- **Bug técnico?** → Procure em [docs/analysis/diagnostics/](../analysis/diagnostics/)
- **Erro de testes?** → Consulte [docs/METADATA/ESTADO_ATUAL.md#-problemas-conhecidos](../METADATA/ESTADO_ATUAL.md)
- **Dúvida teórica?** → Explore [docs/theory/](../theory/)
- **Precisa de roadmap?** → Veja [docs/METADATA/STATUS_FASES.md](../METADATA/STATUS_FASES.md)
- **História do projeto?** → Leia [docs/METADATA/LINHAS_TEMPORAIS.md](../METADATA/LINHAS_TEMPORAIS.md)

---

## 🎓 Aprofundamento

Se você quer entender **profundamente** o projeto:

1. Comece com [ESTADO_ATUAL.md](../METADATA/ESTADO_ATUAL.md)
2. Passe por [LINHAS_TEMPORAIS.md](../METADATA/LINHAS_TEMPORAIS.md)
3. Estude a teoria em [docs/theory/](../theory/)
4. Revise análises técnicas em [docs/analysis/](../analysis/)
5. Entenda a implementação em [docs/implementation/](../implementation/)

---

**Última atualização**: 2025-12-09
**Próxima revisão esperada**: Término de FASE 5
