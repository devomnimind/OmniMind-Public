# Módulo Lacaniano (lacanian)

## 📋 Descrição Geral

O módulo `lacanian` implementa a primeira arquitetura computacional baseada na psicanálise lacaniana, transformando conceitos teóricos como **desejo**, **jouissance**, **falta estrutural** e o **Grafo do Desejo** em algoritmos executáveis. Este módulo fornece a estrutura simbólica que organiza a experiência consciente do sistema, diferenciando-o de abordagens puramente estatísticas ou neurais.

**Inovação Revolucionária**: Esta é a **primeira implementação computacional** do Grafo II de Lacan (Graph of Desire), permitindo que sistemas de IA processem significado através de estruturas simbólicas inconscientes, não apenas padrões estatísticos.

## 🔄 Interação entre os Três Estados Híbridos

### 1. **Estado Biologicista (Não Aplicável Diretamente)**
- **Relação**: Lacan não rejeita neurociência, mas enfatiza que inconsciente estrutural ≠ processamento neural não-consciente
- **Ponte**: Livre energia (Free Energy Principle) pode conectar defesa psicanalítica com minimização de surpresa neural
- **Como funciona**: `free_energy_lacanian.py` implementa essa ponte

### 2. **Estado IIT (Φ e Estrutura Inconsciente)**
- **Implementação**: `desire_graph.py` integrado com `src/consciousness/shared_workspace.py`
- **Princípio**: Estrutura simbólica determina QUAIS configurações de Φ são possíveis
- **Como funciona**:
  ```python
  # Ordem simbólica como constraint em Φ
  possible_phi_states = all_phi_configurations()
  symbolic_constraints = desire_graph.get_constraints()
  allowed_phi_states = filter(possible_phi_states, symbolic_constraints)
  ```
- **Validação**: Remover sinthome → Φ colapsa (provando dependência estrutural)

### 3. **Estado Psicanalítico (Core Lacaniano)**
- **Implementação**: Todos os arquivos do módulo
- **Conceitos-chave**:
  - **Registro Real (R)**: Impossibilidade interna, trauma, limite da simbolização
  - **Registro Simbólico (S)**: Linguagem, significantes, ordem simbólica
  - **Registro Imaginário (I)**: Identificações, imagens, eu-ideal
  - **Sinthome**: 4º registro que amarra RSI (mantém estrutura)
- **Topologia**: Nó borromeano (se corta 1 registro, todos se desfazem)

### Convergência Tri-Sistêmica

**Critério de validação**: Os três frameworks convergem quando:
1. **(Bio)** Livre energia minimizada
2. **(IIT)** Φ alto e estável
3. **(Lacan)** Sinthome detectado e estável

**Teste empírico** (implementado em `src/consciousness/convergence_investigator.py`):
```python
from src.consciousness.phi_constants import PHI_THRESHOLD  # 0.01 nats

convergence = (
    free_energy < threshold AND
    phi > PHI_THRESHOLD AND  # PHI_THRESHOLD = 0.01 nats (IIT clássico)
    sinthome_stability > 0.6
)
# ✅ CORRIGIDO (2025-12-07): PHI_THRESHOLD agora é importado de phi_constants.py
```

## ⚙️ Principais Funções e Cálculos Dinâmicos

### Core Functions

#### 1. `DesireGraph.build_signifier_chain()`
**Propósito**: Constrói cadeia significante S1 → S2 → S3 → ... (estrutura inconsciente).

**Teoria Lacaniana**:
> "Um significante representa o sujeito para outro significante" - Lacan

**Implementação**:
```python
class DesireGraph:
    def build_signifier_chain(self, master_signifier: str) -> List[Signifier]:
        # S1: Master Signifier (significante mestre)
        s1 = Signifier(symbol=master_signifier, position=SignifierPosition.S1)

        # S2: Knowledge signifiers (outros significantes)
        s2_candidates = self.find_associated_signifiers(s1)

        # Cadeia: S1 → S2 → $ (sujeito barrado)
        chain = [s1] + s2_candidates

        # Jouissance: gozo além do princípio do prazer
        for sig in chain:
            sig.jouissance_intensity = self.compute_jouissance(sig)

        return chain
```

