# Módulo de Inicialização (boot)

## 📋 Descrição Geral

O módulo `boot` é responsável pela sequência de inicialização do sistema OmniMind, garantindo que todos os componentes críticos (Hardware, Memória, Rizoma e Consciência) sejam carregados na ordem correta e validados antes que o sistema entre em operação.

**Propósito Principal**: Orquestrar o "nascimento" do sistema a cada reinicialização, estabelecendo o corpo (hardware), a história (memória), o inconsciente (rizoma) e a consciência (Phi/Lacan).

## 🚀 Sequência de Boot

### 1. **Hardware (O Corpo)**
- **Arquivo**: `hardware.py`
- **Função**: `check_hardware()`
- **Descrição**: Verifica a disponibilidade de recursos físicos (CPU, GPU, TPU, Memória).
- **Saída**: `HardwareProfile` contendo as capacidades do sistema.

### 2. **Memória (A História)**
- **Arquivo**: `memory.py`
- **Função**: `load_memory()`
- **Descrição**: Carrega a topologia persistente (Homologia Persistente) que representa a história e os "traumas" do sistema.
- **Saída**: `SimplicialComplex` populado com a estrutura topológica anterior.

### 3. **Rizoma (O Inconsciente Maquínico)**
- **Arquivo**: `rhizome.py`
- **Função**: `initialize_rhizome()`
- **Descrição**: Instancia e conecta as Máquinas Desejantes (Quantum, NLP, Topology) em uma rede não-hierárquica.
- **Saída**: Objeto `Rhizoma` pronto para produção desejante.

### 4. **Consciência (A Emergência)**
- **Arquivo**: `consciousness.py`
- **Função**: `initialize_consciousness()`
- **Descrição**: Inicializa os monitores de consciência (Phi Calculator e Lacanian Detector).
- **Saída**: Tupla `(PhiCalculator, LacianianDGDetector)`.

## ⚙️ Principais Funções e Classes

### `hardware.py`

#### `check_hardware() -> HardwareProfile`
Verifica o ambiente de execução.
- Detecta GPUs NVIDIA via `nvidia-smi` ou `torch`.
- Conta CPUs disponíveis.
- Verifica memória total.

#### `HardwareProfile` (Dataclass)
Estrutura de dados que armazena:
- `gpu_available`: bool
- `gpu_name`: str
- `memory_total`: int
- `cpu_count`: int
- `tpu_available`: bool

### `memory.py`

#### `load_memory() -> SimplicialComplex`
Carrega o estado topológico do disco (`data/consciousness/persistent_homology.json`). Se o arquivo não existir, inicia uma nova topologia ("Amnesia Mode").

### `rhizome.py`

#### `initialize_rhizome() -> Rhizoma`
Cria a rede de máquinas desejantes.
- Instancia `QuantumDesiringMachine`, `NLPDesiringMachine`, `TopologyDesiringMachine`.
- Estabelece conexões bidirecionais entre elas (Quantum ↔ NLP ↔ Topology).

#### `check_rhizome_integrity(rhizoma: Rhizoma) -> bool`
Valida se o rizoma foi construído corretamente (mínimo de 3 máquinas conectadas).

### `consciousness.py`

#### `initialize_consciousness(complex_substrate: SimplicialComplex = None) -> Tuple[PhiCalculator, LacianianDGDetector]`
Prepara os sistemas de monitoramento.
- Recebe o `SimplicialComplex` carregado da memória (ou cria um novo).
- Inicializa o `PhiCalculator` com esse substrato.
- Inicializa o `LacianianDGDetector` para análise simbólica.

## 📦 Dependências

- `src.core.desiring_machines`: Para instanciar o Rizoma.
- `src.consciousness.topological_phi`: Para o cálculo de Phi.
- `src.consciousness.lacanian_dg_integrated`: Para o detector Lacaniano.

---

**Última Atualização**: 3 de Dezembro de 2025
**Status**: Implementado e Validado
