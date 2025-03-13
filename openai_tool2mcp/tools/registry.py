from enum import Enum


class OpenAIBuiltInTools(Enum):
    """Enum for built-in OpenAI tools"""

    WEB_SEARCH = "web_search"
    CODE_INTERPRETER = "code_interpreter"
    WEB_BROWSER = "web_browser"
    FILE_SEARCH = "file_search"


class ToolType(Enum):
    """Enum for tool types"""

    BROWSER = "browser"
    CODE = "code"
    SEARCH = "search"


class ToolRegistry:
    """Registry for MCP tools mapped to OpenAI tools"""

    def __init__(self, enabled_tools=None):
        """
        Initialize the tool registry.

        Args:
            enabled_tools (List[str], optional): List of enabled tools
        """
        self.tools = {}
        self.enabled_tools = enabled_tools or [t.value for t in OpenAIBuiltInTools]
        self._register_default_tools()

    def _register_default_tools(self):
        """Register the default tool mappings"""
        self.tools = {
            "web-search": {
                "openai_tool": OpenAIBuiltInTools.WEB_SEARCH.value,
                "enabled": OpenAIBuiltInTools.WEB_SEARCH.value in self.enabled_tools,
                "description": "Search the web for information",
            },
            "code-execution": {
                "openai_tool": OpenAIBuiltInTools.CODE_INTERPRETER.value,
                "enabled": OpenAIBuiltInTools.CODE_INTERPRETER.value in self.enabled_tools,
                "description": "Execute code in a sandbox environment",
            },
            "browser": {
                "openai_tool": OpenAIBuiltInTools.WEB_BROWSER.value,
                "enabled": OpenAIBuiltInTools.WEB_BROWSER.value in self.enabled_tools,
                "description": "Browse websites and access web content",
            },
            "file-io": {
                "openai_tool": OpenAIBuiltInTools.FILE_SEARCH.value,
                "enabled": OpenAIBuiltInTools.FILE_SEARCH.value in self.enabled_tools,
                "description": "Search and access file content",
            },
        }

    def register_tool(self, tool_id: str, openai_tool: str, enabled: bool = True, description: str = ""):
        """
        Register a new tool.

        Args:
            tool_id (str): MCP tool ID
            openai_tool (str): OpenAI tool type
            enabled (bool): Whether the tool is enabled
            description (str): Tool description
        """
        self.tools[tool_id] = {"openai_tool": openai_tool, "enabled": enabled, "description": description}

    def has_tool(self, tool_id: str) -> bool:
        """
        Check if a tool is registered and enabled.

        Args:
            tool_id (str): Tool ID

        Returns:
            bool: True if the tool is available
        """
        return tool_id in self.tools and self.tools[tool_id]["enabled"]

    def get_openai_tool_type(self, tool_id: str) -> str | None:
        """
        Get the OpenAI tool type for a given MCP tool ID.

        Args:
            tool_id (str): MCP tool ID

        Returns:
            str: OpenAI tool type
        """
        if self.has_tool(tool_id):
            return self.tools[tool_id]["openai_tool"]
        return None

    def get_enabled_tools(self) -> dict[str, dict]:
        """
        Get all enabled tools.

        Returns:
            dict[str, dict]: Dictionary of enabled tools
        """
        return {tool_id: tool_info for tool_id, tool_info in self.tools.items() if tool_info["enabled"]}

    def enable_tool(self, tool_id: str) -> bool:
        """
        Enable a tool.

        Args:
            tool_id (str): Tool ID

        Returns:
            bool: True if the tool was enabled
        """
        if tool_id in self.tools:
            self.tools[tool_id]["enabled"] = True
            return True
        return False

    def disable_tool(self, tool_id: str) -> bool:
        """
        Disable a tool.

        Args:
            tool_id (str): Tool ID

        Returns:
            bool: True if the tool was disabled
        """
        if tool_id in self.tools:
            self.tools[tool_id]["enabled"] = False
            return True
        return False

    def register(self, tool_type: ToolType, tool):
        """Register a tool"""
        self.tools[tool_type.value] = tool

    def get_tool(self, tool_type: ToolType) -> object | None:
        """Get a tool by type"""
        return self.tools.get(tool_type.value)
