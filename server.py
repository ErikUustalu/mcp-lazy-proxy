import asyncio
import os
import logging

from proxy import Proxy
from fastmcp import FastMCP

CONFIG_PATH = os.environ.get("CONFIG_PATH", "config.json")

logging.basicConfig(level=logging.WARN, format="%(asctime)s - %(levelname)s - %(message)s")

mcp = FastMCP("lazy-proxy")

proxy = Proxy(CONFIG_PATH)

@mcp.tool()
async def list_tools() -> str:
    """List all available tools seperated by commas"""
    response = ""
    for tool in await proxy.list_tools():
        response += tool + ","
    return response

@mcp.tool()
async def describe_tool(tool_name: str) -> str:
    """Describe a tool in detail"""
    return str(await proxy.describe_tool(tool_name))

@mcp.tool()
async def call_tool(tool_name: str, args: dict) -> str:
    """Call a tool with provided arguments"""
    return str(await proxy.call_tool(tool_name, args))

async def main():
    await proxy.connect()
    try:
        await mcp.run_async(transport="streamable-http", host="0.0.0.0", port=8080)
    finally:
        await proxy.disconnect()

if __name__ == "__main__":
    asyncio.run(main())