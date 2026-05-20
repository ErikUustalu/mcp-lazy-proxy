import asyncio
import os
import logging

from proxy import Proxy
from fastmcp import FastMCP

CONFIG_PATH = os.environ.get("CONFIG_PATH", "config/config.json")

logging.basicConfig(level=logging.WARN, format="%(asctime)s - %(levelname)s - %(message)s")

mcp = FastMCP("lazy-proxy")

proxy = Proxy(CONFIG_PATH)

@mcp.tool()
async def list_tools() -> str:
    """List all available tools categorized by server and seperated by ;"""
    response = ""
    tools = await proxy.list_tools()
    keys = tools.keys()
    for key in keys:
        response += f"\n{key}: "
        for tool in tools[key]:
            response += f"{tool};"
    return response

@mcp.tool()
async def describe_tool(tool_name: str) -> str:
    """Describe a tool in detail"""
    return str(await proxy.describe_tool(tool_name))

@mcp.tool()
async def call_tool(tool_name: str, args: dict) -> str:
    """Call a tool with provided arguments"""
    return str(await proxy.call_tool(tool_name, args))

@mcp.tool()
async def search_tools(query: str) -> str:
    """Search for tools by name or description"""
    return str(await proxy.search_tools(query))

async def main():
    await proxy.connect()
    try:
        await mcp.run_async(transport="streamable-http", host="0.0.0.0", port=8080)
    finally:
        await proxy.disconnect()

if __name__ == "__main__":
    asyncio.run(main())