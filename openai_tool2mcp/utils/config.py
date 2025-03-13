import os

from dotenv import load_dotenv


class APIKeyMissingError(ValueError):
    """Exception raised when the API key is missing"""

    def __init__(self):
        super().__init__("No API key")


class ServerConfig:
    """Configuration class for the MCP server"""

    def __init__(
        self,
        openai_api_key: str | None = None,
        tools: list[str] | None = None,
        request_timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize server configuration.

        Args:
            openai_api_key: OpenAI API key (defaults to environment variable)
            tools: List of enabled tools (defaults to all)
            request_timeout: Timeout for API requests in seconds
            max_retries: Maximum number of retries for failed requests
        """
        # Load environment variables
        load_dotenv()

        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise APIKeyMissingError()

        self.tools = tools or []  # Will default to all tools in the ToolRegistry
        self.request_timeout = request_timeout
        self.max_retries = max_retries


def load_config(config_file=None) -> dict:
    """
    Load configuration from file.

    Args:
        config_file (str, optional): Path to configuration file

    Returns:
        dict: Configuration dictionary
    """
    # If a specific config file is provided, load it
    if config_file and os.path.exists(config_file):
        # For now, just return a simple config dictionary
        # In a real implementation, parse the file
        return {"openai_api_key": os.environ.get("OPENAI_API_KEY")}

    # Default configuration
    return {"openai_api_key": os.environ.get("OPENAI_API_KEY")}
