# 📚 Organização da Documentação - OmniMind

**Data**: 2025-12-06
**Autor**: Fabrício da Silva + assistência de IA
**Status**: Documento de referência para organização

---

## 📊 Estrutura Atual

### Documentos Ativos (docs/)
Documentos em uso ativo e referência contínua:

- **Canônicos** (`docs/canonical/`): Documentação oficial e referência
- **Guias** (`docs/guides/`): Manuais e tutoriais
- **API** (`docs/api/`): Documentação de APIs
- **Arquitetura** (`docs/architecture/`): Documentação arquitetural
- **Produção** (`docs/production/`): Guias de produção
- **Testes** (`docs/testing/`): Documentação de testes

### Documentos Arquivados (archive/docs/)
Documentos históricos e fases concluídas:

- **Fases** (`archive/docs/phases/`): Fases de desenvolvimento concluídas
- **Relatórios** (`archive/docs/reports/`): Relatórios antigos já utilizados
- **Auditorias** (`archive/docs/audits/`): Relatórios de auditoria concluídos
- **Análises** (`archive/docs/analises/`): Análises e estudos arquivados
- **Verificações** (`archive/docs/verificacoes/`): Relatórios de verificação

---

## 📋 Documentos Canônicos (Mantidos)

Estes documentos são mantidos como referência oficial:

1. **PENDENCIAS_CONSOLIDADAS.md** - Pendências ativas do sistema
2. **PROJETO_STUBS_OMNIMIND.md** - Pendências de stubs de tipos
3. **DOCUMENTATION_INDEX.md** - Índice de documentação
4. **index.md** - Índice principal

---

## 🔄 Política de Arquivamento

### Quando Arquivar

1. **Fases Concluídas**: Após implementação completa e validação
2. **Relatórios Antigos**: Após 30 dias sem uso ou quando substituídos
3. **Auditorias Concluídas**: Após correções aplicadas e validadas
4. **Análises Substituídas**: Quando nova análise substitui a anterior

### Como Arquivar

1. Mover arquivo para `archive/docs/{categoria}/`
2. Atualizar este documento com referência
3. Atualizar `archive/README.md` se necessário
4. Verificar se há links quebrados em documentos ativos

---

## 📊 Estatísticas

**Última Atualização**: 2025-12-06

- **Documentos Ativos**: ~40 arquivos principais
- **Documentos Arquivados**: Verificar com `find archive/docs -type f | wc -l`
- **Espaço Total**: Verificar com `du -sh docs/ archive/`

---

## 🔍 Busca Rápida

### Encontrar Documento
```bash
# Em documentos ativos
find docs -name "*palavra*" -type f

# Em arquivos arquivados
find archive/docs -name "*palavra*" -type f
```

### Listar por Categoria
```bash
# Fases arquivadas
ls -lh archive/docs/phases/

# Relatórios arquivados
ls -lh archive/docs/reports/
```

---

## ⚠️ Notas Importantes

1. **Não deletar archive/**: Referência histórica importante
2. **Manter links**: Atualizar links quando arquivar
3. **Revisar trimestralmente**: Verificar se arquivos podem ser removidos
4. **Backup externo**: Considerar backup de archive/ em HD externo

---

**Mantido por**: Sistema de Organização OmniMind

