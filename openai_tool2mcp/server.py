from fastapi import FastAPI, HTTPException

from .models.mcp import MCPRequest
from .openai_client.client import OpenAIClient
from .tools import BrowserAdapter, CodeInterpreterAdapter, FileManagerAdapter, ToolRegistry, WebSearchAdapter
from .translator import mcp_to_openai, openai_to_mcp
from .utils.config import APIKeyMissingError, ServerConfig
from .utils.logging import logger


class MCPServer:
    """MCP server that wraps OpenAI tools"""

    def __init__(self, config=None):
        """
        Initialize the MCP server.

        Args:
            config (ServerConfig, optional): Server configuration
        """
        self.app = FastAPI(
            title="OpenAI Tool2MCP Server", description="MCP server that wraps OpenAI built-in tools", version="0.1.0"
        )
        self.config = config or ServerConfig()

        # Ensure we have an API key
        if not self.config.openai_api_key:
            raise APIKeyMissingError()

        self.openai_client = OpenAIClient(
            api_key=self.config.openai_api_key,
            request_timeout=self.config.request_timeout,
            max_retries=self.config.max_retries,
        )
        self.tool_registry = ToolRegistry(self.config.tools)
        self.tools_map = self._build_tools_map()

        # Register routes
        self.register_routes()

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

    def register_routes(self):
        """Register FastAPI routes for the MCP protocol"""

        @self.app.get("/")
        async def root():
            """Root endpoint for the API"""
            return {
                "name": "OpenAI Tool2MCP Server",
                "version": "0.1.0",
                "tools": [
                    {"id": tool_id, "description": adapter.description} for tool_id, adapter in self.tools_map.items()
                ],
            }

        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            return {"status": "ok"}

        @self.app.get("/tools")
        async def list_tools():
            """List available tools"""
            return {
                "tools": [
                    {"id": tool_id, "description": adapter.description} for tool_id, adapter in self.tools_map.items()
                ]
            }

        @self.app.post("/v1/tools/{tool_id}/invoke")
        async def invoke_tool(tool_id: str, request: MCPRequest):
            """
            Invoke a tool with the specified ID.

            Args:
                tool_id (str): ID of the tool to invoke
                request (MCPRequest): Tool request

            Returns:
                MCPResponse: Tool response
            """
            # Check if tool exists
            if tool_id not in self.tools_map:
                raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")

            logger.info(f"Invoking tool: {tool_id}")

            try:
                # Get the tool adapter
                adapter = self.tools_map[tool_id]

                # Translate the request parameters using the adapter
                parameters = await adapter.translate_request(request)

                # Create an OpenAI tool request
                openai_request = mcp_to_openai.translate_request(request, tool_id)

                # Override the parameters with the adapter-specific ones
                openai_request.parameters = parameters

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
                else:
                    # Fallback to generic translation if no tool output is available
                    mcp_response = openai_to_mcp.translate_response(openai_response)
            except Exception as e:
                logger.error(f"Error invoking tool {tool_id}: {e!s}")
                raise HTTPException(status_code=500, detail=str(e)) from e
            else:
                return mcp_response

    def start(self, host="127.0.0.1", port=8000):
        """
        Start the MCP server.

        Args:
            host (str): Host address to bind to
            port (int): Port to listen on
        """
        import uvicorn

        logger.info(f"Starting MCP server on {host}:{port}")
        logger.info(f"Available tools: {', '.join(self.tools_map.keys())}")

        uvicorn.run(self.app, host=host, port=port)
