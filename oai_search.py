import json
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("openai-search")

# Constants
OPENAI_API_BASE = "https://api.openai.com/v1"
USER_AGENT = "openai-search-app/1.0"

# Get API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY environment variable not set")


async def make_openai_request(endpoint: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Make a request to the OpenAI API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json; charset=utf-8",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    url = f"{OPENAI_API_BASE}/{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=90.0)
            response.raise_for_status()
            # Ensure proper UTF-8 decoding
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Request error: {e!s}")
            return None
        except Exception as e:
            print(f"Error making OpenAI request: {e!s}")
            return None


def ensure_unicode(text: str) -> str:
    """Ensure text is properly decoded as unicode."""
    if not isinstance(text, str):
        return str(text)

    # Convert any potential escaped unicode to proper unicode characters
    try:
        # This handles cases where text might contain \uXXXX escape sequences
        return json.loads(f'"{text}"') if "\\u" in text else text
    except Exception:
        return text


@mcp.tool()
async def web_search(query: str) -> str:
    """Search the web for information on a topic.

    Args:
        query: The search query
    """
    data = {
        "model": "gpt-4o-mini-search-preview",
        "web_search_options": {},
        "messages": [{"role": "user", "content": query}],
    }

    response = await make_openai_request("chat/completions", data)

    if not response or "choices" not in response:
        return "Unable to perform web search or no results found."

    try:
        assistant_message = response["choices"][0]["message"]["content"]
        # Ensure proper unicode handling
        return ensure_unicode(assistant_message)
    except (KeyError, IndexError) as e:
        return f"Error processing search results: {e!s}"


@mcp.tool()
async def web_search_detailed(query: str, include_references: bool = True) -> str:
    """Search the web for information with optional source citations.

    Args:
        query: The search query
        include_references: Whether to include source citations (default: True)
    """
    # Modify the query to request citations if needed
    enhanced_query = query
    if include_references:
        enhanced_query = f"{query} Please include sources/citations for your information."

    data = {
        "model": "gpt-4o-mini-search-preview",
        "web_search_options": {},
        "messages": [{"role": "user", "content": enhanced_query}],
    }

    response = await make_openai_request("chat/completions", data)

    if not response or "choices" not in response:
        return "Unable to perform web search or no results found."

    try:
        assistant_message = response["choices"][0]["message"]["content"]
        # Ensure proper unicode handling
        return ensure_unicode(assistant_message)
    except (KeyError, IndexError) as e:
        return f"Error processing search results: {e!s}"


if __name__ == "__main__":
    # Set proper encoding for stdout/stderr
    import io
    import sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    # Initialize and run the server
    mcp.run(transport="stdio")
