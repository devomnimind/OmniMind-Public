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
Enhanced API Documentation Generator for OmniMind.

This module provides comprehensive API documentation including:
- Complete OpenAPI/Swagger specification
- Interactive API playground
- Example requests/responses for all endpoints
- SDK generation support
- Integration tutorials and code samples
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class APIEndpoint:
    """API endpoint documentation."""

    path: str
    method: str
    summary: str
    description: str
    tags: List[str] = field(default_factory=list)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    security: List[Dict[str, List[str]]] = field(default_factory=list)
    examples: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_openapi(self) -> Dict[str, Any]:
        """Convert to OpenAPI specification format."""
        spec = {
            "summary": self.summary,
            "description": self.description,
            "tags": self.tags,
            "parameters": self.parameters,
            "responses": self.responses,
        }

        if self.request_body:
            spec["requestBody"] = self.request_body

        if self.security:
            spec["security"] = self.security

        return spec


class APIDocumentationGenerator:
    """Generates comprehensive API documentation for OmniMind."""

    def __init__(self, output_dir: Path = Path("docs/api")):
        """
        Initialize API documentation generator.

        Args:
            output_dir: Directory to output documentation
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.endpoints: Dict[str, Dict[str, APIEndpoint]] = {}
        self.schemas: Dict[str, Dict[str, Any]] = {}

        self._initialize_schemas()
        self._initialize_endpoints()

        logger.info(f"API Documentation Generator initialized: {self.output_dir}")

    def _initialize_schemas(self) -> None:
        """Initialize common API schemas."""
        # Task Schema
        self.schemas["Task"] = {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Unique task identifier"},
                "description": {"type": "string", "description": "Task description"},
                "status": {
                    "type": "string",
                    "enum": ["pending", "running", "completed", "failed"],
                    "description": "Task execution status",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Task priority level",
                },
                "created_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Task creation timestamp",
                },
                "result": {
                    "type": "object",
                    "description": "Task execution result (when completed)",
                },
            },
            "required": ["task_id", "description", "status"],
        }

        # Agent Schema
        self.schemas["Agent"] = {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "Unique agent identifier",
                },
                "name": {"type": "string", "description": "Agent name"},
                "type": {
                    "type": "string",
                    "enum": ["orchestrator", "security", "ethics", "metacognition"],
                    "description": "Agent type",
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "idle", "busy", "error"],
                    "description": "Agent status",
                },
                "capabilities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Agent capabilities",
                },
            },
            "required": ["agent_id", "name", "type", "status"],
        }

        # Security Event Schema
        self.schemas["SecurityEvent"] = {
            "type": "object",
            "properties": {
                "event_id": {
                    "type": "string",
                    "description": "Unique event identifier",
                },
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Event timestamp",
                },
                "severity": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low", "info"],
                    "description": "Event severity",
                },
                "category": {
                    "type": "string",
                    "description": "Event category (e.g., 'authentication', 'authorization')",
                },
                "description": {"type": "string", "description": "Event description"},
                "metadata": {
                    "type": "object",
                    "description": "Additional event metadata",
                },
            },
            "required": [
                "event_id",
                "timestamp",
                "severity",
                "category",
                "description",
            ],
        }

        # Metacognition Insight Schema
        self.schemas["MetacognitionInsight"] = {
            "type": "object",
            "properties": {
                "insight_id": {
                    "type": "string",
                    "description": "Unique insight identifier",
                },
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Insight generation timestamp",
                },
                "type": {
                    "type": "string",
                    "enum": ["pattern", "anomaly", "optimization", "goal"],
                    "description": "Insight type",
                },
                "description": {"type": "string", "description": "Insight description"},
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Confidence score (0-1)",
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional insight metadata",
                },
            },
            "required": [
                "insight_id",
                "timestamp",
                "type",
                "description",
                "confidence",
            ],
        }

        # Error Schema
        self.schemas["Error"] = {
            "type": "object",
            "properties": {
                "error": {"type": "string", "description": "Error message"},
                "detail": {
                    "type": "string",
                    "description": "Detailed error description",
                },
                "code": {"type": "string", "description": "Error code"},
            },
            "required": ["error"],
        }

    def _initialize_endpoints(self) -> None:
        """Initialize API endpoint documentation."""
        # Health Check Endpoint
        self.add_endpoint(
            APIEndpoint(
                path="/health",
                method="GET",
                summary="Health Check",
                description="Check if the API is running and healthy",
                tags=["System"],
                responses={
                    "200": {
                        "description": "Service is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "example": "healthy",
                                        },
                                        "version": {
                                            "type": "string",
                                            "example": "1.0.0",
                                        },
                                    },
                                }
                            }
                        },
                    }
                },
                examples={"success": {"response": {"status": "healthy", "version": "1.0.0"}}},
            )
        )

        # Task Submission Endpoint
        self.add_endpoint(
            APIEndpoint(
                path="/tasks",
                method="POST",
                summary="Submit Task",
                description="Submit a new task for execution by the orchestrator agent",
                tags=["Tasks"],
                request_body={
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "description": {
                                        "type": "string",
                                        "description": "Task description",
                                    },
                                    "priority": {
                                        "type": "string",
                                        "enum": ["low", "medium", "high", "critical"],
                                        "default": "medium",
                                    },
                                },
                                "required": ["description"],
                            }
                        }
                    },
                },
                responses={
                    "200": {
                        "description": "Task submitted successfully",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Task"}}
                        },
                    },
                    "400": {
                        "description": "Invalid request",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                        },
                    },
                },
                security=[{"basicAuth": []}],
                examples={
                    "request": {
                        "description": "Analyze repository security vulnerabilities",
                        "priority": "high",
                    },
                    "response": {
                        "task_id": "task_20231119_120000",
                        "description": "Analyze repository security vulnerabilities",
                        "status": "pending",
                        "priority": "high",
                        "created_at": "2023-11-19T12:00:00Z",
                    },
                },
            )
        )

        # List Tasks Endpoint
        self.add_endpoint(
            APIEndpoint(
                path="/tasks",
                method="GET",
                summary="List Tasks",
                description="List all tasks with optional filtering",
                tags=["Tasks"],
                parameters=[
                    {
                        "name": "status",
                        "in": "query",
                        "description": "Filter by task status",
                        "required": False,
                        "schema": {
                            "type": "string",
                            "enum": ["pending", "running", "completed", "failed"],
                        },
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "description": "Maximum number of tasks to return",
                        "required": False,
                        "schema": {"type": "integer", "default": 10, "minimum": 1},
                    },
                ],
                responses={
                    "200": {
                        "description": "List of tasks",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Task"},
                                }
                            }
                        },
                    }
                },
                security=[{"basicAuth": []}],
            )
        )

        # Get Task Status Endpoint
        self.add_endpoint(
            APIEndpoint(
                path="/tasks/{task_id}",
                method="GET",
                summary="Get Task Status",
                description="Get detailed status of a specific task",
                tags=["Tasks"],
                parameters=[
                    {
                        "name": "task_id",
                        "in": "path",
                        "description": "Task identifier",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                responses={
                    "200": {
                        "description": "Task details",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Task"}}
                        },
                    },
                    "404": {
                        "description": "Task not found",
                        "content": {
                            "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                        },
                    },
                },
                security=[{"basicAuth": []}],
            )
        )

        # List Agents Endpoint
        self.add_endpoint(
            APIEndpoint(
                path="/agents",
                method="GET",
                summary="List Agents",
                description="List all available agents and their status",
                tags=["Agents"],
                responses={
                    "200": {
                        "description": "List of agents",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Agent"},
                                }
                            }
                        },
                    }
                },
                security=[{"basicAuth": []}],
            )
        )

        # Security Events Endpoint
        self.add_endpoint(
            APIEndpoint(
                path="/security/events",
                method="GET",
                summary="List Security Events",
                description="List security events with optional filtering",
                tags=["Security"],
                parameters=[
                    {
                        "name": "severity",
                        "in": "query",
                        "description": "Filter by severity level",
                        "required": False,
                        "schema": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "low", "info"],
                        },
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "description": "Maximum number of events to return",
                        "required": False,
                        "schema": {"type": "integer", "default": 10},
                    },
                ],
                responses={
                    "200": {
                        "description": "List of security events",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/SecurityEvent"},
                                }
                            }
                        },
                    }
                },
                security=[{"basicAuth": []}],
            )
        )

        # Metacognition Insights Endpoint
        self.add_endpoint(
            APIEndpoint(
                path="/metacognition/insights",
                method="GET",
                summary="Get Metacognition Insights",
                description="Get insights from the metacognition system",
                tags=["Metacognition"],
                parameters=[
                    {
                        "name": "type",
                        "in": "query",
                        "description": "Filter by insight type",
                        "required": False,
                        "schema": {
                            "type": "string",
                            "enum": ["pattern", "anomaly", "optimization", "goal"],
                        },
                    }
                ],
                responses={
                    "200": {
                        "description": "List of insights",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/MetacognitionInsight"},
                                }
                            }
                        },
                    }
                },
                security=[{"basicAuth": []}],
            )
        )

    def add_endpoint(self, endpoint: APIEndpoint) -> None:
        """
        Add an endpoint to the documentation.

        Args:
            endpoint: API endpoint documentation
        """
        if endpoint.path not in self.endpoints:
            self.endpoints[endpoint.path] = {}
        self.endpoints[endpoint.path][endpoint.method] = endpoint

    def generate_openapi_spec(self) -> Dict[str, Any]:
        """
        Generate complete OpenAPI 3.0 specification.

        Returns:
            OpenAPI specification dictionary
        """
        spec: Dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {
                "title": "OmniMind API",
                "version": "1.0.0",
                "description": (
                    "OmniMind Autonomous AI System API - "
                    "Complete REST API for interacting with the multi-agent system, "
                    "including task orchestration, agent management, security monitoring, "
                    "and metacognition insights."
                ),
                "contact": {
                    "name": "OmniMind Support",
                    "email": "support@omnimind.ai",
                },
                "license": {
                    "name": "MIT",
                    "url": "https://opensource.org/licenses/MIT",
                },
            },
            "servers": [
                {
                    "url": "http://localhost:8000",
                    "description": "Development server",
                },
                {
                    "url": "https://api.omnimind.ai",
                    "description": "Production server",
                },
            ],
            "tags": [
                {"name": "System", "description": "System health and information"},
                {"name": "Tasks", "description": "Task management and orchestration"},
                {"name": "Agents", "description": "Agent status and management"},
                {"name": "Security", "description": "Security events and monitoring"},
                {
                    "name": "Metacognition",
                    "description": "Metacognition insights and analytics",
                },
            ],
            "paths": {},
            "components": {
                "schemas": self.schemas,
                "securitySchemes": {
                    "basicAuth": {
                        "type": "http",
                        "scheme": "basic",
                        "description": "Basic HTTP authentication",
                    }
                },
            },
        }

        # Add endpoints to paths
        for path, methods in self.endpoints.items():
            spec["paths"][path] = {}
            for method, endpoint in methods.items():
                spec["paths"][path][method.lower()] = endpoint.to_openapi()

        return spec

    def export_openapi_json(self, filename: str = "openapi.json") -> Path:
        """
        Export OpenAPI specification to JSON file.

        Args:
            filename: Output filename

        Returns:
            Path to exported file
        """
        spec = self.generate_openapi_spec()
        output_path = self.output_dir / filename

        with output_path.open("w") as f:
            json.dump(spec, f, indent=2)

        logger.info(f"OpenAPI specification exported: {output_path}")
        return output_path

    def generate_markdown_docs(self) -> Path:
        """
        Generate Markdown documentation for all endpoints.

        Returns:
            Path to generated documentation
        """
        output_path = self.output_dir / "API_DOCUMENTATION.md"

        with output_path.open("w") as f:
            f.write("# OmniMind API Documentation\n\n")
            f.write("**Version:** 1.0.0\n\n")
            f.write("Complete REST API documentation for OmniMind Autonomous AI System.\n\n")

            # Group by tags
            by_tag = {}  # type: ignore[var-annotated]
            for methods in self.endpoints.values():
                for endpoint in methods.values():
                    for tag in endpoint.tags:
                        if tag not in by_tag:
                            by_tag[tag] = []
                        by_tag[tag].append(endpoint)

            # Write sections
            for tag, endpoints in sorted(by_tag.items()):
                f.write(f"## {tag}\n\n")

                for endpoint in endpoints:
                    f.write(f"### {endpoint.method} {endpoint.path}\n\n")
                    f.write(f"**Summary:** {endpoint.summary}\n\n")
                    f.write(f"{endpoint.description}\n\n")

                    # Parameters
                    if endpoint.parameters:
                        f.write("**Parameters:**\n\n")
                        for param in endpoint.parameters:
                            f.write(
                                f"- `{param['name']}` ({param['in']}): "
                                f"{param.get('description', 'No description')}\n"
                            )
                        f.write("\n")

                    # Request body
                    if endpoint.request_body:
                        f.write("**Request Body:**\n\n")
                        f.write("```json\n")
                        if "request" in endpoint.examples:
                            f.write(json.dumps(endpoint.examples["request"], indent=2))
                        f.write("\n```\n\n")

                    # Responses
                    if endpoint.responses:
                        f.write("**Responses:**\n\n")
                        for code, response in endpoint.responses.items():
                            f.write(f"- `{code}`: {response['description']}\n")
                        f.write("\n")

                    # Example
                    if "response" in endpoint.examples:
                        f.write("**Example Response:**\n\n")
                        f.write("```json\n")
                        f.write(json.dumps(endpoint.examples["response"], indent=2))
                        f.write("\n```\n\n")

                    f.write("---\n\n")

        logger.info(f"Markdown documentation generated: {output_path}")
        return output_path

    def generate_sdk_template(self, language: str = "python") -> Path:
        """
        Generate SDK template for specified language.

        Args:
            language: Programming language (python, javascript)

        Returns:
            Path to generated SDK template
        """
        if language == "python":
            return self._generate_python_sdk()
        elif language == "javascript":
            return self._generate_javascript_sdk()
        else:
            raise ValueError(f"Unsupported language: {language}")

    def _generate_python_sdk(self) -> Path:
        """Generate Python SDK template."""
        output_path = self.output_dir / "omnimind_sdk.py"

        sdk_code = '''"""
