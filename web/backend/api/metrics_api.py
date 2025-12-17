"""
API de Métricas de Consciência em Tempo Real

Conforme Task 2.6.1, provê endpoints para:
1. GET /api/metrics/phi-timeseries - Série temporal de Φ
2. GET /api/metrics/modules - Métricas de todos os módulos
3. GET /api/metrics/health - Status de saúde do sistema

Author: OmniMind Team
Date: 2025-12-11
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(prefix="/api/metrics", tags=["metrics"])


class PhiDataPoint(BaseModel):
    """Ponto de dados de Φ."""
    
    timestamp: float = Field(..., description="Timestamp Unix")
    cycle: int = Field(..., description="Número do ciclo")
    value_nats: float = Field(..., description="Valor de Φ em nats")
    normalized: float = Field(..., description="Valor de Φ normalizado [0,1]")
    is_conscious: bool = Field(..., description="Se está acima do limiar de consciência")


class PhiTimeseriesResponse(BaseModel):
    """Resposta da série temporal de Φ."""
    
    data_points: List[PhiDataPoint] = Field(..., description="Lista de pontos de dados")
    total_points: int = Field(..., description="Total de pontos retornados")
    timespan_minutes: float = Field(..., description="Período de tempo coberto (minutos)")
    mean_phi: float = Field(..., description="Média de Φ no período")
    min_phi: float = Field(..., description="Mínimo de Φ no período")
    max_phi: float = Field(..., description="Máximo de Φ no período")


class ModuleMetrics(BaseModel):
    """Métricas de um módulo."""
    
    module_name: str
    timestamp: float
    metrics: Dict[str, Any]
    status: str = "unknown"  # "healthy", "warning", "critical", "silent"


class ModulesMetricsResponse(BaseModel):
    """Resposta de métricas de módulos."""
    
    modules: List[ModuleMetrics]
    total_modules: int
    timestamp: float


class HealthStatus(BaseModel):
    """Status de saúde do sistema."""
    
    status: str = Field(..., description="Status geral: healthy, degraded, critical")
    phi_status: str = Field(..., description="Status de Φ")
    phi_value: Optional[float] = Field(None, description="Valor atual de Φ em nats")
    total_modules: int
    healthy_modules: int
    warning_modules: int
    critical_modules: int
    silent_modules: int
    recommendations: List[str]
    timestamp: float


class MetricsStorage:
    """Gerenciador de armazenamento de métricas."""
    
    def __init__(self):
        self.data_dir = Path("data/metrics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics_file = self.data_dir / "metrics.jsonl"
        self.snapshot_file = self.data_dir / "metrics_snapshot_latest.json"
        self.health_file = self.data_dir / "health_report_latest.json"
    
    def load_timeseries(self, max_points: int = 100, hours: float = 2.0) -> List[Dict[str, Any]]:
        """
        Carrega série temporal de métricas.
        
        Args:
            max_points: Número máximo de pontos
            hours: Horas para trás a partir de agora
            
        Returns:
            Lista de snapshots de métricas
        """
        import time
        
        if not self.metrics_file.exists():
            return []
        
        # Calcular timestamp mínimo
        min_timestamp = time.time() - (hours * 3600)
        
        # Carregar métricas do JSONL
        metrics = []
        try:
            with open(self.metrics_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            snapshot = json.loads(line)
                            if snapshot.get("timestamp", 0) >= min_timestamp:
                                metrics.append(snapshot)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Erro ao carregar métricas: {e}")
        
        # Limitar número de pontos
        if len(metrics) > max_points:
            # Fazer downsampling uniforme
            step = len(metrics) // max_points
            metrics = metrics[::step]
        
        return metrics
    
    def load_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Carrega último snapshot de métricas.
        
        Returns:
            Snapshot de métricas ou None
        """
        if not self.snapshot_file.exists():
            return None
        
        try:
            with open(self.snapshot_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar snapshot: {e}")
            return None
    
    def load_health_report(self) -> Optional[Dict[str, Any]]:
        """
        Carrega último relatório de saúde.
        
        Returns:
            Relatório de saúde ou None
        """
        if not self.health_file.exists():
            return None
        
        try:
            with open(self.health_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar health report: {e}")
            return None


# Instância global do storage
metrics_storage = MetricsStorage()


@router.get(
    "/phi-timeseries",
    response_model=PhiTimeseriesResponse,
    summary="Série Temporal de Φ",
    description="Retorna série temporal de Φ (Phi) para as últimas N horas"
)
async def get_phi_timeseries(
    max_points: int = Query(100, ge=1, le=1000, description="Número máximo de pontos"),
    hours: float = Query(2.0, ge=0.1, le=24.0, description="Horas para trás")
) -> PhiTimeseriesResponse:
    """
    Obtém série temporal de Φ (Phi).
    
    Args:
        max_points: Número máximo de pontos a retornar
        hours: Horas para trás a partir de agora
        
    Returns:
        PhiTimeseriesResponse com dados de Φ
    """
    try:
        # Carregar timeseries
        metrics = metrics_storage.load_timeseries(max_points=max_points, hours=hours)
        
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma métrica disponível para o período especificado"
            )
        
        # Extrair pontos de Φ
        phi_points = []
        phi_values = []
        
        for snapshot in metrics:
            if "phi" in snapshot:
                phi_data = snapshot["phi"]
                phi_value = phi_data.get("value_nats")
                
                if phi_value is not None:
                    point = PhiDataPoint(
                        timestamp=snapshot.get("timestamp", 0.0),
                        cycle=snapshot.get("cycle", 0),
                        value_nats=phi_value,
                        normalized=phi_data.get("normalized", 0.0),
                        is_conscious=phi_data.get("is_conscious", False)
                    )
                    phi_points.append(point)
                    phi_values.append(phi_value)
        
        if not phi_points:
            raise HTTPException(
                status_code=404,
                detail="Nenhum dado de Φ disponível para o período especificado"
            )
        
        # Calcular estatísticas
        mean_phi = float(np.mean(phi_values))
        min_phi = float(np.min(phi_values))
        max_phi = float(np.max(phi_values))
        
        # Calcular timespan
        timestamps = [p.timestamp for p in phi_points]
        timespan_seconds = timestamps[-1] - timestamps[0]
        timespan_minutes = timespan_seconds / 60.0
        
        return PhiTimeseriesResponse(
            data_points=phi_points,
            total_points=len(phi_points),
            timespan_minutes=timespan_minutes,
            mean_phi=mean_phi,
            min_phi=min_phi,
            max_phi=max_phi
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao obter série temporal de Φ: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get(
    "/modules",
    response_model=ModulesMetricsResponse,
    summary="Métricas de Módulos",
    description="Retorna métricas de todos os módulos do sistema"
)
async def get_modules_metrics() -> ModulesMetricsResponse:
    """
    Obtém métricas de todos os módulos.
    
    Returns:
        ModulesMetricsResponse com métricas de todos os módulos
    """
    try:
        # Carregar último snapshot
        snapshot = metrics_storage.load_latest_snapshot()
        
        if not snapshot or "modules" not in snapshot:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma métrica de módulo disponível"
            )
        
        # Extrair métricas de módulos
        modules = []
        
        for module_name, module_metrics in snapshot["modules"].items():
            # Determinar status (simplificado - pode usar health report para precisão)
            timestamp = module_metrics.get("timestamp", 0.0)
            age_seconds = time.time() - timestamp
            
            if age_seconds > 300:  # 5 minutos
                status = "silent"
            else:
                status = "healthy"  # Simplificado
            
            modules.append(ModuleMetrics(
                module_name=module_name,
                timestamp=timestamp,
                metrics=module_metrics,
                status=status
            ))
        
        return ModulesMetricsResponse(
            modules=modules,
            total_modules=len(modules),
            timestamp=snapshot.get("timestamp", time.time())
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao obter métricas de módulos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get(
    "/health",
    response_model=HealthStatus,
    summary="Status de Saúde",
    description="Retorna status de saúde do sistema de métricas"
)
async def get_health_status() -> HealthStatus:
    """
    Obtém status de saúde do sistema.
    
    Returns:
        HealthStatus com status geral do sistema
    """
    try:
        # Carregar health report
        health_report = metrics_storage.load_health_report()
        
        if not health_report:
            # Fallback: criar report básico do snapshot
            snapshot = metrics_storage.load_latest_snapshot()
            
            if not snapshot:
                raise HTTPException(
                    status_code=404,
                    detail="Nenhum relatório de saúde ou snapshot disponível"
                )
            
            # Report básico
            phi_value = None
            phi_status = "unknown"
            
            if "phi" in snapshot:
                phi_value = snapshot["phi"].get("value_nats")
                if phi_value is not None:
                    if phi_value < 0.001:
                        phi_status = "critical"
                    elif phi_value < 0.01:
                        phi_status = "warning"
                    else:
                        phi_status = "healthy"
            
            total_modules = len(snapshot.get("modules", {}))
            
            return HealthStatus(
                status="unknown",
                phi_status=phi_status,
                phi_value=phi_value,
                total_modules=total_modules,
                healthy_modules=0,
                warning_modules=0,
                critical_modules=0,
                silent_modules=0,
                recommendations=["Execute health_check_metrics.py para análise completa"],
                timestamp=time.time()
            )
        
        # Usar health report
        modules = health_report.get("modules", [])
        
        # Contar status de módulos
        healthy = sum(1 for m in modules if m.get("status") == "healthy")
        warning = sum(1 for m in modules if m.get("status") == "warning")
        critical = sum(1 for m in modules if m.get("status") == "critical")
        silent = sum(1 for m in modules if m.get("status") == "silent")
        
        return HealthStatus(
            status=health_report.get("status", "unknown"),
            phi_status=health_report.get("phi_status", "unknown"),
            phi_value=health_report.get("phi_value"),
            total_modules=health_report.get("total_modules", 0),
            healthy_modules=healthy,
            warning_modules=warning,
            critical_modules=critical,
            silent_modules=silent,
            recommendations=health_report.get("recommendations", []),
            timestamp=health_report.get("timestamp", time.time())
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao obter status de saúde: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.get(
    "/latest",
    summary="Último Snapshot",
    description="Retorna último snapshot completo de métricas"
)
async def get_latest_snapshot() -> Dict[str, Any]:
    """
    Obtém último snapshot completo de métricas.
    
    Returns:
        Dict com snapshot completo
    """
    try:
        snapshot = metrics_storage.load_latest_snapshot()
        
        if not snapshot:
            raise HTTPException(
                status_code=404,
                detail="Nenhum snapshot disponível"
            )
        
        return snapshot
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao obter snapshot: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
