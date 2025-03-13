# API Reference

This page provides comprehensive documentation for the openai-tool2mcp API, including classes, methods, and configuration options.

## Core Classes

### MCPServer

The main server class that implements the MCP protocol and manages tool execution.

```python
class MCPServer:
    def __init__(self, config=None):
        """
        Initialize the MCP server.

        Args:
            config (ServerConfig, optional): Server configuration
        """
        pass

    def register_routes(self):
        """Register FastAPI routes for the MCP protocol"""
        pass

    def start(self, host="127.0.0.1", port=8000):
        """
        Start the MCP server.

        Args:
            host (str): Host address to bind to
            port (int): Port to listen on
        """
        pass
```

### ServerConfig

Configuration class for the MCP server.

```python
class ServerConfig:
    def __init__(
        self,
        openai_api_key=None,
        tools=None,
        request_timeout=30,
        max_retries=3
    ):
        """
        Initialize server configuration.

        Args:
            openai_api_key (str, optional): OpenAI API key
            tools (List[str], optional): List of enabled tools
            request_timeout (int): Request timeout in seconds
            max_retries (int): Maximum number of retries
        """
        pass
```

### OpenAIClient

Client for interacting with the OpenAI API.

```python
class OpenAIClient:
    def __init__(self, api_key):
        """
        Initialize the OpenAI client.

        Args:
            api_key (str): OpenAI API key
        """
        pass

    async def invoke_tool(self, request):
        """
        Invoke an OpenAI tool.

        Args:
            request (OpenAIToolRequest): Tool request

        Returns:
            OpenAIToolResponse: Tool response
        """
        pass
```

### ToolRegistry

Registry of available tools and their configurations.

```python
class ToolRegistry:
    def __init__(self, enabled_tools=None):
        """
        Initialize the tool registry.

        Args:
            enabled_tools (List[str], optional): List of enabled tools
        """
        pass

    def has_tool(self, tool_id):
        """
        Check if a tool is registered and enabled.

        Args:
            tool_id (str): Tool ID

        Returns:
            bool: True if the tool is available
        """
        pass

    def get_openai_tool_type(self, tool_id):
        """
        Get the OpenAI tool type for a given MCP tool ID.

        Args:
            tool_id (str): MCP tool ID

        Returns:
            str: OpenAI tool type
        """
        pass
```

## MCP Protocol Models

### MCPRequest

Model for MCP tool requests.

```python
class MCPRequest(BaseModel):
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = Field(default=None)
```

**Fields**:

- `parameters`: Dictionary of tool parameters
- `context`: Dictionary of context information

### MCPResponse

Model for MCP tool responses.

```python
class MCPResponse(BaseModel):
    content: str
    error: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
```

**Fields**:

- `content`: Response content
- `error`: Optional error message
- `context`: Dictionary of context information

## OpenAI API Models

### OpenAIToolRequest

Model for OpenAI tool requests.

```python
class OpenAIToolRequest(BaseModel):
    tool_type: str
    parameters: Dict[str, Any]
    thread_id: Optional[str] = None
    instructions: Optional[str] = None
```

**Fields**:

- `tool_type`: OpenAI tool type
- `parameters`: Dictionary of tool parameters
- `thread_id`: Optional thread ID for continued conversations
- `instructions`: Optional instructions for the assistant

### OpenAIToolResponse

Model for OpenAI tool responses.

```python
class OpenAIToolResponse(BaseModel):
    thread_id: str
    tool_outputs: List[Any]
```

**Fields**:

- `thread_id`: Thread ID for the conversation
- `tool_outputs`: List of tool outputs

## Built-in Tools

### OpenAIBuiltInTools

Enum of built-in OpenAI tools.

```python
class OpenAIBuiltInTools(Enum):
    WEB_SEARCH = "retrieval"
    CODE_INTERPRETER = "code_interpreter"
    WEB_BROWSER = "web_browser"
    FILE_SEARCH = "file_search"
```

## Tool Adapters

### ToolAdapter

Abstract base class for tool adapters.

```python
class ToolAdapter(ABC):
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
```

## HTTP API Endpoints

The MCP server exposes the following HTTP endpoints:

### Tool Invocation

**Endpoint**: `POST /v1/tools/{tool_id}/invoke`

Invokes a tool with the specified ID.

**Path Parameters**:

- `tool_id` (string): ID of the tool to invoke

**Request Body**:

```json
{
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "context": {
    "thread_id": "optional-thread-id",
    "instructions": "optional-instructions"
  }
}
```

**Response**:

```json
{
  "content": "Tool response content",
  "error": null,
  "context": {
    "thread_id": "thread-id"
  }
}
```

**Status Codes**:

- `200 OK`: Tool executed successfully
- `404 Not Found`: Tool not found
- `400 Bad Request`: Invalid request
- `500 Internal Server Error`: Server error

