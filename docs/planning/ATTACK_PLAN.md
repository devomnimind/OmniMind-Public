# Plano de Ataque - Consolidação OmniMind

## Visão Geral
Este plano foca na consolidação das Fases 19, 20 e 21, garantindo que a documentação e a arquitetura estejam alinhadas antes de prosseguir para novas funcionalidades.

## Prioridades Imediatas (Quick Wins)

- [ ] **Criar Relatórios de Status**:
    - `docs/reports/PHASE19_STATUS.md` (Swarm Intelligence)
    - `docs/reports/PHASE20_STATUS.md` (Autopoiesis)
    - `docs/reports/PHASE21_STATUS.md` (Quantum Consciousness)
- [ ] **Formalizar Regras**:
    - Criar `.github/copilot-instructions.md` com base nas regras atuais.

## Médio Prazo (Próxima Sprint)

- [ ] **Refatoração de Swarm Intelligence**:
    - Avaliar `src/collective_intelligence` vs `src/swarm`.
    - Migrar funcionalidades úteis de `collective_intelligence` para `swarm` (ou vice-versa, definindo o canônico).
    - Remover o módulo obsoleto.
    - Atualizar imports em todo o projeto.

## Longo Prazo (Ongoing)

- [ ] **Pesquisa Quântica**:
    - Manter `src/quantum_consciousness` atualizado com novas descobertas.
    - Tentar aumentar cobertura de testes com simuladores.

## Bloqueadores
- Nenhum bloqueador crítico identificado no momento. Apenas débitos técnicos de organização.
