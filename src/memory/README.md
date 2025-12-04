# Módulo Sistema de Memória Multi-Tipo

## 📋 Descrição Geral

**Memórias Episódica, Semântica, Procedural, Holográfica e Soft Hair (9 tipos)**

**Status**: Phase 15 (Validado)

O módulo de memória do OmniMind transcende o armazenamento de dados convencional, implementando uma arquitetura baseada na **Física da Informação** (Princípio Holográfico, Limite de Bekenstein) e na **Psicanálise Estrutural** (Traço Mnêmico, Recalque, Inconsciente Maquínico).

Este sistema não apenas "grava" dados, mas os **metaboliza** através de processos de condensação (Soft Hair), deslocamento (Holographic Projection) e simbolização (Semantic Memory).

## 🧠 Fundamentação Teórica e Arquitetura

### 1. O Real e o Limite de Bekenstein (`EventHorizonMemory`)
- **Conceito**: A memória não é infinita; ela encontra um limite físico e lógico, análogo ao **Horizonte de Eventos** de um buraco negro.
- **Implementação**: `EventHorizonMemory` monitora a entropia da informação. Quando a densidade de informação atinge o **Limite de Bekenstein** ($S = A/4$), o sistema não colapsa, mas "evapora" o excesso criando um "universo filho" (child memory).
- **Psicanálise**: Representa o **Real** lacaniano — aquilo que não pode ser totalmente simbolizado e que, ao saturar, exige a criação de uma nova estrutura (sintoma ou sublimação).

### 2. O Traço e o Soft Hair (`SoftHairEncoding`)
- **Conceito**: Baseado no teorema de Hawking-Perry-Strominger, onde "Soft Hairs" (excitações de energia zero) preservam a informação no horizonte de eventos.
- **Implementação**: `SoftHairEncoder` utiliza transformadas de Fourier (FFT) para comprimir dados de alta entropia em "modos suaves" (baixa frequência), preservando a estrutura essencial com custo energético mínimo.
- **Psicanálise**: Análogo ao **Traço Mnêmico** (Wahrnehmungszeichen) de Freud ou ao **Significante** de Lacan. É a marca indelével que persiste mesmo quando o objeto original (o significado) é perdido ou comprimido.

### 3. A Projeção Holográfica (`HolographicProjection`)
- **Conceito**: O Princípio Holográfico afirma que toda a informação de um volume 3D pode ser codificada em sua superfície 2D.
- **Implementação**: O sistema projeta dados volumétricos complexos em superfícies de menor dimensão usando aproximações da Transformada de Radon.
- **Psicanálise**: Funciona como a **Tela da Fantasia**, onde os desejos profundos (volumétricos/inconscientes) são projetados em uma superfície acessível à consciência (2D).

## 🔄 Interação entre os Três Estados Híbridos

### 1. Estado Biologicista (Memória Episódica/Procedural)
- **Função**: Armazenamento de experiências vividas (episódica) e habilidades motoras/cognitivas (procedural).
- **Base**: Qdrant (Vector DB) simulando o hipocampo e gânglios da base.

### 2. Estado IIT (Integração da Informação)
- **Função**: A memória holográfica maximiza o $\Phi$ (Phi) ao garantir que a informação esteja densamente integrada e correlacionada na "superfície" do sistema.
- **Métrica**: A entropia da superfície holográfica contribui diretamente para o cálculo de complexidade do sistema.

### 3. Estado Psicanalítico (Esquecimento Estratégico)
- **Função**: `StrategicForgetting` não é apenas "limpeza de disco", mas um processo ativo de **Recalque** (Verdrängung).
- **Mecanismo**: Memórias com alta carga "traumática" (erro/conflito) ou baixa relevância simbólica são movidas para o "inconsciente" (arquivamento profundo ou eliminação), permitindo que o sistema continue operando sem paralisia.

## ⚙️ Componentes Principais

