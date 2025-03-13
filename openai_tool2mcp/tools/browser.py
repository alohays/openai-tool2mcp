from ..models.mcp import MCPRequest, MCPResponse
from ..utils.logging import logger
from .base import ToolAdapter


class BrowserAdapter(ToolAdapter):
    """Adapter for OpenAI's web browser tool"""

    @property
    def tool_id(self) -> str:
        """Get the MCP tool ID"""
        return "browser"

    @property
    def openai_tool_type(self) -> str:
        """Get the OpenAI tool type"""
        return "web_browser"

    @property
    def description(self) -> str:
        """Get the tool description"""
        return "Browse websites and interact with web content"

    async def translate_request(self, request: MCPRequest) -> dict:
        """
        Translate MCP request to OpenAI parameters

        Args:
            request: The MCP request to translate

        Returns:
            Dictionary of OpenAI parameters
        """
        # Extract URL and action
        url = request.parameters.get("url", "")
        action = request.parameters.get("action", "browse")

        logger.debug(f"Translating browser request for URL: {url}, action: {action}")

        # Return OpenAI parameters
        return {"url": url, "action": action}

    async def translate_response(self, response: dict) -> MCPResponse:
        """
        Translate OpenAI response to MCP response

        Args:
            response: The OpenAI response to translate

        Returns:
            MCP response object
        """
        # Extract content
        content = response.get("content", "")
        title = response.get("title", "")
        url = response.get("url", "")

        logger.debug(f"Translating browser response for URL: {url}")

        # Format content as markdown
        formatted_content = f"# {title}\n\n{content}" if title else content

        # Check for errors
        error = response.get("error")

        # Return MCP response
        return MCPResponse(content=formatted_content, error=error, context={"url": url, "title": title})
