# Implementation Guide

This guide provides detailed technical information on implementing the openai-tool2mcp bridge, focusing on code structure, key components, and protocol details.

## Project Structure

The project follows a modular architecture with the following structure:

```
openai_tool2mcp/
├── __init__.py             # Package exports
├── server.py               # MCP server implementation
├── translator/
│   ├── __init__.py
│   ├── mcp_to_openai.py    # MCP to OpenAI translation
│   └── openai_to_mcp.py    # OpenAI to MCP translation
├── openai_client/
│   ├── __init__.py
│   ├── client.py           # OpenAI API client
│   └── assistants.py       # Assistants API wrapper
├── tools/
│   ├── __init__.py
│   ├── registry.py         # Tool registry
│   ├── web_search.py       # Web search implementation
│   ├── code_interpreter.py # Code interpreter implementation
│   ├── browser.py          # Web browser implementation
│   └── file_manager.py     # File management implementation
├── models/
│   ├── __init__.py
│   ├── mcp.py              # MCP protocol models
│   └── openai.py           # OpenAI API models
└── utils/
    ├── __init__.py
    ├── config.py           # Configuration management
    ├── logging.py          # Logging utilities
    └── security.py         # Security utilities
```

## Core Components

### 1. MCP Server Implementation

The MCP server is implemented using FastAPI for high performance and compatibility with async operations:

```python
from fastapi import FastAPI, HTTPException, Depends
from .models.mcp import MCPRequest, MCPResponse
from .translator import mcp_to_openai, openai_to_mcp
from .openai_client import OpenAIClient
from .tools import ToolRegistry

class MCPServer:
    def __init__(self, config=None):
        self.app = FastAPI()
        self.config = config or ServerConfig()
        self.openai_client = OpenAIClient(self.config.openai_api_key)
        self.tool_registry = ToolRegistry(self.config.tools)

        # Register routes
        self.register_routes()

    def register_routes(self):
        @self.app.post("/v1/tools/{tool_id}/invoke")
        async def invoke_tool(tool_id: str, request: MCPRequest):
            # Validate tool exists
            if not self.tool_registry.has_tool(tool_id):
                raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")

            # Translate MCP request to OpenAI format
            openai_request = mcp_to_openai.translate_request(request, tool_id)

            # Call OpenAI API
            openai_response = await self.openai_client.invoke_tool(openai_request)

            # Translate OpenAI response to MCP format
            mcp_response = openai_to_mcp.translate_response(openai_response)

            return mcp_response

    def start(self, host="127.0.0.1", port=8000):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)
```

### 2. Protocol Translation

The translation layer handles the mapping between MCP and OpenAI formats:

#### MCP to OpenAI Translation

```python
from ..models.mcp import MCPRequest
from ..models.openai import OpenAIToolRequest

def translate_request(mcp_request: MCPRequest, tool_id: str) -> OpenAIToolRequest:
    """
    Translate an MCP request to an OpenAI request format.

    Args:
        mcp_request: The MCP request to translate
        tool_id: The ID of the tool to invoke

    Returns:
        An OpenAI tool request object
    """
    # Extract tool parameters
    parameters = mcp_request.parameters

    # Extract context information
    context = mcp_request.context or {}

    # Determine if this is a new or existing conversation
    thread_id = context.get("thread_id")

    # Create OpenAI request
    openai_request = OpenAIToolRequest(
        tool_type=map_tool_id_to_openai_type(tool_id),
        parameters=parameters,
        thread_id=thread_id,
        instructions=context.get("instructions", "")
    )

    return openai_request

def map_tool_id_to_openai_type(tool_id: str) -> str:
    """Map MCP tool IDs to OpenAI tool types"""
    mapping = {
        "web-search": "retrieval",
        "code-execution": "code_interpreter",
        "browser": "web_browser",
        "file-io": "file_search"
    }
    return mapping.get(tool_id, tool_id)
```

#### OpenAI to MCP Translation

```python
from ..models.mcp import MCPResponse
from ..models.openai import OpenAIToolResponse

def translate_response(openai_response: OpenAIToolResponse) -> MCPResponse:
    """
    Translate an OpenAI response to an MCP response format.

    Args:
        openai_response: The OpenAI response to translate

    Returns:
        An MCP response object
    """
    # Extract tool output
    tool_output = openai_response.tool_outputs[0] if openai_response.tool_outputs else None

    if not tool_output:
        return MCPResponse(
            content="No result",
            error="Tool returned no output",
            context={"thread_id": openai_response.thread_id}
        )

    # Create MCP response
    mcp_response = MCPResponse(
        content=tool_output.output,
        error=tool_output.error if hasattr(tool_output, "error") else None,
        context={"thread_id": openai_response.thread_id}
    )

    return mcp_response
```

