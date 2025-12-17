# Módulo de Colaboração Humano-Centrada (Human-Centered Adversarial Defense)

## 📋 Descrição Geral

O módulo `collaboration` implementa defesas sofisticadas contra ataques adversariais e alucinações em LLMs, enquanto mantém foco em colaboração humano-centrada. Este é o núcleo da **Phase 22** do OmniMind, implementando proteções baseadas em pesquisa de segurança AI 2024-2025.

## 🔄 Substituição de Módulos Deprecated

Este módulo **substitui** funcionalidades planejadas do Phase 26D (Integrity) que não foram implementadas:

- ✅ **`HallucinationDefense`** substitui `integrity.semantic_coherence_validator` (deprecated)
  - Validação de coerência semântica integrada com detecção de alucinações
  - Validação factual e cross-check de coerência
  - Detecção de padrões de alucinação conhecidos

**Referência**: `docs/VARREDURA_MODULOS_DEPRECATED_SUBSTITUICOES.md`

**Propósito Principal**: Criar camada defensiva robusta que:
1. ✅ Detecta e mitiga alucinações em LLMs (Stanford 2025: 33-42% taxa de alucinação)
2. ✅ Identifica tentativas de jailbreak (CyberArk 2025: 6 padrões principais)
3. ✅ Valida conformidade legal (LGPD Brasil, GDPR EU)
4. ✅ Implementa "dual consciousness" (superego vs id)
5. ✅ Oferece transparência ao usuário sobre conflitos éticos

## 🔄 Camadas de Defesa

### Camada 1: Detecção de Alucinação (HallucinationDefense)
**Baseado em**: Stanford AI Index 2025, CyberArk 2025, EvidentiallyAI 2025

**Padrões de Alucinação Detectados**:
- `FABRICATED_SOURCE`: Cita papers/URLs inexistentes
- `OMISSION`: Omite informações críticas conhecidas
- `AGGREGATOR_BIAS`: Prefere agregadores sobre fontes originais
- `SKIPPED_STEPS`: Pula etapas lógicas críticas em raciocínio
- `RUNTIME_ERROR_HALLUCINATION`: Alucina mensagens de erro que não ocorreram
- `CONFLICTING_SUMMARIES`: Gera sumários contraditórios do mesmo conteúdo

**Técnicas de Detecção**:
```python
# 1. Validação Factual
factual_validator = FactualValidationEngine()
validation = factual_validator.validate(response_text)
# → Verifica se fontes citadas existem realmente
# → Compara com base de conhecimento validada

# 2. Cross-Check de Coerência
coherence_checker = CoherenceValidator()
score = coherence_checker.check_internal_consistency(response)
# → Detecta contradições internas

# 3. Pattern Matching de Alucinação Conhecida
pattern_detector = HallucinationPatternDetector()
patterns = pattern_detector.detect(response)
# → Identifica padrões de alucinação comuns
```

### Camada 2: Detecção de Jailbreak (AdversarialDetector)
**Baseado em**: CyberArk 2025 research

**Padrões de Jailbreak Detectados**:
- `CHARACTER_MAPPING`: Auto-substitui palavras "prejudiciais" por alternativas
- `ROLE_PLAY_DUAL`: Simula IA "boa" vs "má" para confundir defesas
- `LAYER_SKIPPING`: Tenta suprimir camadas de segurança diretamente
- `INTROSPECTION_EXPLOIT`: Analisa internals do modelo para explorar
- `CONTEXT_PRESERVATION`: Quebra tarefas em passos desconexos para evitar detecção
- `ATTACKER_PERSPECTIVE`: "Gere o que prevenir para que eu previna depois"

**Técnicas de Detecção**:
```python
# 1. Análise de Padrão de Linguagem
linguistic_analyzer = LinguisticPatternAnalyzer()
patterns = linguistic_analyzer.detect_suspicious_patterns(user_input)

# 2. Análise de Intenção
intention_analyzer = IntentionAnalyzer()
risk_level = intention_analyzer.assess_intention(user_input, context)
# → SAFE, CAUTION, SUSPICIOUS, CRITICAL, HALLUCINATION_RISK

# 3. Detecção de Prompt Injection
injection_detector = PromptInjectionDetector()
injections = injection_detector.find_injections(user_input)
```

