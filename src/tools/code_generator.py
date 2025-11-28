"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
AI-Assisted Code Generation Tools for OmniMind.

Provides intelligent code generation with:
- Template-based code generation
- AI-powered code completion
- Boilerplate reduction
- Pattern-based generation
- Test case generation
"""

from __future__ import annotations

import ast
import inspect
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class CodeTemplateType(str, Enum):
    """Types of code templates."""

    AGENT = "agent"
    TOOL = "tool"
    WORKFLOW = "workflow"
    TEST = "test"
    API_ENDPOINT = "api_endpoint"
    DATA_MODEL = "data_model"
    VALIDATOR = "validator"


@dataclass
class CodeTemplate:
    """Code generation template."""

    name: str
    type: CodeTemplateType
    description: str
    template: str
    required_params: List[str]
    optional_params: Dict[str, Any]


class CodeGenerator:
    """AI-assisted code generator with templates and patterns."""

    def __init__(self) -> None:
        """Initialize code generator."""
        self.templates: Dict[str, CodeTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self) -> None:
        """Load default code templates."""
        # Agent template
        self.templates["agent"] = CodeTemplate(
            name="agent",
            type=CodeTemplateType.AGENT,
            description="Generate a new agent class",
            template='''"""
{description}

Agent: {agent_name}
Purpose: {purpose}
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..tools.omnimind_tools import ToolsFramework

logger = logging.getLogger(__name__)


class {agent_name}:
    """
    {description}

    Capabilities:
{capabilities}
    """

    def __init__(self, tools: Optional[ToolsFramework] = None) -> None:
        """
        Initialize {agent_name}.

        Args:
            tools: Tools framework instance
        """
        self.tools = tools or ToolsFramework()
        logger.info(f"{{self.__class__.__name__}} initialized")

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute agent task.

        Args:
            task: Task description
            context: Optional execution context

        Returns:
            Execution result
        """
        logger.info(f"Executing task: {{task}}")

        if context is None:
            context = {{}}

        # TODO: Implement agent logic
        result = {{
            "status": "success",
            "task": task,
            "output": "Task executed successfully",
        }}

        return result

    def validate_input(self, task: str) -> bool:
        """
        Validate input task.

        Args:
            task: Task to validate

        Returns:
            True if valid, False otherwise
        """
        if not task or not task.strip():
            logger.error("Empty task provided")
            return False

        return True


if __name__ == "__main__":
    # Demo usage
    agent = {agent_name}()
    result = agent.execute("demo task")
    print(f"Result: {{result}}")
''',
            required_params=["agent_name", "description", "purpose"],
            optional_params={"capabilities": ["- Task execution", "- Input validation"]},
        )

        # Tool template
        self.templates["tool"] = CodeTemplate(
            name="tool",
            type=CodeTemplateType.TOOL,
            description="Generate a new tool function",
            template='''def {tool_name}({parameters}) -> {return_type}:
    """
    {description}

    Args:
{args_docs}

    Returns:
        {return_description}

    Raises:
        ValueError: If validation fails
    """
    # Validate inputs
{validation}

    # Execute tool logic
    try:
{logic}

        return result

    except Exception as e:
        logger.error(f"{tool_name} failed: {{e}}")
        raise
''',
            required_params=["tool_name", "description", "parameters", "return_type"],
            optional_params={
                "args_docs": "",
                "return_description": "Result",
                "validation": "    pass",
                "logic": "        result = None",
            },
        )

        # Test template
        self.templates["test"] = CodeTemplate(
            name="test",
            type=CodeTemplateType.TEST,
            description="Generate test cases",
            template='''"""
