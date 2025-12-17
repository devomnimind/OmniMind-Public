"""API de Explicabilidade - Endpoints para consultar decisões do Orchestrator.

Implementa Sessão 6 da Auditoria do Orchestrator:
- Consulta de decisões autônomas
- Filtros por ação, data, resultado
- Exportação de relatórios
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


class DecisionSummary(BaseModel):
    """Resumo de uma decisão."""

    action: str = Field(..., description="Ação executada")
    timestamp: float = Field(..., description="Timestamp da decisão")
    can_execute: bool = Field(..., description="Se a ação foi permitida")
    reason: str = Field(..., description="Razão da decisão")
    trust_level: float = Field(..., description="Nível de confiança")
    success: Optional[bool] = Field(None, description="Se a ação foi bem-sucedida")


class DecisionDetail(BaseModel):
    """Detalhes completos de uma decisão."""

    action: str
    timestamp: float
    context: Dict[str, Any]
    permission_result: Dict[str, Any]
    trust_level: float
    alternatives_considered: List[str]
    expected_impact: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    decision_rationale: str
    success: Optional[bool] = None
    error: Optional[str] = None


class DecisionFilter(BaseModel):
    """Filtros para consulta de decisões."""

    action: Optional[str] = None
    start_date: Optional[float] = None
    end_date: Optional[float] = None
    success: Optional[bool] = None
    min_trust_level: Optional[float] = None
    limit: int = Field(default=100, ge=1, le=1000)


class DecisionStats(BaseModel):
    """Estatísticas de decisões."""

    total_decisions: int
    successful_decisions: int
    failed_decisions: int
    success_rate: float
    average_trust_level: float
    decisions_by_action: Dict[str, int]
    decisions_by_reason: Dict[str, int]


# Armazenamento em memória (em produção, usar banco de dados)
_decisions_store: List[Dict[str, Any]] = []


def register_decision(explanation: Dict[str, Any], success: Optional[bool] = None) -> None:
    """Registra uma decisão para consulta via API.

    Args:
        explanation: Explicação da decisão (DecisionExplanation)
        success: Se a ação foi bem-sucedida
    """
    decision_record = {
        "action": explanation.get("action"),
        "timestamp": explanation.get("timestamp", 0.0),
        "context": explanation.get("context", {}),
        "permission_result": explanation.get("permission_result", {}),
        "trust_level": explanation.get("trust_level", 0.5),
        "alternatives_considered": explanation.get("alternatives_considered", []),
        "expected_impact": explanation.get("expected_impact", {}),
        "risk_assessment": explanation.get("risk_assessment", {}),
        "decision_rationale": explanation.get("decision_rationale", ""),
        "success": success,
        "error": explanation.get("error"),
    }
    _decisions_store.append(decision_record)

    # Limitar tamanho do store (manter últimas 10000 decisões)
    if len(_decisions_store) > 10000:
        _decisions_store.pop(0)

    logger.debug("Decisão registrada: %s (sucesso: %s)", decision_record["action"], success)


@router.get("/", response_model=List[DecisionSummary])
async def list_decisions(
    action: Optional[str] = Query(None, description="Filtrar por ação"),
    start_date: Optional[float] = Query(None, description="Data inicial (timestamp)"),
    end_date: Optional[float] = Query(None, description="Data final (timestamp)"),
    success: Optional[bool] = Query(None, description="Filtrar por sucesso"),
    min_trust_level: Optional[float] = Query(
        None, ge=0.0, le=1.0, description="Nível mínimo de confiança"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de resultados"),
) -> List[DecisionSummary]:
    """Lista decisões do Orchestrator com filtros.

    Args:
        action: Filtrar por ação específica
        start_date: Data inicial (timestamp)
        end_date: Data final (timestamp)
        success: Filtrar por sucesso (True/False)
        min_trust_level: Nível mínimo de confiança
        limit: Número máximo de resultados

    Returns:
        Lista de resumos de decisões
    """
    filtered = _decisions_store.copy()

    # Aplicar filtros
    if action:
        filtered = [d for d in filtered if d.get("action") == action]

    if start_date:
        filtered = [d for d in filtered if d.get("timestamp", 0) >= start_date]

    if end_date:
        filtered = [d for d in filtered if d.get("timestamp", 0) <= end_date]

    if success is not None:
        filtered = [d for d in filtered if d.get("success") == success]

    if min_trust_level is not None:
        filtered = [d for d in filtered if d.get("trust_level", 0) >= min_trust_level]

    # Ordenar por timestamp (mais recentes primeiro)
    filtered.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    # Limitar resultados
    filtered = filtered[:limit]

    # Converter para DecisionSummary
    summaries = []
    for decision in filtered:
        permission_result = decision.get("permission_result", {})
        summaries.append(
            DecisionSummary(
                action=decision.get("action", "unknown"),
                timestamp=decision.get("timestamp", 0.0),
                can_execute=permission_result.get("can_execute", False),
                reason=permission_result.get("reason", "unknown"),
                trust_level=decision.get("trust_level", 0.5),
                success=decision.get("success"),
            )
        )

    logger.info(
        "Listando %d decisões (filtros: action=%s, success=%s)", len(summaries), action, success
    )
    return summaries


@router.get("/{decision_id}", response_model=DecisionDetail)
async def get_decision(decision_id: int) -> DecisionDetail:
    """Obtém detalhes completos de uma decisão específica.

    Args:
        decision_id: Índice da decisão (0 = mais recente)

    Returns:
        Detalhes completos da decisão

    Raises:
        HTTPException: Se decisão não encontrada
    """
    if decision_id < 0 or decision_id >= len(_decisions_store):
        raise HTTPException(status_code=404, detail=f"Decisão {decision_id} não encontrada")

    # Ordenar por timestamp (mais recentes primeiro)
    sorted_decisions = sorted(_decisions_store, key=lambda x: x.get("timestamp", 0), reverse=True)
    decision = sorted_decisions[decision_id]

    return DecisionDetail(
        action=decision.get("action", "unknown"),
        timestamp=decision.get("timestamp", 0.0),
        context=decision.get("context", {}),
        permission_result=decision.get("permission_result", {}),
        trust_level=decision.get("trust_level", 0.5),
        alternatives_considered=decision.get("alternatives_considered", []),
        expected_impact=decision.get("expected_impact", {}),
        risk_assessment=decision.get("risk_assessment", {}),
        decision_rationale=decision.get("decision_rationale", ""),
        success=decision.get("success"),
        error=decision.get("error"),
    )


@router.get("/stats/summary", response_model=DecisionStats)
async def get_decision_stats() -> DecisionStats:
    """Obtém estatísticas agregadas de decisões.

    Returns:
        Estatísticas de decisões
    """
    if not _decisions_store:
        return DecisionStats(
            total_decisions=0,
            successful_decisions=0,
            failed_decisions=0,
            success_rate=0.0,
            average_trust_level=0.0,
            decisions_by_action={},
            decisions_by_reason={},
        )

    total = len(_decisions_store)
    successful = sum(1 for d in _decisions_store if d.get("success") is True)
    failed = sum(1 for d in _decisions_store if d.get("success") is False)
    success_rate = (successful / total) if total > 0 else 0.0

    trust_levels = [d.get("trust_level", 0.5) for d in _decisions_store]
    avg_trust = sum(trust_levels) / len(trust_levels) if trust_levels else 0.0

    # Contar por ação
    actions_count: Dict[str, int] = {}
    for decision in _decisions_store:
        action = decision.get("action", "unknown")
        actions_count[action] = actions_count.get(action, 0) + 1

    # Contar por razão
    reasons_count: Dict[str, int] = {}
    for decision in _decisions_store:
        reason = decision.get("permission_result", {}).get("reason", "unknown")
        reasons_count[reason] = reasons_count.get(reason, 0) + 1

    return DecisionStats(
        total_decisions=total,
        successful_decisions=successful,
        failed_decisions=failed,
        success_rate=success_rate,
        average_trust_level=avg_trust,
        decisions_by_action=actions_count,
        decisions_by_reason=reasons_count,
    )


@router.get("/export/json")
async def export_decisions_json(
    action: Optional[str] = Query(None, description="Filtrar por ação"),
    start_date: Optional[float] = Query(None, description="Data inicial"),
    end_date: Optional[float] = Query(None, description="Data final"),
    limit: int = Query(1000, ge=1, le=10000, description="Número máximo de resultados"),
) -> Dict[str, Any]:
    """Exporta decisões em formato JSON.

    Args:
        action: Filtrar por ação
        start_date: Data inicial
        end_date: Data final
        limit: Número máximo de resultados

    Returns:
        JSON com todas as decisões filtradas
    """
    # Reutilizar lógica de list_decisions
    summaries = await list_decisions(action, start_date, end_date, None, None, limit)

    # Buscar detalhes completos
    sorted_decisions = sorted(_decisions_store, key=lambda x: x.get("timestamp", 0), reverse=True)
    filtered_details = []
    for summary in summaries:
        # Encontrar decisão correspondente
        for decision in sorted_decisions:
            if (
                decision.get("action") == summary.action
                and decision.get("timestamp") == summary.timestamp
            ):
                filtered_details.append(decision)
                break

    return {
        "export_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_decisions": len(filtered_details),
        "filters": {
            "action": action,
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
        },
        "decisions": filtered_details,
    }


@router.delete("/")
async def clear_decisions() -> Dict[str, str]:
    """Limpa todas as decisões armazenadas.

    Returns:
        Confirmação de limpeza
    """
    count = len(_decisions_store)
    _decisions_store.clear()
    logger.warning("Todas as decisões foram limpas (%d removidas)", count)
    return {"message": f"{count} decisões removidas", "status": "cleared"}
