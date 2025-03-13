# Getting Started

This guide will help you quickly set up and start using openai-tool2mcp to bring OpenAI's powerful built-in tools to your MCP-compatible models.

## Prerequisites

Before you begin, make sure you have:

- Python 3.10 or higher
- An OpenAI API key with access to the Assistant API
- A MCP-compatible client (like Claude App)
- (Recommended) `uv` package manager for MCP compatibility

## Installation

### Using uv (Recommended for MCP compatibility)

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) recommends using `uv` for package management and execution:

```bash
# Install uv if you don't have it
pip install uv

# Install openai-tool2mcp using uv
uv pip install openai-tool2mcp
```

For more details on using `uv` with openai-tool2mcp, see our [dedicated guide](uv-integration.md).

### From PyPI

```bash
pip install openai-tool2mcp
```

### From Source

```bash
git clone https://github.com/alohays/openai-tool2mcp.git
cd openai-tool2mcp
pip install -e .
```

## Basic Setup

### 1. Set Your OpenAI API Key

You can set your API key in one of two ways:

**Option 1: Environment Variable**

```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
```

**Option 2: Configuration File**

Create a file named `.env` in your project directory:

```
OPENAI_API_KEY=your-api-key-here
```

### 2. Start the MCP Server

#### Using uv (Recommended for MCP compatibility)

```bash
# Start the server using the standalone entry script
uv run openai_tool2mcp/server_entry.py --transport stdio
```

#### Using the CLI

```bash
# Alternative: Using the CLI
openai-tool2mcp start --transport stdio
```

### 3. Connect Your MCP Client

Configure your MCP-compatible client to connect to your local server:

- **Server URL**: `http://localhost:8000`

## Using with Claude App

Claude App supports the Model Context Protocol, making it a perfect client for openai-tool2mcp.

### Setting Up Claude App

1. Open Claude App
2. Go to Settings > API & Integrations
3. Add a new MCP server with the URL `http://localhost:8000`
4. Save your settings

### Available Tools in Claude

Once configured, you'll see new tools available in Claude:

- **Web Search**: Access OpenAI's powerful web search capability
- **Code Execution**: Run code using OpenAI's code interpreter
- **Web Browser**: Browse the web using OpenAI's web browser
- **File Management**: Manage files using OpenAI's file tools

### Example Usage in Claude

Here's how to use the tools in Claude:

```
Claude, can you search the web for the latest news about AI regulations?
```

Claude will use the OpenAI web search tool through your local MCP server to fetch the latest news.

## Programmatic Usage

You can also use openai-tool2mcp programmatically in your Python applications:

```python
from openai_tool2mcp import MCPServer, ServerConfig
from openai_tool2mcp.tools import OpenAIBuiltInTools

# Configure the server
config = ServerConfig(
    openai_api_key="your-api-key-here",  # Optional if set in environment
    tools=[
        OpenAIBuiltInTools.WEB_SEARCH.value,
        OpenAIBuiltInTools.CODE_INTERPRETER.value
    ]
)

# Create and start the server
server = MCPServer(config)
server.start(host="127.0.0.1", port=8000)
```

## Advanced Configuration

### Server Configuration Options

You can customize your server with these options:

```python
config = ServerConfig(
    openai_api_key="your-api-key-here",
    tools=["retrieval", "code_interpreter"],  # Enable specific tools
    request_timeout=60,                       # Timeout in seconds
    max_retries=5                            # Max retries for failed requests
)
```

### Command-Line Options

The CLI provides several configuration options:

```bash
openai-tool2mcp start --help
```

**Available options**:

- `--host`: Host address to bind to (default: 127.0.0.1)
- `--port`: Port to listen on (default: 8000)
- `--api-key`: OpenAI API key (alternative to environment variable)
- `--tools`: Space-separated list of tools to enable
- `--timeout`: Request timeout in seconds
- `--retries`: Maximum number of retries for failed requests

### Docker Deployment

You can also run openai-tool2mcp in Docker:

```bash
# Build the Docker image
docker build -t openai-tool2mcp .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY="your-api-key-here" openai-tool2mcp
```

## Troubleshooting

### Common Issues

#### 1. Server Won't Start

Make sure:

- Your OpenAI API key is valid
- You have proper network permissions
- The port (default 8000) is not already in use

#### 2. Tool Calls Fail

Check:

- Your OpenAI account has access to the Assistant API
- Your API key has the necessary permissions
- You have sufficient API credits/quota

#### 3. Connection Issues

Verify:

- The server is running (you should see log messages)
- Your client is correctly configured with the server URL
- Your network allows the connection

### Logs

For more detailed troubleshooting, enable debug logs:

```bash
openai-tool2mcp start --log-level debug
```

## Next Steps

Now that you have openai-tool2mcp up and running, consider:

- Reading the [Architecture Overview](architecture.md) to understand how it works
- Exploring the [Implementation Guide](implementation.md) for technical details
- Checking the [API Reference](api-reference.md) for complete documentation

For any issues or contributions, visit our [GitHub repository](https://github.com/alohays/openai-tool2mcp).
