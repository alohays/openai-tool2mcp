from mcp.server.fastmcp import FastMCP

from .models.mcp import MCPRequest
from .openai_client.client import OpenAIClient
from .tools import BrowserAdapter, CodeInterpreterAdapter, FileManagerAdapter, ToolRegistry, WebSearchAdapter
from .translator import mcp_to_openai, openai_to_mcp
from .utils.config import APIKeyMissingError, ServerConfig
from .utils.logging import logger


class ToolInvocationError(ValueError):
    """Error raised when a tool invocation fails."""

    def __init__(self):
        super().__init__("Error invoking tool")


class MCPServer:
    """MCP server that wraps OpenAI tools"""

    def __init__(self, config=None):
        """
        Initialize the MCP server.

        Args:
            config (ServerConfig, optional): Server configuration
        """
        self.config = config or ServerConfig()

        # Ensure we have an API key
        if not self.config.openai_api_key:
            raise APIKeyMissingError()

        # Initialize the FastMCP server
        self.mcp = FastMCP("openai-tool2mcp")

        self.openai_client = OpenAIClient(
            api_key=self.config.openai_api_key,
            request_timeout=self.config.request_timeout,
            max_retries=self.config.max_retries,
        )
        self.tool_registry = ToolRegistry(self.config.tools)
        self.tools_map = self._build_tools_map()

        # Register tools with MCP SDK
        self._register_mcp_tools()

    def _build_tools_map(self):
        """Build a map of tool adapters"""
        tools_map = {}

        # Register default tool adapters
        adapters = [WebSearchAdapter(), CodeInterpreterAdapter(), BrowserAdapter(), FileManagerAdapter()]

        for adapter in adapters:
            # Only register if the tool is enabled
            if adapter.openai_tool_type in self.config.tools:
                tools_map[adapter.tool_id] = adapter

        return tools_map

    def _register_mcp_tools(self):
        """Register tools with the MCP SDK"""
        for tool_id, adapter in self.tools_map.items():
            # Define a tool handler for each adapter
            # Create a closure to properly capture the values
            def create_tool_handler(tool_id=tool_id, adapter=adapter):
                @self.mcp.tool(name=tool_id, description=adapter.description)
                async def tool_handler(**parameters):
                    """
                    MCP tool handler for OpenAI tools.
                    """
                    # Create an MCP request from the parameters
                    mcp_request = MCPRequest(parameters=parameters)

                    # Translate the request parameters using the adapter
                    translated_params = await adapter.translate_request(mcp_request)

                    # Create an OpenAI tool request
                    openai_request = mcp_to_openai.translate_request(mcp_request, tool_id)

                    # Override the parameters with the adapter-specific ones
                    openai_request.parameters = translated_params

                    try:
                        # Call OpenAI API to execute the tool
                        openai_response = await self.openai_client.invoke_tool(openai_request)

                        # Translate the OpenAI response to MCP format using the adapter
                        if openai_response.tool_outputs:
                            # Use the adapter to translate the tool-specific response
                            mcp_response = await adapter.translate_response(openai_response.tool_outputs[0].output)

                            # Add thread_id to context for state management
                            if mcp_response.context is None:
                                mcp_response.context = {}
                            mcp_response.context["thread_id"] = openai_response.thread_id

                            # Return the response content which will be used by MCP SDK
                            return mcp_response.content
                        else:
                            # Fallback to generic translation
                            mcp_response = openai_to_mcp.translate_response(openai_response)
                            return mcp_response.content
                    except Exception as e:
                        logger.error(f"Error invoking tool {tool_id}: {e!s}")
                        # Using custom exception class to fix TRY003
                        raise ToolInvocationError() from e

                return tool_handler

            # Create and register the tool handler
            create_tool_handler()

    def start(self, host="127.0.0.1", port=8000, transport=None):
        """
        Start the MCP server.

        Args:
            host (str): Host address to bind to (used if a custom HTTP server is started)
            port (int): Port to listen on (used if a custom HTTP server is started)
            transport (str, optional): Transport method ('stdio' or 'sse')
        """
        logger.info("Starting MCP server")
        logger.info(f"Available tools: {', '.join(self.tools_map.keys())}")

        # If stdio transport is specified, use it
        if transport == "stdio":
            logger.info("Using STDIO transport")
            self.mcp.run(transport="stdio")
        # If sse transport is specified, use it
        elif transport == "sse":
            logger.info("Using SSE transport")
            self.mcp.run(transport="sse")
        # Otherwise start a custom HTTP server
        else:
            logger.info(f"Using custom HTTP transport on {host}:{port}")
            import uvicorn
            from fastapi import FastAPI

            app = FastAPI(
                title="OpenAI Tool2MCP Server",
                description="MCP server that wraps OpenAI built-in tools",
                version="0.1.0",
            )

            # Define the root endpoint
            @app.get("/")
            async def root():
                return {
                    "name": "OpenAI Tool2MCP Server",
                    "version": "0.1.0",
                    "tools": [
                        {"id": tool_id, "description": adapter.description}
                        for tool_id, adapter in self.tools_map.items()
                    ],
                }

            # Define the health check endpoint
            @app.get("/health")
            async def health():
                return {"status": "ok"}

            # Start the custom HTTP server
            uvicorn.run(app, host=host, port=port)
