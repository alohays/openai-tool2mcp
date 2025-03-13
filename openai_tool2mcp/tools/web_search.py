import json
from typing import Any

from ..models.mcp import MCPRequest, MCPResponse
from ..utils.logging import logger
from .base import ToolAdapter


class WebSearchAdapter(ToolAdapter):
    """Adapter for OpenAI's web search tool"""

    @property
    def tool_id(self) -> str:
        """Get the MCP tool ID"""
        return "web-search"

    @property
    def openai_tool_type(self) -> str:
        """Get the OpenAI tool type"""
        return "web_search"

    @property
    def description(self) -> str:
        """Get the tool description"""
        return "Search the web for real-time information"

    async def translate_request(self, request: MCPRequest) -> dict:
        """
        Translate MCP request to OpenAI parameters.

        Args:
            request (MCPRequest): MCP request

        Returns:
            dict: Dictionary of OpenAI parameters
        """
        parameters = {}
        if "search_term" in request.parameters:
            parameters["query"] = request.parameters["search_term"]
        elif "parameters" in request.parameters:
            # 경우에 따라 parameters 필드 내에 직접 쿼리가 문자열로 전달될 수 있음
            parameters["query"] = request.parameters["parameters"]

        # 향상된 로깅 추가
        logger.info(f"[WEB SEARCH] Translated MCP request to tool parameters: {parameters}")

        return parameters

    async def translate_response(self, response: Any) -> MCPResponse:
        """
        Translate OpenAI tool response to MCP response.

        Args:
            response (Any): OpenAI tool response (JSON string or dictionary)

        Returns:
            MCPResponse: MCP response
        """
        # 향상된 디버그 로깅 추가
        logger.debug(f"[WEB SEARCH] Translating response of type: {type(response)}")

        # 응답이 이미 JSON 문자열인지 확인
        if isinstance(response, str):
            try:
                # 이미 JSON 문자열인 경우 파싱
                logger.debug("[WEB SEARCH] Response is a string, attempting to parse as JSON")
                parsed_response = json.loads(response)

                # 응답 내용 확인 및 추출
                logger.debug(
                    f"[WEB SEARCH] Parsed JSON with keys: {list(parsed_response.keys()) if isinstance(parsed_response, dict) else 'not a dict'}"
                )

                # 콘텐츠 추출 (문자열로 변환)
                if isinstance(parsed_response, dict) and "content" in parsed_response:
                    content = str(parsed_response["content"])
                    logger.info(f"[WEB SEARCH] Extracted content from JSON response, length: {len(content)}")
                    return MCPResponse(content=content, context={"raw_response": response})
                else:
                    # 콘텐츠 키가 없으면 전체 응답을 문자열로 변환
                    content_str = json.dumps(parsed_response)
                    logger.info(
                        f"[WEB SEARCH] No content key found, using full response as content, length: {len(content_str)}"
                    )
                    return MCPResponse(content=content_str, context={"raw_response": response})

            except json.JSONDecodeError:
                # JSON 파싱 실패 시 원본 문자열 사용
                logger.warning("[WEB SEARCH] Failed to parse response as JSON, using raw string")
                return MCPResponse(content=response, context={"raw_response": response})

        # 딕셔너리인 경우
        elif isinstance(response, dict):
            logger.debug(f"[WEB SEARCH] Response is a dict with keys: {list(response.keys())}")

            # 콘텐츠 키가 있으면 해당 값 사용
            if "content" in response:
                # 반드시 content를 문자열로 변환
                content = str(response["content"])
                logger.info(f"[WEB SEARCH] Extracted content from dict response, length: {len(content)}")
                return MCPResponse(content=content, context={"raw_response": json.dumps(response)})

            # 콘텐츠 키가 없으면 전체 딕셔너리를 JSON 문자열로 변환
            content_str = json.dumps(response)
            logger.info(
                f"[WEB SEARCH] No content key in dict, using full dict as JSON string, length: {len(content_str)}"
            )
            return MCPResponse(content=content_str, context={"raw_response": content_str})

        # 다른 모든 타입의 경우
        else:
            # 안전하게 문자열로 변환
            logger.warning(f"[WEB SEARCH] Unexpected response type: {type(response)}, converting to string")
            content_str = str(response)
            return MCPResponse(content=content_str, context={"raw_response": content_str})
