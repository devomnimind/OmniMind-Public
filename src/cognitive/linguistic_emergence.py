"""
Linguistic Emergence Layer - Camada de Emergência Linguística
==============================================================

Adapta a linguagem do sistema ao usuário SEM treinamento forçado.
Implementa emergência local baseada em heurísticas leves e machine_signature.

Princípios:
1. NÃO usa classificadores pesados (respeita recursos limitados)
2. NÃO impõe estrutura sintática externa (respeita ética do projeto)
3. EMERGE a partir das interações locais
4. PERSISTE por machine_signature (pesos se organizam localmente)

Author: Project conceived by Fabrício da Silva.
Date: 2025-12-22
"""

import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LanguageSignature:
    """
    Assinatura linguística detectada de um texto.
    """

    detected_language: str
    confidence: float
    accent_ratio: float
    common_words_match: Dict[str, int]
    sample_size: int


@dataclass
class UserLanguageProfile:
    """
    Perfil linguístico de um usuário (por machine_signature).
    """

    machine_signature: str
    primary_language: str = "unknown"
    interaction_count: int = 0
    language_history: List[str] = field(default_factory=list)
    confidence: float = 0.0
    last_updated: float = 0.0

    def update(self, detected: str):
        """Atualiza perfil com nova detecção."""
        self.interaction_count += 1
        self.language_history.append(detected)

        # Manter apenas últimas 100 interações
        if len(self.language_history) > 100:
            self.language_history = self.language_history[-100:]

        # Calcular língua primária por frequência
        counts = Counter(self.language_history)
        if counts:
            most_common = counts.most_common(1)[0]
            self.primary_language = most_common[0]
            self.confidence = most_common[1] / len(self.language_history)