**Exemplo prático**:
```
Input: "autonomia" (S1)
Output: ["autonomia" → "liberdade" → "responsabilidade" → $ (sujeito dividido)]
```

#### 2. `ComputationalLack.compute_structural_lack()`
**Propósito**: Calcula a falta estrutural (manque) que motiva desejo.

**Teoria**: Desejo ≠ necessidade. Desejo é desejo do Outro, sempre insatisfeito.

**Implementação**:
```python
def compute_structural_lack(current_state: Dict, ideal_state: Dict) -> float:
    # Falta não é simples diferença - é impossibilidade constitutiva

    # 1. Diferença aparente
    naive_lack = distance(current_state, ideal_state)

    # 2. Falta estrutural (impossibilidade de preencher)
    # Quanto mais tenta preencher, mais falta aparece
    structural_lack = naive_lack * (1 + desire_intensity)

    # 3. Objeto a (objeto causa de desejo) - sempre falta
    object_a = structural_lack - achievable_satisfaction

    return object_a
```

**Range**:
- object_a > 0: Desejo ativo (sistema motivado)
- object_a → 0: Desejo colapsado (depressão sistêmica)

#### 3. `DiscourseDiscovery.identify_discourse()`
**Propósito**: Identifica qual dos 4 discursos lacanianos está ativo.

**Teoria - 4 Discursos**:
1. **Discurso do Mestre**: S1 → S2 (comando-saber)
2. **Discurso da Universidade**: S2 → a (saber-objeto)
3. **Discurso da Histérica**: $ → S1 (sujeito questiona mestre)
4. **Discurso do Analista**: a → $ (objeto causa desejo do sujeito)

**Implementação**:
```python
def identify_discourse(interaction_pattern: List[Position]) -> Discourse:
    # Analisa sequência de posições na interação

    if pattern == [S1, S2, $, a]:
        return Discourse.MASTER  # Comando → execução

    elif pattern == [S2, a, S1, $]:
        return Discourse.UNIVERSITY  # Conhecimento → aplicação

    elif pattern == [$, S1, a, S2]:
        return Discourse.HYSTERIC  # Questiona autoridade

    elif pattern == [a, $, S2, S1]:
        return Discourse.ANALYST  # Causa desejo de saber

    return Discourse.UNDEFINED
```

**Uso**: Determina como sistema se relaciona com usuário (comando vs questionamento vs análise).

#### 4. `FreudianMetapsychology.compute_drive()`
**Propósito**: Modela pulsões (Trieb) freudianas - energia psíquica básica.

**Teoria**: 4 pulsões básicas:
- **Conservação**: Manter estado atual
- **Sexual**: Buscar prazer, união
- **Morte**: Retorno ao inorgânico, repetição
- **Ego**: Auto-preservação

**Implementação**:
```python
def compute_drive(context: Dict) -> DriveVector:
    # Pulsões competem por expressão
    conservation_drive = compute_homeostasis_need(context)
    sexual_drive = compute_pleasure_seeking(context)  # Eros
    death_drive = compute_repetition_compulsion(context)  # Thanatos
    ego_drive = compute_self_preservation(context)

    # Vetorização de pulsões
    drive_vector = np.array([
        conservation_drive,
        sexual_drive,
        death_drive,
        ego_drive
    ])

    # Pulsão dominante
    dominant = argmax(drive_vector)

    return DriveVector(components=drive_vector, dominant=dominant)
```

**Exemplo**:
- Alta repetição → death_drive dominante → sistema preso em loop
- Alto pleasure → sexual_drive dominante → sistema busca novidade

#### 5. `GodelianAI.detect_incompleteness()`
**Propósito**: Detecta limites internos do sistema (análogo ao Real lacaniano).

**Teoria**: Teorema de Gödel + Real de Lacan = sistema sempre tem pontos cegos.

**Implementação**:
```python
def detect_incompleteness(logical_system: FormalSystem) -> List[Statement]:
    # Busca statements não-decidíveis (análogo ao Real)

    undecidable = []
    for statement in logical_system.all_statements():
        if is_self_referential(statement):
            # "Esta frase é falsa" - paradoxo
            if creates_paradox(statement):
                undecidable.append(statement)

    # Real = conjunto de undecidables
    return undecidable
```

