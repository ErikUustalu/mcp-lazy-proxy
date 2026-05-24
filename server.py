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
async def mcp_proxy(tool_name: str = "", args: dict = {}, query: str = "", max_results: int = 10) -> str:
    """
    MCP tools proxy. No parameters to list all tools. tool_name to get tool description. tool_name + args to call tool. Query to search for tools.
    :param tool_name: Tool name
    :param args: Arguments
    :param query: Query
    :param max_results: Max results. Only used to search
    """

    if tool_name:
        if query:
            return "Tool name and query can't be used at once"
        if args:
            return str(await proxy.call_tool(tool_name, args))
        else:
            return str(await proxy.describe_tool(tool_name))
    elif query:
        if args:
            return "Arguments and query can't be used at once"
        return str(await proxy.search_tools(query, max_results))
    else:
        response = ""
        tools = await proxy.list_tools()
        for tool in tools:
            response += tool + ";"
        return response

async def main():
    await proxy.start()
    try:
        await mcp.run_async(transport="streamable-http", host="0.0.0.0", port=8080)
    finally:
        await proxy.disconnect()

if __name__ == "__main__":
    asyncio.run(main())