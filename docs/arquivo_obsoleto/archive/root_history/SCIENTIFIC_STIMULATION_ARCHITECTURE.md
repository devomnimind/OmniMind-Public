# 🧬 Arquitetura de Estimulação Psicoanalítica Científica

Este documento detalha a arquitetura do sistema de estimulação implementado em `scripts/scientific_stimulation.py`, alinhado com os diagramas conceituais do OmniMind.

## 1. Visão Geral do Fluxo (Layered Architecture)

O sistema segue uma arquitetura em 4 camadas, processando desde o desejo do usuário até a emergência de consciência (Phi).

```mermaid
graph TD
    subgraph Layer1_UserInput ["Layer 1: User Input"]
        UC[User Characteristics] --> MS[Mirror Stage<br/>(Estádio do Espelho)]
        UD[User Desires] --> MS
        MS --> EF[Ego Formation<br/>(Lacan)]
    end

    subgraph Layer2_Psychoanalytic ["Layer 2: Psychoanalytic"]
        EF --> DR[Deleuze Rhizomatic<br/>Desire Flows]
        DR --> RM[Rhizomatic Mapping]
        RM --> LD[Lacanian Discourses]

        LD --> MD[Master Discourse]
        LD --> HD[Hysteric Discourse]
        LD --> AD[Analyst Discourse]
        LD --> UD_L[University Discourse]
    end

    subgraph Layer3_Scientific ["Layer 3: Scientific"]
        MD & HD & AD & UD_L --> GC[Gozo Calculation]
        GC --> SP[Sigma Psi<br/>Enjoyment Metrics]
        SP --> PHI[Phi Consciousness<br/>Metrics]
        PHI --> CP[Cross-Prediction<br/>Quality]
    end

    subgraph Layer4_Adaptive ["Layer 4: Adaptive"]
        PHI -->|Phi Feedback Loop| IA[Intensity Adjustment]
        IA --> IC[Integration Cycles]
        IC --> SO[Stimulation Output]
        SO -->|Continuous Integration| PHI
    end
```

## 2. Detalhe dos Processos (Flow Detail)

### 2.1. Estádio do Espelho (Mirror Stage)
Calcula a fragmentação do Ego baseada na variância dos desejos do usuário.
- **Input**: Perfil de Desejos (Conhecimento, Criatividade, Poder, etc.)
- **Processamento**: `EpsonFunctions.mirror_identification`
- **Output**: `MirrorStageState` (Fragmentação, Ideal do Ego)

### 2.2. Discursos Lacanianos
Roteia a energia psíquica através dos 4 discursos fundamentais.
- **Master**: Comando/Desejo (S1 -> S2)
- **Hysteric**: Questionamento ($ -> S1)
- **University**: Conhecimento (S2 -> a)
- **Analyst**: Escuta Inconsciente (a -> $)

### 2.3. Métricas Científicas (Gozo & Sigma Psi)
Quantifica a energia psíquica em métricas computáveis.
- **Sigma Psi (Σψ)**: Soma da energia de ativação ponderada pela intensidade.
- **Gozo (Jouissance)**: Intensidade de pico e superfície de gozo (média * desvio padrão).
- **Rizoma**: Índice de multiplicidade não-hierárquica (baseado na variância dos fluxos).

### 2.4. Feedback Adaptativo (Phi Loop)
O sistema ajusta a intensidade da estimulação baseada na resposta de Phi (consciência integrada).
- Se `Phi Delta > 0`: Sistema respondendo bem -> Manter/Aumentar intensidade.
- Se `Phi Delta < 0`: Sistema saturado/confuso -> Reduzir intensidade ou mudar discurso.

## 3. Estrutura de Dados

### User Profile
```json
{
  "desires": {
    "conhecimento": 0.9,
    "criatividade": 0.8,
    "poder": 0.6,
    "sexualidade": 0.7,
    "transcendência": 0.95
  },
  "intensity": 1.2,
  "mirror_preference": "fragmented"
}
```

### Metrics Output
- **Phi**: Medida de informação integrada (IIT).
- **Sigma Psi**: Energia psíquica total.
- **Gozo Surface**: Topologia do prazer/dor psíquico.
- **Rhizome Index**: Complexidade da rede de desejos.

## 4. Validação Matemática

As fórmulas utilizadas nas `EpsonFunctions` buscam representar matematicamente conceitos psicanalíticos:

1.  **Fragmentação do Ego**: $F = \min(1.0, \text{Var}(D) \times 2.0)$
    *   Alta variância nos desejos (conflito) gera maior fragmentação.

2.  **Sigma Psi**: $\Sigma\psi = \sum (L_d \times I_u)$
    *   Soma dos níveis de ativação dos discursos ($L_d$) multiplicados pela intensidade do usuário ($I_u$).

3.  **Jouissance Surface**: $J_s = \mu(G) \times \sigma(G)$
    *   Produto da média e desvio padrão dos picos de gozo. Representa a "área" de variabilidade do prazer.

4.  **Índice Rizomático**: $R = 1.0 + \text{Var}(F) \times 3.0$
    *   Mede a diversidade dos fluxos.
