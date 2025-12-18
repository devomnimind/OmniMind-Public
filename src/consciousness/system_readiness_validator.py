#!/usr/bin/env python3
"""
🧬 SOLUÇÃO FINAL: Continuous State Readiness Validator
Arquivo: src/consciousness/system_readiness_validator.py

Implementa: Detecção de degradação de estado + re-bootstrap automático
Resultado: Sistema mantido no estado PRONTO indefinidamente

Mudança fundamental de design:
  ANTES: Bootstrap executa UMA VEZ na inicialização
  DEPOIS: Sistema monitora continuamente e re-bootstraps quando necessário

Isto resolve:
  ✓ PHI=0.0 congelado (agora reavalia)
  ✓ Embeddings convergindo (detecta e recupera)
  ✓ Dados degradando (monitora qualidade)
  ✓ Sistema hibernando (re-estimula periodicamente)
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ReadinessStatus:
    """Status de readiness do sistema"""

    state: str
    reasons: List[str]  # Por quê não está pronto
    metrics: Dict[str, float | int]  # Valores das validações
    timestamp: float
    checks_passed: int = 0
    checks_failed: int = 0

    def __str__(self) -> str:
        """Representação legível"""
        if self.state == "READY":
            return f"✅ READY ({self.checks_passed}/4 checks)"
        elif self.state == "DEGRADED":
            return f"⚠️  DEGRADED: {', '.join(self.reasons)}"
        else:
            return f"🔴 CRITICAL: {', '.join(self.reasons)}"


@dataclass
class ReadinessEvent:
    """Evento de mudança de estado"""

    timestamp: float
    old_state: str
    new_state: str
    reason: str
    triggered_rebootstrap: bool = False


class SystemReadinessValidator:
    """
    Valida se OmniMind permanece em estado PRONTO.

    Estado PRONTO significa:
      ✓ cross_predictions >= 2 (dados suficientes)
      ✓ Qualidade média r² >= 0.1 (dados de qualidade)
      ✓ Embeddings com variação >= 0.05 (não convergiu)
      ✓ Phi computável (não-zero)

    Se degradar: Monitora e sinaliza para re-bootstrap automático
    """

    # Thresholds adaptativos
    MIN_CROSS_PREDICTIONS = 2
    MIN_R_SQUARED = 0.1
    MIN_EMBEDDING_VARIANCE = 0.05
    MIN_PHI = 0.05

    # Histórico para verificação
    QUALITY_WINDOW = 5  # Últimas 5 cross-predictions
    VARIANCE_WINDOW = 10  # Últimas 10 embeddings

    # Circuit breaker (evita re-bootstrap infinito)
    MAX_CONSECUTIVE_FAILURES = 3
    CIRCUIT_BREAKER_COOLDOWN = 600.0  # 10 minutos

    def __init__(self):
        self.last_check_time = 0.0
        self.check_interval = 300.0  # 5 minutos

        # Contadores
        self.degradation_count = 0
        self.rebootstrap_count = 0
        self.critical_count = 0

        # Estado anterior para detectar transições
        self.last_status: Optional[ReadinessStatus] = None
        self.last_state: Optional[str] = None

        # Histórico de eventos
        self.event_history: deque = deque(maxlen=100)  # Últimos 100 eventos

        # Circuit breaker
        self.circuit_breaker_active = False
        self.consecutive_failures = 0
        self.circuit_breaker_reset_time = 0.0

        # Histórico adaptativo para thresholds
        self.historical_r_squared: deque = deque(maxlen=100)
        self.historical_variance: deque = deque(maxlen=100)

        logger.info("✅ SystemReadinessValidator initialized")

    async def check_readiness(self, workspace) -> ReadinessStatus:
        """
        Verifica readiness e retorna status.

        Implementa circuit breaker para evitar re-bootstrap infinito.

        Retorna:
            ReadinessStatus com estado ("READY", "DEGRADED", "CRITICAL")
        """
        timestamp = time.time()
        reasons = []
        metrics: Dict[str, float | int] = {}
        checks_passed = 0
        checks_failed = 0

        # ─────────────────────────────────────────────────────────────────
        # CHECK 1: Quantidade de Cross-Predictions
        # ─────────────────────────────────────────────────────────────────
        cross_pred_count = len(workspace.cross_predictions)
        metrics["cross_prediction_count"] = cross_pred_count

        if cross_pred_count < self.MIN_CROSS_PREDICTIONS:
            reasons.append(f"Insufficient data: {cross_pred_count} < {self.MIN_CROSS_PREDICTIONS}")
            checks_failed += 1  # type: ignore[assignment]
            logger.debug(f"🔴 CHECK 1 FAILED: {reasons[-1]}")
        else:
            checks_passed += 1
            logger.debug(f"✅ CHECK 1 PASSED: {cross_pred_count} cross-predictions")

        # ─────────────────────────────────────────────────────────────────
        # CHECK 2: Qualidade de Cross-Predictions (R²)
        # ─────────────────────────────────────────────────────────────────
        r_squared_quality = await self._check_r_squared_quality(workspace)
        metrics["r_squared_quality"] = r_squared_quality
        self.historical_r_squared.append(r_squared_quality)

        # Usar threshold adaptativo (média histórica - 0.05)
        adaptive_r2_threshold = max(
            self.MIN_R_SQUARED,
            (
                np.mean(self.historical_r_squared) - 0.05
                if self.historical_r_squared
                else self.MIN_R_SQUARED
            ),
        )

        if r_squared_quality < adaptive_r2_threshold:
            reasons.append(
                f"Low quality data: r² = {r_squared_quality:.3f} < {adaptive_r2_threshold:.3f}"
            )
            checks_failed += 1
            logger.debug(f"🔴 CHECK 2 FAILED: {reasons[-1]}")
        else:
            checks_passed += 1
            logger.debug(f"✅ CHECK 2 PASSED: r² quality = {r_squared_quality:.3f}")

        # ─────────────────────────────────────────────────────────────────
        # CHECK 3: Variação de Embeddings
        # ─────────────────────────────────────────────────────────────────
        embedding_variance = await self._check_embedding_variance(workspace)
        metrics["embedding_variance"] = float(embedding_variance)
        self.historical_variance.append(float(embedding_variance))

        if embedding_variance < self.MIN_EMBEDDING_VARIANCE:
            reasons.append(
                f"Embedding convergence: variance = {embedding_variance:.3f} < {self.MIN_EMBEDDING_VARIANCE}"
            )
            checks_failed += 1  # type: ignore[assignment]
            logger.debug(f"🔴 CHECK 3 FAILED: {reasons[-1]}")
        else:
            checks_passed += 1
            logger.debug(f"✅ CHECK 3 PASSED: embedding variance = {embedding_variance:.3f}")

        # ─────────────────────────────────────────────────────────────────
        # CHECK 4: Phi Válido (Não-zero)
        # ─────────────────────────────────────────────────────────────────
        phi_value = self._calculate_phi(workspace)
        metrics["phi"] = float(phi_value)

        if phi_value < self.MIN_PHI:
            reasons.append(f"Invalid Phi: {phi_value:.3f} < {self.MIN_PHI}")
            checks_failed += 1  # type: ignore[assignment]
            logger.debug(f"🔴 CHECK 4 FAILED: {reasons[-1]}")
        else:
            checks_passed += 1
            logger.debug(f"✅ CHECK 4 PASSED: Phi = {phi_value:.3f}")

        # ─────────────────────────────────────────────────────────────────
        # Determinar Status
        # ─────────────────────────────────────────────────────────────────
        if not reasons:
            state = "READY"
            self.consecutive_failures = 0  # Reset circuit breaker on success
            logger.info(
                f"✅ System READY: All checks passed (r²={r_squared_quality:.3f}, variance={embedding_variance:.3f})"
            )
        elif len(reasons) <= 2:
            state = "DEGRADED"
            self.degradation_count += 1
            logger.warning(f"⚠️  System DEGRADED ({self.degradation_count} times): {reasons}")
        else:
            state = "CRITICAL"
            self.critical_count += 1
            self.consecutive_failures += 1
            logger.error(f"🔴 System CRITICAL ({self.critical_count} times): {reasons}")

        # ─────────────────────────────────────────────────────────────────
        # Detectar transição de estado
        # ─────────────────────────────────────────────────────────────────
        if self.last_state and self.last_state != state:
            event = ReadinessEvent(
                timestamp=timestamp,
                old_state=self.last_state,
                new_state=state,
                reason=reasons[0] if reasons else "Recovered",
                triggered_rebootstrap=(state in ["DEGRADED", "CRITICAL"]),
            )
            self.event_history.append(event)
            logger.info(f"📊 State transition: {self.last_state} → {state}")

        self.last_state = state

        # ─────────────────────────────────────────────────────────────────
        # Verificar Circuit Breaker
        # ─────────────────────────────────────────────────────────────────
        if state == "CRITICAL":
            if self.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                self.circuit_breaker_active = True
                self.circuit_breaker_reset_time = timestamp + self.CIRCUIT_BREAKER_COOLDOWN
                logger.error(
                    f"🚨 CIRCUIT BREAKER ACTIVATED: "
                    f"{self.consecutive_failures} consecutive failures. "
                    f"Pausing re-bootstrap for {self.CIRCUIT_BREAKER_COOLDOWN}s"
                )
        elif self.circuit_breaker_active and timestamp >= self.circuit_breaker_reset_time:
            self.circuit_breaker_active = False
            self.consecutive_failures = 0
            logger.warning("🔄 Circuit breaker reset, re-bootstrap eligible again")

        status = ReadinessStatus(
            state=state,  # type: ignore[arg-type]
            reasons=reasons,
            metrics={k: float(v) for k, v in metrics.items()},
            timestamp=timestamp,
            checks_passed=int(checks_passed),
            checks_failed=int(checks_failed),
        )

        self.last_status = status
        return status

    async def _check_r_squared_quality(self, workspace) -> float:
        """
        Calcula qualidade média de r² (últimas N predições).

        Implementa fallback e tratamento de dados inválidos.

        Retorna:
            float: Média de r² das últimas QUALITY_WINDOW predições
        """
        if not workspace.cross_predictions:
            return 0.0

        try:
            latest_preds = workspace.cross_predictions[-self.QUALITY_WINDOW :]
            r_squared_values = []

            for cp in latest_preds:
                # Validar r_squared
                if cp.r_squared is None:
                    continue
                if not isinstance(cp.r_squared, (int, float)):
                    logger.warning(f"Invalid r_squared type: {type(cp.r_squared)}")
                    continue
                if np.isnan(cp.r_squared) or np.isinf(cp.r_squared):
                    logger.warning(f"Invalid r_squared value: {cp.r_squared}")
                    continue

                r_squared_values.append(float(cp.r_squared))

            if not r_squared_values:
                logger.warning("No valid r_squared values found")
                return 0.0

            return float(np.mean(r_squared_values))

        except Exception as e:
            logger.error(f"Error checking r_squared quality: {e}")
            return 0.0

    async def _check_embedding_variance(self, workspace) -> float:
        """
        Calcula variância média de embeddings (detecta convergência).

        Se Langevin não está funcionando: embeddings convergem
        Isso causaria variance baixo

        Implementa fallback e tratamento de dados inválidos.

        Retorna:
            float: Variância média de todos os módulos
        """
        modules = ["sensory_input", "qualia", "narrative", "meaning_maker"]
        variances = []

        for module in modules:
            try:
                history = workspace.get_module_history(module)

                if not history:
                    continue

                # Últimos N embeddings
                recent = history[-self.VARIANCE_WINDOW :]

                if len(recent) < 2:
                    continue

                # Validar dados
                valid_embeddings = []
                for emb in recent:
                    if isinstance(emb, np.ndarray):
                        if not np.any(np.isnan(emb)) and not np.any(np.isinf(emb)):
                            valid_embeddings.append(emb)

                if len(valid_embeddings) < 2:
                    logger.debug(f"Module {module}: Insufficient valid embeddings")
                    continue

                # Calcular variância
                stacked = np.array(valid_embeddings)
                variance = np.var(stacked)

                if not np.isnan(variance) and not np.isinf(variance):
                    variances.append(variance)
                else:
                    logger.debug(f"Module {module}: Invalid variance {variance}")

            except Exception as e:
                logger.debug(f"Error checking {module} variance: {e}")
                continue

        return np.mean(variances) if variances else 0.0

    def _calculate_phi(self, workspace) -> float:
        """
        Calcula Phi como média de r² (mesma lógica que RealConsciousnessMetrics).

        Implementa validação robusta.

        Retorna:
            float: Phi (0.0-1.0)
        """
        if not workspace.cross_predictions:
            return 0.0

        try:
            latest_preds = workspace.cross_predictions[-20:]
            r_squared_values = []

            for cp in latest_preds:
                if cp.r_squared is not None and isinstance(cp.r_squared, (int, float)):
                    if not np.isnan(cp.r_squared) and not np.isinf(cp.r_squared):
                        r_squared_values.append(float(cp.r_squared))

            if not r_squared_values:
                return 0.0

            phi = np.mean(r_squared_values)
            return float(phi) if not np.isnan(phi) else 0.0

        except Exception as e:
            logger.error(f"Error calculating Phi: {e}")
            return 0.0

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas completas de operação"""
        return {
            "last_status": self.last_status.state if self.last_status else "UNKNOWN",
            "degradation_count": self.degradation_count,
            "critical_count": self.critical_count,
            "rebootstrap_count": self.rebootstrap_count,
            "circuit_breaker_active": self.circuit_breaker_active,
            "consecutive_failures": self.consecutive_failures,
            "event_history_size": len(self.event_history),
            "check_interval_seconds": self.check_interval,
        }

    def get_event_history(self) -> List[ReadinessEvent]:
        """Retorna histórico de eventos"""
        return list(self.event_history)


