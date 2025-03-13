from ..models.mcp import MCPRequest, MCPResponse
from ..translator.openai_to_mcp import format_search_results
from ..utils.logging import logger
from .base import ToolAdapter


class WebSearchAdapter(ToolAdapter):
    """Adapter for OpenAI's web search tool"""

    @property
    def tool_id(self) -> str:
        """Get the MCP tool ID"""
        return "web-search"

    @property
    def openai_tool_type(self) -> str:
        """Get the OpenAI tool type"""
        return "retrieval"

    @property
    def description(self) -> str:
        """Get the tool description"""
        return "Search the web for real-time information"

    async def translate_request(self, request: MCPRequest) -> dict:
        """
        Translate MCP request to OpenAI parameters

        Args:
            request: The MCP request to translate

        Returns:
            Dictionary of OpenAI parameters
        """
        # Extract search query
        query = request.parameters.get("query", "")

        logger.debug(f"Translating web search request with query: {query}")

        # Return OpenAI parameters
        return {"query": query}

    async def translate_response(self, response: dict) -> MCPResponse:
        """
        Translate OpenAI response to MCP response

        Args:
            response: The OpenAI response to translate

        Returns:
            MCP response object
        """
        # Extract search results
        results = response.get("results", [])

        logger.debug(f"Translating web search response with {len(results)} results")

        # Format results as markdown
        content = format_search_results(results)

        # Return MCP response
        return MCPResponse(content=content, context={"search_count": len(results)})
