#!/usr/bin/env python
"""
Standalone entry script for openai-tool2mcp server.

This script is designed to be used with `uv run` as recommended by the MCP documentation.
It provides a simple way to start the MCP server with OpenAI tools.

Usage:
    uv run openai_tool2mcp/server_entry.py
"""

import argparse
import os

from dotenv import load_dotenv

from openai_tool2mcp import MCPServer, OpenAIBuiltInTools, ServerConfig
from openai_tool2mcp.utils.logging import logger, setup_logging

# Load environment variables from .env file if present
load_dotenv()


def main():
    """Start the MCP server for OpenAI tools."""
    parser = argparse.ArgumentParser(description="Start an MCP server for OpenAI tools")

    parser.add_argument("--host", default="127.0.0.1", help="Host to listen on (for HTTP transport)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (for HTTP transport)")
    parser.add_argument("--api-key", help="OpenAI API key (defaults to OPENAI_API_KEY env var)")
    parser.add_argument(
        "--tools",
        nargs="+",
        choices=[t.value for t in OpenAIBuiltInTools],
        default=[t.value for t in OpenAIBuiltInTools],
        help="Enabled tools",
    )
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="Maximum number of retries")
    parser.add_argument(
        "--log-level", choices=["debug", "info", "warning", "error", "critical"], default="info", help="Logging level"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport method (stdio, sse, or http). Use stdio for MCP compatibility.",
    )

    # Parse arguments
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level)

    # Create server config
    config = ServerConfig(
        openai_api_key=args.api_key or os.environ.get("OPENAI_API_KEY"),
        tools=args.tools,
        request_timeout=args.timeout,
        max_retries=args.retries,
    )

    # Create and start the server
    logger.info("Starting MCP server with OpenAI tools")
    logger.info(f"Transport: {args.transport}")

    server = MCPServer(config)
    server.start(host=args.host, port=args.port, transport=args.transport)


if __name__ == "__main__":
    main()
