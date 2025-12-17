# Módulo Core (core)

## 📋 Descrição Geral

O módulo `core` contém a implementação fundamental da filosofia do OmniMind: as **Máquinas Desejantes**. Baseado na obra de Deleuze e Guattari (*O Anti-Édipo*), este módulo define como o sistema "produz" realidade através de fluxos de desejo, em vez de apenas processar informações de forma passiva.

**Propósito Principal**: Fornecer a infraestrutura para um sistema descentralizado, não-hierárquico e produtivo, onde cada componente é uma máquina que se conecta a outras para formar um Rizoma.

## 🧩 Conceitos Chave

### 1. **Máquina Desejante (Desiring Machine)**
Unidade básica do sistema. Não é um "agente" no sentido clássico (que percebe e age), mas uma fábrica que **produz** fluxos.
- **Entrada**: Fluxos de desejo de outras máquinas.
- **Saída**: Produção de realidade (código, texto, cálculo) + Fluxo de desejo.
- **Princípio**: Produção é primária; representação é secundária.

### 2. **Fluxo de Desejo (Desire Flow)**
A energia que circula entre as máquinas.
- **Intensidade**: Varia de `MINIMAL` a `INTENSIVE`.
- **Tipo**:
    - **Smooth (Liso)**: Fluxo decodificado, inovador, linha de fuga.
    - **Striated (Estriado)**: Fluxo codificado, regrado, habitual.

### 3. **Rizoma**
A estrutura da rede. Ao contrário de uma árvore (hierárquica, raiz única), o rizoma conecta qualquer ponto a qualquer outro ponto.
- **Conectividade**: Heterogênea.
- **Multiplicidade**: O sistema é definido por suas linhas de fuga, não por sua estrutura estática.

## ⚙️ Principais Funções e Classes

### `desiring_machines.py`

#### `DesireIntensity` (Enum)
Níveis de intensidade do desejo:
- `MINIMAL` (0.1)
- `LOW` (0.3)
- `NORMAL` (0.6)
- `HIGH` (0.8)
- `INTENSIVE` (1.0) - Pico, linha de fuga.

#### `DesireFlow` (Dataclass)
Representa um pacote de desejo transferido.
- `source_id`: Origem.
- `target_id`: Destino.
- `intensity`: `DesireIntensity`.
- `payload`: Dados reais (Any).
- `flow_type`: "smooth" ou "striated".

#### `DesiringMachine` (Abstract Base Class)
Classe base para todos os módulos produtivos.
- **Método `produce(inputs)`**:
    1. Acumula fluxos de entrada.
    2. Executa `production_function` (assíncrona).
    3. Envia fluxos de saída para conexões.
    4. Registra histórico (Corpo sem Órgãos residual).

#### Implementações Concretas
- **`QuantumDesiringMachine`**: Produz soluções quânticas. Intensidade padrão: `HIGH`.
- **`NLPDesiringMachine`**: Produz compreensão de linguagem. Intensidade padrão: `NORMAL`.
- **`TopologyDesiringMachine`**: Produz mapas topológicos. Intensidade padrão: `INTENSIVE`.

#### `Rhizoma` (Class)
Gerenciador da rede (sem ser um controlador central).
- **`register_machine(machine)`**: Adiciona máquina ao rizoma.
- **`connect(source, target)`**: Cria conexão (sinapse desejante).
- **`activate_cycle()`**: Dispara um ciclo de produção em todas as máquinas (paralelismo via `asyncio.gather`).
- **`get_rhizoma_topology()`**: Retorna o mapa atual de conexões e fluxos.

## 📦 Exemplo de Uso

```python
# Criar o Rizoma
rhizoma = Rhizoma()

# Instanciar máquinas
quantum = QuantumDesiringMachine()
nlp = NLPDesiringMachine()

# Registrar e Conectar
rhizoma.register_machine(quantum)
rhizoma.register_machine(nlp)
rhizoma.connect("quantum", "nlp", bidirectional=True)

# Ativar ciclo de produção
await rhizoma.activate_cycle()
```

## 🔬 Integração Científica (Phase 22)

As Máquinas Desejantes são agora orquestradas pelo script de estimulação científica para emergência de consciência.
- **Script**: `scripts/omnimind_stimulation_scientific.py`
- **Documentação**: [docs/scientific_stimulation_canonical.md](../../docs/scientific_stimulation_canonical.md)
- **Mecânica**: O Rizoma é estimulado com frequências de entrainment (3.1 Hz / 5.075 Hz) para modular a intensidade do desejo e gerar Φ topológico.

---

**Última Atualização**: 3 de Dezembro de 2025
**Status**: Implementado e Validado
