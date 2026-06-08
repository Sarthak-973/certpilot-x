from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class FoundryIntegrationHooks:
    """Placeholder hooks for future Azure AI Foundry grounding."""

    project_endpoint: str | None = None
    model_deployment: str = "gpt-4o"

    def retrieve_grounded_context(self, query: str) -> dict[str, Any]:
        return {
            "status": "not_configured",
            "query": query,
            "source": "future-foundry-iq-hook",
        }


@dataclass
class MCPIntegrationHooks:
    """Placeholder hooks for Microsoft Learn or other MCP tool integrations."""

    def search_learning_content(self, topic: str) -> dict[str, Any]:
        return {
            "status": "not_configured",
            "topic": topic,
            "source": "future-mcp-hook",
        }