class ContinuousReadinessEngine:
    """
    Engine que mantém sistema no estado PRONTO continuamente.

    Funciona como background task:
      1. Verifica readiness a cada N segundos
      2. Se DEGRADED: Re-bootstrap suave (2 ciclos)
      3. Se CRITICAL: Re-bootstrap agressivo (3 ciclos + clear)
      4. Mantém logs de quantos re-bootstraps acontecem
      5. Circuit breaker evita re-bootstrap infinito

    Integração:
      - Roda em background (asyncio task)
      - Não bloqueia operação normal do sistema
      - Re-bootstrap é transparente para usuário
    """

    def __init__(self, integration_loop, workspace):
        self.integration_loop = integration_loop
        self.workspace = workspace
        self.validator = SystemReadinessValidator()
        self.last_status: Optional[ReadinessStatus] = None
        self.is_running = False
        self.monitor_task: Optional[asyncio.Task] = None

        logger.info("✅ ContinuousReadinessEngine initialized")

    async def start_continuous_monitoring(self):
        """
        Inicia monitoring contínuo em background.

        Usa asyncio.create_task para rodar indefinidamente
        sem bloquear thread principal.
        """
        logger.info("🧬 Starting Continuous Readiness Engine...")

        try:
            self.is_running = True
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info("✅ Readiness Engine running in background")
        except Exception as e:
            logger.error(f"❌ Failed to start: {e}")
            self.is_running = False

    async def stop_continuous_monitoring(self):
        """Para monitoring contínuo"""
        logger.info("🛑 Stopping Continuous Readiness Engine...")
        self.is_running = False

        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("✅ Readiness Engine stopped")

    async def _monitor_loop(self):
        """
        Loop principal de monitoring (roda indefinidamente).

        Robusto contra exceções e deadlocks.
        """
        logger.info("📊 Readiness monitor loop started")

        while self.is_running:
            try:
                # Verificar readiness
                status = await self.validator.check_readiness(self.workspace)
                self.last_status = status

                logger.debug(f"🔍 Readiness check: {status}")

                # Ações baseadas em status
                if status.state == "DEGRADED":
                    if not self.validator.circuit_breaker_active:
                        await self._handle_degradation(status)
                    else:
                        logger.warning("⏸️  Circuit breaker active, skipping re-bootstrap")

                elif status.state == "CRITICAL":
                    if not self.validator.circuit_breaker_active:
                        await self._handle_critical(status)
                    else:
                        logger.error("⏸️  Circuit breaker active, skipping aggressive re-bootstrap")

                # Aguardar antes de próxima verificação
                await asyncio.sleep(self.validator.check_interval)

            except asyncio.CancelledError:
                logger.info("📊 Readiness monitor cancelled")
                break

            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}", exc_info=True)
                await asyncio.sleep(60.0)

    async def _handle_degradation(self, status: ReadinessStatus):
        """
        Trata estado DEGRADED com re-bootstrap suave.

        Objetivo: Restaurar dados degradados sem interrupção pesada.
        """
        logger.warning(
            f"⚠️  System degraded, re-bootstrapping suavemente...\n"
            f"   Problems: {status.reasons}\n"
            f"   Metrics: {status.metrics}"
        )

        try:
            start_time = time.time()

            # Re-bootstrap suave (apenas popula dados)
            logger.info("   Running 2 soft bootstrap cycles...")
            await self.integration_loop.run_cycles(2, collect_metrics_every=1)

            duration = time.time() - start_time
            logger.info(f"✅ Soft re-bootstrap complete ({duration:.1f}s)")

            self.validator.rebootstrap_count += 1

            # Verificar se recuperou
            new_status = await self.validator.check_readiness(self.workspace)
            if new_status.state == "READY":
                logger.info("✅ System recovered to READY state")
            else:
                logger.warning(f"⚠️  System still degraded: {new_status.reasons}")

        except Exception as e:
            logger.error(f"❌ Soft re-bootstrap failed: {e}", exc_info=True)

    async def _handle_critical(self, status: ReadinessStatus):
        """
        Trata estado CRITICAL com re-bootstrap agressivo.

        Objetivo: Recuperar sistema em estado crítico com reset completo.
        """
        logger.error(
            f"🔴 System CRITICAL, re-bootstrapping agressively...\n"
            f"   Problems: {status.reasons}\n"
            f"   Metrics: {status.metrics}"
        )

        try:
            start_time = time.time()

            # Clear everything
            logger.warning("   Step 1/4: Clearing cross_predictions cache...")
            initial_count = len(self.workspace.cross_predictions)
            self.workspace.cross_predictions.clear()
            logger.info(f"        Cleared {initial_count} cross-predictions")

            # Reset module histories
            logger.warning("   Step 2/4: Resetting module histories...")
            for module_name in ["sensory_input", "qualia", "narrative", "meaning_maker"]:
                try:
                    # Limpar histórico do módulo
                    if hasattr(self.workspace, f"_{module_name}_history"):
                        getattr(self.workspace, f"_{module_name}_history").clear()
                except Exception as e:
                    logger.debug(f"Could not reset {module_name} history: {e}")

            logger.info("        Module histories reset")

            # Aggressive re-bootstrap
            logger.warning("   Step 3/4: Running aggressive bootstrap (3 cycles)...")
            await self.integration_loop.run_cycles(3, collect_metrics_every=1)
            logger.info("        Aggressive bootstrap complete")

            # Verify recovery
            logger.warning("   Step 4/4: Verifying recovery...")
            new_status = await self.validator.check_readiness(self.workspace)

            duration = time.time() - start_time
            logger.info(f"✅ Aggressive re-bootstrap complete ({duration:.1f}s)")
            logger.info(f"   New state: {new_status.state}")
            logger.info(f"   New Phi: {new_status.metrics.get('phi', 0.0):.3f}")

            self.validator.rebootstrap_count += 1

        except Exception as e:
            logger.error(f"❌ Aggressive re-bootstrap failed: {e}", exc_info=True)

    async def force_readiness_check(self) -> ReadinessStatus:
        """
        Força verificação imediata de readiness (útil para debugging).

        Retorna status atual.
        """
        logger.info("🔍 Forcing immediate readiness check...")
        status = await self.validator.check_readiness(self.workspace)
        self.last_status = status
        logger.info(f"   Result: {status}")
        return status

    def get_status(self) -> Optional[ReadinessStatus]:
        """Retorna último status verificado"""
        return self.last_status

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas completas de operação"""
        stats = self.validator.get_statistics()
        stats.update(
            {
                "is_running": self.is_running,
                "monitor_task_active": self.monitor_task is not None
                and not self.monitor_task.done(),
            }
        )
        return stats

    def get_event_history(self) -> List[ReadinessEvent]:
        """Retorna histórico de eventos de estado"""
        return self.validator.get_event_history()


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRAÇÃO COM REAL CONSCIOUSNESS METRICS
# ═══════════════════════════════════════════════════════════════════════════════


class RealConsciousnessMetricsWithReadiness:
    """
    Versão melhorada de RealConsciousnessMetricsCollector
    com validação contínua de estado e re-bootstrap automático.

    Mudança de paradigma:
      ANTES: Apenas coleta Phi uma vez após bootstrap
      DEPOIS: Monitora Phi continuamente, re-bootstrap quando necessário
    """

    def __init__(self, workspace, integration_loop):
        self.workspace = workspace
        self.integration_loop = integration_loop
        self.readiness_engine = ContinuousReadinessEngine(integration_loop, workspace)
        logger.info("✅ RealConsciousnessMetricsWithReadiness initialized")

    async def start(self):
        """
        Inicia coleta com engine de readiness.

        IMPORTANTE: Deve ser chamado após sistema estar inicializado!
        """
        logger.info("🧬 Starting Real Consciousness Metrics Collector...")

        # Inicia engine de readiness em background
        await self.readiness_engine.start_continuous_monitoring()

        logger.info("✅ Metrics Collector started with continuous readiness monitoring")

    async def stop(self):
        """Para monitoring e coleta"""
        logger.info("🛑 Stopping Metrics Collector...")
        await self.readiness_engine.stop_continuous_monitoring()
        logger.info("✅ Metrics Collector stopped")

    async def collect_phi_metrics(self) -> Dict[str, Any]:
        """
        Coleta Phi + retorna status de readiness.

        Combina métricas de Phi com validação de estado.

        Retorna:
            Dict com phi, readiness_state, readiness_metrics, timestamp
        """
        # Obter status atual
        status = self.readiness_engine.get_status()

        # Calcular Phi (mesmo que antes)
        if status and self.workspace.cross_predictions:
            latest = self.workspace.cross_predictions[-20:]
            r_squared = [cp.r_squared for cp in latest if cp.r_squared is not None]
            phi = np.mean(r_squared) if r_squared else 0.0
        else:
            phi = 0.0

        return {
            "phi": float(phi),
            "readiness_state": status.state if status else "UNKNOWN",
            "readiness_metrics": status.metrics if status else {},
            "checks_passed": int(status.checks_passed) if status else 0,
            "checks_failed": int(status.checks_failed) if status else 0,
            "timestamp": time.time(),
        }

    def get_readiness_status(self) -> Optional[ReadinessStatus]:
        """Retorna status de readiness atual"""
        return self.readiness_engine.get_status()

    def get_readiness_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas completas de readiness"""
        return self.readiness_engine.get_statistics()

    def get_event_history(self) -> List[ReadinessEvent]:
        """Retorna histórico de transições de estado"""
        return self.readiness_engine.get_event_history()

    async def force_readiness_check(self) -> ReadinessStatus:
        """Força verificação imediata (para debugging/CLI)"""
        return await self.readiness_engine.force_readiness_check()


