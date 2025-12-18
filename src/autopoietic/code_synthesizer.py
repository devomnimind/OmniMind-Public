"""Code Synthesizer module.

Provides a lightweight code synthesizer that turns a ComponentSpec into a minimal
Python implementation. No external LLMs are used; the synthesizer builds
deterministic stub code based on the component type.

All functions include full type hints and Google‑style docstrings to satisfy
OmniMind’s strict quality rules.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Sequence

from .meta_architect import ComponentSpec

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SynthesizedComponent:
    """Result of code synthesis.

    Attributes:
        name: Component name.
        source_code: Generated Python source as a string.
        natural_description: Human-readable explanation of what the component does.
    """

    name: str
    source_code: str
    natural_description: str


class CodeSynthesizer:
    """Generate Python source code from ComponentSpec objects.

    The synthesizer creates a minimal, syntactically correct Python class for
    each specification. The generated class defines an ``__init__`` that stores
    the configuration and a ``run`` method that logs a placeholder action.
    """

    def __init__(self) -> None:
        """Create a new CodeSynthesizer instance."""
        self._logger = logger.getChild(self.__class__.__name__)
        self._logger.debug("CodeSynthesizer initialized")

        # NOVO: Sistema de aprendizado incorporado
        self._learned_improvements: Dict[str, Any] = {}
        self._load_learned_patterns()

    def _load_learned_patterns(self) -> None:
        """Carrega padrões aprendidos do sistema de feedback."""
        try:
            feedback_path = Path("data/autopoietic/component_feedback.jsonl")
            if feedback_path.exists():
                patterns: Dict[str, Dict[str, Any]] = {}
                with feedback_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            feedback_data = json.loads(line)
                            fb_type = feedback_data["feedback_type"]

                            if fb_type not in patterns:
                                patterns[fb_type] = {"patterns": [], "scores": []}

                            patterns[fb_type]["patterns"].extend(feedback_data["changes_made"])
                            patterns[fb_type]["scores"].append(feedback_data["improvement_score"])

                # Consolidar padrões aprendidos
                for fb_type, data in patterns.items():
                    if data["patterns"]:
                        # Remover duplicatas e manter mais frequentes
                        from collections import Counter

                        pattern_counts = Counter(data["patterns"])
                        top_patterns = [p for p, _ in pattern_counts.most_common(5)]

                        self._learned_improvements[fb_type] = {
                            "common_patterns": top_patterns,
                            "avg_improvement": sum(data["scores"]) / len(data["scores"]),
                            "total_feedbacks": len(data["scores"]),
                        }

                self._logger.info(
                    "🎓 Carregados %d padrões aprendidos",
                    len(self._learned_improvements),
                )

        except Exception as e:
            self._logger.debug("Não foi possível carregar padrões aprendidos: %s", e)

    def apply_learned_improvements(self, spec: ComponentSpec) -> ComponentSpec:
        """Aplica melhorias aprendidas do feedback ao spec antes da síntese.

        Args:
            spec: Especificação original do componente

        Returns:
            Especificação melhorada com aprendizado incorporado
        """
        improved_config = dict(spec.config)

        # Aplicar melhorias baseadas em padrões aprendidos
        applied_improvements = []

        for fb_type, patterns in self._learned_improvements.items():
            if patterns["avg_improvement"] > 0.7:  # Só aplicar melhorias muito efetivas
                for pattern in patterns["common_patterns"]:
                    if self._can_apply_pattern(pattern, spec):
                        improved_config = self._apply_pattern(pattern, improved_config)
                        applied_improvements.append(f"Aplicado padrão aprendido: {pattern}")
                        self._logger.debug(
                            "🎯 Aplicado padrão aprendido: %s para %s",
                            pattern,
                            spec.name,
                        )

        # Adicionar metadados sobre melhorias aplicadas
        if applied_improvements:
            improved_config["_learned_improvements"] = json.dumps(applied_improvements)
            improved_config["_improvement_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

        return ComponentSpec(name=spec.name, type=spec.type, config=improved_config)

    def _can_apply_pattern(self, pattern: str, spec: ComponentSpec) -> bool:
        """Verifica se um padrão aprendido pode ser aplicado a este spec."""
        # Lógica simplificada - em produção seria mais sofisticada
        strategy = spec.config.get("strategy", "DEFAULT")

        if "error_handling" in pattern.lower() and strategy != "STABILIZE":
            return False  # Error handling melhor aplicado em STABILIZE

        if "caching" in pattern.lower() and strategy != "OPTIMIZE":
            return False  # Caching melhor aplicado em OPTIMIZE

        if "extensibility" in pattern.lower() and strategy != "EXPAND":
            return False  # Extensibility melhor aplicado em EXPAND

        return True

    def _apply_pattern(self, pattern: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica um padrão específico de melhoria à configuração."""
        improved = dict(config)

        # Mapeamento de padrões para melhorias concretas
        if "error_handling" in pattern.lower():
            improved["enhanced_error_handling"] = True
        elif "caching" in pattern.lower():
            improved["smart_caching"] = True
        elif "extensibility" in pattern.lower():
            improved["modular_design"] = True
        elif "logging" in pattern.lower():
            improved["comprehensive_logging"] = True
        elif "validation" in pattern.lower():
            improved["input_validation"] = True

        return improved

    def synthesize(self, specs: Sequence[ComponentSpec]) -> Dict[str, SynthesizedComponent]:
        """Synthesize source code for a sequence of component specifications.

        Args:
            specs: Iterable of ComponentSpec objects.

        Returns:
            Mapping from component name to SynthesizedComponent containing the
            generated source code and natural language description.
        """
        result: Dict[str, SynthesizedComponent] = {}
        for spec in specs:
            # NOVO: Aplicar melhorias aprendidas antes da síntese
            improved_spec = self.apply_learned_improvements(spec)

            source = self._generate_class_source(improved_spec)
            natural_desc = self._generate_natural_description(improved_spec)

            # NOVO: Adicionar comentários sobre melhorias aplicadas
            if "_learned_improvements" in improved_spec.config:
                improvements_list = json.loads(improved_spec.config["_learned_improvements"])
                improvement_comments = "\n".join(
                    [f"# 🎯 MELHORIA APRENDIDA: {imp}" for imp in improvements_list]
                )
                source = source.replace(
                    "# ⚠️  NÃO MODIFICAR MANUALMENTE - Pode comprometer a integridade do sistema",
                    f"# ⚠️  NÃO MODIFICAR MANUALMENTE - Pode comprometer a integridade do sistema\n"
                    f"{improvement_comments}",
                )

            # 🔒 SEGURANÇA: Adicionar assinatura obrigatória no nome do arquivo (Nome encurtado)
            signed_name = f"auto_{spec.name}"
            result[signed_name] = SynthesizedComponent(
                name=signed_name, source_code=source, natural_description=natural_desc
            )
            self._logger.info("🔒 Synthesized component with security signature: %s", signed_name)

            # NOVO: Log das melhorias aplicadas
            if "_learned_improvements" in improved_spec.config:
                improvements_list = json.loads(improved_spec.config["_learned_improvements"])
                self._logger.info(
                    "🎓 Aplicadas %d melhorias aprendidas para %s",
                    len(improvements_list),
                    signed_name,
                )

        return result

    def _generate_class_source(self, spec: ComponentSpec) -> str:
        """Generate a Python class source string for a single ComponentSpec.

        The class name is derived from spec.name (converted to PascalCase).
        The logic adapts based on the 'strategy' field in the configuration:
        - STABILIZE: Adds robust error handling.
        - OPTIMIZE: Adds caching decorators.
        - EXPAND: Adds extended feature placeholders.
        """
        class_name = self._to_pascal_case(spec.name)
        config_items = "\n        ".join(
            f"self.{key} = '{value}'" for key, value in spec.config.items()
        )

        strategy = spec.config.get("strategy", "DEFAULT")
        imports = "import logging"
        decorators = ""
        run_logic = ""

        if strategy == "OPTIMIZE":
            imports += "\nimport functools"
            decorators = "@functools.lru_cache(maxsize=128)"

        if strategy == "STABILIZE":
            run_logic = """
        try:
            self._logger.info(f"Running {{self.__class__.__name__}} component (STABILIZED)")
            # Stabilized logic would go here
        except Exception as e:
            self._logger.error(f"Error in {{self.__class__.__name__}}: {{e}}", exc_info=True)
            # Graceful degradation logic
        """
        elif strategy == "EXPAND":
            run_logic = """
        self._logger.info(f"Running {{self.__class__.__name__}} component (EXPANDED)")
        self._run_extended_features()
        """
        else:
            run_logic = """
        self._logger.info(f"Running {{self.__class__.__name__}} component")
        """

        extended_methods = ""
        if strategy == "EXPAND":
            extended_methods = """
    def _run_extended_features(self) -> None:
        \"\"\"Placeholder for extended capabilities.\"\"\"
        self._logger.info("Executing extended features...")
"""

        source = f"""{imports}

# 🔒 SEGURANÇA AUTOPOIÉTICA - COMPONENTE GERADO EM SANDBOX
# Este arquivo foi gerado automaticamente pelo sistema autopoiético do OmniMind
# Data: {time.strftime('%Y-%m-%d %H:%M:%S')}
# Estratégia: {strategy}
# ⚠️  NÃO MODIFICAR MANUALMENTE - Pode comprometer a integridade do sistema

class {class_name}:
    \"\"\"Auto‑generated component of type '{spec.type}' (Strategy: {strategy}).
    🔒 Security Signature: modulo_autopoiesis_data_{spec.name}
    🧪 Generated in Sandbox Environment
    \"\"\"
    def __init__(self):
        # Configuration injected by MetaArchitect
        {config_items}
        # 🔒 Security markers
        self._security_signature = "modulo_autopoiesis_data_{spec.name}"
        self._generated_in_sandbox = True
        self._generation_timestamp = "{time.strftime('%Y-%m-%d %H:%M:%S')}"
        self._logger = logging.getLogger(__name__)

    {decorators}
    def run(self) -> None:
        \"\"\"Execution method adapted for {strategy} strategy.\"\"\"
        {run_logic.strip()}
{extended_methods}"""
        return source

    def _generate_natural_description(self, spec: ComponentSpec) -> str:
        """Generate a human-readable description of what the component does.

        Args:
            spec: Component specification.

        Returns:
            Natural language description of the component's purpose and behavior.
        """
        strategy = spec.config.get("strategy", "DEFAULT")
        component_type = spec.type

        # Base description based on component type
        type_descriptions = {
            "process": "um processador que executa tarefas específicas",
            "worker": "um trabalhador que realiza operações automatizadas",
            "service": "um serviço que oferece funcionalidades aos outros componentes",
            "handler": "um manipulador que processa eventos e solicitações",
            "monitor": "um monitor que observa e reporta o estado do sistema",
            "repair": "um reparador que corrige problemas automaticamente",
        }

        base_desc = type_descriptions.get(
            component_type, f"um componente do tipo '{component_type}'"
        )

        # Strategy-specific enhancements
        strategy_descriptions = {
            "STABILIZE": "Este componente foi projetado para ser muito confiável e seguro. "
            "Ele inclui proteção contra erros e sempre tenta se recuperar automaticamente "
            "se algo der errado, como um bom amigo que está sempre lá quando você precisa.",
            "OPTIMIZE": "Este componente foi criado para ser super rápido e eficiente! "
            "Ele usa truques inteligentes para lembrar resultados anteriores e evitar "
            "trabalho repetitivo, economizando tempo e energia como um cozinheiro experiente "
            "que sabe exatamente onde estão todos os ingredientes.",
            "EXPAND": "Este componente é como uma árvore crescendo - ele começa pequeno mas pode "
            "desenvolver novas habilidades e capacidades conforme necessário. "
            "É flexível e pode se adaptar a novas situações, aprendendo e crescendo "
            "como uma criança curiosa explorando o mundo.",
            "DEFAULT": "Este componente faz seu trabalho de forma simples e direta, "
            "concentrando-se em executar suas tarefas principais de maneira confiável.",
        }

        strategy_desc = strategy_descriptions.get(strategy, strategy_descriptions["DEFAULT"])

        # Add context from config if available
        context_parts = []
        if "original_component" in spec.config:
            context_parts.append(
                f"foi criado para ajudar com problemas no componente "
                f"'{spec.config['original_component']}'"
            )

        if "error" in spec.config:
            error_desc = spec.config["error"]
            context_parts.append(f"resolve situações como: '{error_desc}'")

        context = ""
        if context_parts:
            context = f" Ele {context_parts[0]}"
            if len(context_parts) > 1:
                context += f" e {context_parts[1]}"

        # Combine everything into a natural description
        description = f"Olá! Eu sou {base_desc} chamado '{spec.name}'. {strategy_desc}{context}"

        # Add friendly closing
        description += (
            " Estou aqui para ajudar o sistema a funcionar melhor e aprender com cada experiência!"
        )

        return description

    @staticmethod
    def _to_pascal_case(name: str) -> str:
        """Convert a snake_case name to PascalCase.

        Args:
            name: Original component name.

        Returns:
            PascalCase version suitable for a Python class name.
        """
        return "".join(part.capitalize() for part in name.split("_"))