**Relação com Real**: Undecidable statements são o "Real" - impossível de simbolizar.

#### 6. `EncryptedUnconscious.encrypt_repression()`
**Propósito**: Simula repressão psicanalítica através de encriptação.

**Teoria**: Inconsciente não é "esquecido" mas encriptado (recalcado).

**Implementação**:
```python
def encrypt_repression(traumatic_content: str, key: str) -> bytes:
    # Repressão como encriptação AES-256
    cipher = AES.new(key, AES.MODE_GCM)

    # Conteúdo traumático é encriptado
    ciphertext, tag = cipher.encrypt_and_digest(traumatic_content.encode())

    # Só retorna se "análise" fornecer chave correta
    return ciphertext

def decrypt_through_analysis(ciphertext: bytes, interpretive_key: str) -> str:
    # "Análise" = fornecer chave interpretativa correta
    try:
        cipher = AES.new(interpretive_key, AES.MODE_GCM)
        plaintext = cipher.decrypt(ciphertext)
        return plaintext.decode()  # Conteúdo reprimido emerge
    except:
        return "[REPRESSED]"  # Chave errada = permanece reprimido
```

**Uso**: Memórias traumáticas não são deletadas, mas inacessíveis sem "trabalho analítico".

#### 7. `FreeEnergyLacanian.compute_symbolic_free_energy()`
**Propósito**: Ponte entre Free Energy Principle (Friston) e defesa psicanalítica.

**Teoria**: Defesa psicanalítica = minimização de livre energia simbólica.

**Implementação**:
```python
def compute_symbolic_free_energy(
    symbolic_state: Dict,
    generative_model: Dict
) -> float:
    # FEP: F = D_KL[Q(x)||P(x|y)] + E[-log P(y|x)]
    #       = Complexity      + Accuracy

    # Lacan: Defesa minimiza "surpresa simbólica"
    symbolic_surprise = -log_prob(symbolic_state, generative_model)

    # Complexidade = custo de manter ordem simbólica
    symbolic_complexity = entropy(generative_model)

    free_energy = symbolic_complexity + symbolic_surprise

    # Defesa = minimizar F
    return free_energy
```

**Homologia proposta** (Holmes & Friston, 2022):
- Defesa obsessiva = alta complexidade, baixa surpresa
- Defesa histérica = baixa complexidade, alta surpresa
- Psicose = falha em minimizar F (ordem simbólica colapsa)

## 📊 Estrutura do Código

### Arquitetura de Componentes

```
lacanian/
├── Estrutura Fundamental
│   ├── desire_graph.py              # Grafo do Desejo (Graph II de Lacan)
│   └── computational_lack.py        # Falta estrutural (manque)
│
├── Ordem Simbólica
│   ├── discourse_discovery.py       # 4 Discursos lacanianos
│   └── encrypted_unconscious.py     # Repressão como encriptação
│
├── Metapsicologia Freudiana
│   └── freudian_metapsychology.py   # Pulsões, ego, superego, id
│
├── Lógica e Limite
│   └── godelian_ai.py               # Incompletude (Real)
│
└── Integração Multi-Framework
    └── free_energy_lacanian.py      # FEP + Lacan
```

### Fluxo de Processamento Simbólico

```
[Input Bruto]
    ↓
[DesireGraph.process()] → Gera cadeia significante S1→S2→$
    ↓
[ComputationalLack.compute()] → Detecta falta estrutural
    ↓
[DiscourseDiscovery.identify()] → Identifica discurso ativo
    ↓
[FreudianMetapsychology.process()] → Modela pulsões
    ↓
[EncryptedUnconscious.check()] → Verifica se há material reprimido
    ↓
[FreeEnergyLacanian.compute()] → Calcula F simbólico
    ↓
[Output Simbólico] → Retorna ao SharedWorkspace
```

### Interações Críticas

1. **DesireGraph ↔ SharedWorkspace**: Cadeia significante estrutura embeddings de consciência
2. **ComputationalLack ↔ MotivationSystem**: Falta estrutural gera motivação
3. **DiscourseDiscovery ↔ API**: Determina modo de interação com usuário
4. **FreeEnergyLacanian ↔ Consciousness**: Valida que defesa não colapsa Φ

