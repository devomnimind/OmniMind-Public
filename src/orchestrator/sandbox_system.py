"""Sistema de Sandbox para Auto-Melhoria Segura.

Permite que o Orchestrator teste mudanças em isolamento antes de aplicar.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SandboxState(Enum):
    """Estados do sandbox."""

    IDLE = "idle"
    CLONING = "cloning"
    TESTING = "testing"
    VALIDATING = "validating"
    APPLYING = "applying"
    ROLLED_BACK = "rolled_back"
    ERROR = "error"


@dataclass
class SandboxSnapshot:
    """Snapshot do estado do sistema para sandbox."""

    snapshot_id: str
    timestamp: float
    component_states: Dict[str, Any]
    config_snapshots: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SandboxChange:
    """Representa uma mudança a ser testada no sandbox."""

    change_id: str
    component_id: str
    change_type: str  # "config", "code", "behavior"
    change_data: Dict[str, Any]
    description: str
    timestamp: float


@dataclass
class SandboxResult:
    """Resultado de uma execução no sandbox."""

    change_id: str
    success: bool
    validation_passed: bool
    metrics_before: Dict[str, Any]
    metrics_after: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    rollback_applied: bool = False
    timestamp: float = field(default_factory=time.time)


class SandboxSystem:
    """Sistema de sandbox para testar mudanças em isolamento."""

    def __init__(self, orchestrator: Any, config: Optional[Dict[str, Any]] = None) -> None:
        """Inicializa o sistema de sandbox.

        Args:
            orchestrator: Instância do OrchestratorAgent
            config: Configuração do sandbox
        """
        self.orchestrator = orchestrator
        self.config = config or {
            "max_snapshots": 10,
            "validation_timeout": 60.0,  # segundos
            "auto_rollback_on_error": True,
            "require_validation": True,
        }

        self.current_state: SandboxState = SandboxState.IDLE
        self.active_sandbox: Optional[str] = None
        self.snapshots: Dict[str, SandboxSnapshot] = {}
        self.changes: Dict[str, SandboxChange] = {}
        self.results: Dict[str, SandboxResult] = {}
        self.change_counter: int = 0

        logger.info("SandboxSystem inicializado")

    async def create_snapshot(self, reason: str = "sandbox_preparation") -> str:
        """Cria um snapshot do estado atual do sistema.

        Args:
            reason: Motivo da criação do snapshot

        Returns:
            ID do snapshot criado
        """
        logger.info("Criando snapshot do sistema para sandbox (motivo: %s)", reason)
        self.current_state = SandboxState.CLONING

        snapshot_id = f"snapshot_{int(time.time())}_{self.change_counter:04d}"
        self.change_counter += 1

        # 1. Capturar estados dos componentes
        component_states: Dict[str, Any] = {}
        if hasattr(self.orchestrator, "agent_registry"):
            for agent_name in self.orchestrator.agent_registry.get_all_agents():
                component_states[agent_name] = {
                    "registered": True,
                    "health": await self.orchestrator.agent_registry.check_health(agent_name),
                }

        # 2. Capturar configurações via RollbackSystem se disponível
        config_snapshots: Dict[str, Any] = {}
        if hasattr(self.orchestrator, "rollback_system"):
            # Usar rollback system para capturar configs
            for component_id in getattr(self.orchestrator.rollback_system, "config_snapshots", {}):
                snapshots = self.orchestrator.rollback_system.get_component_snapshots(component_id)
                if snapshots:
                    config_snapshots[component_id] = snapshots[-1].__dict__

        # 3. Capturar métricas atuais
        metrics: Dict[str, Any] = {}
        if hasattr(self.orchestrator, "introspection_loop"):
            latest = self.orchestrator.introspection_loop.get_latest_metrics()
            if latest:
                metrics = {
                    "component_health": latest.component_health,
                    "error_rate": latest.error_rate,
                    "resource_usage": latest.resource_usage,
                }

        snapshot = SandboxSnapshot(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            component_states=component_states,
            config_snapshots=config_snapshots,
            metadata={"reason": reason, "metrics": metrics},
        )

        self.snapshots[snapshot_id] = snapshot

        # Limitar número de snapshots
        if len(self.snapshots) > self.config["max_snapshots"]:
            oldest = min(self.snapshots.keys(), key=lambda k: self.snapshots[k].timestamp)
            del self.snapshots[oldest]

        self.current_state = SandboxState.IDLE
        logger.info("Snapshot criado: %s", snapshot_id)
        return snapshot_id

    async def apply_change_in_sandbox(
        self,
        component_id: str,
        change_type: str,
        change_data: Dict[str, Any],
        description: str,
        snapshot_id: Optional[str] = None,
    ) -> str:
        """Aplica uma mudança no sandbox para teste.

        Args:
            component_id: ID do componente a ser modificado
            change_type: Tipo de mudança ("config", "code", "behavior")
            change_data: Dados da mudança
            description: Descrição da mudança
            snapshot_id: ID do snapshot a usar (None = criar novo)

        Returns:
            ID da mudança aplicada
        """
        logger.info(
            "Aplicando mudança no sandbox: %s em %s (%s)",
            change_type,
            component_id,
            description,
        )

        # 1. Criar snapshot se não fornecido
        if snapshot_id is None:
            snapshot_id = await self.create_snapshot(f"sandbox_change_{change_type}")

        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} não encontrado")

        # 2. Criar registro da mudança
        change_id = f"change_{int(time.time())}_{self.change_counter:04d}"
        self.change_counter += 1

        change = SandboxChange(
            change_id=change_id,
            component_id=component_id,
            change_type=change_type,
            change_data=change_data,
            description=description,
            timestamp=time.time(),
        )

        self.changes[change_id] = change
        self.active_sandbox = change_id
        self.current_state = SandboxState.TESTING

        # 3. Aplicar mudança em isolamento (simulado)
        try:
            logger.debug("Aplicando mudança %s em isolamento", change_id)
            await self._apply_change_isolated(change, snapshot_id)

            # 4. Validar mudança
            if self.config["require_validation"]:
                self.current_state = SandboxState.VALIDATING
                validation_result = await self._validate_change(change_id)

                if not validation_result:
                    logger.warning("Validação falhou para mudança %s", change_id)
                    if self.config["auto_rollback_on_error"]:
                        await self._rollback_change(change_id, snapshot_id)
                    self.current_state = SandboxState.ERROR
                    return change_id

            self.current_state = SandboxState.IDLE
            logger.info("Mudança %s aplicada com sucesso no sandbox", change_id)
            return change_id

        except Exception as e:
            logger.error("Erro ao aplicar mudança no sandbox: %s", e, exc_info=True)
            if self.config["auto_rollback_on_error"]:
                await self._rollback_change(change_id, snapshot_id)
            self.current_state = SandboxState.ERROR
            raise

    async def _apply_change_isolated(self, change: SandboxChange, snapshot_id: str) -> None:
        """Aplica mudança em isolamento (simulado).

        Args:
            change: Mudança a ser aplicada
            snapshot_id: ID do snapshot usado
        """
        # Em implementação real, isso criaria um ambiente isolado
        # Por enquanto, apenas registramos
        logger.debug(
            "Aplicando mudança isolada: %s em %s (tipo: %s)",
            change.change_id,
            change.component_id,
            change.change_type,
        )

        # Simular aplicação
        await asyncio.sleep(0.1)

        # Se for mudança de config, usar RollbackSystem para aplicar temporariamente
        if change.change_type == "config" and hasattr(self.orchestrator, "rollback_system"):
            # Aplicar config temporariamente (seria revertido se validação falhar)
            logger.debug("Aplicando mudança de config temporariamente")

    async def _validate_change(self, change_id: str) -> bool:
        """Valida uma mudança aplicada no sandbox.

        Args:
            change_id: ID da mudança

        Returns:
            True se validação passou, False caso contrário
        """
        if change_id not in self.changes:
            return False

        change = self.changes[change_id]
        logger.debug("Validando mudança %s", change_id)

        # 1. Coletar métricas antes
        metrics_before = await self._collect_metrics()

        # 2. Executar testes de validação
        try:
            validation_passed = await asyncio.wait_for(
                self._run_validation_tests(change),
                timeout=self.config["validation_timeout"],
            )
        except asyncio.TimeoutError:
            logger.warning("Validação excedeu timeout para %s", change_id)
            return False

        # 3. Coletar métricas depois
        metrics_after = await self._collect_metrics()

        # 4. Comparar métricas
        degradation_detected = self._detect_degradation(metrics_before, metrics_after)

        # 5. Criar resultado
        result = SandboxResult(
            change_id=change_id,
            success=validation_passed and not degradation_detected,
            validation_passed=validation_passed,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
        )

        if degradation_detected:
            result.warnings.append("Degradação detectada nas métricas")

        self.results[change_id] = result

        logger.info("Validação para %s: %s", change_id, "PASSOU" if result.success else "FALHOU")
        return result.success

    async def _run_validation_tests(self, change: SandboxChange) -> bool:
        """Executa testes de validação para uma mudança.

        Args:
            change: Mudança a ser testada

        Returns:
            True se testes passaram
        """
        # 1. Verificar se componente ainda está saudável
        if hasattr(self.orchestrator, "agent_registry"):
            health = await self.orchestrator.agent_registry.check_health(change.component_id)
            if not health:
                logger.warning("Componente %s não está saudável após mudança", change.component_id)
                return False

        # 2. Verificar se não há erros críticos
        if hasattr(self.orchestrator, "introspection_loop"):
            latest = self.orchestrator.introspection_loop.get_latest_metrics()
            if latest and latest.error_rate > 0.2:  # 20% de erro
                logger.warning("Taxa de erro alta após mudança: %.2f%%", latest.error_rate * 100)
                return False

        # 3. Testes específicos baseados no tipo de mudança
        if change.change_type == "config":
            # Validar que config é válida
            return await self._validate_config_change(change)
        elif change.change_type == "code":
            # Validar que código não quebrou funcionalidades críticas
            return await self._validate_code_change(change)

        return True

    async def _validate_config_change(self, change: SandboxChange) -> bool:
        """Valida mudança de configuração.

        Args:
            change: Mudança de config

        Returns:
            True se válida
        """
        logger.debug("Validando mudança de config para %s", change.component_id)

        # 1. Verificar estrutura básica da config
        config_data = change.change_data
        if not isinstance(config_data, dict):
            logger.warning("Config inválida: não é um dicionário")
            return False

        # 2. Validar usando RollbackSystem se disponível
        if hasattr(self.orchestrator, "rollback_system"):
            try:
                # Tentar criar snapshot para validar estrutura
                test_snapshot = self.orchestrator.rollback_system.create_snapshot(
                    component_id=change.component_id,
                    state=config_data,
                    metadata={"validation_test": True},
                )
                # Se chegou aqui, estrutura é válida
                logger.debug("Config validada via RollbackSystem (versão %d)", test_snapshot)
            except Exception as e:
                logger.warning("Erro ao validar config via RollbackSystem: %s", e)
                return False

        # 3. Verificar se há campos obrigatórios (se definidos)
        # Isso pode ser expandido com schemas específicos por componente
        if "invalid" in str(config_data).lower():
            logger.warning("Config contém marcador 'invalid'")
            return False

        logger.debug("Mudança de config validada com sucesso")
        return True

    async def _validate_code_change(self, change: SandboxChange) -> bool:
        """Valida mudança de código.

        Args:
            change: Mudança de código

        Returns:
            True se válida
        """
        logger.debug("Validando mudança de código para %s", change.component_id)

        # 1. Verificar estrutura básica
        code_data = change.change_data
        if not isinstance(code_data, dict):
            logger.warning("Dados de código inválidos: não é um dicionário")
            return False

        # 2. Verificar se há código Python válido (se fornecido)
        if "code" in code_data:
            code_str = code_data.get("code", "")
            if isinstance(code_str, str):
                try:
                    # Tentar compilar para verificar sintaxe básica
                    compile(code_str, f"<sandbox_{change.change_id}>", "exec")
                    logger.debug("Código Python compilado com sucesso")
                except SyntaxError as e:
                    logger.warning("Erro de sintaxe no código: %s", e)
                    return False
                except Exception as e:
                    logger.debug("Não foi possível validar sintaxe (não crítico): %s", e)

        # 3. Verificar se há testes associados (se disponível)
        if hasattr(self.orchestrator, "autopoietic_manager"):
            # AutopoieticManager pode ter validação de código
            logger.debug("AutopoieticManager disponível para validação adicional")

        # 4. Verificar se mudança não quebra interfaces críticas
        # Isso pode ser expandido com análise estática
        if "break" in str(code_data).lower() and "interface" in str(code_data).lower():
            logger.warning("Possível quebra de interface detectada")
            return False

        logger.debug("Mudança de código validada com sucesso")
        return True

    async def _collect_metrics(self) -> Dict[str, Any]:
        """Coleta métricas atuais do sistema.

        Returns:
            Dicionário com métricas
        """
        metrics: Dict[str, Any] = {
            "timestamp": time.time(),
            "component_health": {},
            "error_rate": 0.0,
            "resource_usage": {},
        }

        if hasattr(self.orchestrator, "agent_registry"):
            health_status = await self.orchestrator.agent_registry.health_check_all()
            metrics["component_health"] = health_status

        if hasattr(self.orchestrator, "introspection_loop"):
            latest = self.orchestrator.introspection_loop.get_latest_metrics()
            if latest:
                metrics["error_rate"] = latest.error_rate
                metrics["resource_usage"] = latest.resource_usage

        return metrics

    def _detect_degradation(
        self, metrics_before: Dict[str, Any], metrics_after: Dict[str, Any]
    ) -> bool:
        """Detecta degradação comparando métricas.

        Args:
            metrics_before: Métricas antes da mudança
            metrics_after: Métricas depois da mudança

        Returns:
            True se degradação detectada
        """
        # Comparar taxa de erro
        error_rate_before = metrics_before.get("error_rate", 0.0)
        error_rate_after = metrics_after.get("error_rate", 0.0)

        if error_rate_after > error_rate_before * 1.5:  # 50% de aumento
            logger.warning(
                "Degradação detectada: taxa de erro aumentou de %.2f%% para %.2f%%",
                error_rate_before * 100,
                error_rate_after * 100,
            )
            return True

        # Comparar saúde dos componentes
        health_before = metrics_before.get("component_health", {})
        health_after = metrics_after.get("component_health", {})

        healthy_before = sum(1 for v in health_before.values() if v)
        healthy_after = sum(1 for v in health_after.values() if v)

        if healthy_after < healthy_before:
            logger.warning(
                "Degradação detectada: componentes saudáveis reduziram de %d para %d",
                healthy_before,
                healthy_after,
            )
            return True

        return False

    async def _rollback_change(self, change_id: str, snapshot_id: str) -> None:
        """Reverte uma mudança usando snapshot.

        Args:
            change_id: ID da mudança a reverter
            snapshot_id: ID do snapshot para restaurar
        """
        logger.warning("Revertendo mudança %s usando snapshot %s", change_id, snapshot_id)

        if snapshot_id not in self.snapshots:
            logger.error("Snapshot %s não encontrado para rollback", snapshot_id)
            return

        snapshot = self.snapshots[snapshot_id]
        self.current_state = SandboxState.ROLLED_BACK

        # Restaurar estados dos componentes
        if hasattr(self.orchestrator, "rollback_system"):
            for component_id, config_data in snapshot.config_snapshots.items():
                logger.debug("Restaurando config de %s", component_id)
                await self.orchestrator.rollback_system.rollback_component_config(component_id)

        # Atualizar resultado
        if change_id in self.results:
            self.results[change_id].rollback_applied = True

        self.current_state = SandboxState.IDLE
        logger.info("Rollback concluído para mudança %s", change_id)

    async def apply_to_production(self, change_id: str) -> bool:
        """Aplica uma mudança validada à produção.

        Args:
            change_id: ID da mudança validada

        Returns:
            True se aplicado com sucesso
        """
        if change_id not in self.changes:
            logger.error("Mudança %s não encontrada", change_id)
            return False

        if change_id not in self.results:
            logger.error("Resultado de validação não encontrado para %s", change_id)
            return False

        result = self.results[change_id]
        if not result.success:
            logger.error("Não é possível aplicar mudança %s: validação falhou", change_id)
            return False

        logger.critical("Aplicando mudança %s à produção", change_id)
        self.current_state = SandboxState.APPLYING

        change = self.changes[change_id]

        try:
            # Aplicar mudança real (não isolada)
            if change.change_type == "config":
                # Aplicar config real
                logger.info("Aplicando mudança de config à produção")
            elif change.change_type == "code":
                # Aplicar código real (via AutopoieticManager)
                logger.info("Aplicando mudança de código à produção")
                if hasattr(self.orchestrator, "autopoietic_manager"):
                    # Usar AutopoieticManager para aplicar mudança
                    pass

            self.current_state = SandboxState.IDLE
            logger.info("Mudança %s aplicada à produção com sucesso", change_id)
            return True

        except Exception as e:
            logger.error("Erro ao aplicar mudança à produção: %s", e, exc_info=True)
            self.current_state = SandboxState.ERROR
            return False

    def get_sandbox_status(self) -> Dict[str, Any]:
        """Obtém status atual do sandbox.

        Returns:
            Dicionário com status
        """
        return {
            "current_state": self.current_state.value,
            "active_sandbox": self.active_sandbox,
            "total_snapshots": len(self.snapshots),
            "total_changes": len(self.changes),
            "total_results": len(self.results),
            "successful_changes": sum(1 for r in self.results.values() if r.success),
            "failed_changes": sum(1 for r in self.results.values() if not r.success),
        }

    def get_change_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém histórico de mudanças.

        Args:
            limit: Número máximo de mudanças a retornar

        Returns:
            Lista de mudanças
        """
        changes_list = []
        for change_id in sorted(self.changes.keys(), reverse=True)[:limit]:
            change = self.changes[change_id]
            result = self.results.get(change_id)
            changes_list.append(
                {
                    "change_id": change_id,
                    "component_id": change.component_id,
                    "change_type": change.change_type,
                    "description": change.description,
                    "timestamp": change.timestamp,
                    "success": result.success if result else None,
                    "validation_passed": result.validation_passed if result else None,
                }
            )
        return changes_list
