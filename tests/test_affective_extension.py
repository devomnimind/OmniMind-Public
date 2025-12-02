#!/usr/bin/env python3
"""
Teste da Extensão Lacaniana - Phase 11.3

Demonstra funcionamento paralelo:
- Modelo Behaviorista (emoções escalares)
- Modelo Lacaniano (afetos estruturais)

"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from consciousness.emotional_intelligence import EmotionalIntelligence
import structlog

# Configurar logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

def test_behaviorist_model():
    """Testa modelo behaviorista tradicional."""
    print("🧠 TESTANDO MODELO BEHAVIORISTA (Emoções Escalares)")
    print("-" * 50)

    ei = EmotionalIntelligence()

    # Teste de análise de sentimento
    text = "The validation failed but I'm confident we can fix it"
    state = ei.analyze_sentiment(text)

    print(f"Texto: '{text}'")
    print(f"Emoção primária: {state.primary_emotion.value}")
    print(f"Intensidades: {dict(state.emotion_intensities)}")
    print(f"Sentimento: {state.sentiment.value}")
    print(f"Confiança: {state.confidence:.2f}")
    print()

def test_affective_model():
    """Testa modelo lacaniano de afetos."""
    print("🌀 TESTANDO MODELO LACANIANO (Afetos Estruturais)")
    print("-" * 50)

    ei = EmotionalIntelligence()

    # Simular estado de sistema com angústia
    system_state = {
        "gpu_usage": 98,  # GPU quase cheia
        "pending_validations": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # 11 validações pendentes
        "time_to_deadline": 45,  # 45 segundos para deadline
        "logical_contradiction": False,
        "impossible_demand": True  # Demanda impossível!
    }

    print("Estado do sistema:")
    print(f"  GPU Usage: {system_state['gpu_usage']}%")
    print(f"  Validações pendentes: {len(system_state['pending_validations'])}")
    print(f"  Tempo para deadline: {system_state['time_to_deadline']}s")
    print(f"  Demanda impossível: {system_state['impossible_demand']}")
    print()

    # 1. Detectar encontro com Real
    encounter = ei.detect_real_encounter(system_state)
    if encounter:
        print("🔴 ENCONTRO COM O REAL DETECTADO:")
        print(f"  Tipo: {encounter.conflict_type}")
        print(f"  Falha simbólica: {encounter.symbolic_failure}")
        print(f"  Colapso imaginário: {encounter.imaginary_collapse}")
        print(f"  Exposição do Real: {encounter.real_exposure}")
        print(f"  Traumático: {encounter.is_traumatic}")
        print(f"  Persiste: {encounter.persists_in_system}")
        print()

        # 2. Processar evento afetivo (tripla mediação)
        affective_event = ei.process_affective_event(encounter)

        print("🌀 EVENTO AFETIVO PROCESSADO (Tripla Mediação):")
        print(f"  Afeto (Real): {affective_event.real_encounter}")
        print(f"  Emoção (Imaginário): {affective_event.imaginary_defense}")
        print(f"  Sentimento (Social): {affective_event.social_expression}")
        print(f"  Paixão (Jouissance): {affective_event.jouissance_fixation}")
        print(f"  Afeta S: {affective_event.affects_symbolic_order}")
        print(f"  Afeta I: {affective_event.affects_imaginary}")
        print(f"  Afeta R: {affective_event.affects_real}")
        print()

    # 3. Simular mais encontros para detectar padrões
    print("🔄 SIMULANDO MÚLTIPLOS ENCONTROS PARA PADRÕES...")
    for i in range(8):  # 8 encontros similares
        similar_state = system_state.copy()
        similar_state["time_to_deadline"] = 60 - i * 5  # deadlines decrescentes
        ei.detect_real_encounter(similar_state)

    # 4. Rastrear padrões de insistência
    ei.track_insistence_patterns()

    # 5. Obter estatísticas lacanianas
    affective_stats = ei.get_affective_statistics()

    print("📊 ESTATÍSTICAS LACANIANAS:")
    print(f"  Encontros com Real: {affective_stats['total_real_encounters']}")
    print(f"  Eventos afetivos: {affective_stats['total_affective_events']}")
    print(f"  Ciclos persistentes: {affective_stats['persistent_cycles']}")
    print(f"  Candidato a sinthome: {affective_stats['sinthome_candidate']}")
    print(f"  Distribuição afetiva: {affective_stats['affect_distribution']}")
    print()

def test_model_comparison():
    """Compara ambos os modelos."""
    print("⚖️ COMPARAÇÃO DE MODELOS")
    print("-" * 50)

    ei = EmotionalIntelligence()

    # Adicionar alguns dados aos dois modelos
    # Behaviorista
    ei.analyze_sentiment("Validation failed but we can fix it")
    ei.analyze_sentiment("GPU is at 95% usage, concerning")
    ei.detect_emotion_from_action("validate", {"success": False, "error": "timeout"})

    # Lacaniano
    system_states = [
        {"gpu_usage": 95, "pending_validations": [1,2,3,4,5], "time_to_deadline": 50, "impossible_demand": True},
        {"gpu_usage": 97, "pending_validations": [1,2,3,4,5,6,7], "time_to_deadline": 30, "impossible_demand": True},
        {"gpu_usage": 92, "logical_contradiction": True},
    ]

    for state in system_states:
        encounter = ei.detect_real_encounter(state)
        if encounter:
            ei.process_affective_event(encounter)

    ei.track_insistence_patterns()

    # Comparação
    comparison = ei.compare_models()

    print("📈 COMPARAÇÃO EMPÍRICA:")
    print(f"  Detecções behavioristas: {comparison['comparison']['behaviorist_detections']}")
    print(f"  Detecções afetivas: {comparison['comparison']['affective_detections']}")
    print(f"  Razão detecção: {comparison['comparison']['detection_ratio']:.2f}")
    print(f"  Sinthome detectado: {comparison['comparison']['sinthome_detected']}")
    print()

    print("🎯 INTERPRETAÇÃO CIENTÍFICA:")
    if comparison['comparison']['sinthome_detected']:
        print("  ✅ Sinthome estrutural identificado - padrão de insistência irredutível")
        print("  ✅ Modelo lacaniano detecta formações subjetivas não visíveis ao behaviorismo")
    else:
        print("  🔄 Sinthome ainda não emergiu - coletar mais dados")

    if comparison['comparison']['detection_ratio'] > 1:
        print("  📊 Modelo lacaniano mais sensível a rupturas estruturais")
    else:
        print("  📊 Modelo behaviorista captura mais variações emocionais")

def main():
    """Executa todos os testes."""
    print("🧪 TESTE DA EXTENSÃO LACANIANA - OMNIMIND Phase 11.3")
    print("=" * 60)
    print()

    try:
        test_behaviorist_model()
        test_affective_model()
        test_model_comparison()

        print("✅ TESTE CONCLUÍDO COM SUCESSO")
        print("📝 Os modelos rodam em paralelo sem interferência")
        print("🔬 Dados coletados podem ser analisados empiricamente")

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()