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
