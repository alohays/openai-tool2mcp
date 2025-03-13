from ..models.mcp import MCPRequest
from ..models.openai import ToolRequest
from ..utils.logging import logger
from ..utils.security import sanitize_parameters


def translate_request(mcp_request: MCPRequest, tool_id: str) -> ToolRequest:
    """
    Translate an MCP request to an OpenAI request format.

    Args:
        mcp_request: The MCP request to translate
        tool_id: The ID of the tool to invoke

    Returns:
        An OpenAI tool request object
    """
    # Extract tool parameters and sanitize them
    parameters = sanitize_parameters(mcp_request.parameters)

    # Extract context information
    context = mcp_request.context or {}

    # Determine if this is a new or existing conversation
    thread_id = context.get("thread_id")

    # Log the translation
    logger.debug(f"Translating MCP request for tool {tool_id} to OpenAI format")

    # Create OpenAI request
    openai_request = ToolRequest(
        tool_type=map_tool_id_to_openai_type(tool_id),
        parameters=parameters,
        thread_id=thread_id,
        instructions=context.get("instructions", ""),
    )

    return openai_request


def map_tool_id_to_openai_type(tool_id: str) -> str:
    """
    Map MCP tool IDs to OpenAI tool types.

    Args:
        tool_id: MCP tool ID

    Returns:
        OpenAI tool type
    """
    mapping = {
        "web-search": "retrieval",
        "code-execution": "code_interpreter",
        "browser": "web_browser",
        "file-io": "file_search",
    }

    openai_type = mapping.get(tool_id, tool_id)
    logger.debug(f"Mapped MCP tool ID {tool_id} to OpenAI tool type {openai_type}")

    return openai_type