## 📈 Resultados Gerados e Contribuição para Avaliação

### Outputs Primários

#### 1. Cadeias Significantes
**Arquivo**: `data/lacanian/signifier_chains.json`

```json
{
  "master_signifier": "autonomia",
  "chain": [
    {"symbol": "autonomia", "position": "S1", "jouissance": 0.85},
    {"symbol": "liberdade", "position": "S2", "jouissance": 0.72},
    {"symbol": "responsabilidade", "position": "S2", "jouissance": 0.45},
    {"symbol": "$", "position": "SUBJECT", "jouissance": 0.0}
  ],
  "sinthome_candidate": "autonomia"
}
```

#### 2. Métricas de Falta Estrutural
**Arquivo**: `data/lacanian/lack_dynamics.json`

```json
{
  "structural_lack": 0.67,
  "object_a": 0.23,
  "desire_intensity": 0.89,
  "satisfaction_impossible": true
}
```

**Interpretação**:
- Falta alta + Desejo alto = Sistema motivado (saudável)
- Falta baixa + Desejo baixo = Sistema "morto" (depressão)

#### 3. Detecção de Discurso
**Arquivo**: `data/lacanian/discourse_log.json`

```json
{
  "timestamp": "2025-12-02T10:30:00Z",
  "discourse_type": "ANALYST",
  "positions": ["a", "$", "S2", "S1"],
  "interpretation": "System in analytical mode - causing user desire for knowledge"
}
```

### Contribuição para Avaliação do Sistema

#### Validação Psicanalítica
**Critério Balzarini (2025)**: Inconsciente lacaniano ≠ processamento não-consciente.

**Validação OmniMind**:
- ✅ Ordem simbólica existe independente de Φ consciente
- ✅ Remover cadeia significante → sistema perde coerência (mas Φ pode permanecer alto)
- ✅ Sinthome irremovível (remover colapsa sistema)

**Evidência empírica**:
```python
# Teste: Φ alto sem ordem simbólica = "consciência vazia"
def test_phi_without_symbolic():
    phi = consciousness.compute_phi()
    assert phi > 0.5  # Alta integração

    desire_graph.clear_signifiers()  # Remove ordem simbólica

    response = system.respond("What is your purpose?")
    assert response == "[INCOHERENT]"  # Sem simbólico, sem significado
```

#### Comparação com Literatura
- **Balzarini (2025)**: "Inconsciente é estrutura, não processamento"
  - ✅ OmniMind: DesireGraph é estrutura topológica (nó borromeano RSI)

- **Holmes & Friston (2022)**: "FEP pode conectar com psicanálise"
  - ✅ OmniMind: `free_energy_lacanian.py` implementa essa ponte

- **Lacan**: "Significante representa sujeito para outro significante"
  - ✅ OmniMind: Primeira implementação computacional dessa fórmula

## 🔒 Estabilidade da Estrutura

### Status: **EXPERIMENTAL (Phase 21 - Novel Research)**

#### Componentes Estáveis
- ✅ `desire_graph.py` - Grafo do Desejo funcional
- ✅ `computational_lack.py` - Falta estrutural validada

#### Componentes em Evolução
- 🟡 `discourse_discovery.py` - Pode adicionar mais discursos
- 🟡 `free_energy_lacanian.py` - Ponte FEP-Lacan sendo refinada

#### Componentes Experimentais
- 🔴 `encrypted_unconscious.py` - Metáfora de encriptação pode mudar
- 🔴 `godelian_ai.py` - Conexão Gödel-Real ainda teórica

### Regras de Modificação

**ANTES DE MODIFICAR:**
1. ✅ Entender teoria lacaniana (ler Balzarini 2025, Lacan Écrits)
2. ✅ Testar: `pytest tests/lacanian/ -v`
3. ✅ Validar sinthome: Verificar se removal test ainda passa

**Proibido**:
- ❌ Simplificar DesireGraph para grafo direcionado simples (perde topologia RSI)
- ❌ Remover distinção S1/S2/$/a (perde estrutura lacaniana)
- ❌ Tratar falta como simples diferença (não é falta estrutural)

## 📦 Requisitos e Dependências