### 3. OpenAI Client

The OpenAI client manages interactions with the OpenAI API:

```python
import openai
from ..models.openai import OpenAIToolRequest, OpenAIToolResponse

class OpenAIClient:
    def __init__(self, api_key):
        self.client = openai.Client(api_key=api_key)

    async def invoke_tool(self, request: OpenAIToolRequest) -> OpenAIToolResponse:
        """
        Invoke an OpenAI tool.

        Args:
            request: The tool request

        Returns:
            The tool response
        """
        # Create or get thread
        thread_id = request.thread_id
        if not thread_id:
            thread = await self.client.beta.threads.create()
            thread_id = thread.id

        # Create message with tool call
        message = await self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"Please use the {request.tool_type} tool with these parameters: {request.parameters}",
        )

        # Create assistant with the appropriate tool
        assistant = await self.client.beta.assistants.create(
            name="Tool Executor",
            instructions=request.instructions or "Execute the requested tool function.",
            tools=[{"type": request.tool_type}],
            model="gpt-4o-mini-search-preview"
        )

        # Run the assistant
        run = await self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant.id
        )

        # Wait for completion
        run = await self._wait_for_run(thread_id, run.id)

        # Get tool outputs
        tool_outputs = run.required_action.submit_tool_outputs.tool_calls if hasattr(run, "required_action") else []

        # Create response
        response = OpenAIToolResponse(
            thread_id=thread_id,
            tool_outputs=tool_outputs
        )

        return response

    async def _wait_for_run(self, thread_id, run_id):
        """Wait for a run to complete"""
        import time

        while True:
            run = await self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )

            if run.status in ["completed", "failed", "requires_action"]:
                return run

            time.sleep(1)
```

### 4. Tool Registry

The tool registry manages available tools and their configurations:

```python
from enum import Enum, auto
from typing import List, Optional

class OpenAIBuiltInTools(Enum):
    WEB_SEARCH = "retrieval"
    CODE_INTERPRETER = "code_interpreter"
    WEB_BROWSER = "web_browser"
    FILE_SEARCH = "file_search"

class ToolRegistry:
    def __init__(self, enabled_tools=None):
        self.tools = {}
        self.enabled_tools = enabled_tools or [t.value for t in OpenAIBuiltInTools]
        self._register_default_tools()

    def _register_default_tools(self):
        """Register the default tool mappings"""
        self.tools = {
            "web-search": {
                "openai_tool": OpenAIBuiltInTools.WEB_SEARCH.value,
                "enabled": OpenAIBuiltInTools.WEB_SEARCH.value in self.enabled_tools
            },
            "code-execution": {
                "openai_tool": OpenAIBuiltInTools.CODE_INTERPRETER.value,
                "enabled": OpenAIBuiltInTools.CODE_INTERPRETER.value in self.enabled_tools
            },
            "browser": {
                "openai_tool": OpenAIBuiltInTools.WEB_BROWSER.value,
                "enabled": OpenAIBuiltInTools.WEB_BROWSER.value in self.enabled_tools
            },
            "file-io": {
                "openai_tool": OpenAIBuiltInTools.FILE_SEARCH.value,
                "enabled": OpenAIBuiltInTools.FILE_SEARCH.value in self.enabled_tools
            }
        }

    def has_tool(self, tool_id: str) -> bool:
        """Check if a tool is registered and enabled"""
        return tool_id in self.tools and self.tools[tool_id]["enabled"]

    def get_openai_tool_type(self, tool_id: str) -> Optional[str]:
        """Get the OpenAI tool type for a given MCP tool ID"""
        if self.has_tool(tool_id):
            return self.tools[tool_id]["openai_tool"]
        return None
```

## Configuration

Configuration is managed through a dedicated ServerConfig class:

```python
from typing import List, Optional
from .tools import OpenAIBuiltInTools

class ServerConfig:
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        tools: Optional[List[str]] = None,
        request_timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize server configuration.

        Args:
            openai_api_key: OpenAI API key (defaults to environment variable)
            tools: List of enabled tools (defaults to all)
            request_timeout: Timeout for API requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        import os

        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")

        self.tools = tools or [t.value for t in OpenAIBuiltInTools]
        self.request_timeout = request_timeout
        self.max_retries = max_retries
```

