import asyncio
import json
import time
from typing import Any

import openai

from ..models.openai import ToolOutput, ToolRequest, ToolResponse
from ..utils.logging import logger


class ThreadCreationError(RuntimeError):
    """Exception raised when thread creation fails"""

    def __init__(self):
        super().__init__("Thread creation failed")


class AssistantCreationError(RuntimeError):
    """Exception raised when assistant creation fails"""

    def __init__(self):
        super().__init__("Assistant creation failed")


class RunCreationError(RuntimeError):
    """Exception raised when run creation fails"""

    def __init__(self):
        super().__init__("Run creation failed")


class RunTimeoutError(TimeoutError):
    """Exception raised when run times out"""

    def __init__(self):
        super().__init__("Run timed out")


class NoChoicesError(ValueError):
    """Exception raised when no choices are found in response"""

    def __init__(self):
        super().__init__("No choices")


class OpenAIClient:
    """Client for interacting with the OpenAI API"""

    def __init__(self, api_key: str | None, request_timeout: int = 30, max_retries: int = 3):
        """
        Initialize the OpenAI client.

        Args:
            api_key (str): OpenAI API key
            request_timeout (int): Request timeout in seconds
            max_retries (int): Maximum number of retries
        """
        self.client = openai.Client(api_key=api_key, timeout=request_timeout)
        self.max_retries = max_retries
        self.retry_delay = 1  # Assuming a default retry_delay

    async def invoke_tool(self, request: ToolRequest) -> ToolResponse:
        """
        Invoke an OpenAI tool.

        Args:
            request (ToolRequest): Tool request

        Returns:
            ToolResponse: Tool response
        """
        # Special handling for web search
        if request.tool_type == "web_search":
            return await self._handle_web_search(request)

        # Create or get thread
        thread_id = request.thread_id
        if not thread_id:
            thread = await self._create_thread()
            if thread is None:
                raise ThreadCreationError()
            thread_id = thread.id

        # Create message with tool call
        await self._create_message(
            thread_id=thread_id,
            content=f"Please use the {request.tool_type} tool with these parameters: {request.parameters}",
        )

        # Create assistant with the appropriate tool
        assistant = await self._create_assistant(
            tools=[{"type": request.tool_type}],
            instructions=request.instructions or "Execute the requested tool function.",
        )
        if assistant is None:
            raise AssistantCreationError()

        # Run the assistant
        run = await self._create_run(thread_id=thread_id, assistant_id=assistant.id)
        if run is None:
            raise RunCreationError()

        # Wait for completion
        run = await self._wait_for_run(thread_id, run.id)

        # Get tool outputs
        tool_outputs = []
        if hasattr(run, "required_action") and hasattr(run.required_action, "submit_tool_outputs"):
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                # Process each tool call
                tool_outputs.append(ToolOutput(output=tool_call.function.arguments, error=None))

        # Create response
        response = ToolResponse(thread_id=thread_id, tool_outputs=tool_outputs)

        return response

    async def _create_thread(self) -> Any | None:
        """Create a new thread"""
        for attempt in range(self.max_retries):
            try:
                thread = await asyncio.to_thread(self.client.beta.threads.create)
            except Exception as e:
                logger.error(f"Error creating thread (attempt {attempt + 1}/{self.max_retries}): {e!s}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay)
            else:
                return thread
        return None

    async def _create_message(self, thread_id: str, content: str) -> Any | None:
        """Create a new message in a thread"""
        for attempt in range(self.max_retries):
            try:
                message = await asyncio.to_thread(
                    self.client.beta.threads.messages.create, thread_id=thread_id, role="user", content=content
                )
            except Exception as e:
                logger.error(f"Error creating message (attempt {attempt + 1}/{self.max_retries}): {e!s}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay)
            else:
                return message
        return None

    async def _create_assistant(
        self, tools: list[dict], instructions: str = "", model: str = "gpt-4o-mini"
    ) -> Any | None:
        """Create a new assistant with the specified tools"""
        for attempt in range(self.max_retries):
            try:
                # Prepare assistant parameters based on tool type
                assistant_params = self._prepare_assistant_params(tools, instructions, model)

                # Create the assistant with prepared parameters
                assistant = await asyncio.to_thread(self.client.beta.assistants.create, **assistant_params)

                logger.info(f"Assistant created: {assistant.id}")
            except Exception as e:
                logger.error(f"Error creating assistant (attempt {attempt + 1}/{self.max_retries}): {e!s}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay)
            else:
                return assistant
        return None

    def _prepare_assistant_params(self, tools: list[dict], instructions: str, model: str) -> dict:
        """Prepare parameters for assistant creation based on tool types"""
        # Check for web search tool
        if tools and tools[0].get("type") == "web_search":
            return self._prepare_web_search_assistant_params(instructions)
        else:
            return self._prepare_standard_assistant_params(tools, instructions, model)

    def _prepare_web_search_assistant_params(self, instructions: str) -> dict:
        """Prepare parameters specifically for web search assistant"""
        model = "gpt-4o-mini-search-preview"
        logger.info(f"Creating assistant with {model} for web search")

        return {"name": "Tool Assistant", "model": model, "instructions": instructions}

    def _prepare_standard_assistant_params(self, tools: list[dict], instructions: str, model: str) -> dict:
        """Prepare parameters for standard assistant with various tools"""
        # Convert tools to format expected by OpenAI
        formatted_tools = self._format_tools(tools)

        assistant_params = {"name": "Tool Assistant", "model": model, "instructions": instructions}

        # Add tools only if present
        if formatted_tools:
            assistant_params["tools"] = formatted_tools

        logger.info(f"Creating assistant with model {model} and tools: {formatted_tools}")
        return assistant_params

    def _format_tools(self, tools: list[dict]) -> list[dict]:
        """Format tools list for OpenAI API compatibility"""
        formatted_tools = []
        for tool in tools:
            tool_type = tool.get("type", "")
            if tool_type == "code_interpreter":
                formatted_tools.append({"type": "code_interpreter"})
            elif tool_type == "file_search":
                formatted_tools.append({"type": "retrieval"})
            elif tool_type == "web_browser":
                # This type is not directly supported, so we substitute with retrieval
                formatted_tools.append({"type": "retrieval"})

        return formatted_tools

    async def _create_run(self, thread_id: str, assistant_id: str) -> Any | None:
        """Create a new run"""
        for attempt in range(self.max_retries):
            try:
                run = await asyncio.to_thread(
                    self.client.beta.threads.runs.create, thread_id=thread_id, assistant_id=assistant_id
                )
            except Exception as e:
                logger.error(f"Error creating run (attempt {attempt + 1}/{self.max_retries}): {e!s}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay)
            else:
                return run
        return None

    async def _wait_for_run(self, thread_id: str, run_id: str) -> Any:
        """Wait for a run to complete"""
        max_wait_time = 60  # Maximum wait time in seconds
        start_time = time.time()

        while True:
            if time.time() - start_time > max_wait_time:
                raise RunTimeoutError()

            for attempt in range(self.max_retries):
                try:
                    run = await asyncio.to_thread(
                        self.client.beta.threads.runs.retrieve, thread_id=thread_id, run_id=run_id
                    )
                    break
                except Exception as e:
                    logger.error(f"Error retrieving run (attempt {attempt + 1}/{self.max_retries}): {e!s}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(self.retry_delay)

            if run.status in ["completed", "failed", "requires_action"]:
                return run

            await asyncio.sleep(1)

    async def _handle_web_search(self, request: ToolRequest) -> ToolResponse:
        """
        Handle web search request using the chat completions API.

        Args:
            request (ToolRequest): Tool request

        Returns:
            ToolResponse: Tool response
        """
        logger.info(f"[WEB SEARCH] Handling request: {request.parameters}")

        # Validate and extract query
        query = request.parameters.get("query", "")
        if not query:
            logger.warning("[WEB SEARCH] Empty query received")
            return self._create_error_response(request.thread_id, "No query provided")

        logger.info(f"[WEB SEARCH] Executing with query: '{query}'")

        # Try multiple attempts based on max_retries
        for attempt in range(self.max_retries):
            try:
                # Create and send request to OpenAI
                response = await self._execute_web_search_request(query, attempt)

                # Process the response
                output_json = await self._process_web_search_response(response)

                # Return successful response
                logger.info("[WEB SEARCH] Successfully completed request")
                return ToolResponse(
                    thread_id=request.thread_id or f"web_search_{int(time.time())}",
                    tool_outputs=[ToolOutput(output=output_json, error=None)],
                )

            except Exception as e:
                if not await self._handle_web_search_error(e, attempt):
                    # Return error response on final attempt
                    error_msg = str(e)
                    return self._create_error_response(request.thread_id, error_msg)

        # Unexpected situation - all attempts failed without exception
        logger.error("[WEB SEARCH] Unexpected end of method without result or error")
        return self._create_error_response(request.thread_id, "Unknown error in web search process")

    def _create_error_response(self, thread_id: str | None, error_msg: str) -> ToolResponse:
        """Create an error response for web search"""
        return ToolResponse(
            thread_id=thread_id or "error",
            tool_outputs=[ToolOutput(output=json.dumps({"error": error_msg}), error=error_msg)],
        )

    async def _execute_web_search_request(self, query: str, attempt: int) -> Any:
        """Execute the web search request to OpenAI API"""
        logger.debug(f"[WEB SEARCH] Request attempt {attempt + 1}/{self.max_retries}")
        logger.debug("[WEB SEARCH] Creating request with model: 'gpt-4o-mini-search-preview'")

        # Prepare request data
        request_data = {
            "model": "gpt-4o-mini-search-preview",
            "messages": [{"role": "user", "content": query}],
            "web_search_options": {},  # Empty object to enable web search
            "store": True,  # Store the response (optional)
        }

        logger.debug(f"[WEB SEARCH] Full request data: {json.dumps(request_data)}")

        # Execute API call
        return await asyncio.to_thread(self.client.chat.completions.create, **request_data)

    async def _handle_web_search_error(self, error: Exception, attempt: int) -> bool:
        """Handle errors in web search. Returns True if should retry, False if should stop."""
        logger.error(f"[WEB SEARCH] Error: {error!s}")

        if attempt == self.max_retries - 1:
            logger.error(f"[WEB SEARCH] All attempts failed. Last error: {error}")
            return False

        # Delay before retrying
        logger.info(f"[WEB SEARCH] Retrying in {self.retry_delay}s...")
        await asyncio.sleep(self.retry_delay)
        return True

    async def _process_web_search_response(self, response: Any) -> str:
        """Process the web search response and return the serialized JSON output"""
        # Log response information for debugging
        logger.debug(f"[WEB SEARCH] Response type: {type(response)}")
        logger.debug(f"[WEB SEARCH] Response attributes: {dir(response)}")

        # Check if response has choices
        if not response.choices:
            logger.warning("[WEB SEARCH] No choices found in response")
            raise NoChoicesError()

        # Extract message content
        message = response.choices[0].message
        logger.debug(f"[WEB SEARCH] Message role: {message.role}")
        logger.debug(f"[WEB SEARCH] Message attributes: {dir(message)}")

        # Get content
        content = message.content or ""
        logger.info(f"[WEB SEARCH] Response content length: {len(content)}")
        logger.debug(f"[WEB SEARCH] Content preview: {content[:100]}...")

        # Check for annotations
        annotations = self._extract_annotations(message)

        # Prepare response data
        response_data = {"content": content, "annotations": annotations}
        logger.debug(f"[WEB SEARCH] Constructed response data with keys: {list(response_data.keys())}")

        # Serialize to JSON
        return self._serialize_response_data(response_data, content)

    def _extract_annotations(self, message: Any) -> list:
        """Extract annotations from the message if available"""
        annotations = []
        has_annotations = hasattr(message, "annotations")
        logger.debug(f"[WEB SEARCH] Has annotations attribute: {has_annotations}")

        if has_annotations and message.annotations is not None:
            annotations = message.annotations
            logger.info(f"[WEB SEARCH] Found {len(annotations)} annotations")

            # Log annotation details
            for i, annotation in enumerate(annotations):
                logger.debug(f"[WEB SEARCH] Annotation {i + 1}: {type(annotation)}")
                if hasattr(annotation, "type"):
                    logger.debug(f"[WEB SEARCH] Annotation type: {annotation.type}")

        return annotations

    def _serialize_response_data(self, response_data: dict, content: str) -> str:
        """Serialize the response data to JSON"""
        try:
            # Helper function for serializing complex objects
            def serialize_openai_objects(obj):
                if hasattr(obj, "model_dump_json"):
                    # Use model_dump_json for Pydantic objects
                    return json.loads(obj.model_dump_json())
                elif hasattr(obj, "to_dict"):
                    # Use to_dict method if available
                    return obj.to_dict()
                elif hasattr(obj, "__dict__"):
                    # Use __dict__ attribute if available
                    return obj.__dict__
                else:
                    # Convert to string for other objects
                    return str(obj)

            # Convert complex OpenAI objects to standard Python objects
            output_json = json.dumps(response_data, default=serialize_openai_objects)
            logger.debug(f"[WEB SEARCH] Successfully serialized to JSON (length: {len(output_json)})")
        except (TypeError, Exception) as e:
            logger.error(f"[WEB SEARCH] JSON serialization error: {e}")

            # Fallback response
            fallback_data = {"content": content, "error": f"Failed to serialize annotations: {e!s}"}
            output_json = json.dumps(fallback_data)
            logger.debug(f"[WEB SEARCH] Using fallback JSON: {output_json[:100]}...")

        return output_json
