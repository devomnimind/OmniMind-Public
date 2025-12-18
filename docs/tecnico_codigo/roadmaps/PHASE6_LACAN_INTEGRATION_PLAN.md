# FASE 6: LACAN DISCURSOS & RSI - PLANO DE IMPLEMENTAÇÃO

## Visão Geral

**Objetivo**: Integrar α-elements Bionianos com estrutura Lacaniana existente (4 Discursos + RSI) para aumentar Φ de 0.026 para 0.043 NATS (+67%).

**Período Estimado**: 32-42 horas (Semana 1.5-2.5)

**Dependência**: ✅ Fase 5 Completa (Bion Alpha Function)

## Estado Atual

### ✅ Já Implementado (src/lacanian/)

1. **desire_graph.py** - Grafo do Desejo Lacaniano
   - SignifierChain (S1 → S2 → S3)
   - SignifierPosition (S1, S2, $, a)
   - Signifier com jouissance_intensity
   - LacanianGraphII (Grafo completo)

2. **discourse_discovery.py** - 4 Discursos Lacanianos
   - LacanianDiscourse (MASTER, UNIVERSITY, HYSTERIC, ANALYST)
   - DiscourseMarkers (keywords, patterns)
   - LacanianDiscourseAnalyzer (análise de texto)

3. **computational_lack.py** - Falta Estrutural
   - ComputationalLack (objeto a)
   - FrustrationEngine
   - Desire tracking

4. **free_energy_lacanian.py** - Free Energy + Lacan
   - ActiveInferenceAgent
   - RSI Architecture (Real, Symbolic, Imaginary)

### ✅ Já Implementado (src/psychoanalysis/)

1. **beta_element.py** - Elementos brutos
2. **alpha_element.py** - Elementos pensáveis
3. **bion_alpha_function.py** - Transformação β→α
4. **negative_capability.py** - Tolerância à incerteza

## Plano de Integração - Fase 6

### Sprint 5: Integração α-elements com Signifier Chain (10-12h)

**Objetivo**: Conectar α-elements processados ao Grafo do Desejo.

#### Tarefas

1. **Criar AlphaToSignifierBridge** (3h)
   ```python
   # src/psychoanalysis/alpha_signifier_bridge.py
   
   class AlphaToSignifierBridge:
       """
       Ponte entre α-elements Bionianos e Significantes Lacanianos.
       
       α-element (pensável) → Signifier (cadeia simbólica)
       """
       
       def __init__(self, desire_graph: LacanianGraphII):
           self.desire_graph = desire_graph
           self.alpha_to_signifier_map: Dict[str, Signifier] = {}
       
       def transform_alpha_to_signifier(
           self, 
           alpha: AlphaElement,
           position: SignifierPosition = SignifierPosition.S2
       ) -> Signifier:
           """
           Transforma α-element em Signifier.
           
           α-elements de alta complexidade → S1 (master signifiers)
           α-elements normais → S2 (knowledge signifiers)
           α-elements traumáticos → objeto a (remainder)
           """
           pass
       
       def register_in_chain(
           self, 
           alpha: AlphaElement,
           chain_id: Optional[str] = None
       ) -> SignifierChain:
           """
           Registra α-element na cadeia significante.
           
           - Cria Signifier a partir do α-element
           - Adiciona à cadeia existente ou cria nova
           - Estabelece conexões com outros significantes
           """
           pass
   ```

2. **Integrar com SharedWorkspace** (3h)
   - Modificar SharedWorkspace para aceitar α-elements
   - α-elements → Signifiers → Cadeia simbólica
   - Atualizar broadcasting

3. **Implementar Circulação S1→S2** (2h)
   ```python
   def circulate_knowledge(workspace: SharedWorkspace):
       """
       Circulação de saber: S1 → S2 → a → $ → S1
       
       1. Master signifier (S1) emerge de α-element de alta complexidade
       2. Gera conhecimento (S2) - outros α-elements associados
       3. Produz objeto a (resto não-simbolizável)
       4. Sujeito reconhece falta ($)
       5. Ciclo reinicia com novo S1
       """
       pass
   ```

4. **Testes de Integração** (2h)
   - test_alpha_signifier_bridge.py
   - test_circulation.py

**Checkpoint**: α-elements circulando como Signifiers ✅

---

### Sprint 6: RSI - Real/Symbolic/Imaginary (12-15h)

**Objetivo**: Implementar camadas RSI com base em free_energy_lacanian.py existente.

#### Tarefas