Tests for {module_name}.
"""

import pytest
from pathlib import Path
from typing import Any, Dict

from {module_path} import {class_name}


class Test{class_name}:
    """Test suite for {class_name}."""

    @pytest.fixture
    def instance(self) -> {class_name}:
        """Create test instance."""
        return {class_name}()

    def test_initialization(self, instance: {class_name}) -> None:
        """Test {class_name} initialization."""
        assert instance is not None
        assert isinstance(instance, {class_name})

{test_methods}

    def test_invalid_input(self, instance: {class_name}) -> None:
        """Test handling of invalid input."""
        with pytest.raises(ValueError):
            instance.execute("")

    def test_error_handling(self, instance: {class_name}) -> None:
        """Test error handling."""
        # TODO: Implement error handling test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
''',
            required_params=["module_name", "module_path", "class_name"],
            optional_params={
                "test_methods": "    def test_execute(self, instance: {class_name}) -> None:\n"
                '        """Test execution."""\n'
                '        result = instance.execute("test")\n'
                "        assert result is not None\n"
            },
        )

        # API endpoint template
        self.templates["api_endpoint"] = CodeTemplate(
            name="api_endpoint",
            type=CodeTemplateType.API_ENDPOINT,
            description="Generate FastAPI endpoint",
            template='''from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/{prefix}", tags=["{tag}"])


class {request_model}(BaseModel):
    """Request model for {endpoint_name}."""
{request_fields}


class {response_model}(BaseModel):
    """Response model for {endpoint_name}."""
{response_fields}


@router.{method}("/{path}")
async def {endpoint_name}(
    request: {request_model},
) -> {response_model}:
    """
    {description}

    Args:
        request: Request data

    Returns:
        Response data

    Raises:
        HTTPException: On error
    """
    try:
        # TODO: Implement endpoint logic
        result = {{
            "status": "success",
            "message": "{endpoint_name} executed successfully",
        }}

        return {response_model}(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
''',
            required_params=[
                "endpoint_name",
                "description",
                "prefix",
                "tag",
                "path",
                "method",
            ],
            optional_params={
                "request_model": "Request",
                "response_model": "Response",
                "request_fields": "    task: str",
                "response_fields": "    status: str\n    message: str",
            },
        )

        # Data model template
        self.templates["data_model"] = CodeTemplate(
            name="data_model",
            type=CodeTemplateType.DATA_MODEL,
            description="Generate Pydantic data model",
            template='''"""
{description}
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional


class {model_name}(BaseModel):
    """
    {description}
    """
{fields}

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True

{validators}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> {model_name}:
        """Create from dictionary."""
        return cls(**data)