## MCP Protocol Implementation

The implementation follows the MCP protocol specification:

```python
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class MCPRequest(BaseModel):
    """Model for MCP tool request"""
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default=None)

class MCPResponse(BaseModel):
    """Model for MCP tool response"""
    content: str
    error: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
```

## Running the Server

To run the server with default configuration:

```python
from openai_tool2mcp import MCPServer, ServerConfig, OpenAIBuiltInTools

# Create server with all tools enabled
config = ServerConfig(
    tools=[t.value for t in OpenAIBuiltInTools]
)

# Start server
server = MCPServer(config)
server.start(host="127.0.0.1", port=8000)
```

## CLI Interface

The package includes a CLI interface for easy server startup:

```python
import argparse
import os
from .server import MCPServer, ServerConfig
from .tools import OpenAIBuiltInTools

def main():
    parser = argparse.ArgumentParser(description="Start an MCP server for OpenAI tools")
    parser.add_argument("--host", default="127.0.0.1", help="Host to listen on")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--api-key", help="OpenAI API key (defaults to OPENAI_API_KEY env var)")
    parser.add_argument("--tools", nargs="+", choices=[t.value for t in OpenAIBuiltInTools],
                        default=[t.value for t in OpenAIBuiltInTools],
                        help="Enabled tools")

    args = parser.parse_args()

    # Create server config
    config = ServerConfig(
        openai_api_key=args.api_key or os.environ.get("OPENAI_API_KEY"),
        tools=args.tools
    )

    # Start server
    server = MCPServer(config)
    print(f"Starting MCP server on {args.host}:{args.port}")
    server.start(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
```

## Error Handling

Robust error handling is implemented across the system:

```python
class MCPError(Exception):
    """Base class for all MCP errors"""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ToolNotFoundError(MCPError):
    """Error raised when a requested tool is not found"""
    def __init__(self, tool_id):
        super().__init__(f"Tool {tool_id} not found", 404)

class OpenAIError(MCPError):
    """Error raised when there's an issue with the OpenAI API"""
    def __init__(self, message, status_code=500):
        super().__init__(f"OpenAI API error: {message}", status_code)

class ConfigurationError(MCPError):
    """Error raised when there's an issue with configuration"""
    def __init__(self, message):
        super().__init__(f"Configuration error: {message}", 500)
```

## Advanced Usage

### Custom Tool Implementation

To implement a custom tool adapter:

```python
from ..models.mcp import MCPRequest, MCPResponse
from abc import ABC, abstractmethod

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

    @abstractmethod
    async def translate_request(self, request: MCPRequest) -> dict:
        """Translate MCP request to OpenAI parameters"""
        pass

    @abstractmethod
    async def translate_response(self, response: dict) -> MCPResponse:
        """Translate OpenAI response to MCP response"""
        pass

# Example implementation for web search
class WebSearchAdapter(ToolAdapter):
    @property
    def tool_id(self) -> str:
        return "web-search"

    @property
    def openai_tool_type(self) -> str:
        return "retrieval"

    async def translate_request(self, request: MCPRequest) -> dict:
        # Extract search query
        query = request.parameters.get("query", "")

        # Return OpenAI parameters
        return {"query": query}

    async def translate_response(self, response: dict) -> MCPResponse:
        # Extract search results
        results = response.get("results", [])

        # Format results as markdown
        content = "# Search Results\n\n"
        for i, result in enumerate(results):
            content += f"## {i+1}. {result.get('title', 'No title')}\n"
            content += f"**URL**: {result.get('url', 'No URL')}\n"
            content += f"{result.get('snippet', 'No snippet')}\n\n"

        # Return MCP response
        return MCPResponse(
            content=content,
            context={"search_query": query}
        )
```

### Middleware Support

Middleware can be used to add cross-cutting functionality:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Log request
        print(f"Request: {request.method} {request.url}")

        # Call next middleware
        response = await call_next(request)

        # Log response
        print(f"Response: {response.status_code}")

        return response

def add_middleware(app: FastAPI):
    """Add middleware to FastAPI app"""
    app.add_middleware(LoggingMiddleware)
```

This implementation guide provides a comprehensive blueprint for building the openai-tool2mcp bridge. By following this architecture and implementation details, you can create a fully functional MCP server that leverages OpenAI's powerful built-in tools.