OmniMind Python SDK

Official Python client for the OmniMind API.
"""

import requests
from typing import Any, Dict, List, Optional


class OmniMindClient:
    """OmniMind API client."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        username: str = "",
        password: str = "",
    ):
        """
        Initialize OmniMind client.

        Args:
            base_url: API base URL
            username: Basic auth username
            password: Basic auth password
        """
        self.base_url = base_url.rstrip("/")
        self.auth = (username, password) if username else None

    def submit_task(self, description: str, priority: str = "medium") -> Dict[str, Any]:
        """
        Submit a new task.

        Args:
            description: Task description
            priority: Task priority (low, medium, high, critical)

        Returns:
            Task object
        """
        response = requests.post(
            f"{self.base_url}/tasks",
            json={"description": description, "priority": priority},
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Get task status.

        Args:
            task_id: Task identifier

        Returns:
            Task object
        """
        response = requests.get(
            f"{self.base_url}/tasks/{task_id}",
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()

    def list_tasks(
        self, status: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List tasks.

        Args:
            status: Filter by status
            limit: Maximum number of tasks

        Returns:
            List of task objects
        """
        params = {"limit": limit}
        if status:
            params["status"] = status

        response = requests.get(
            f"{self.base_url}/tasks",
            params=params,
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List agents.

        Returns:
            List of agent objects
        """
        response = requests.get(
            f"{self.base_url}/agents",
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()

    def get_security_events(
        self, severity: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get security events.

        Args:
            severity: Filter by severity
            limit: Maximum number of events

        Returns:
            List of security event objects
        """
        params = {"limit": limit}
        if severity:
            params["severity"] = severity

        response = requests.get(
            f"{self.base_url}/security/events",
            params=params,
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()

    def get_metacognition_insights(
        self, insight_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metacognition insights.

        Args:
            insight_type: Filter by type

        Returns:
            List of insight objects
        """
        params = {}
        if insight_type:
            params["type"] = insight_type

        response = requests.get(
            f"{self.base_url}/metacognition/insights",
            params=params,
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()
'''

        with output_path.open("w") as f:
            f.write(sdk_code)

        logger.info(f"Python SDK generated: {output_path}")
        return output_path

    def _generate_javascript_sdk(self) -> Path:
        """Generate JavaScript SDK template."""
        output_path = self.output_dir / "omnimind-sdk.js"

        sdk_code = """/**
 * OmniMind JavaScript SDK
 *
 * Official JavaScript client for the OmniMind API.
 */

class OmniMindClient {
    /**
     * Initialize OmniMind client.
     *
     * @param {string} baseURL - API base URL
     * @param {string} username - Basic auth username
     * @param {string} password - Basic auth password
     */
    constructor(baseURL = 'http://localhost:8000', username = '', password = '') {
        this.baseURL = baseURL.replace(/\\/$/, '');
        this.auth = username ? btoa(`${username}:${password}`) : null;
    }

    /**
     * Make authenticated request.
     *
     * @private
     */
    async _request(method, path, data = null) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (this.auth) {
            headers['Authorization'] = `Basic ${this.auth}`;
        }

        const options = {
            method,
            headers,
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${this.baseURL}${path}`, options);

        if (!response.ok) {
            throw new Error(`API request failed: ${response.statusText}`);
        }

        return response.json();
    }

    /**
     * Submit a new task.
     *
     * @param {string} description - Task description
     * @param {string} priority - Task priority
     * @returns {Promise<object>} Task object
     */
    async submitTask(description, priority = 'medium') {
        return this._request('POST', '/tasks', { description, priority });
    }

    /**
     * Get task status.
     *
     * @param {string} taskId - Task identifier
     * @returns {Promise<object>} Task object
     */
    async getTask(taskId) {
        return this._request('GET', `/tasks/${taskId}`);
    }

    /**
     * List tasks.
     *
     * @param {string} status - Filter by status
     * @param {number} limit - Maximum number of tasks
     * @returns {Promise<Array>} List of task objects
     */
    async listTasks(status = null, limit = 10) {
        const params = new URLSearchParams({ limit });
        if (status) params.append('status', status);
        return this._request('GET', `/tasks?${params}`);
    }

    /**
     * List agents.
     *
     * @returns {Promise<Array>} List of agent objects
     */
    async listAgents() {
        return this._request('GET', '/agents');
    }

    /**
     * Get security events.
     *
     * @param {string} severity - Filter by severity
     * @param {number} limit - Maximum number of events
     * @returns {Promise<Array>} List of security event objects
     */
    async getSecurityEvents(severity = null, limit = 10) {
        const params = new URLSearchParams({ limit });
        if (severity) params.append('severity', severity);
        return this._request('GET', `/security/events?${params}`);
    }

    /**
     * Get metacognition insights.
     *
     * @param {string} type - Filter by type
     * @returns {Promise<Array>} List of insight objects
     */
    async getMetacognitionInsights(type = null) {
        const params = type ? `?type=${type}` : '';
        return this._request('GET', `/metacognition/insights${params}`);
    }
}

// Export for Node.js and browsers
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OmniMindClient;
}
"""

        with output_path.open("w") as f:
            f.write(sdk_code)

        logger.info(f"JavaScript SDK generated: {output_path}")
        return output_path

    def generate_postman_collection(self) -> Path:
        """
        Generate Postman collection for API testing.

        Returns:
            Path to Postman collection file
        """
        collection = {
            "info": {
                "name": "OmniMind API",
                "description": "Complete API collection for OmniMind",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "auth": {
                "type": "basic",
                "basic": [
                    {"key": "username", "value": "{{username}}", "type": "string"},
                    {"key": "password", "value": "{{password}}", "type": "string"},
                ],
            },
            "item": [],
        }

        # Group by tags
        by_tag: Dict[str, List[APIEndpoint]] = {}
        for methods in self.endpoints.values():
            for endpoint in methods.values():
                for tag in endpoint.tags:
                    if tag not in by_tag:
                        by_tag[tag] = []
                    by_tag[tag].append(endpoint)

        # Add items
        for tag, endpoints in sorted(by_tag.items()):
            folder = {"name": tag, "item": []}

            for endpoint in endpoints:
                item: Dict[str, Any] = {
                    "name": endpoint.summary,
                    "request": {
                        "method": endpoint.method,
                        "header": [],
                        "url": {
                            "raw": f"{{{{base_url}}}}{endpoint.path}",
                            "host": ["{{base_url}}"],
                            "path": endpoint.path.strip("/").split("/"),
                        },
                    },
                }

                # Add request body if present
                if endpoint.request_body and "request" in endpoint.examples:
                    item["request"]["body"] = {
                        "mode": "raw",
                        "raw": json.dumps(endpoint.examples["request"], indent=2),
                        "options": {"raw": {"language": "json"}},
                    }

                folder["item"].append(item)  # type: ignore[attr-defined]

            collection["item"].append(folder)  # type: ignore[attr-defined]

        output_path = self.output_dir / "OmniMind_API.postman_collection.json"
        with output_path.open("w") as f:
            json.dump(collection, f, indent=2)

        logger.info(f"Postman collection generated: {output_path}")
        return output_path

    def generate_all_documentation(self) -> Dict[str, Path]:
        """
        Generate all documentation formats.

        Returns:
            Dictionary of generated file paths
        """
        logger.info("Generating complete API documentation...")

        outputs = {
            "openapi": self.export_openapi_json(),
            "markdown": self.generate_markdown_docs(),
            "python_sdk": self.generate_sdk_template("python"),
            "javascript_sdk": self.generate_sdk_template("javascript"),
            "postman": self.generate_postman_collection(),
        }

        logger.info("All API documentation generated successfully")
        return outputs