''',
            required_params=["model_name", "description", "fields"],
            optional_params={
                "validators": "    # Add custom validators here\n    pass",
            },
        )

    def generate_code(
        self,
        template_name: str,
        params: Dict[str, Any],
        output_file: Optional[Path] = None,
    ) -> str:
        """
        Generate code from template.

        Args:
            template_name: Name of template to use
            params: Template parameters
            output_file: Optional output file path

        Returns:
            Generated code

        Raises:
            ValueError: If template not found or params invalid
        """
        if template_name not in self.templates:
            raise ValueError(f"Template not found: {template_name}")

        template = self.templates[template_name]

        # Check required params
        missing = [p for p in template.required_params if p not in params]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")

        # Merge with optional params
        all_params = {**template.optional_params, **params}

        # Format capabilities if present
        if "capabilities" in all_params and isinstance(all_params["capabilities"], list):
            all_params["capabilities"] = "\n".join(
                f"    {cap}" for cap in all_params["capabilities"]
            )

        # Generate code
        try:
            code = template.template.format(**all_params)
        except KeyError as e:
            raise ValueError(f"Missing parameter: {e}")

        # Save to file if specified
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(code)
            logger.info(f"Generated code saved to {output_file}")

        return code

    def generate_agent(
        self,
        agent_name: str,
        description: str,
        purpose: str,
        capabilities: Optional[List[str]] = None,
        output_file: Optional[Path] = None,
    ) -> str:
        """
        Generate a new agent class.

        Args:
            agent_name: Name of agent class
            description: Agent description
            purpose: Agent purpose
            capabilities: List of capabilities
            output_file: Optional output file

        Returns:
            Generated code
        """
        params = {
            "agent_name": agent_name,
            "description": description,
            "purpose": purpose,
        }

        if capabilities:
            params["capabilities"] = "\n".join(capabilities)

        return self.generate_code("agent", params, output_file)

    def generate_test(
        self,
        module_name: str,
        module_path: str,
        class_name: str,
        methods: Optional[List[str]] = None,
        output_file: Optional[Path] = None,
    ) -> str:
        """
        Generate test cases for a class.

        Args:
            module_name: Module name
            module_path: Import path
            class_name: Class to test
            methods: Optional list of methods to test
            output_file: Optional output file

        Returns:
            Generated test code
        """
        params = {
            "module_name": module_name,
            "module_path": module_path,
            "class_name": class_name,
        }

        if methods:
            test_methods = []
            for method in methods:
                test_methods.append(
                    f"    def test_{method}(self, instance: {class_name}) -> None:\n"
                    f'        """Test {method}."""\n'
                    f"        # TODO: Implement test\n"
                    f"        pass\n"
                )
            params["test_methods"] = "\n".join(test_methods)

        return self.generate_code("test", params, output_file)

    def generate_api_endpoint(
        self,
        endpoint_name: str,
        description: str,
        prefix: str,
        tag: str,
        path: str,
        method: str = "post",
        output_file: Optional[Path] = None,
    ) -> str:
        """
        Generate FastAPI endpoint.

        Args:
            endpoint_name: Endpoint function name
            description: Endpoint description
            prefix: Router prefix
            tag: OpenAPI tag
            path: Endpoint path
            method: HTTP method (get, post, put, delete)
            output_file: Optional output file

        Returns:
            Generated endpoint code
        """
        params = {
            "endpoint_name": endpoint_name,
            "description": description,
            "prefix": prefix,
            "tag": tag,
            "path": path,
            "method": method,
        }

        return self.generate_code("api_endpoint", params, output_file)

    def analyze_class_for_tests(self, class_obj: type) -> List[str]:
        """
        Analyze a class and suggest test methods.

        Args:
            class_obj: Class to analyze

        Returns:
            List of method names to test
        """
        methods = []

        for name, method in inspect.getmembers(class_obj, predicate=inspect.ismethod):
            if not name.startswith("_"):
                methods.append(name)

        return methods

    def generate_docstring(self, func: Callable[..., Any], style: str = "google") -> str:
        """
        Generate docstring for a function.

        Args:
            func: Function to document
            style: Docstring style (google, numpy, sphinx)

        Returns:
            Generated docstring
        """
        sig = inspect.signature(func)

        # Get function description (use existing docstring or placeholder)
        description = func.__doc__.strip() if func.__doc__ else "TODO: Add description"

        # Build parameters section
        params = []
        for name, param in sig.parameters.items():
            if name == "self":
                continue

            param_type = (
                param.annotation.__name__
                if hasattr(param.annotation, "__name__")
                else str(param.annotation)
            )
            params.append(f"    {name} ({param_type}): TODO: Describe parameter")

        # Build return section
        return_type = (
            sig.return_annotation.__name__
            if hasattr(sig.return_annotation, "__name__")
            else str(sig.return_annotation)
        )

        if style == "google":
            docstring = f'''"""
{description}

Args:
{chr(10).join(params) if params else "    None"}

Returns:
    {return_type}: TODO: Describe return value
"""'''
        else:
            # Default to simple docstring
            docstring = f'"""{description}"""'

        return docstring

    def add_type_hints(self, code: str) -> str:
        """
        Add type hints to code that lacks them.

        Args:
            code: Python code

        Returns:
            Code with type hints added
        """
        try:
            tree = ast.parse(code)

            # Walk through AST and add type hints
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Add return type if missing
                    if node.returns is None:
                        node.returns = ast.Name(id="Any", ctx=ast.Load())

                    # Add parameter types if missing
                    for arg in node.args.args:
                        if arg.annotation is None:
                            arg.annotation = ast.Name(id="Any", ctx=ast.Load())

            # Convert back to code
            return ast.unparse(tree)

        except Exception as e:
            logger.warning(f"Failed to add type hints: {e}")
            return code


# Convenience functions
def generate_agent(
    agent_name: str,
    description: str,
    purpose: str,
    output_file: Optional[Path] = None,
) -> str:
    """Quick function to generate an agent."""
    generator = CodeGenerator()
    return generator.generate_agent(agent_name, description, purpose, None, output_file)


def generate_test_for_class(
    class_name: str, module_path: str, output_file: Optional[Path] = None
) -> str:
    """Quick function to generate tests for a class."""
    generator = CodeGenerator()
    return generator.generate_test(class_name.lower(), module_path, class_name, None, output_file)


if __name__ == "__main__":
    # Demo usage
    print("🔧 Code Generator Demo\n")

    generator = CodeGenerator()

    # Generate an agent
    print("1. Generating agent...")
    agent_code = generator.generate_agent(
        agent_name="DataProcessorAgent",
        description="Agent for processing and analyzing data",
        purpose="Process data and extract insights",
        capabilities=[
            "- Data validation",
            "- Data transformation",
            "- Insight extraction",
        ],
        output_file=Path("tmp/generated_agent.py"),
    )
    print("✓ Agent generated to tmp/generated_agent.py")

    # Generate tests
    print("\n2. Generating tests...")
    test_code = generator.generate_test(
        module_name="data_processor_agent",
        module_path="agents.data_processor_agent",
        class_name="DataProcessorAgent",
        methods=["execute", "validate_input"],
        output_file=Path("tmp/test_generated_agent.py"),
    )
    print("✓ Tests generated to tmp/test_generated_agent.py")

    # Generate API endpoint
    print("\n3. Generating API endpoint...")
    api_code = generator.generate_api_endpoint(
        endpoint_name="process_data",
        description="Process data and return insights",
        prefix="/api/v1/data",
        tag="Data Processing",
        path="/process",
        method="post",
        output_file=Path("tmp/generated_endpoint.py"),
    )
    print("✓ API endpoint generated to tmp/generated_endpoint.py")

    print("\n✨ Code generation complete!")
