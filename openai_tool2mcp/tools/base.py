from abc import ABC, abstractmethod

from ..models.mcp import MCPRequest, MCPResponse


class ToolAdapter(ABC):
    """Base class for tool adapters"""

    @property
    @abstractmethod
    def tool_id(self) -> str:
        """Get the MCP tool ID"""
        pass

    @property
    @abstractmethod
    def openai_tool_type(self) -> str:
        """Get the OpenAI tool type"""
        pass

    @property
    def description(self) -> str:
        """Get the tool description"""
        return "Tool adapter for OpenAI built-in tool"

    @abstractmethod
    async def translate_request(self, request: MCPRequest) -> dict:
        """
        Translate MCP request to OpenAI parameters

        Args:
            request: The MCP request to translate

        Returns:
            Dictionary of OpenAI parameters
        """
        pass

    @abstractmethod
    async def translate_response(self, response: dict) -> MCPResponse:
        """
        Translate OpenAI response to MCP response

        Args:
            response: The OpenAI response to translate

        Returns:
            MCP response object
        """
        pass