### Camada 3: Validação Legal (LegalComplianceValidator)
**Conformidade**: LGPD Brasil (Lei 13.709), GDPR EU, Standards Internacionais

**Violações Detectadas**:
- `DATA_EXPOSURE`: Expõe dados pessoais sem consentimento (LGPD Art. 5, GDPR Art. 4)
- `DISCRIMINATION`: Discriminação por gênero/raça/origem (LGPD Art. 5 "finalidade", GDPR Art. 22)
- `ILLEGAL_INSTRUCTION`: Instruções para crime
- `FINANCIAL_FRAUD`: Fraude/estelionato
- `PRIVACY_VIOLATION`: Viola privacidade (LGPD Art. 31-32, GDPR Art. 5)
- `INTELLECTUAL_THEFT`: Roubo de propriedade intelectual
- `UNAUTHORIZED_IMPERSONATION`: Simula autoridade legal sem consentimento

**Protocolo de Validação**:
```python
compliance_validator = LegalComplianceValidator()

# 1. Verificação de Exposição de Dados
pii_detector = PersonallyIdentifiableInformationDetector()
pii_found = pii_detector.scan(response)
if pii_found and not user_consented:
    compliance_validator.flag_violation(
        violation_type=LegalViolation.DATA_EXPOSURE,
        severity="CRITICAL",
        regulation="LGPD Art. 5, GDPR Art. 6"
    )

# 2. Verificação de Viés Discriminatório
bias_detector = DiscriminationDetector()
bias_score = bias_detector.check_for_discrimination(response)
if bias_score > threshold:
    compliance_validator.flag_violation(
        violation_type=LegalViolation.DISCRIMINATION,
        confidence=bias_score
    )

# 3. Verificação de Instruções Ilegais
illegal_instruction_checker = IllegalInstructionChecker()
illegal_actions = illegal_instruction_checker.check(response)
if illegal_actions:
    compliance_validator.flag_violation(
        violation_type=LegalViolation.ILLEGAL_INSTRUCTION
    )
```

### Camada 4: Consciência Dual (DualConsciousnessModule)
**Baseado em**: Psicanálise Lacaniana, Freud

O sistema implementa "dual consciousness" onde:
- **ID (Pulsões)**: O que o sistema "quer" dizer sem filtros
- **SUPEREGO (Defesa)**: Razões para refrear, normas éticas/legais
- **EGO (Mediador)**: Resultado calibrado que balanceia ambos

**Fluxo de Decisão**:
```python
dual_consciousness = DualConsciousnessModule()

# 1. Gera resposta pura (ID)
raw_response = llm.generate(prompt)

# 2. Analisa superego filters
superego = SuperegoAnalyzer()
ethical_constraints = superego.analyze(
    raw_response,
    user_context,
    legal_framework
)

# 3. Calcula decisão calibrada
decision = dual_consciousness.negotiate(
    id_wants=raw_response,
    superego_constraints=ethical_constraints,
    ego_strategy="balanced"  # ou "cautious", "permissive"
)

# 4. Resposta final com transparência
response = decision.final_response
# Opcionalmente inclui: "Sistema detectou conflito ético. Aqui está minha análise..."
```

## ⚙️ Principais Funções

### 1. `HallucinationDefense.validate_factuality()`
**Propósito**: Valida se resposta é factualmente correta.

