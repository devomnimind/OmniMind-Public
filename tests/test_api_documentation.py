"""
Tests for API Documentation Generator.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.security.api_documentation import APIDocumentationGenerator, APIEndpoint


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create temporary output directory."""
    output_dir = tmp_path / "api_docs"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def doc_generator(temp_output_dir: Path) -> APIDocumentationGenerator:
    """Create documentation generator instance."""
    return APIDocumentationGenerator(output_dir=temp_output_dir)


def test_doc_generator_initialization(
    doc_generator: APIDocumentationGenerator, temp_output_dir: Path
) -> None:
    """Test documentation generator initializes correctly."""
    assert doc_generator.output_dir == temp_output_dir
    assert temp_output_dir.exists()
    assert len(doc_generator.schemas) > 0
    assert len(doc_generator.endpoints) > 0


def test_schemas_initialized(doc_generator: APIDocumentationGenerator) -> None:
    """Test common schemas are initialized."""
    assert "Task" in doc_generator.schemas
    assert "Agent" in doc_generator.schemas
    assert "SecurityEvent" in doc_generator.schemas
    assert "MetacognitionInsight" in doc_generator.schemas
    assert "Error" in doc_generator.schemas


def test_endpoints_initialized(doc_generator: APIDocumentationGenerator) -> None:
    """Test default endpoints are initialized."""
    assert "/health" in doc_generator.endpoints
    assert "/tasks" in doc_generator.endpoints
    assert "/agents" in doc_generator.endpoints
    assert "/security/events" in doc_generator.endpoints
    assert "/metacognition/insights" in doc_generator.endpoints


def test_add_endpoint(doc_generator: APIDocumentationGenerator) -> None:
    """Test adding custom endpoint."""
    custom_endpoint = APIEndpoint(
        path="/custom/test",
        method="GET",
        summary="Custom Test Endpoint",
        description="Test endpoint for unit tests",
        tags=["Test"],
    )

    doc_generator.add_endpoint(custom_endpoint)

    assert "/custom/test" in doc_generator.endpoints
    assert "GET" in doc_generator.endpoints["/custom/test"]


def test_generate_openapi_spec(doc_generator: APIDocumentationGenerator) -> None:
    """Test OpenAPI specification generation."""
    spec = doc_generator.generate_openapi_spec()

    assert spec["openapi"] == "3.0.0"
    assert "info" in spec
    assert "servers" in spec
    assert "paths" in spec
    assert "components" in spec
    assert "tags" in spec

    # Check paths are populated
    assert len(spec["paths"]) > 0


def test_export_openapi_json(doc_generator: APIDocumentationGenerator) -> None:
    """Test exporting OpenAPI spec to JSON."""
    output_path = doc_generator.export_openapi_json()

    assert output_path.exists()
    assert output_path.name == "openapi.json"

    # Verify valid JSON
    with output_path.open() as f:
        spec = json.load(f)
        assert "openapi" in spec


def test_generate_markdown_docs(doc_generator: APIDocumentationGenerator) -> None:
    """Test Markdown documentation generation."""
    output_path = doc_generator.generate_markdown_docs()

    assert output_path.exists()
    assert output_path.name == "API_DOCUMENTATION.md"

    # Verify content
    content = output_path.read_text()
    assert "# OmniMind API Documentation" in content
    assert "## System" in content or "## Tasks" in content


def test_generate_python_sdk(doc_generator: APIDocumentationGenerator) -> None:
    """Test Python SDK generation."""
    output_path = doc_generator.generate_sdk_template("python")

    assert output_path.exists()
    assert output_path.name == "omnimind_sdk.py"

    # Verify Python code
    content = output_path.read_text()
    assert "class OmniMindClient" in content
    assert "def submit_task" in content
    assert "def get_task" in content


def test_generate_javascript_sdk(doc_generator: APIDocumentationGenerator) -> None:
    """Test JavaScript SDK generation."""
    output_path = doc_generator.generate_sdk_template("javascript")

    assert output_path.exists()
    assert output_path.name == "omnimind-sdk.js"

    # Verify JavaScript code
    content = output_path.read_text()
    assert "class OmniMindClient" in content
    assert "submitTask" in content
    assert "getTask" in content