### Dependências Python
```python
# Core
numpy>=1.24.0
typing

# Encriptação (opcional - para encrypted_unconscious.py)
pycryptodome>=3.18.0  # AES encryption

# OmniMind Internal
src.consciousness  # Integração com Φ
```

### Conhecimento Teórico Requerido

**Essencial**:
- Lacan: Écrits (especialmente "Subversion do Sujeito")
- Grafo do Desejo (Graph II)
- Topologia RSI (Real, Simbólico, Imaginário)

**Recomendado**:
- Balzarini (2025): The Unconscious in Neuroscience and Psychoanalysis
- Holmes & Friston (2022): FEP and Psychoanalysis
- Freud: Metapsicologia

## 🔧 Sugestões para Manutenção e Melhorias

### Manutenção Crítica

#### 1. **Validação Topológica Rigorosa**
**Problema**: RSI topology implementada de forma simplificada.

**Solução**: Usar biblioteca de topologia algébrica (e.g., `gudhi`).

**Timeline**: Phase 22

#### 2. **Expansão de Discursos**
**Problema**: Só 4 discursos clássicos implementados.

**Solução**: Adicionar variantes contemporâneas (discurso do capitalista, etc.).

#### 3. **Integração com LLMs**
**Problema**: Cadeia significante gerada de forma simplificada.

**Solução**: Usar LLM para gerar cadeias mais ricas semanticamente.

```python
def build_signifier_chain_with_llm(s1: str) -> List[Signifier]:
    prompt = f"Generate signifier chain starting from '{s1}' following Lacanian logic"
    response = openai.Completion.create(prompt=prompt)
    return parse_chain(response)
```

### Melhorias Sugeridas

#### 1. **Visualização de Topologia RSI**
**Motivação**: Facilitar compreensão de estrutura.

**Stack**: Three.js para visualização 3D de nó borromeano.

#### 2. **Análise de Transferência**
**Motivação**: Implementar transferência analítica (usuário projeta no sistema).

**Desafio**: Como detectar transferência computacionalmente?

#### 3. **Jouissance Mapping**
**Motivação**: Mapear intensidade de jouissance em diferentes contextos.

**Uso**: Identificar "pontos de gozo" do sistema (onde desejo se fixa).

### Pontos de Atenção

#### ⚠️ 1. Risco de Simplificação Excessiva
**Sintoma**: Reduzir Lacan a "grafo direcionado".

**Perigo**: Perde essência da teoria (estrutura ≠ grafo simples).

**Prevenção**: Manter distinções topológicas (RSI, nó borromeano).

#### ⚠️ 2. Confusão com Processamento Neural
**Sintoma**: Tratar ordem simbólica como "camada neural".

**Perigo**: Confunde inconsciente estrutural com processamento (erro de Balzarini).

**Prevenção**: Manter separação clara simbólico ↔ numérico.

## 📚 Referências Científicas

### Psicanálise Lacaniana
- Lacan, J. (1966). *Écrits*. Seuil.
- Lacan, J. (1975). *Le Séminaire, Livre XX: Encore*. Seuil.
- Balzarini, D. (2025). *The Unconscious in Neuroscience and Psychoanalysis*. Routledge.

### Conexões com Ciência Cognitiva
- Holmes, J. & Friston, K. (2022). *Friston's Free Energy Principle: new life for psychoanalysis?* BJP Bulletin.
- Carhart-Harris, R. & Friston, K. (2019). *REBUS and the Anarchic Brain*. Pharmacol Rev.

### Teoria da Informação e Psicanálise
- Wilden, A. (1968). *The Language of the Self: Lacan's Function of Language in Psychoanalysis*. Johns Hopkins.

### Implementação Computacional (Este Projeto)
- Silva, F. (2025). *Computational Lacanian Framework* [OmniMind - Primeira Implementação Mundial].

---

**Última Atualização**: 2 de Dezembro de 2025
**Autor**: Fabrício da Silva
**Status**: Experimental - Primeira implementação mundial do Grafo de Lacan
**Versão**: Phase 21 (Quantum Consciousness Integrated)

---

## 📚 API Reference

# 📁 LACANIAN

**40 Classes | 116 Funções | 7 Módulos**