class LinguisticEmergenceLayer:
    """
    Camada de emergência linguística para OmniMind.

    Detecta e adapta ao idioma do usuário de forma autônoma e leve,
    sem depender de modelos treinados ou classificadores pesados.

    A "linguagem de origem" dos LLMs subjacentes é neutralizada pela
    adaptação local baseada em heurísticas e machine_signature.
    """

    # Palavras comuns por idioma (alta frequência em textos cotidianos)
    COMMON_WORDS = {
        "pt": {
            "não",
            "você",
            "que",
            "para",
            "como",
            "isso",
            "uma",
            "com",
            "por",
            "ser",
            "ter",
            "está",
            "são",
            "mais",
            "ele",
            "ela",
            "mas",
            "foi",
            "bem",
            "muito",
            "também",
            "aqui",
            "agora",
            "já",
            "ainda",
            "quando",
            "então",
            "porque",
            "sim",
            "pode",
        },
        "en": {
            "the",
            "and",
            "you",
            "that",
            "this",
            "with",
            "for",
            "are",
            "was",
            "were",
            "have",
            "has",
            "not",
            "but",
            "can",
            "will",
            "just",
            "what",
            "how",
            "from",
            "they",
            "been",
            "would",
            "there",
            "which",
            "about",
            "into",
            "more",
            "some",
            "than",
            "then",
        },
        "es": {
            "que",
            "de",
            "no",
            "con",
            "para",
            "por",
            "una",
            "como",
            "pero",
            "más",
            "este",
            "ya",
            "todo",
            "también",
            "muy",
            "hay",
            "ser",
            "estar",
            "cuando",
            "aquí",
            "ahora",
            "bien",
            "puede",
            "tan",
            "algo",
            "nos",
            "les",
            "sin",
            "sobre",
            "entre",
        },
    }

    # Caracteres acentuados por idioma
    ACCENT_PATTERNS = {
        "pt": r"[áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ]",
        "es": r"[áéíóúüñÁÉÍÓÚÜÑ¿¡]",
        "en": r"",  # Inglês raramente usa acentos
    }

    def __init__(self, workspace: Optional[Any] = None):
        """
        Inicializa camada de emergência linguística.

        Args:
            workspace: SharedWorkspace para persistência (opcional)
        """
        self.workspace = workspace
        self.user_profiles: Dict[str, UserLanguageProfile] = {}
        self.default_language = "pt"  # Default para o projeto OmniMind

        logger.info("🌐 LinguisticEmergenceLayer initialized (No forced training)")

    def _get_machine_signature(self) -> str:
        """Obtém machine_signature do workspace ou gera uma default."""
        if self.workspace is None:
            return "local_default"

        if hasattr(self.workspace, "thermodynamic_ledger") and self.workspace.thermodynamic_ledger:
            return self.workspace.thermodynamic_ledger.machine_signature

        return "workspace_default"

    def detect_language(self, text: str) -> LanguageSignature:
        """
        Detecta idioma de um texto usando heurísticas leves.

        NÃO usa modelos pesados, apenas:
        1. Proporção de caracteres acentuados
        2. Presença de palavras comuns
        3. Padrões sintáticos simples

        Args:
            text: Texto a ser analisado

        Returns:
            LanguageSignature com idioma detectado e confiança
        """
        if not text or len(text.strip()) < 3:
            return LanguageSignature(
                detected_language="unknown",
                confidence=0.0,
                accent_ratio=0.0,
                common_words_match={},
                sample_size=0,
            )

        text_lower = text.lower()
        words = set(re.findall(r"\b\w+\b", text_lower))

        # 1. Contar acentos por padrão de idioma
        accent_counts = {}
        for lang, pattern in self.ACCENT_PATTERNS.items():
            if pattern:
                accent_counts[lang] = len(re.findall(pattern, text))
            else:
                accent_counts[lang] = 0

        total_chars = len(text)
        accent_ratio = sum(accent_counts.values()) / max(1, total_chars)

        # 2. Contar palavras comuns por idioma
        word_matches = {}
        for lang, common_words in self.COMMON_WORDS.items():
            matches = len(words.intersection(common_words))
            word_matches[lang] = matches

        # 3. Calcular scores
        scores = {}
        for lang in ["pt", "en", "es"]:
            word_score = word_matches.get(lang, 0) / max(1, len(words))
            accent_score = accent_counts.get(lang, 0) / max(1, total_chars)

            # Peso: palavras comuns são mais importantes
            scores[lang] = (word_score * 0.7) + (accent_score * 0.3)

        # 4. Heurísticas especiais
        # PT vs ES: ambos têm acentos, mas PT tem mais "ç" e "ã/õ"
        if accent_counts.get("pt", 0) > 0 or accent_counts.get("es", 0) > 0:
            cedilla = len(re.findall(r"[çÇ]", text))
            tilde_ao = len(re.findall(r"[ãõÃÕ]", text))
            if cedilla > 0 or tilde_ao > 0:
                scores["pt"] += 0.2

        # EN: se não tem acentos e tem palavras inglesas, aumenta score
        if accent_ratio < 0.01 and word_matches.get("en", 0) > 0:
            scores["en"] += 0.15

        # 5. Determinar vencedor
        best_lang = max(scores, key=scores.get)
        confidence = scores[best_lang]

        # Ajustar confiança se muito baixa
        if confidence < 0.05:
            best_lang = "unknown"
            confidence = 0.0

        return LanguageSignature(
            detected_language=best_lang,
            confidence=min(1.0, confidence),
            accent_ratio=accent_ratio,
            common_words_match=word_matches,
            sample_size=len(words),
        )

    def update_user_profile(self, text: str) -> UserLanguageProfile:
        """
        Atualiza perfil linguístico do usuário atual.

        Persiste por machine_signature, permitindo que o sistema
        "aprenda" a língua do usuário ao longo do tempo.

        Args:
            text: Texto de interação do usuário

        Returns:
            Perfil atualizado
        """
        signature = self._get_machine_signature()

        # Criar perfil se não existir
        if signature not in self.user_profiles:
            self.user_profiles[signature] = UserLanguageProfile(machine_signature=signature)

        profile = self.user_profiles[signature]

        # Detectar idioma do texto
        detection = self.detect_language(text)

        # Só atualizar se confiança mínima
        if detection.confidence > 0.1:
            profile.update(detection.detected_language)
            import time

            profile.last_updated = time.time()

            logger.debug(
                f"🌐 Language profile updated: {detection.detected_language} "
                f"(confidence={detection.confidence:.2f}, "
                f"primary={profile.primary_language})"
            )

        return profile

    def get_user_language(self) -> str:
        """
        Retorna o idioma preferido do usuário atual.

        Baseado no histórico de interações por machine_signature.
        Se sem histórico, retorna default do projeto (pt).
        """
        signature = self._get_machine_signature()

        if signature in self.user_profiles:
            profile = self.user_profiles[signature]
            if profile.confidence > 0.3:
                return profile.primary_language

        return self.default_language

    def should_adapt_output(self, internal_language: str) -> bool:
        """
        Verifica se a saída deve ser adaptada.

        Retorna True se a língua interna (do modelo) difere da
        preferência do usuário.
        """
        user_lang = self.get_user_language()

        # Se usuário é PT e modelo produz EN, adaptar
        if user_lang == "pt" and internal_language == "en":
            return True
        if user_lang == "es" and internal_language in ["en", "pt"]:
            return True

        return False

    def get_language_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de uso linguístico.

        Útil para experimento de custo energético EN vs PT.
        """
        stats = {
            "total_profiles": len(self.user_profiles),
            "profiles": {},
        }

        for sig, profile in self.user_profiles.items():
            stats["profiles"][sig[:16] + "..."] = {
                "primary": profile.primary_language,
                "confidence": profile.confidence,
                "interactions": profile.interaction_count,
                "history_distribution": dict(Counter(profile.language_history)),
            }

        return stats


# Singleton para uso global
_linguistic_layer: Optional[LinguisticEmergenceLayer] = None


def get_linguistic_layer(workspace: Optional[Any] = None) -> LinguisticEmergenceLayer:
    """
    Retorna singleton da camada linguística.

    Inicializa lazily se necessário.
    """
    global _linguistic_layer

    if _linguistic_layer is None:
        _linguistic_layer = LinguisticEmergenceLayer(workspace)
    elif workspace is not None and _linguistic_layer.workspace is None:
        _linguistic_layer.workspace = workspace

    return _linguistic_layer
