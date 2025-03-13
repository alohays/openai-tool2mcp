#!/usr/bin/env python
"""
Web Search MCP Server Example

This script sets up an MCP server with OpenAI's web search functionality.
It demonstrates how to configure the server to work with Claude or other MCP clients.

Usage:
    uv run examples/web_search_server.py
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from openai_tool2mcp import MCPServer, OpenAIBuiltInTools, ServerConfig
from openai_tool2mcp.utils.logging import logger, setup_logging

# Add the parent directory to sys.path to allow importing the package
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Load environment variables from .env file
load_dotenv()


def test_openai_connection(api_key):
    """API 키를 사용해 간단한 OpenAI API 호출을 테스트합니다."""
    import openai

    try:
        client = openai.Client(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": "Say hello"}], max_tokens=10
        )
        logger.info(f"OpenAI API test successful: {response.choices[0].message.content}")
    except Exception as e:
        logger.error(f"OpenAI API test failed: {e}")
        return False
    else:
        return True


def main():
    """Run the web search MCP server"""
    # Set up logging with high verbosity
    setup_logging("debug")
    logger.setLevel(logging.DEBUG)

    # 추가 로깅을 위한 스트림 핸들러 설정
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("=" * 50)
    logger.info("Starting OpenAI Web Search MCP Server")
    logger.info("=" * 50)

    # API 키 확인 및 로깅
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)
    else:
        # API 키를 마스킹하여 로깅
        masked_key = api_key[:8] + "..." + api_key[-4:]
        logger.info(f"Found OpenAI API key: {masked_key}")

    # OpenAI API 연결 테스트
    logger.info("Testing OpenAI API connection...")
    if not test_openai_connection(api_key):
        logger.warning("OpenAI API test failed. Server might not work correctly.")

    # API 요청 타임아웃 및 재시도 설정
    request_timeout = int(os.environ.get("REQUEST_TIMEOUT", "60"))
    max_retries = int(os.environ.get("MAX_RETRIES", "3"))

    logger.info(f"Request timeout: {request_timeout}s, Max retries: {max_retries}")

    # Create server configuration with web search tool enabled
    logger.info("Creating server configuration...")
    config = ServerConfig(
        openai_api_key=api_key,
        tools=[OpenAIBuiltInTools.WEB_SEARCH.value],
        request_timeout=request_timeout,
        max_retries=max_retries,
    )

    # OpenAI 모델 확인
    logger.info("Using model: gpt-4o-mini-search-preview for web search")

    # 디버깅을 위한 도구 정보 출력
    logger.info(f"Enabled tools: {config.tools}")

    # Create and start the server (using stdio for MCP compatibility)
    logger.info("Starting server with stdio transport...")
    server = MCPServer(config)

    try:
        # 서버 시작
        logger.info("Server starting...")
        server.start(transport="stdio")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise


if __name__ == "__main__":
    main()
