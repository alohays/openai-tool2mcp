from typing import Any

from pydantic import BaseModel, Field


class MCPRequest(BaseModel):
    """Model for MCP tool request"""

    parameters: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] | None = Field(default=None)


class MCPResponse(BaseModel):
    """Model for MCP tool response"""

    content: str
    error: str | None = None
    context: dict[str, Any] | None = Field(default_factory=dict)