## Translation Functions

### MCP to OpenAI Translation

```python
def translate_request(mcp_request: MCPRequest, tool_id: str) -> OpenAIToolRequest:
    """
    Translate an MCP request to an OpenAI request format.

    Args:
        mcp_request: The MCP request to translate
        tool_id: The ID of the tool to invoke

    Returns:
        An OpenAI tool request object
    """
    pass

def map_tool_id_to_openai_type(tool_id: str) -> str:
    """
    Map MCP tool IDs to OpenAI tool types.

    Args:
        tool_id: MCP tool ID

    Returns:
        OpenAI tool type
    """
    pass
```

### OpenAI to MCP Translation

```python
def translate_response(openai_response: OpenAIToolResponse) -> MCPResponse:
    """
    Translate an OpenAI response to an MCP response format.

    Args:
        openai_response: The OpenAI response to translate

    Returns:
        An MCP response object
    """
    pass
```

## Error Handling

### MCPError

Base class for all MCP errors.

```python
class MCPError(Exception):
    def __init__(self, message, status_code=500):
        """
        Initialize MCP error.

        Args:
            message (str): Error message
            status_code (int): HTTP status code
        """
        pass
```

### ToolNotFoundError

Error raised when a requested tool is not found.

```python
class ToolNotFoundError(MCPError):
    def __init__(self, tool_id):
        """
        Initialize tool not found error.

        Args:
            tool_id (str): Tool ID
        """
        pass
```

### OpenAIError

Error raised when there's an issue with the OpenAI API.

```python
class OpenAIError(MCPError):
    def __init__(self, message, status_code=500):
        """
        Initialize OpenAI error.

        Args:
            message (str): Error message
            status_code (int): HTTP status code
        """
        pass
```

### ConfigurationError

Error raised when there's an issue with configuration.

```python
class ConfigurationError(MCPError):
    def __init__(self, message):
        """
        Initialize configuration error.

        Args:
            message (str): Error message
        """
        pass
```

## Command-Line Interface

### Main Function

```python
def main():
    """Main function for CLI"""
    pass
```

**Command-Line Arguments**:

- `--host`: Host address to bind to (default: 127.0.0.1)
- `--port`: Port to listen on (default: 8000)
- `--api-key`: OpenAI API key (defaults to OPENAI_API_KEY env var)
- `--tools`: List of enabled tools (defaults to all)
- `--timeout`: Request timeout in seconds (default: 30)
- `--retries`: Maximum number of retries for failed requests (default: 3)
- `--log-level`: Logging level (default: info)

## Utility Functions

### Configuration Management

```python
def load_config(config_file=None):
    """
    Load configuration from file.

    Args:
        config_file (str, optional): Path to configuration file

    Returns:
        dict: Configuration dictionary
    """
    pass
```

### Logging Utilities

```python
def setup_logging(level="info"):
    """
    Set up logging.

    Args:
        level (str): Logging level
    """
    pass
```

### Security Utilities

```python
def validate_api_key(api_key):
    """
    Validate OpenAI API key.

    Args:
        api_key (str): API key to validate

    Returns:
        bool: True if valid
    """
    pass
```

## Examples

### Basic Server Example

```python
from openai_tool2mcp import MCPServer, ServerConfig

# Create server with default configuration
server = MCPServer()
server.start()
```

### Custom Configuration Example

```python
from openai_tool2mcp import MCPServer, ServerConfig
from openai_tool2mcp.tools import OpenAIBuiltInTools

# Create server with custom configuration
config = ServerConfig(
    openai_api_key="your-api-key",
    tools=[
        OpenAIBuiltInTools.WEB_SEARCH.value,
        OpenAIBuiltInTools.CODE_INTERPRETER.value
    ],
    request_timeout=60,
    max_retries=5
)

server = MCPServer(config)
server.start(host="127.0.0.1", port=8888)
```

### Custom Tool Adapter Example

```python
from openai_tool2mcp.models.mcp import MCPRequest, MCPResponse
from openai_tool2mcp.tools import ToolAdapter

class CustomToolAdapter(ToolAdapter):
    @property
    def tool_id(self) -> str:
        return "custom-tool"

    @property
    def openai_tool_type(self) -> str:
        return "retrieval"

    async def translate_request(self, request: MCPRequest) -> dict:
        # Custom request translation logic
        return {"query": request.parameters.get("query", "")}

    async def translate_response(self, response: dict) -> MCPResponse:
        # Custom response translation logic
        return MCPResponse(
            content="Custom response",
            context={"custom_context": "value"}
        )
```

This API reference provides a comprehensive overview of the openai-tool2mcp library's classes, methods, and functionalities. For more detailed examples and guides, refer to the [Implementation Guide](implementation.md) and [Getting Started](getting-started.md) documentation.
