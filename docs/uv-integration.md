# Using uv with openai-tool2mcp

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) recommends using `uv` as the package manager and execution environment for MCP servers. This guide explains how to integrate `openai-tool2mcp` with `uv` for optimal MCP compatibility.

## Why use uv?

`uv` is a fast, reliable Python package manager and execution environment that provides:

- Reproducible installations with exact dependency resolution
- Isolated execution environments for each project
- Improved compatibility with the Claude Desktop app and other MCP-compatible clients
- Simplified configuration for MCP servers

## Installation

First, install `uv` if you haven't already:

```bash
pip install uv
```

Then, install `openai-tool2mcp` using `uv`:

```bash
uv pip install openai-tool2mcp
```

## Running the Server with uv

There are two main ways to run `openai-tool2mcp` with `uv`:

### 1. Using the Standalone Entry Script

The package provides a standalone entry script that can be run directly with `uv`:

```bash
uv run openai_tool2mcp/server_entry.py --transport stdio
```

This approach is recommended for MCP compatibility as it matches the execution model expected by the MCP protocol.

### 2. Creating Your Own Script

You can also create your own script and run it with `uv`:

```python
# my_openai_tools_server.py
import os
from dotenv import load_dotenv
from openai_tool2mcp import MCPServer, ServerConfig, OpenAIBuiltInTools

# Load environment variables
load_dotenv()

# Create a server config with desired tools
config = ServerConfig(
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    tools=[
        OpenAIBuiltInTools.WEB_SEARCH.value,
        OpenAIBuiltInTools.CODE_INTERPRETER.value,
    ]
)

# Create and start the server
server = MCPServer(config)
server.start(transport="stdio")
```

Run this script with:

```bash
uv run my_openai_tools_server.py
```

## Configuring Claude for Desktop

To configure Claude for Desktop to use `openai-tool2mcp` with `uv`, edit your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "openai-tools": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/your/openai-tool2mcp",
        "run",
        "openai_tool2mcp/server_entry.py"
      ]
    }
  }
}
```

The config file is located at:

- MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%AppData%\Claude\claude_desktop_config.json`

## Advanced Configuration

You can pass additional arguments to the server by adding them to the `args` array:

```json
{
  "mcpServers": {
    "openai-tools": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/your/openai-tool2mcp",
        "run",
        "openai_tool2mcp/server_entry.py",
        "--tools",
        "web_search",
        "code_interpreter"
      ]
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Path Not Found**: Ensure you're using the absolute path to your openai-tool2mcp installation
2. **Missing Dependencies**: Make sure all dependencies are installed with `uv pip install -e .`
3. **API Key Issues**: Verify that your OpenAI API key is properly set in the environment

### Debugging

To enable debugging output, add the `--log-level debug` argument:

```json
{
  "mcpServers": {
    "openai-tools": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/your/openai-tool2mcp",
        "run",
        "openai_tool2mcp/server_entry.py",
        "--log-level",
        "debug"
      ]
    }
  }
}
```