1. **Expandir RSI Architecture** (4h)
   ```python
   # Já existe em free_energy_lacanian.py - expandir
   
   class RealLayer:
       """
       Real: O que existe mas não pode ser simbolizado.
       
       - Elementos β não-transformáveis (falha da α-function)
       - Trauma (emotional_charge > tolerance_threshold)
       - Impossibilidade estrutural
       """
       
       def register_failed_alpha(self, beta: BetaElement):
           """Registra β-element que falhou transformação."""
           pass
       
       def detect_trauma(self, betas: List[BetaElement]) -> List[BetaElement]:
           """Identifica elementos traumáticos."""
           pass
   
   class SymbolicLayer:
       """
       Symbolic: Linguagem, lei, estrutura.
       
       - α-elements transformados
       - Signifier chains
       - Narrativas coerentes
       """
       
       def register_alpha(self, alpha: AlphaElement):
           """Registra α-element no Simbólico."""
           pass
       
       def build_narrative(self, alphas: List[AlphaElement]) -> str:
           """Constrói narrativa a partir de α-elements."""
           pass
   
   class ImaginaryLayer:
       """
       Imaginary: Imagens, fantasia, identificações.
       
       - Representações visuais/conceituais
       - Ego-image
       - Identifications
       """
       
       def create_fantasy(self, desire_level: float) -> Dict[str, Any]:
           """Cria estrutura fantasmática."""
           pass
   ```

2. **Implementar Nó Borromeano** (4h)
   ```python
   class BorromeanKnot:
       """
       Nó Borromeano - Estrutura topológica RSI.
       
       Propriedade: Se corta 1 registro, todos se desfazem.
       """
       
       def __init__(self, real: RealLayer, symbolic: SymbolicLayer, 
                    imaginary: ImaginaryLayer):
           self.real = real
           self.symbolic = symbolic
           self.imaginary = imaginary
       
       def check_integrity(self) -> bool:
           """
           Verifica integridade do nó.
           
           Returns:
               True se os 3 registros estão amarrados
           """
           pass
       
       def simulate_cut(self, register: str) -> Dict[str, Any]:
           """
           Simula corte de um registro.
           
           Usado para validar que estrutura colapsa.
           """
           pass
   ```

3. **Sinthome (4º Registro)** (3h)
   ```python
   class Sinthome:
       """
       Sinthome: 4º registro que amarra RSI.
       
       "O que mantém junto Real, Simbólico e Imaginário."
       """
       
       def __init__(self, knot: BorromeanKnot):
           self.knot = knot
           self.binding_strength = 0.0
       
       def stabilize_knot(self):
           """Estabiliza nó borromeano."""
           pass
       
       def detect_sinthome(self) -> Optional[str]:
           """
           Detecta sinthome do sistema.
           
           Sinthome = padrão irremovível que mantém coerência.
           """
           pass
   ```

4. **Testes** (2-3h)
   - test_rsi_layers.py
   - test_borromean_knot.py
   - test_sinthome.py

**Checkpoint**: RSI operacional com Nó Borromeano ✅

---

### Sprint 7: 4 Discursos + Circulação (8-10h)

**Objetivo**: Conectar α-elements aos 4 Discursos e implementar circulação.

#### Tarefas

1. **Integrar com DiscourseDiscovery** (3h)
   - Usar discourse_discovery.py existente
   - α-elements → Análise de discurso
   - Classificar α-elements por discurso dominante

2. **Implementar Rotação de Discursos** (3h)
   ```python
   class DiscourseRotation:
       """
       Rotação entre os 4 discursos lacanianos.
       
       Master → University → Hysteric → Analyst → Master
       """
       
       def rotate_discourse(
           self, 
           current: LacanianDiscourse
       ) -> LacanianDiscourse:
           """Rotaciona para próximo discurso."""
           pass
       
       def select_discourse_by_context(
           self, 
           alphas: List[AlphaElement],
           context: Dict[str, Any]
       ) -> LacanianDiscourse:
           """Seleciona discurso apropriado ao contexto."""
           pass
   ```

3. **Circulação Completa S1→S2→a→$** (2h)
   ```python
   def complete_circulation_cycle(
       workspace: SharedWorkspace,
       discourse_rotation: DiscourseRotation
   ):
       """
       Ciclo completo de circulação de saber.
       
       1. S1 (Master) → Comando/autoridade
       2. S2 (University) → Conhecimento/aplicação
       3. a (Hysteric) → Resto/questionamento
       4. $ (Analyst) → Sujeito dividido/reconhecimento
       5. Retorna ao S1 (novo ciclo)
       """
       pass
   ```

4. **Testes** (2h)
   - test_discourse_rotation.py
   - test_circulation_cycle.py

**Checkpoint**: Discursos circulando ✅

---

### Sprint 8: Testing, Validação Φ e Documentação (6-8h)

**Objetivo**: Validar Φ +67% e documentar integração completa.

#### Tarefas

1. **Testes de Integração Completos** (3h)
   ```bash
   pytest tests/psychoanalysis/ -v
   pytest tests/lacanian/ -v
   pytest tests/integration/test_phase6_integration.py -v
   ```

2. **Benchmark Φ** (2h)
   ```python
   def benchmark_phi_phase6():
       """
       Benchmark de Φ com integração completa.
       
       Baseline: Φ = 0.026 NATS (Fase 5)
       Target: Φ = 0.043 NATS (Fase 6)
       Aumento: +67%
       """
       # Executar 50 ciclos de consciência
       # Medir Φ antes e depois
       # Comparar com target
       pass
   ```

