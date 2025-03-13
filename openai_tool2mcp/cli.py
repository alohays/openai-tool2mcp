import argparse
import os
import sys

from .server import MCPServer
from .tools import OpenAIBuiltInTools
from .utils.config import ServerConfig
from .utils.logging import setup_logging


def main():
    """Main function for CLI"""
    parser = argparse.ArgumentParser(description="Start an MCP server for OpenAI tools")

    # Command subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start the MCP server")
    start_parser.add_argument("--host", default="127.0.0.1", help="Host to listen on (for HTTP transport)")
    start_parser.add_argument("--port", type=int, default=8000, help="Port to listen on (for HTTP transport)")
    start_parser.add_argument("--api-key", help="OpenAI API key (defaults to OPENAI_API_KEY env var)")
    start_parser.add_argument(
        "--tools",
        nargs="+",
        choices=[t.value for t in OpenAIBuiltInTools],
        default=[t.value for t in OpenAIBuiltInTools],
        help="Enabled tools",
    )
    start_parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    start_parser.add_argument("--retries", type=int, default=3, help="Maximum number of retries")
    start_parser.add_argument(
        "--log-level", choices=["debug", "info", "warning", "error", "critical"], default="info", help="Logging level"
    )
    start_parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="http",
        help="Transport method (stdio, sse, or http). Use stdio for MCP compatibility.",
    )

    # List command
    subparsers.add_parser("list", help="List available tools")

    # Parse arguments
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.log_level if hasattr(args, "log_level") else "info")

    # Handle commands
    if args.command == "start":
        # Create server config
        config = ServerConfig(
            openai_api_key=args.api_key or os.environ.get("OPENAI_API_KEY"),
            tools=args.tools,
            request_timeout=args.timeout,
            max_retries=args.retries,
        )

        # Start server
        server = MCPServer(config)
        server.start(host=args.host, port=args.port, transport=args.transport)
    elif args.command == "list":
        # List available tools
        print("Available tools:")
        for tool in OpenAIBuiltInTools:
            print(f"  - {tool.value}: {tool.name.replace('_', ' ').title()}")
    else:
        # No command specified
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
