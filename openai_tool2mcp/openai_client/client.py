import asyncio
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
                assistant = await asyncio.to_thread(
                    self.client.beta.assistants.create,
                    name="Tool Assistant",
                    model=model,
                )
            except Exception as e:
                logger.error(f"Error creating assistant (attempt {attempt + 1}/{self.max_retries}): {e!s}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay)
            else:
                return assistant
        return None

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
