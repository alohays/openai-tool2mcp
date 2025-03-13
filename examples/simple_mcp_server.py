#!/usr/bin/env python
r"""
Simple example of using openai-tool2mcp with the MCP SDK.

This script demonstrates how to set up a simple MCP server that uses OpenAI's
web search and code interpreter tools.

Usage:
    # Recommended approach for MCP compatibility
    uv run examples/simple_mcp_server.py

    # To configure Claude for Desktop to use this script directly:
    # Edit ~/Library/Application Support/Claude/claude_desktop_config.json (MacOS)
    # or %AppData%\Claude\claude_desktop_config.json (Windows):

    {
      "mcpServers": {
        "openai-tools-example": {
          "command": "uv",
          "args": [
            "--directory",
            "/absolute/path/to/openai-tool2mcp",
            "run",
            "examples/simple_mcp_server.py"
          ]
        }
      }
    }
"""

import os

from dotenv import load_dotenv

from openai_tool2mcp import MCPServer, OpenAIBuiltInTools, ServerConfig

# Load environment variables from .env file
load_dotenv()


def main():
    """Start a simple MCP server with OpenAI's web search tool."""
    # Ensure we have an API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        return

    # Create a server config with web search and code interpreter tools
    config = ServerConfig(
        openai_api_key=api_key,
        tools=[
            OpenAIBuiltInTools.WEB_SEARCH.value,
            OpenAIBuiltInTools.CODE_INTERPRETER.value,
        ],
        request_timeout=30,
        max_retries=3,
    )

    # Create and start the server
    server = MCPServer(config)

    print("Starting MCP server with OpenAI web search and code interpreter tools")
    print("Press Ctrl+C to stop the server")

    # Start the server using stdio transport (for MCP compatibility)
    server.start(transport="stdio")


if __name__ == "__main__":
    main()
