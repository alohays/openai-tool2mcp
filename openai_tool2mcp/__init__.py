"""
openai-tool2mcp: MCP wrapper for OpenAI built-in tools.

This package provides an MCP-compatible server that wraps
OpenAI's built-in tools, allowing them to be used with
MCP-compatible clients like Claude App.
"""

__version__ = "0.1.0"

from .server import MCPServer
from .tools import OpenAIBuiltInTools, ToolRegistry
from .utils.config import ServerConfig

__all__ = ["MCPServer", "ServerConfig", "OpenAIBuiltInTools", "ToolRegistry"]