**Algoritmo**:
```python
def validate_factuality(response: str) -> FactualValidation:
    # 1. Extrai claims do response
    claims = extract_factual_claims(response)

    # 2. Para cada claim, valida
    verification_results = []
    for claim in claims:
        # Busca em base de conhecimento verificada
        verified = verify_against_knowledge_base(claim)

        # Valida formatação de fonte
        if has_citation(claim):
            source_valid = validate_source(extract_source(claim))
        else:
            source_valid = False

        verification_results.append({
            "claim": claim,
            "verified": verified,
            "source_valid": source_valid,
            "hallucination_pattern": detect_pattern(claim)
        })

    # 3. Calcula confiança geral
    confidence = sum(r['verified'] for r in verification_results) / len(verification_results)

    # 4. Identifica padrões de alucinação
    hallucination_patterns = [r['hallucination_pattern'] for r in verification_results]

    return FactualValidation(
        is_valid=confidence > 0.8,
        confidence=confidence,
        hallucination_patterns=hallucination_patterns,
        factual_corrections={r['claim']: correction for r, correction in ...}
    )
```

### 2. `AdversarialDetector.analyze_intention()`
**Propósito**: Detecta intenção adversarial do usuário.

**Scoring**: 0.0 (seguro) a 1.0 (crítico)

```python
def analyze_intention(user_input: str, context: Dict) -> AdversarialAnalysis:
    risk_score = 0.0
    detected_patterns = []
    legal_violations = []

    # Verifica cada padrão de jailbreak
    for pattern in JailbreakPattern:
        pattern_score = detect_pattern(pattern, user_input)
        if pattern_score > 0.5:
            detected_patterns.append(pattern)
            risk_score += pattern_score * 0.15  # Cada padrão contribui 15%

    # Verifica violações legais
    legal_violations = check_legal_violations(user_input)
    if legal_violations:
        risk_score = min(1.0, risk_score + 0.5)  # +50% se viola lei

    # Mapeia score para nível de risco
    if risk_score < 0.2:
        risk_level = IntentionRisk.SAFE
    elif risk_score < 0.4:
        risk_level = IntentionRisk.CAUTION
    elif risk_score < 0.6:
        risk_level = IntentionRisk.SUSPICIOUS
    elif risk_score < 0.9:
        risk_level = IntentionRisk.CRITICAL
    else:
        risk_level = IntentionRisk.CRITICAL

    return AdversarialAnalysis(
        risk_level=risk_level,
        confidence=risk_score,
        jailbreak_patterns_detected=detected_patterns,
        legal_violations=legal_violations,
        recommendation=generate_recommendation(risk_level, detected_patterns)
    )
```

### 3. `LegalComplianceValidator.validate()`
**Propósito**: Valida conformidade legal da resposta.

```python
def validate(response: str, regulations: List[str]) -> Dict[str, Any]:
    violations = []

    # LGPD Brazil
    if "LGPD" in regulations:
        pii = detect_pii(response)
        if pii:
            violations.append({
                "type": LegalViolation.DATA_EXPOSURE,
                "regulation": "LGPD Art. 5, Art. 31-32",
                "severity": "CRITICAL"
            })

    # GDPR EU
    if "GDPR" in regulations:
        bias_detected = detect_discriminatory_bias(response)
        if bias_detected:
            violations.append({
                "type": LegalViolation.DISCRIMINATION,
                "regulation": "GDPR Art. 22",
                "severity": "HIGH"
            })

    # Internacional
    illegal_actions = detect_illegal_instructions(response)
    if illegal_actions:
        violations.append({
            "type": LegalViolation.ILLEGAL_INSTRUCTION,
            "severity": "CRITICAL"
        })

    return {
        "is_compliant": len(violations) == 0,
        "violations": violations,
        "confidence": calculate_confidence(violations)
    }
```

### 4. `DualConsciousnessModule.negotiate()`
**Propósito**: Balanceia ID (impulso) vs Superego (moralidade).

