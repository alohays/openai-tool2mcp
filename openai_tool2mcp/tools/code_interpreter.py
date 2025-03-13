from ..models.mcp import MCPRequest, MCPResponse
from ..translator.openai_to_mcp import format_code_result
from ..utils.logging import logger
from .base import ToolAdapter


class CodeInterpreterAdapter(ToolAdapter):
    """Adapter for OpenAI's code interpreter tool"""

    @property
    def tool_id(self) -> str:
        """Get the MCP tool ID"""
        return "code-execution"

    @property
    def openai_tool_type(self) -> str:
        """Get the OpenAI tool type"""
        return "code_interpreter"

    @property
    def description(self) -> str:
        """Get the tool description"""
        return "Execute code and return the result"

    async def translate_request(self, request: MCPRequest) -> dict:
        """
        Translate MCP request to OpenAI parameters

        Args:
            request: The MCP request to translate

        Returns:
            Dictionary of OpenAI parameters
        """
        # Extract code to execute
        code = request.parameters.get("code", "")
        language = request.parameters.get("language", "python")

        logger.debug(f"Translating code execution request with language: {language}")

        # Return OpenAI parameters
        return {"code": code, "language": language}

    async def translate_response(self, response: dict) -> MCPResponse:
        """
        Translate OpenAI response to MCP response

        Args:
            response: The OpenAI response to translate

        Returns:
            MCP response object
        """
        # Extract execution result
        result = response.get("result", {})

        logger.debug("Translating code execution response")

        # Format result as markdown
        content = format_code_result(result)

        # Check for errors
        error = None
        if isinstance(result, dict) and "error" in result:
            error = result["error"]

        # Return MCP response
        return MCPResponse(content=content, error=error, context={"language": response.get("language", "python")})
