from typing import Any, Optional

from pydantic import BaseModel, Field


class ToolRequest(BaseModel):
    """Model for OpenAI tool request"""

    tool_type: str
    parameters: dict[str, Any]
    thread_id: Optional[str] = None
    instructions: Optional[str] = None


class ToolOutput(BaseModel):
    """Model for OpenAI tool output"""

    output: str
    error: Optional[str] = None


class ToolResponse(BaseModel):
    """Model for OpenAI tool response"""

    thread_id: str
    tool_outputs: list[Any] = Field(default_factory=list)
