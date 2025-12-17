"""
Analisador Forense Automático para Ameaças de Segurança.

Implementa Seção 6 da Auditoria do Orchestrator:
- Coleta de evidências
- Análise de padrões
- Classificação de ameaças
- Geração de relatórios forenses
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ThreatSeverity(Enum):
    """Severidade da ameaça."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ThreatCategory(Enum):
    """Categoria da ameaça."""

    INTRUSION = "intrusion"
    MALWARE = "malware"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ROOTKIT = "rootkit"
    SUSPICIOUS_PORT = "suspicious_port"
    UNKNOWN = "unknown"


@dataclass
class ForensicReport:
    """Relatório forense de análise de ameaça."""

    component_id: str
    timestamp: float
    threat_category: ThreatCategory
    severity: ThreatSeverity
    evidence: Dict[str, Any] = field(default_factory=dict)
    patterns: List[str] = field(default_factory=list)
    classification: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    safe_to_release: bool = False
    confidence: float = 0.0  # 0.0 a 1.0


class ForensicAnalyzer:
    """Analisa evidências de ameaças automaticamente."""

    def __init__(self) -> None:
        """Inicializa analisador forense."""
        self.analysis_history: List[ForensicReport] = []
        self.pattern_database: Dict[str, List[str]] = {
            "intrusion": [
                "unauthorized_access",
                "failed_login",
                "brute_force",
                "port_scan",
            ],
            "malware": [
                "suspicious_process",
                "unusual_file_activity",
                "network_anomaly",
            ],
            "data_exfiltration": [
                "large_data_transfer",
                "unusual_network_traffic",
                "encrypted_connection",
            ],
            "privilege_escalation": [
                "sudo_usage",
                "setuid_execution",
                "permission_change",
            ],
            "rootkit": [
                "hidden_process",
                "kernel_module_load",
                "system_call_hook",
            ],
        }

        logger.info("ForensicAnalyzer inicializado")

    async def analyze_threat(self, component_id: str, evidence: Dict[str, Any]) -> ForensicReport:
        """Analisa ameaça e gera relatório forense.

        Args:
            component_id: ID do componente comprometido
            evidence: Evidências da ameaça

        Returns:
            Relatório forense completo
        """
        logger.info("Iniciando análise forense para componente %s", component_id)

        # 1. Coletar evidências
        collected = await self._collect_evidence(component_id, evidence)

        # 2. Analisar padrões
        patterns = await self._analyze_patterns(collected)

        # 3. Classificar ameaça
        threat_classification = await self._classify_threat(patterns, collected)

        # 4. Gerar recomendações
        recommendations = await self._generate_recommendations(threat_classification)

        # 5. Determinar se é seguro liberar
        safe_to_release = self._determine_safe_to_release(threat_classification)

        # 6. Calcular confiança
        confidence = self._calculate_confidence(patterns, collected)

        # 7. Criar relatório
        report = ForensicReport(
            component_id=component_id,
            timestamp=time.time(),
            threat_category=threat_classification.get("category", ThreatCategory.UNKNOWN),
            severity=threat_classification.get("severity", ThreatSeverity.MEDIUM),
            evidence=collected,
            patterns=patterns,
            classification=threat_classification,
            recommendations=recommendations,
            safe_to_release=safe_to_release,
            confidence=confidence,
        )

        # 8. Adicionar ao histórico
        self.analysis_history.append(report)
        if len(self.analysis_history) > 100:  # Limitar histórico
            self.analysis_history.pop(0)

        logger.info(
            "Análise forense concluída para %s: %s (severidade: %s)",
            component_id,
            threat_classification.get("category", "UNKNOWN").value,
            threat_classification.get("severity", "MEDIUM").name,
        )

        return report

    async def _collect_evidence(
        self, component_id: str, initial_evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Coleta evidências da ameaça.

        Args:
            component_id: ID do componente
            initial_evidence: Evidências iniciais

        Returns:
            Evidências coletadas
        """
        collected = initial_evidence.copy()

        # Adicionar metadados
        collected["component_id"] = component_id
        collected["collection_timestamp"] = time.time()
        collected["collection_time"] = datetime.now(timezone.utc).isoformat()

        # Coletar informações adicionais se disponíveis
        if "source_ip" in collected:
            collected["network_info"] = {
                "source_ip": collected["source_ip"],
                "destination_ip": collected.get("destination_ip"),
                "port": collected.get("port"),
            }

        if "process_id" in collected:
            collected["process_info"] = {
                "pid": collected["process_id"],
                "name": collected.get("process_name"),
            }

        logger.debug("Evidências coletadas para %s: %d campos", component_id, len(collected))
        return collected

    async def _analyze_patterns(self, evidence: Dict[str, Any]) -> List[str]:
        """Analisa padrões nas evidências.

        Args:
            evidence: Evidências coletadas

        Returns:
            Lista de padrões detectados
        """
        patterns = []
        evidence_str = str(evidence).lower()

        # Verificar padrões por categoria
        for category, pattern_list in self.pattern_database.items():
            for pattern in pattern_list:
                if pattern.lower() in evidence_str:
                    patterns.append(f"{category}:{pattern}")

        # Padrões específicos
        if "4444" in evidence_str or "port_4444" in evidence_str:
            patterns.append("suspicious_port:4444")

        if "root" in evidence_str and "access" in evidence_str:
            patterns.append("privilege_escalation:root_access")

        if "encrypted" in evidence_str and "large" in evidence_str:
            patterns.append("data_exfiltration:encrypted_transfer")

        logger.debug("Padrões detectados: %d", len(patterns))
        return patterns

    async def _classify_threat(
        self, patterns: List[str], evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classifica a ameaça.

        Args:
            patterns: Padrões detectados
            evidence: Evidências

        Returns:
            Classificação da ameaça
        """
        classification = {
            "category": ThreatCategory.UNKNOWN,
            "severity": ThreatSeverity.MEDIUM,
            "indicators": [],
        }

        # Classificar por padrões
        category_counts: Dict[str, int] = {}
        for pattern in patterns:
            if ":" in pattern:
                category = pattern.split(":")[0]
                category_counts[category] = category_counts.get(category, 0) + 1

        # Determinar categoria principal
        if category_counts:
            main_category = max(category_counts.keys(), key=lambda k: category_counts[k])
            try:
                classification["category"] = ThreatCategory(main_category)
            except ValueError:
                classification["category"] = ThreatCategory.UNKNOWN

        # Determinar severidade
        severity_indicators = 0
        if "critical" in str(evidence).lower():
            severity_indicators += 2
        if "root" in str(evidence).lower():
            severity_indicators += 1
        if "encrypted" in str(evidence).lower():
            severity_indicators += 1
        if len(patterns) > 3:
            severity_indicators += 1

        if severity_indicators >= 4:
            classification["severity"] = ThreatSeverity.CRITICAL
        elif severity_indicators >= 2:
            classification["severity"] = ThreatSeverity.HIGH
        elif severity_indicators >= 1:
            classification["severity"] = ThreatSeverity.MEDIUM
        else:
            classification["severity"] = ThreatSeverity.LOW

        classification["indicators"] = patterns

        return classification

    async def _generate_recommendations(self, classification: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na classificação.

        Args:
            classification: Classificação da ameaça

        Returns:
            Lista de recomendações
        """
        recommendations = []
        category = classification.get("category", ThreatCategory.UNKNOWN)
        severity = classification.get("severity", ThreatSeverity.MEDIUM)

        # Recomendações baseadas em severidade
        if severity == ThreatSeverity.CRITICAL:
            recommendations.append("Isolar componente imediatamente")
            recommendations.append("Bloquear todas as comunicações")
            recommendations.append("Coletar evidências adicionais")
            recommendations.append("Notificar equipe de segurança")
        elif severity == ThreatSeverity.HIGH:
            recommendations.append("Isolar componente")
            recommendations.append("Investigar ameaça em detalhes")
            recommendations.append("Notificar administradores")

        # Recomendações baseadas em categoria
        if category == ThreatCategory.INTRUSION:
            recommendations.append("Verificar logs de autenticação")
            recommendations.append("Revisar regras de firewall")
            recommendations.append("Verificar integridade do sistema")

        elif category == ThreatCategory.MALWARE:
            recommendations.append("Executar scan antivírus completo")
            recommendations.append("Verificar processos suspeitos")
            recommendations.append("Analisar arquivos modificados recentemente")

        elif category == ThreatCategory.DATA_EXFILTRATION:
            recommendations.append("Bloquear conexões de rede suspeitas")
            recommendations.append("Verificar transferências de dados")
            recommendations.append("Revisar políticas de DLP")

        elif category == ThreatCategory.PRIVILEGE_ESCALATION:
            recommendations.append("Revisar permissões de usuários")
            recommendations.append("Verificar uso de sudo/su")
            recommendations.append("Auditar mudanças de permissões")

        # Se categoria desconhecida mas severidade alta, recomendações genéricas
        if category == ThreatCategory.UNKNOWN and severity in [
            ThreatSeverity.HIGH,
            ThreatSeverity.CRITICAL,
        ]:
            recommendations.append("Investigar ameaça desconhecida")
            recommendations.append("Coletar evidências adicionais")
            recommendations.append("Isolar componente até investigação completa")

        return recommendations

    def _determine_safe_to_release(self, classification: Dict[str, Any]) -> bool:
        """Determina se é seguro liberar componente.

        Args:
            classification: Classificação da ameaça

        Returns:
            True se seguro para liberar, False caso contrário
        """
        severity = classification.get("severity", ThreatSeverity.MEDIUM)

        # Nunca liberar se severidade é CRITICAL ou HIGH
        if severity in [ThreatSeverity.CRITICAL, ThreatSeverity.HIGH]:
            return False

        # Liberar apenas se severidade é LOW e não há indicadores críticos
        if severity == ThreatSeverity.LOW:
            indicators = classification.get("indicators", [])
            critical_indicators = [
                "root",
                "encrypted",
                "unauthorized",
                "privilege_escalation",
            ]
            if not any(ind in str(indicators).lower() for ind in critical_indicators):
                return True

        return False

    def _calculate_confidence(self, patterns: List[str], evidence: Dict[str, Any]) -> float:
        """Calcula confiança na análise.

        Args:
            patterns: Padrões detectados
            evidence: Evidências

        Returns:
            Confiança (0.0 a 1.0)
        """
        confidence = 0.5  # Base

        # Mais padrões = maior confiança
        if len(patterns) > 0:
            confidence += min(0.3, len(patterns) * 0.05)

        # Mais evidências = maior confiança
        if len(evidence) > 5:
            confidence += 0.1

        # Evidências específicas aumentam confiança
        if "source_ip" in evidence:
            confidence += 0.05
        if "process_id" in evidence:
            confidence += 0.05

        return min(1.0, confidence)

    def get_analysis_history(self, limit: int = 10) -> List[ForensicReport]:
        """Obtém histórico de análises.

        Args:
            limit: Limite de análises a retornar

        Returns:
            Lista de relatórios forenses
        """
        return self.analysis_history[-limit:]