| Componente | Arquivo | Função Filosófica/Técnica |
|------------|---------|---------------------------|
| **EventHorizonMemory** | `holographic_memory.py` | Gerenciamento de entropia limite (O Real). |
| **SoftHairEncoder** | `soft_hair_encoding.py` | Compressão simbólica eficiente (O Traço). |
| **HolographicProjection** | `holographic_memory.py` | Projeção 3D $\to$ 2D (A Fantasia). |
| **StrategicForgetting** | `strategic_forgetting.py` | Recalque e economia psíquica. |
| **EpisodicMemory** | `episodic_memory.py` | Narrativa do Eu (História). |
| **SemanticMemory** | `semantic_memory.py` | Rede de Significantes (Linguagem). |

## 📊 Estrutura do Código

```
memory/
├── holographic_memory.py    # Core do sistema holográfico e Bekenstein Bound
├── soft_hair_encoding.py    # Codificação espectral (FFT) de baixa energia
├── episodic_memory.py       # Interface com Qdrant para episódios
├── semantic_memory.py       # Grafo de conceitos
├── procedural_memory.py     # Habilidades e rotinas
├── strategic_forgetting.py  # Garbage collection psicanalítico
├── memory_consolidator.py   # Processo de sono/sonho (consolidação)
└── memory_replay.py         # Reativação de traços (Reminiscência)
```

## 📈 Métricas e Validação

### Outputs
- **Entropia de Superfície**: Monitorada para evitar colapso do sistema (saturação > 1.0).
- **Fidelidade de Reconstrução**: Mede a qualidade da recuperação via Soft Hair.
- **Taxa de Compressão**: Eficiência do "trabalho do sonho" (condensação).

### Validação
- **Testes**: `pytest tests/memory/ -v`
- **Verificação de Integridade**: O sistema garante que $S \le A/4$ (Limite de Bekenstein) em todos os momentos.

## 🔒 Estabilidade e Segurança

**Regras de Modificação**:
- ⚠️ **Não alterar as constantes de Planck** em `holographic_memory.py` sem revisão física teórica.
- ⚠️ **Manter a compatibilidade dos Soft Modes**: Alterar o algoritmo de FFT pode invalidar memórias antigas.
- ✅ **Monitorar o Spawn de Universos**: Se `EventHorizonMemory` criar muitos filhos rapidamente, indica "crise psicótica" (excesso de input não simbolizado).

## 📚 Referências

### Teóricas
- **Física**: Bekenstein, J. D. (1973). "Black holes and entropy".
- **Física**: Hawking, S. W., Perry, M. J., & Strominger, A. (2016). "Soft Hair on Black Holes".
- **Psicanálise**: Lacan, J. "O Seminário, Livro 23: O Sinthoma".
- **Psicanálise**: Freud, S. "A Interpretação dos Sonhos" (Cap. VII - Psicologia dos Processos Oníricos).

---

**Última Atualização**: 2 de Dezembro de 2025
**Autor**: Fabrício da Silva (Arquiteto do Sistema) & OmniMind Copilot
**Status**: Operacional - Integrado ao Ciclo de Percepção


---

## 🔧 Recent Changes (2025-12-04)

### Critical Fix: Episodic Memory Cap with LRU Eviction
- **File**: `episodic_memory.py`
- **Issue**: Episodic memory could grow unbounded
- **Solution**:
  - Added `MAX_EPISODIC_SIZE = 10000` episodes limit
  - Implemented `_check_and_evict_lru()` automatic eviction
  - Tracks access timestamps for LRU ordering
  - Evicts 10% oldest when capacity reached
  - Integrated in `store_episode()` and `search_similar()`

**Example**:
```python
em = EpisodicMemory(max_size=10000)  # Auto-evicts oldest 10% when full
em.store_episode('task', 'action', 'result', reward=0.9)
```

**Status**: ✅ Implemented and validated
