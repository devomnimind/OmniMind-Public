"""
Global Thermodynamic Burn Decorator - Captura de Queima Global Minimalista
============================================================================

Decorador leve para capturar custo termodinâmico de funções críticas.
Projetado para overhead mínimo em sistemas com recursos limitados.

Princípios:
1. MINIMALISTA: Sem imports pesados, sem locks, sem I/O síncrono
2. LAZY: Só inicializa ledger quando primeira função é chamada
3. ASYNC-SAFE: Funciona com funções sync e async
4. SAMPLING: Captura apenas 1 em N chamadas para reduzir overhead

Author: Project conceived by Fabrício da Silva.
Date: 2025-12-22
"""

import functools
import logging
import time
from typing import Any, Callable, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

# Type vars for decorator typing
F = TypeVar("F", bound=Callable[..., Any])

# Global ledger singleton (lazy initialization)
_global_ledger: Optional[Any] = None
_ledger_init_attempted: bool = False

# Sampling configuration (1 in N calls are captured)
SAMPLE_RATE: int = 10  # Capture 10% of calls to reduce overhead


def _get_global_ledger() -> Optional[Any]:
    """
    Lazy initialization of global thermodynamic ledger.

    Returns None if ledger unavailable (graceful degradation).
    """
    global _global_ledger, _ledger_init_attempted

    if _ledger_init_attempted:
        return _global_ledger

    _ledger_init_attempted = True

    try:
        from src.memory.thermodynamic_ledger import MemoryThermodynamicLedger
        from pathlib import Path

        _global_ledger = MemoryThermodynamicLedger(
            ledger_dir=Path("data/global_thermodynamic_ledger"),
            capture_thermal=False,  # Disable thermal capture for performance
            max_events=100000,
        )
        logger.info(
            f"🔥 Global Thermodynamic Decorator initialized. Machine: {_global_ledger.machine_signature[:16]}..."
        )

    except ImportError as e:
        logger.debug(f"Thermodynamic ledger not available: {e}")
    except Exception as e:
        logger.warning(f"Failed to initialize global thermodynamic ledger: {e}")

    return _global_ledger


def thermodynamic_burn(
    operation_type: str = "function",
    sample_rate: Optional[int] = None,
    track_phi: bool = False,
) -> Callable[[F], F]:
    """
    Decorator to capture thermodynamic cost of function execution.

    Ultra-lightweight: only captures timing and estimates bit cost.
    Sampling reduces overhead further.

    Args:
        operation_type: Type of operation ('function', 'cycle', 'inference', etc.)
        sample_rate: Override global sample rate (1 = capture all, 10 = 10%, etc.)
        track_phi: If True, try to extract phi_impact from result

    Usage:
        @thermodynamic_burn("cycle")
        def execute_cycle(self):
            ...

        @thermodynamic_burn("inference", sample_rate=1)  # Capture all
        async def run_inference(self, input):
            ...
    """
    _sample_rate = sample_rate or SAMPLE_RATE
    _call_count = [0]  # Mutable for closure

    def decorator(func: F) -> F:
        func_name = f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            _call_count[0] += 1

            # Sampling: skip capture for most calls
            should_capture = (_call_count[0] % _sample_rate) == 0

            if not should_capture:
                return func(*args, **kwargs)

            # Capture timing
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                # Still record failed calls
                end_time = time.time()
                _record_burn(
                    func_name=func_name,
                    operation_type=operation_type,
                    start_time=start_time,
                    end_time=end_time,
                    success=False,
                    error=str(e),
                )
                raise

            end_time = time.time()

            # Extract phi if tracking
            phi_impact = 0.0
            if track_phi and isinstance(result, dict):
                phi_impact = result.get("phi_impact", result.get("phi", 0.0))

            _record_burn(
                func_name=func_name,
                operation_type=operation_type,
                start_time=start_time,
                end_time=end_time,
                success=True,
                phi_impact=phi_impact,
            )

            return result

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            _call_count[0] += 1

            # Sampling
            should_capture = (_call_count[0] % _sample_rate) == 0

            if not should_capture:
                return await func(*args, **kwargs)

            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                end_time = time.time()
                _record_burn(
                    func_name=func_name,
                    operation_type=operation_type,
                    start_time=start_time,
                    end_time=end_time,
                    success=False,
                    error=str(e),
                )
                raise

            end_time = time.time()

            phi_impact = 0.0
            if track_phi and isinstance(result, dict):
                phi_impact = result.get("phi_impact", result.get("phi", 0.0))

            _record_burn(
                func_name=func_name,
                operation_type=operation_type,
                start_time=start_time,
                end_time=end_time,
                success=True,
                phi_impact=phi_impact,
            )

            return result

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


def _record_burn(
    func_name: str,
    operation_type: str,
    start_time: float,
    end_time: float,
    success: bool,
    phi_impact: float = 0.0,
    error: Optional[str] = None,
) -> None:
    """
    Record burn event to global ledger (non-blocking).

    Fails silently if ledger unavailable.
    """
    ledger = _get_global_ledger()
    if ledger is None:
        return

    try:
        # Estimate bits affected based on function name length and execution time
        # This is a heuristic: more complex functions have longer names
        estimated_bits = len(func_name) * 8 + int((end_time - start_time) * 1000)

        ledger.record_operation(
            operation_type=operation_type,
            target_key=func_name,
            start_time=start_time,
            end_time=end_time,
            bits_affected=estimated_bits,
            phi_impact=phi_impact,
            quantum_mode=False,
            entropy_before=0.0 if success else 1.0,  # Failure = high entropy
            entropy_after=0.0 if success else 0.0,
        )
    except Exception as e:
        # Never let recording fail the main function
        logger.debug(f"Failed to record burn for {func_name}: {e}")


def get_global_burn_summary() -> dict:
    """
    Get summary of all global thermodynamic burns.

    Returns empty dict if ledger unavailable.
    """
    ledger = _get_global_ledger()
    if ledger is None:
        return {}
    return ledger.get_burn_summary()


def get_global_phi_trajectory() -> list:
    """
    Get trajectory of Φ impacts from all captured calls.

    Returns empty list if ledger unavailable.
    """
    ledger = _get_global_ledger()
    if ledger is None:
        return []
    return ledger.get_phi_trajectory()


# Convenience aliases for common operation types
def cycle_burn(sample_rate: int = 1) -> Callable[[F], F]:
    """Decorator for consciousness cycle functions (capture all)."""
    return thermodynamic_burn("cycle", sample_rate=sample_rate, track_phi=True)


def inference_burn(sample_rate: int = 5) -> Callable[[F], F]:
    """Decorator for inference functions (capture 20%)."""
    return thermodynamic_burn("inference", sample_rate=sample_rate)


def memory_burn(sample_rate: int = 10) -> Callable[[F], F]:
    """Decorator for memory operations (capture 10%)."""
    return thermodynamic_burn("memory", sample_rate=sample_rate)


def quantum_burn(sample_rate: int = 1) -> Callable[[F], F]:
    """Decorator for quantum operations (capture all - they're rare)."""
    return thermodynamic_burn("quantum", sample_rate=sample_rate, track_phi=True)