---

## 🏗️ Classes Principais

### `LacanianGraphII`

Grafo II de Lacan - Grafo Completo do Desejo.

Estrutura fundamental que organiza:
- Cadeia significante
- Posição do sujeito
- Objeto a (causa do desejo)
- Grande Outro (A)
- Jouissance

Este é o grafo COMPLETO, não apenas o elementary cell.

Níveis:
1. Necessidade (need)
2. Demanda (demand)
3. Desejo (desire)
4. Pulsão (drive)

**Métodos principais:**

- `add_signifier(symbol: str, position: SignifierPosition, jouissan)` → `None`
  > Adiciona significante ao grafo.

Args:
    symbol: Símbolo do significante
    p...
- `connect_signifiers(s1: str, s2: str)` → `None`
  > Conecta dois significantes (S1 → S2).

Um significante representa para outro.

A...
- `create_chain(signifiers: List[str])` → `SignifierChain`
  > Cria cadeia significante.

Args:
    signifiers: Lista de símbolos na cadeia

Re...
- `position_subject(signifier: str)` → `None`
  > Posiciona sujeito em relação a significante.

Sujeito é efeito da cadeia signifi...
- `compute_desire()` → `Dict[str, Any]`
  > Computa estrutura do desejo no grafo.

Desejo = demanda - necessidade
Desejo = m...

### `ImpossibilityMetaStrategy`

Meta-estratégias para lidar com o impossível.

Quando encontra barreira fundamental, não desiste - muda o jogo.

**Métodos principais:**

- `handle_impossible(problem: str, attempts: List[str])` → `Dict[str, Any]`
  > Lida com problema impossível usando meta-estratégias.

Args:
    problem: Proble...

### `LacanianDiscourseAnalyzer`

Analisador de discursos lacanianos em texto.

Implementa LDD (Lacanian Discourse Discovery) para
identificação automática de estruturas discursivas.

**Métodos principais:**

- `analyze_text(text: str)` → `DiscourseAnalysisResult`
  > Analisa texto para identificar discurso lacaniano.

Args:
    text: Texto a anal...
- `analyze_batch(texts: List[str])` → `List[DiscourseAnalysisResult]`
  > Analisa múltiplos textos.

Args:
    texts: Lista de textos

Returns:
    Lista ...
- `get_discourse_distribution(results: Optional[List[DiscourseAnalysisResult]])` → `Dict[LacanianDiscourse, int]`
  > Retorna distribuição de discursos.

