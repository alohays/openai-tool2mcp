# OpenAI Tool2MCP Examples

This directory contains examples of how to use the `openai-tool2mcp` package to wrap OpenAI's built-in tools as MCP servers.

## Web Search Example

The `web_search_server.py` script demonstrates how to create an MCP server that provides web search functionality using OpenAI's built-in web search tool.

### Prerequisites

1. Make sure you have an OpenAI API key with access to the gpt-4o-mini-search-preview model
2. Set your OpenAI API key as an environment variable or in the `.env` file:

```bash
# In a .env file or export directly
OPENAI_API_KEY=your-api-key-here
```

### Running the Web Search Server

```bash
# Using uv (recommended)
uv run examples/web_search_server.py

# Or using python directly
python examples/web_search_server.py
```

### Configuring Claude for Desktop

To use this server with Claude for Desktop, update your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "openai-web-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/your/openai-tool2mcp",
        "run",
        "examples/web_search_server.py"
      ],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key"
      }
    }
  }
}
```

The configuration file is located at:

- MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%AppData%\Claude\claude_desktop_config.json`

### Using the Web Search Tool

Once configured, you can use the web search tool in Claude by asking questions that require current information:

1. "What were the latest developments in AI yesterday?"
2. "Can you summarize today's news about climate change?"
3. "What is the current price of Bitcoin?"

Claude will automatically use the web search tool when it determines the question requires up-to-date information.

## Troubleshooting

If you encounter any issues:

1. Check that your OpenAI API key is valid and has access to the `gpt-4o-mini-search-preview` model
2. Make sure the path in the Claude Desktop configuration is correct
3. Check the console output for error messages
4. Try running the server directly to see if there are any error messages

For more detailed information, see the main [README.md](../README.md) file.
