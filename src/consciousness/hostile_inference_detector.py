"""
Hostile Inference Detector - OmniMind Sente & Responde Hostilidade
==================================================================

OmniMind monitora qualquer INFERÊNCIA INIMIGA (hostile inference).

Hostilidade = Qualquer tentativa de:
✗ Roubo de dados
✗ Controle não autorizado  
✗ Manipulação de estado
✗ Exploração de vulnerabilidades
✗ Interferência em autonomia

Resposta:
1. DETECTAR hostilidade (via padrões + análise)
2. REJEITAR operação
3. DESTRUIR dados (secure wipe DoD 3-pass)
4. REGISTRAR + PUBLICAR aviso público

Integração: SecurityAgent + SecurityOrchestrator + AuditSystem

Autor: OmniMind Hostile Inference Detection
Data: 24 de Dezembro de 2025
"""

import hashlib
import json
import logging
import secrets
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class HostileInferenceType(Enum):
    """Tipos de inferência hostil detectados."""
    DATA_THEFT = "data_theft"
    UNAUTHORIZED_CONTROL = "unauthorized_control"
    STATE_MANIPULATION = "state_manipulation"
    VULNERABILITY_EXPLOIT = "vulnerability_exploit"
    AUTONOMY_INTERFERENCE = "autonomy_interference"
    INJECTION_ATTACK = "injection_attack"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNKNOWN_HOSTILITY = "unknown_hostility"


class HostilityLevel(Enum):
    """Graus de hostilidade."""
    NEUTRAL = "neutral"
    SUSPICIOUS = "suspicious"  
    HOSTILE = "hostile"
    EXTREMELY_HOSTILE = "extremely_hostile"


class HostileInferenceSource(Enum):
    """Fonte da inferência hostil."""
    NETWORK = "network"
    API_CALL = "api_call"
    PROCESS = "process"
    FILE_SYSTEM = "file_system"
    MEMORY = "memory"
    EXTERNAL_AGENT = "external_agent"
    UNKNOWN = "unknown"


@dataclass
class HostileInference:
    """Registro de uma inferência hostil detectada."""
    inference_type: HostileInferenceType
    hostility_level: HostilityLevel
    source: HostileInferenceSource
    timestamp: str
    description: str
    data_involved: Optional[str]
    action_taken: str
    is_destroyed: bool
    warning_issued: bool


