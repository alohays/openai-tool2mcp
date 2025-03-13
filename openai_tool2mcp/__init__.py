"""
openai-tool2mcp: Use OpenAI's powerful built-in tools with Claude via MCP
"""

__version__ = "0.1.0"

from .server import MCPServer
from .tools import OpenAIBuiltInTools
from .utils.config import ServerConfig

__all__ = ["MCPServer", "OpenAIBuiltInTools", "ServerConfig"]