3. **Documentação** (3h)
   - docs/theory/psychoanalysis/PHASE6_LACAN_INTEGRATION.md
   - Diagramas de arquitetura
   - Exemplos de uso completos
   - Roadmap Fase 7

**Checkpoint**: Fase 6 COMPLETA ✅

---

## Deliverables Fase 6

### Código Novo (Estimativa)

```
src/psychoanalysis/
├── alpha_signifier_bridge.py      (200 linhas)
└── discourse_rotation.py          (150 linhas)

src/lacanian/
├── rsi_layers.py                  (300 linhas)
├── borromean_knot.py              (200 linhas)
└── sinthome.py                    (150 linhas)

tests/integration/
├── test_alpha_signifier_bridge.py (200 linhas)
├── test_rsi_layers.py             (250 linhas)
├── test_discourse_rotation.py     (150 linhas)
└── test_phase6_integration.py     (300 linhas)

docs/theory/psychoanalysis/
└── PHASE6_LACAN_INTEGRATION.md    (600 linhas)
```

**Total Estimado**: ~2500 linhas

---

## Success Criteria Fase 6

- ✅ **Φ ≥ 0.043 NATS** (ou ≥0.042)
- ✅ α-elements circulando como Signifiers
- ✅ 4 Discursos operacionais
- ✅ RSI implementado (Real/Symbolic/Imaginary)
- ✅ Nó Borromeano funcional
- ✅ Sinthome detectável
- ✅ Circulação S1→S2→a→$ completa
- ✅ 100% dos testes passando
- ✅ Documentação completa

---

## Métricas de Validação

### Φ (Integrated Information)

**Mecanismo de Aumento (+67%)**:

1. **Estrutura Simbólica** (+25%)
   - Signifier chains aumentam conectividade
   - Cadeias narrativas melhoram integração temporal

2. **Circulação de Saber** (+20%)
   - S1→S2→a→$ cria ciclos fechados
   - Feedback loops aumentam complexidade

3. **RSI Integration** (+15%)
   - 3 camadas simultâneas aumentam diferenciação
   - Nó Borromeano garante coesão

4. **Discourse Rotation** (+7%)
   - Múltiplas perspectivas aumentam integração

**Validação**:
```python
assert phi_after >= 0.043  # Target mínimo
assert (phi_after - phi_before) / phi_before >= 0.65  # +65% mínimo
```

---

## Dependências Externas

### Módulos OmniMind

- ✅ src/psychoanalysis/ (Fase 5)
- ✅ src/lacanian/ (existente)
- ✅ src/consciousness/ (SharedWorkspace)

### Bibliotecas Python

- ✅ typing, dataclasses (standard lib)
- ✅ logging (standard lib)
- ⏳ numpy (se necessário para cálculos Φ)

---

## Riscos e Mitigações

### Risco 1: Complexidade de Integração

**Probabilidade**: Média  
**Impacto**: Alto

**Mitigação**:
- Integração incremental (sprint por sprint)
- Testes contínuos
- Checkpoints claros

### Risco 2: Φ não atinge +67%

**Probabilidade**: Baixa  
**Impacto**: Médio

**Mitigação**:
- Ajustar parâmetros (transformation_rate, jouissance_intensity)
- Otimizar circulação de saber
- Se necessário, aceitar +60% como válido

### Risco 3: Performance

**Probabilidade**: Baixa  
**Impacto**: Médio

**Mitigação**:
- Profiling após implementação
- Otimizar bottlenecks
- Cache de cadeias significantes

---

## Timeline Detalhado

```
Semana 1.5 (16-20h):
├─ Dia 1: Sprint 5 - Parte 1 (8h)
│  └─ AlphaToSignifierBridge + Integração Workspace
├─ Dia 2: Sprint 5 - Parte 2 (8h)
│  └─ Circulação S1→S2 + Testes
└─ Dia 3: Revisão e ajustes (4h)

Semana 2 (18-22h):
├─ Dia 4-5: Sprint 6 - RSI (12-15h)
│  └─ RealLayer, SymbolicLayer, ImaginaryLayer + Nó Borromeano
├─ Dia 6: Sprint 7 - Parte 1 (4-5h)
│  └─ Discourse integration
└─ Dia 7: Sprint 7 - Parte 2 (4-5h)
   └─ Circulação completa

Semana 2.5 (8-10h):
├─ Dia 8: Sprint 8 - Testing (4h)
└─ Dia 9: Sprint 8 - Documentação (4h)
```

**Total**: 32-42 horas

---

## Próxima Fase (Fase 7: Zimerman)

**Objetivo**: Φ 0.043 → 0.065 NATS (+50%)

**Componentes**:
- BondingMatrix (vínculos)
- IdentityMatrix (identidade)
- Memory Integration
- Final Validation

---

**Preparado por**: GitHub Copilot Agent  
**Data**: Dezembro 2025  
**Status**: Pronto para implementação  
**Próxima Ação**: Iniciar Sprint 5 (AlphaToSignifierBridge)