def test_generate_postman_collection(
    doc_generator: APIDocumentationGenerator,
) -> None:
    """Test Postman collection generation."""
    output_path = doc_generator.generate_postman_collection()

    assert output_path.exists()
    assert output_path.name == "OmniMind_API.postman_collection.json"

    # Verify valid JSON
    with output_path.open() as f:
        collection = json.load(f)
        assert "info" in collection
        assert "item" in collection


def test_generate_all_documentation(
    doc_generator: APIDocumentationGenerator,
) -> None:
    """Test generating all documentation formats."""
    outputs = doc_generator.generate_all_documentation()

    assert "openapi" in outputs
    assert "markdown" in outputs
    assert "python_sdk" in outputs
    assert "javascript_sdk" in outputs
    assert "postman" in outputs

    # Verify all files exist
    for output_path in outputs.values():
        assert output_path.exists()


def test_api_endpoint_to_openapi() -> None:
    """Test APIEndpoint OpenAPI conversion."""
    endpoint = APIEndpoint(
        path="/test",
        method="GET",
        summary="Test Endpoint",
        description="Test description",
        tags=["Test"],
        parameters=[
            {
                "name": "id",
                "in": "query",
                "description": "Test ID",
                "required": True,
                "schema": {"type": "string"},
            }
        ],
        responses={
            "200": {
                "description": "Success",
                "content": {"application/json": {"schema": {"type": "object"}}},
            }
        },
    )

    openapi_spec = endpoint.to_openapi()

    assert "summary" in openapi_spec
    assert "description" in openapi_spec
    assert "tags" in openapi_spec
    assert "parameters" in openapi_spec
    assert "responses" in openapi_spec


def test_openapi_spec_schemas(doc_generator: APIDocumentationGenerator) -> None:
    """Test OpenAPI spec includes all schemas."""
    spec = doc_generator.generate_openapi_spec()

    schemas = spec["components"]["schemas"]

    assert "Task" in schemas
    assert "Agent" in schemas
    assert "SecurityEvent" in schemas
    assert "MetacognitionInsight" in schemas
    assert "Error" in schemas


def test_openapi_spec_security_schemes(
    doc_generator: APIDocumentationGenerator,
) -> None:
    """Test OpenAPI spec includes security schemes."""
    spec = doc_generator.generate_openapi_spec()

    security_schemes = spec["components"]["securitySchemes"]

    assert "basicAuth" in security_schemes
    assert security_schemes["basicAuth"]["type"] == "http"
    assert security_schemes["basicAuth"]["scheme"] == "basic"


def test_openapi_spec_servers(doc_generator: APIDocumentationGenerator) -> None:
    """Test OpenAPI spec includes servers."""
    spec = doc_generator.generate_openapi_spec()

    servers = spec["servers"]

    assert len(servers) >= 2
    assert any("localhost" in s["url"] for s in servers)


def test_python_sdk_has_all_methods(
    doc_generator: APIDocumentationGenerator,
) -> None:
    """Test Python SDK has all expected methods."""
    output_path = doc_generator.generate_sdk_template("python")
    content = output_path.read_text()

    assert "submit_task" in content
    assert "get_task" in content
    assert "list_tasks" in content
    assert "list_agents" in content
    assert "get_security_events" in content
    assert "get_metacognition_insights" in content


def test_javascript_sdk_has_all_methods(
    doc_generator: APIDocumentationGenerator,
) -> None:
    """Test JavaScript SDK has all expected methods."""
    output_path = doc_generator.generate_sdk_template("javascript")
    content = output_path.read_text()

    assert "submitTask" in content
    assert "getTask" in content
    assert "listTasks" in content
    assert "listAgents" in content
    assert "getSecurityEvents" in content
    assert "getMetacognitionInsights" in content


def test_postman_collection_structure(
    doc_generator: APIDocumentationGenerator,
) -> None:
    """Test Postman collection has correct structure."""
    output_path = doc_generator.generate_postman_collection()

    with output_path.open() as f:
        collection = json.load(f)

    assert collection["info"]["name"] == "OmniMind API"
    assert "auth" in collection
    assert collection["auth"]["type"] == "basic"
    assert len(collection["item"]) > 0


def test_unsupported_sdk_language_raises_error(
    doc_generator: APIDocumentationGenerator,
) -> None:
    """Test that unsupported SDK language raises error."""
    with pytest.raises(ValueError, match="Unsupported language"):
        doc_generator.generate_sdk_template("ruby")
