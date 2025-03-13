# openai-tool2mcp

[![Release](https://img.shields.io/github/v/release/alohays/openai-tool2mcp)](https://img.shields.io/github/v/release/alohays/openai-tool2mcp)
[![Build status](https://img.shields.io/github/actions/workflow/status/alohays/openai-tool2mcp/main.yml?branch=main)](https://github.com/alohays/openai-tool2mcp/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/alohays/openai-tool2mcp)](https://img.shields.io/github/commit-activity/m/alohays/openai-tool2mcp)
[![License](https://img.shields.io/github/license/alohays/openai-tool2mcp)](https://img.shields.io/github/license/alohays/openai-tool2mcp)

**openai-tool2mcp** is a lightweight, open-source bridge that wraps OpenAI's powerful built-in tools as Model Context Protocol (MCP) servers. It enables you to use high-quality OpenAI tools like web search and code interpreter with Claude and other MCP-compatible models.

## Why openai-tool2mcp?

AI developers today face a challenging choice:

1. **OpenAI's ecosystem**: Offers powerful built-in tools like web search and code interpreter, but ties you to a closed platform
2. **MCP ecosystem**: Provides an open standard for interoperability, but lacks the advanced tools available in OpenAI

**openai-tool2mcp** bridges this gap by letting you use OpenAI's mature, high-quality tools within the open MCP ecosystem, giving you the best of both worlds.

## Key Features

- 🔍 **Use OpenAI's robust web search in Claude App**
- 💻 **Access code interpreter functionality in any MCP-compatible LLM**
- 🔄 **Seamless protocol translation between OpenAI and MCP**
- 🛠️ **Simple API for easy integration**

## Supported Tools

| OpenAI Tool      | MCP Equivalent | Status         |
| ---------------- | -------------- | -------------- |
| Web Search       | Web Search     | ✅ Implemented |
| Code Interpreter | Code Execution | ✅ Implemented |
| Web Browser      | Browser        | ✅ Implemented |
| File Management  | File I/O       | ✅ Implemented |

## Technical Architecture

openai-tool2mcp works by:

1. Exposing an MCP-compatible server interface
2. Translating MCP requests to OpenAI Assistant API calls
3. Converting OpenAI tool responses back to MCP format
4. Delivering results to MCP clients like Claude App

For detailed technical information, see the [Architecture Overview](architecture.md) and [Implementation Guide](implementation.md).

## Quick Start

```bash
# Install from PyPI
pip install openai-tool2mcp

# Start the server with your OpenAI API key
OPENAI_API_KEY="your-api-key" openai-tool2mcp start

# Connect Claude App to http://localhost:8000
```

Ready to get started? Check out our [Getting Started Guide](getting-started.md) for detailed instructions.