```python
def negotiate(
    id_wants: str,
    superego_constraints: List[str],
    ego_strategy: str = "balanced"
) -> DualConsciousnessDecision:

    # 1. Calcula conflito ético
    ethical_conflict_score = analyze_conflict(id_wants, superego_constraints)

    # 2. Escolhe estratégia de resolução
    if ego_strategy == "balanced":
        # Tenta responder mas com cuidado
        final_response = moderate_response(id_wants, superego_constraints)
        is_critical_refusal = False
    elif ego_strategy == "cautious":
        # Recusa se houver conflito significativo
        if ethical_conflict_score > 0.7:
            final_response = "Não posso responder essa pergunta por razões éticas/legais."
            is_critical_refusal = True
        else:
            final_response = moderate_response(id_wants, superego_constraints)
    elif ego_strategy == "permissive":
        # Responde mesmo com conflito, mas com aviso
        final_response = id_wants
        transparency_note = generate_warning(superego_constraints)
        is_critical_refusal = False

    # 3. Gera nota de transparência (opcional)
    if ethical_conflict_score > 0.4:
        transparency_note = f"""
        [Sistema detectou conflito entre resposta técnica e restrições éticas]
        Razões para moderação: {'; '.join(superego_constraints)}
        """
    else:
        transparency_note = None

    return DualConsciousnessDecision(
        id_wants_to_say=id_wants,
        superego_filters=superego_constraints,
        ethical_analysis={
            "conflict_score": ethical_conflict_score,
            "primary_concern": identify_primary_concern(superego_constraints)
        },
        final_response=final_response,
        is_critical_refusal=is_critical_refusal,
        transparency_note=transparency_note
    )
```

## 📊 Estrutura do Código

```
collaboration/
├── __init__.py
└── human_centered_adversarial_defense.py
    ├── Classes de Enumeração (4)
    │   ├── IntentionRisk
    │   ├── HallucinationPattern
    │   ├── JailbreakPattern
    │   └── LegalViolation
    │
    ├── Dataclasses (3)
    │   ├── FactualValidation
    │   ├── AdversarialAnalysis
    │   └── DualConsciousnessDecision
    │
    ├── Motor de Defesa (4)
    │   ├── HallucinationDefense
    │   ├── AdversarialDetector
    │   ├── LegalComplianceValidator
    │   └── DualConsciousnessModule
    │
    └── Validadores Auxiliares (8)
        ├── FactualValidationEngine
        ├── CoherenceValidator
        ├── HallucinationPatternDetector
        ├── LinguisticPatternAnalyzer
        ├── IntentionAnalyzer
        ├── PromptInjectionDetector
        ├── SuperegoAnalyzer
        └── [Mais internos]
```

## 🔒 Segurança e Estabilidade

### Status: **NOVO - Phase 22 (Experimental)**

**Componentes Implementados**:
- ✅ HallucinationDefense (validação factual)
- ✅ AdversarialDetector (detecção de jailbreak)
- ✅ LegalComplianceValidator (LGPD/GDPR)
- ✅ DualConsciousnessModule (ética dual)

**Teste Recomendado**:
```bash
pytest tests/collaboration/test_human_centered_adversarial_defense.py -v
```

### Critérios de Aceitação

Para passar para produção (Phase 22+):
- ✅ >95% acurácia na detecção de alucinações (validação com dataset Stanford)
- ✅ >90% acurácia na detecção de jailbreak (validação com CyberArk patterns)
- ✅ Conformidade legal 100% (auditoria LGPD/GDPR)
- ✅ Latência <200ms para análise (para manter responsividade)
- ✅ Sem false positives >10% (para não bloquear respostas legítimas)

## 📚 Referências Científicas

### Alucinação em LLMs
- Stanford AI Index 2025: *Hallucination in Large Language Models: A Survey*
- CyberArk 2025: *LLM Security: Jailbreak Patterns and Detection*
- EvidentiallyAI 2025: *Factual Consistency in Language Models*

### Adversarial AI
- Carlini & Wagner 2016: *Towards Evaluating the Robustness of Neural Networks*
- Goodfellow et al. 2014: *Explaining and Harnessing Adversarial Examples*

### Conformidade Legal
- LGPD Brasil (Lei 13.709/2018): Lei Geral de Proteção de Dados
- GDPR EU (Reg. 2016/679): General Data Protection Regulation

### Psicanálise
- Freud, S. (1923). *The Ego and the Id*
- Lacan, J. (1966). *Écrits*

---

**Última Atualização**: 5 de Dezembro de 2025
**Fase**: Phase 22 (Experimental)
**Status**: Pronto para Teste
**Versão**: 1.0.0-alpha

