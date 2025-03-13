from ..models.mcp import MCPRequest, MCPResponse
from ..utils.logging import logger
from .base import ToolAdapter


class FileManagerAdapter(ToolAdapter):
    """Adapter for OpenAI's file management tool"""

    @property
    def tool_id(self) -> str:
        """Get the MCP tool ID"""
        return "file-io"

    @property
    def openai_tool_type(self) -> str:
        """Get the OpenAI tool type"""
        return "file_search"

    @property
    def description(self) -> str:
        """Get the tool description"""
        return "Search and access file content"

    async def translate_request(self, request: MCPRequest) -> dict:
        """
        Translate MCP request to OpenAI parameters

        Args:
            request: The MCP request to translate

        Returns:
            Dictionary of OpenAI parameters
        """
        # Extract file operation parameters
        operation = request.parameters.get("operation", "read")
        path = request.parameters.get("path", "")
        content = request.parameters.get("content", "")

        logger.debug(f"Translating file request for operation: {operation}, path: {path}")

        # Return OpenAI parameters
        return {"operation": operation, "path": path, "content": content}

    async def translate_response(self, response: dict) -> MCPResponse:
        """
        Translate OpenAI response to MCP response

        Args:
            response: The OpenAI response to translate

        Returns:
            MCP response object
        """
        # Extract result
        path = response.get("path", "")
        operation = response.get("operation", "read")
        content = response.get("content", "")

        logger.debug(f"Translating file response for operation: {operation}, path: {path}")

        # Format content based on operation
        if operation == "read":
            formatted_content = f"# File: {path}\n\n```\n{content}\n```"
        elif operation == "write":
            formatted_content = f"File written to {path}"
        elif operation == "delete":
            formatted_content = f"File deleted: {path}"
        elif operation == "list":
            formatted_content = f"# Directory: {path}\n\n"
            for item in content.split("\n"):
                if item.strip():
                    formatted_content += f"- {item.strip()}\n"
        else:
            formatted_content = f"Operation '{operation}' completed on {path}"

        # Check for errors
        error = response.get("error")

        # Return MCP response
        return MCPResponse(content=formatted_content, error=error, context={"path": path, "operation": operation})