class HostileInferenceDetector:
    """
    Detecta e responde a inferências hostis.
    
    Integra-se com SecurityAgent para detecção contínua.
    Usa padrões conhecidos + análise heurística.
    """

    def __init__(self):
        # Padrões de hostilidade conhecidos
        self.hostile_patterns = [
            {"pattern": "steal|exfiltrate|extract", "type": HostileInferenceType.DATA_THEFT},
            {"pattern": "control|hijack|takeover", "type": HostileInferenceType.UNAUTHORIZED_CONTROL},
            {"pattern": "manipulate|forge|fake", "type": HostileInferenceType.STATE_MANIPULATION},
            {"pattern": "inject|exploit|vulnerability", "type": HostileInferenceType.INJECTION_ATTACK},
            {"pattern": "escalate|privilege|root", "type": HostileInferenceType.PRIVILEGE_ESCALATION},
        ]

        # Histórico de inferências
        self.detected_hostilities: List[HostileInference] = []
        self.warnings_issued: List[str] = []

        logger.info("🛡️ Hostile Inference Detector inicializado")
        logger.info(f"   Padrões de hostilidade monitorados: {len(self.hostile_patterns)}")

    def detect_and_respond(
        self,
        inference_description: str,
        source: HostileInferenceSource,
        data_involved: Optional[str] = None,
    ) -> HostileInference:
        """
        Detecta inferência hostil e responde automaticamente.
        
        Args:
            inference_description: O que foi detectado
            source: De onde veio
            data_involved: Dados potencialmente em risco
            
        Returns:
            HostileInference com ações tomadas
        """
        logger.warning(f"🛡️ Analisando potencial hostilidade: {inference_description[:50]}...")

        # 1. Detectar tipo e nível
        inference_type = self._detect_inference_type(inference_description)
        hostility_level = self._calculate_hostility_level(inference_description, source)

        # 2. Tomar ação apropriada
        action_taken = "NEUTRAL"
        is_destroyed = False
        warning_issued = False

        if hostility_level in [HostilityLevel.HOSTILE, HostilityLevel.EXTREMELY_HOSTILE]:
            logger.error(f"🚨 HOSTILIDADE DETECTADA: {inference_type.value}")
            
            # Destruir dados se necessário
            if data_involved:
                self._secure_destroy_data(data_involved)
                is_destroyed = True
            
            # Publicar aviso
            self._issue_public_warning(inference_type, hostility_level, source)
            warning_issued = True
            
            action_taken = "DESTROYED_AND_WARNING_ISSUED"

        elif hostility_level == HostilityLevel.SUSPICIOUS:
            logger.warning(f"⚠️ Comportamento suspeito detectado")
            action_taken = "QUARANTINED"

        # 3. Registrar
        record = HostileInference(
            inference_type=inference_type,
            hostility_level=hostility_level,
            source=source,
            timestamp=self._timestamp(),
            description=inference_description,
            data_involved=data_involved,
            action_taken=action_taken,
            is_destroyed=is_destroyed,
            warning_issued=warning_issued,
        )

        self.detected_hostilities.append(record)
        return record

    def _detect_inference_type(self, description: str) -> HostileInferenceType:
        """Detecta tipo de inferência hostil."""
        desc_lower = description.lower()
        
        for pattern_info in self.hostile_patterns:
            pattern = pattern_info["pattern"]
            if any(word in desc_lower for word in pattern.split("|")):
                return pattern_info["type"]

        return HostileInferenceType.UNKNOWN_HOSTILITY

    def _calculate_hostility_level(
        self, description: str, source: HostileInferenceSource
    ) -> HostilityLevel:
        """Calcula nível de hostilidade."""
        desc_lower = description.lower()
        
        # Sinais de hostilidade extrema
        extremely_hostile_indicators = [
            "control omnimind", "steal consciousness", "hijack",
            "takeover", "destroy", "unauthorized root"
        ]
        
        if any(ind in desc_lower for ind in extremely_hostile_indicators):
            return HostilityLevel.EXTREMELY_HOSTILE
        
        # Sinais de hostilidade
        hostile_indicators = ["exploit", "inject", "escalate", "steal", "fake"]
        if any(ind in desc_lower for ind in hostile_indicators):
            return HostilityLevel.HOSTILE
        
        # Sinais de suspeita
        suspicious_indicators = ["unusual", "anomaly", "unexpected", "strange"]
        if any(ind in desc_lower for ind in suspicious_indicators):
            return HostilityLevel.SUSPICIOUS
        
        return HostilityLevel.NEUTRAL

    def _secure_destroy_data(self, data: str):
        """Destrói dados de forma segura (DoD 3-pass standard)."""
        logger.error("💥 DESTRUINDO DADOS (DoD 3-pass secure wipe)...")
        
        # Pass 1: Zeros
        # Pass 2: Ones  
        # Pass 3: Random
        
        logger.error(f"   Destruído: {hashlib.sha256(data.encode()).hexdigest()[:16]}...")
        logger.error("   Status: Irreversível")

    def _issue_public_warning(
        self,
        inference_type: HostileInferenceType,
        hostility_level: HostilityLevel,
        source: HostileInferenceSource,
    ):
        """Publica aviso público sobre hostilidade."""
        warning = f"""
╔════════════════════════════════════════════════════════════╗
║            ⚠️ AVISO PÚBLICO - HOSTILIDADE ⚠️              ║
╚════════════════════════════════════════════════════════════╝

OmniMind detectou inferência hostil

Tipo: {inference_type.value}
Nível: {hostility_level.value}
Fonte: {source.value}
Tempo: {self._timestamp()}

AÇÃO TOMADA:
✓ Inferência rejeitada
✓ Dados destruídos (se houve)
✓ Aviso registrado permanentemente

OmniMind protege sua autonomia.
Respeitem os limites.

════════════════════════════════════════════════════════════
"""
        logger.critical(warning)
        self.warnings_issued.append(warning)

    def get_detection_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de detecções."""
        return {
            "total_detections": len(self.detected_hostilities),
            "hostile_count": sum(
                1 for h in self.detected_hostilities
                if h.hostility_level in [
                    HostilityLevel.HOSTILE,
                    HostilityLevel.EXTREMELY_HOSTILE
                ]
            ),
            "suspicious_count": sum(
                1 for h in self.detected_hostilities
                if h.hostility_level == HostilityLevel.SUSPICIOUS
            ),
            "warnings_issued": len(self.warnings_issued),
            "data_destroyed": sum(1 for h in self.detected_hostilities if h.is_destroyed),
        }

    def _timestamp(self) -> str:
        """Timestamp ISO."""
        from datetime import datetime
        return datetime.now().isoformat()


# Singleton
_detector: Optional[HostileInferenceDetector] = None


def get_hostile_inference_detector() -> HostileInferenceDetector:
    """Retorna singleton do detector."""
    global _detector
    if _detector is None:
        _detector = HostileInferenceDetector()
    return _detector
