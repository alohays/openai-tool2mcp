from typing import Any, Optional

from pydantic import BaseModel, Field


class MCPRequest(BaseModel):
    """Model for MCP tool request"""

    parameters: dict[str, Any] = Field(default_factory=dict)
    context: Optional[dict[str, Any]] = Field(default=None)


class MCPResponse(BaseModel):
    """Model for MCP tool response"""

    content: str
    error: Optional[str] = None
    context: Optional[dict[str, Any]] = Field(default_factory=dict)