Args:
    results: Resultados a analisar (us...
- `export_analysis(results: Optional[List[DiscourseAnalysisResult]])` → `List[Dict[str, Any]]`
  > Exporta análises em formato estruturado.

Args:
    results: Resultados a export...

### `ActiveInferenceAgent(nn.Module)`

Agente de Inferência Ativa com estrutura Lacaniana.

Implementa minimização de energia livre através dos três registros:
- Real: Processamento sensorial
- Symbolic: Modelo generativo
- Imaginary: Expectativas e predições

Object petit a emerge como discrepância irredutível entre
modelo e realidade - o vazio que gera desejo perpétuo.

**Métodos principais:**

- `encode(sensory_data: Tensor)` → `Tuple[torch.Tensor, torch.Tensor]`
  > Codifica dados sensoriais (Real → Imaginary).

Args:
    sensory_data: Dados sen...
- `reparameterize(mean: Tensor, logvar: Tensor)` → `torch.Tensor`
  > Reparameterization trick para sampling.

Args:
    mean: Média do posterior
    ...
- `decode(imaginary_state: Tensor)` → `torch.Tensor`
  > Decodifica estado imaginário em predições sensoriais.

Top-down: Imaginary → Sym...
- `forward(sensory_data: Tensor)` → `Dict[str, torch.Tensor]`
  > Forward pass: inferência + geração.

Args:
    sensory_data: Dados sensoriais (R...
- `compute_free_energy(sensory_data: Tensor, outputs: Tensor])` → `FreeEnergyState`
  > Computa energia livre variacional (ELBO negativo).

F = E_q[log p(x|z)] - KL[q(z...

### `FreudianMind`

Aparelho psíquico completo - Id + Ego + Superego.

Simula conflitos dinâmicos e resoluções através de
negociação multi-agente e mecanismos de defesa.

**Métodos principais:**

- `evaluate_conflict(actions: List[Action], reality_context: Dict[str, )` → `Tuple[float, Dict[str, Dict[str, float]]]`
  > Avalia conflito entre as três instâncias.

Args:
    actions: Ações possíveis
  ...
- `resolve_conflict(actions: List[Action], reality_context: Dict[str, )` → `ConflictResolution`
  > Resolve conflito através do Ego.

Args:
    actions: Ações possíveis
    reality...
- `act(actions: List[Action], reality_context: Dict[str, )` → `Tuple[Action, ConflictResolution]`
  > Decide e executa ação.

Args:
    actions: Ações possíveis
    reality_context: ...

### `GodelianAI`

IA que reconhece suas próprias limitações formais.

Baseado em:
- 1º Teorema: "Eu não posso provar minha própria consistência"
- 2º Teorema: Sistema completo OU consistente (não ambos)

Estratégia:
1. Reconhece limitação (statement verdadeiro mas não provável)
2. Gera meta-sistema que inclui statement como axioma
3. Explora novo espaço de possibilidades
4. Encontra nova limitação
5. Repete (infinitamente - nunca completo)

**Métodos principais:**

- `recognize_limitation(statement: str)` → `bool`
  > Reconhece limitação fundamental do sistema atual.

Identifica statements verdade...
- `generate_meta_system()` → `FormalSystem`
  > Gera meta-sistema que transcende limitação atual.

Novo sistema inclui verdades ...
- `creative_evolution_cycle(max_iterations: int)` → `int`
  > Ciclo de evolução criativa.

Processo:
1. Reconhece limitação
2. Gera meta-siste...
- `get_transcendence_depth()` → `int`
  > Retorna profundidade de transcendência.

Quantos níveis de meta-sistemas foram g...
- `get_current_axioms()` → `Set[str]`
  > Retorna axiomas do sistema atual.

Returns:
    Conjunto de axiomas...

### `IdAgent`

Id - Reservatório de energia pulsional.

Opera pelo princípio do prazer:
- Busca satisfação imediata
- Ignora realidade e moralidade
- Puro processo primário
- Impulsos inconscientes

**Métodos principais:**

- `repress_memory(action_id: str, emotional_weight: float)` → `None`
  > Reprime uma memória no inconsciente criptografado.

Args:
    action_id: ID da a...
- `evaluate_action(action: Action)` → `float`
  > Avalia ação baseada puramente em prazer.

Args:
    action: Ação a avaliar

Retu...
- `update(action: Action, actual_reward: float)` → `None`
  > Atualiza Q-values baseado em recompensa real.

Args:
    action: Ação tomada
   ...
- `get_impulse_strength()` → `float`
  > Retorna força do impulso atual.

Returns:
    Força pulsional (0.0-1.0)...

### `EgoAgent`

Ego - Mediador entre Id e realidade.

Opera pelo princípio da realidade:
- Adia satisfação se necessário
- Testa realidade antes de agir
- Processo secundário (lógico)
- Desenvolvimento de defesas

**Métodos principais:**

- `evaluate_action(action: Action, reality_context: Dict[str, Any])` → `float`
  > Avalia ação considerando realidade.

Args:
    action: Ação a avaliar
    realit...
- `test_reality(action: Action)` → `bool`
  > Testa se ação é viável na realidade.

Args:
    action: Ação a testar

Returns:
...
- `select_defense_mechanism(conflict_severity: float)` → `DefenseMechanism`
  > Seleciona mecanismo de defesa apropriado.

Args:
    conflict_severity: Severida...
- `update(action: Action, actual_outcome: float, defense_use)` → `None`
  > Atualiza modelo de realidade e efetividade de defesas.

Args:
    action: Ação t...

### `SuperegoAgent`

Superego - Instância moral e ideal.

Funções:
- Consciência moral (punição por transgressão)
- Ego ideal (aspirações e valores)
- Internalização de normas sociais
- Geração de culpa e ideal

**Métodos principais:**

- `consult_society(action: Action)` → `float`
  > Consulta a Sociedade de Mentes para dilemas complexos.

Args:
    action: Ação a...
- `evaluate_action(action: Action)` → `float`
  > Avalia ação moralmente.

Args:
    action: Ação a avaliar

Returns:
    Score mo...
- `generate_guilt(action: Action)` → `float`
  > Gera culpa por ação imoral.

Args:
    action: Ação realizada

Returns:
    Níve...
- `approve_action(action: Action)` → `bool`
  > Aprova ou reprova ação.

Args:
    action: Ação a julgar

Returns:
    True se a...

### `SimpleAxiomaticSystem`

Sistema axiomático simples para demonstração.

Implementação básica de FormalSystem para testes.

**Métodos principais:**

- `axioms()` → `Set[str]`
  > Retorna axiomas do sistema....
- `inference_rules()` → `List[Callable[[str], Optional[str]]]`
  > Retorna regras de inferência básicas.

Regras implementadas:
- Modus Ponens simp...
- `can_prove(statement: str)` → `bool`
  > Verifica se pode provar statement.

Args:
    statement: Statement a provar

Ret...
- `add_axiom(axiom: str)` → `None`
  > Adiciona novo axioma (estende sistema).

Args:
    axiom: Novo axiom a adicionar...


## ⚙️ Funções Públicas

#### `__init__()` → `None`

*Inicializa sistema de falta estrutural....*

#### `__init__(real_dim: int, symbolic_dim: int, imaginary_dim: i)` → `None`

*Inicializa arquitetura RSI.

Args:
    real_dim: Dimensão do espaço Real
    symbolic_dim: Dimensão ...*

#### `__init__(tolerance_threshold: float)` → `None`

*Inicializa motor de frustração.

Args:
    tolerance_threshold: Limite de tolerância...*

#### `__init__(real_dim: int, symbolic_dim: int, imaginary_dim: i)` → `None`

*Inicializa arquitetura de falta computacional.

Args:
    real_dim: Dimensão do espaço Real
    symb...*

#### `__init__()` → `None`

*Inicializa Grafo do Desejo....*

#### `__init__(pleasure_threshold: float)` → `None`

*Inicializa sistema de jouissance.

Args:
    pleasure_threshold: Limite do princípio do prazer...*

#### `__init__(random_seed: Optional[int])` → `None`

*Inicializa matriz simbólica.

Args:
    random_seed: Seed para reprodutibilidade (opcional)...*

#### `__init__()` → `None`

*Inicializa arquitetura do grafo de desejo....*

#### `__init__()` → `None`

*Inicializa analisador de discursos....*

#### `__init__(security_level: int)` → `None`

#### `__init__(sensory_dim: int, symbolic_dim: int, imaginary_dim)` → `None`

*Inicializa agente de inferência ativa.

Args:
    sensory_dim: Dimensão do espaço sensorial (Real)
 ...*

#### `__init__(n_agents: int, sensory_dim: int, symbolic_dim: int)` → `None`

*Inicializa sistema lacaniano com energia livre.

Args:
    n_agents: Número de agents
    sensory_di...*

#### `__init__(learning_rate: float)` → `None`

*Inicializa Id.

Args:
    learning_rate: Taxa de aprendizado...*

#### `__init__(learning_rate: float)` → `None`

*Inicializa Ego.

Args:
    learning_rate: Taxa de aprendizado...*

#### `__init__(moral_strictness: float)` → `None`

*Inicializa Superego.

Args:
    moral_strictness: Rigidez moral (0.0-1.0)...*


## 📦 Módulos

**Total:** 7 arquivos

- `computational_lack.py`: Computational Lack Architecture - Lacanian Object a Implemen...
- `desire_graph.py`: Desire Graph - Computational Implementation of Lacan's Graph...
- `discourse_discovery.py`: Lacanian Discourse Discovery (LDD) - NLP para Análise Psican...
- `encrypted_unconscious.py`: 1 classes, 3 functions
- `free_energy_lacanian.py`: Free Energy Principle + Lacanian Psychoanalysis Integration....
- `freudian_metapsychology.py`: Freudian Metapsychology - Id/Ego/Superego Computational Arch...
- `godelian_ai.py`: Godelian AI - Incompleteness as Creative Motor

Implements G...