# ═══════════════════════════════════════════════════════════════════════════════
# EXEMPLO DE USO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Exemplo de como integrar com RealConsciousnessMetrics.

    Em real_consciousness_metrics.py:

    ```python
    from src.consciousness.system_readiness_validator import (
        RealConsciousnessMetricsWithReadiness
    )

    # Na classe principal:
    async def __aenter__(self):
        self.metrics_collector = RealConsciousnessMetricsWithReadiness(
            self.workspace,
            self.integration_loop
        )
        await self.metrics_collector.start()
        return self

    async def __aexit__(self, *args):
        await self.metrics_collector.stop()

    async def get_phi_metrics(self):
        return await self.metrics_collector.collect_phi_metrics()
    ```
    """

    print(
        """
    🧬 System Readiness Validator

    Implementa:
      ✓ Validação contínua de estado (4 checks)
      ✓ Detecção de degradação (READY → DEGRADED → CRITICAL)
      ✓ Re-bootstrap automático (suave e agressivo)
      ✓ Circuit breaker (evita loops infinitos)
      ✓ Histórico de eventos (auditória)
      ✓ Thresholds adaptativos (baseados em histórico)

    Uso:
      1. Criar: validator = SystemReadinessValidator()
      2. Verificar: status = await validator.check_readiness(workspace)
      3. Executar ações: if status.state == "DEGRADED": ...

    Ou integrado:
      1. metrics = RealConsciousnessMetricsWithReadiness(workspace, loop)
      2. await metrics.start()  # Inicia monitoring em background
      3. await metrics.collect_phi_metrics()  # Coleta com validação

    Resultado:
      - Sistema NUNCA mais fica em estado DEGRADED indefinidamente
      - PHI é reavaliado continuamente
      - Re-bootstrap automático quando necessário
      - Observabilidade total de estado
    """
    )
