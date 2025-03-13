import json
from typing import Any

from ..models.mcp import MCPResponse
from ..models.openai import ToolResponse
from ..utils.logging import logger


def translate_response(openai_response: ToolResponse) -> MCPResponse:
    """
    Translate an OpenAI response to an MCP response format.

    Args:
        openai_response: The OpenAI response to translate

    Returns:
        An MCP response object
    """
    # Extract tool output
    tool_output = openai_response.tool_outputs[0] if openai_response.tool_outputs else None

    # Log the translation
    logger.debug("Translating OpenAI response to MCP format")

    if not tool_output:
        # Handle case where there's no tool output
        logger.warning("No tool output found in OpenAI response")
        return MCPResponse(
            content="No result", error="Tool returned no output", context={"thread_id": openai_response.thread_id}
        )

    # Format the output content
    try:
        # Try to parse as JSON for structured output
        output_content = tool_output.output
        if isinstance(output_content, str):
            try:
                # If it's a JSON string, parse it
                parsed_content = json.loads(output_content)
                # Format it nicely if possible
                if isinstance(parsed_content, dict) and "result" in parsed_content:
                    content = str(parsed_content["result"])
                else:
                    content = json.dumps(parsed_content, indent=2)
            except json.JSONDecodeError:
                # Not JSON, use as is
                content = output_content
        else:
            # Not a string, convert to string
            content = str(output_content)
    except Exception as e:
        # Fallback for any errors
        logger.error(f"Error formatting tool output: {e!s}")
        content = str(tool_output.output)

    # Create MCP response
    error = tool_output.error if hasattr(tool_output, "error") and tool_output.error else None

    mcp_response = MCPResponse(content=content, error=error, context={"thread_id": openai_response.thread_id})

    return mcp_response


def format_search_results(results: list[dict[str, Any]]) -> str:
    """
    Format search results in a human-readable format
    """
    if not results:
        return "No results found."

    formatted_results = []
    for result in results:
        title = result.get("title", "Untitled")
        content = result.get("content", "")
        formatted_results.append(f"# {title}\n\n{content}")

    return "\n\n".join(formatted_results)


def format_code_result(result: dict[str, Any] | str) -> str:
    """
    Format code execution result in a human-readable format
    """
    if isinstance(result, str):
        return result

    output = result.get("output", "")
    error = result.get("error")
    if error:
        return f"Error: {error}\n\nOutput:\n{output}"
    return output
