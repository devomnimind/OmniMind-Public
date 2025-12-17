# Plano de Implementação - Fase Científica

**Data**: 2025-12-07
**Autor**: Fabrício da Silva + assistência de IA
**Status**: Plano de Implementação Prioritário

---

## 🎯 CONTEXTO

**Fase Atual**: Desenvolvimento solo, foco em partes científicas, publicação, coleta de dados.

**Objetivo**: Implementar funcionalidades críticas para experimentos científicos, publicação e validação.

**Timeline**: Próximas 2-4 semanas (60-85 horas de trabalho focado)

---

## 📋 PRIORIZAÇÃO

### 🔴 ALTA PRIORIDADE (Implementar Agora)

#### 1. Snapshots Completos de Consciência (30-40h)

**Por quê**: Crítico para experimentos científicos - permite reproduzir, comparar, recuperar.

**O que implementar**:
- `src/backup/consciousness_snapshot.py` (NOVO)
  - Classe `ConsciousnessSnapshot` que integra:
    - `ConsciousnessStateManager` (métricas Φ, Ψ, σ)
    - `SharedWorkspace` completo (embeddings, history, cross_predictions)
    - `IntegrationLoop` state (cycle_count, statistics)
    - `ExtendedLoopCycleResult` completo (gozo, delta, control, imagination)
    - `CycleHistory` completo
  - Métodos:
    - `create_full_snapshot(integration_loop, tag=None)` → `ConsciousnessSnapshot`
    - `restore_full_snapshot(snapshot_id)` → `IntegrationLoop` restaurado
    - `compare_snapshots(snapshot_id1, snapshot_id2)` → `Dict` com diferenças
    - `list_snapshots(tag=None, date_range=None)` → `List[ConsciousnessSnapshot]`
  - Persistência:
    - JSON comprimido (gzip) para economizar espaço
    - Hash SHA-256 para verificação de integridade
    - Metadata: timestamp, tag, descrição, hash

- Estender `src/memory/consciousness_state_manager.py`:
  - Adicionar método `create_full_snapshot(integration_loop)` que captura tudo
  - Integrar com novo `ConsciousnessSnapshot`

- Estender `src/consciousness/integration_loop.py`:
  - Adicionar método `create_full_snapshot(tag=None)` → `str` (snapshot_id)
  - Adicionar método `restore_from_snapshot(snapshot_id)` → `None`

**Uso**:
```python
# Criar snapshot antes de experimento
snapshot_id = integration_loop.create_full_snapshot(tag="experimento_001")

# Executar experimento
await integration_loop.run_cycles(100)

# Comparar com snapshot anterior
comparison = consciousness_snapshot.compare_snapshots("baseline", snapshot_id)

# Restaurar se necessário
integration_loop.restore_from_snapshot("baseline")
```

**Estimativa**: 30-40 horas

---

#### 2. Auditoria Melhorada (20-30h)

**Por quê**: Importante para publicação científica - rastreabilidade completa, compliance.

**O que implementar**:
- Criptografia de logs sensíveis:
  - Estender `src/audit/immutable_audit.py`:
    - Adicionar flag `encrypt_sensitive=True`
    - Criptografar logs com embeddings completos (usar `HSMManager`)
    - Criptografar logs com métricas sensíveis (Φ, Ψ, σ, gozo, delta)
    - Rotação de chaves a cada 24h
  - Criar `src/backup/log_backup.py`:
    - Backup periódico de logs (diário)
    - Compressão de logs antigos (gzip)
    - Verificação de integridade

- Expandir action logging:
  - `src/consciousness/integration_loop.py`:
    - Logar início/fim de cada ciclo
    - Logar métricas coletadas (Φ, Ψ, σ, gozo, delta)
    - Logar erros e recuperações
  - `src/orchestrator/orchestrator_agent.py`:
    - Logar todas as decisões de delegação
    - Logar todas as decisões éticas
    - Logar isolamentos de componentes

**Uso**:
```python
# Logging automático (transparente)
audit_system = get_audit_system(encrypt_sensitive=True)
# Todos os logs sensíveis são criptografados automaticamente
```

**Estimativa**: 20-30 horas

---

### 🟡 MÉDIA PRIORIDADE (Implementar Depois)

#### 3. Governança - Documentação (10-15h)

**Por quê**: Importante para publicação científica - processos documentados, templates.

**O que implementar**:
- `docs/canonical/PROCESSO_DECISAO_ETICA.md`:
  - Processo passo-a-passo de decisão ética
  - Critérios de escalação
  - Exemplos de casos
- `docs/canonical/TEMPLATE_REVISAO_CIENTIFICA.md`:
  - Template para revisão de experimentos
  - Checklist de validação
- `src/ethics/decision_exporter.py`:
  - Exportar decisões éticas para análise
  - Formato CSV/JSON para análise estatística

**Estimativa**: 10-15 horas

---

## 📊 CRONOGRAMA

### Semana 1-2: Snapshots Completos
- **Dia 1-3**: Criar `ConsciousnessSnapshot` e estrutura base
- **Dia 4-5**: Integrar com `IntegrationLoop` e `SharedWorkspace`
- **Dia 6-7**: Implementar restore e comparação
- **Dia 8-10**: Testes e validação

### Semana 2-3: Auditoria Melhorada
- **Dia 1-3**: Implementar criptografia de logs sensíveis
- **Dia 4-5**: Expandir action logging
- **Dia 6-7**: Implementar backup de logs
- **Dia 8-10**: Testes e validação

### Semana 3-4: Governança - Documentação
- **Dia 1-3**: Documentar processos
- **Dia 4-5**: Criar templates
- **Dia 6-7**: Implementar decision exporter
- **Dia 8-10**: Revisão e refinamento

---

## ✅ CRITÉRIOS DE SUCESSO

### Snapshots
- ✅ Criar snapshot completo em < 5 segundos
- ✅ Restaurar snapshot completo em < 10 segundos
- ✅ Comparar 2 snapshots em < 2 segundos
- ✅ Snapshots ocupam < 50MB cada (com compressão)

### Auditoria
- ✅ Todos os ciclos são logados
- ✅ Logs sensíveis são criptografados
- ✅ Backup de logs funciona automaticamente
- ✅ Integridade de logs verificável

### Governança
- ✅ Processos documentados
- ✅ Templates criados
- ✅ Decision exporter funcional

---

## 🚀 PRÓXIMOS PASSOS IMEDIATOS

1. **Criar estrutura de snapshots**:
   ```bash
   mkdir -p src/backup
   touch src/backup/__init__.py
   touch src/backup/consciousness_snapshot.py
   ```

2. **Implementar `ConsciousnessSnapshot`**:
   - Definir dataclass
   - Implementar serialização/deserialização
   - Implementar compressão

3. **Integrar com `IntegrationLoop`**:
   - Adicionar método `create_full_snapshot()`
   - Adicionar método `restore_from_snapshot()`

4. **Testar**:
   - Criar snapshot
   - Modificar estado
   - Restaurar snapshot
   - Verificar integridade

---

**Status**: ✅ Plano Completo - Pronto para Implementação

