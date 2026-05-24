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
async def mcp_proxy(tool_name: str = "", call_tool: bool = False, args: dict = {}, query: str = "", max_results: int = 10) -> str:
    """
    MCP tools proxy. No parameters to list all tools. tool_name to get tool description. tool_name + args + call to call tool. Query to search for tools.
    :param tool_name: Tool name
    :param call_tool: True to call tool
    :param args: Arguments
    :param query: Query
    :param max_results: Max results. Only used to search
    """

    if tool_name:
        if query:
            return "Tool name and query can't be used at once"
        elif call_tool:
            return str(await proxy.call_tool(tool_name, args))
        elif args:
            return "Arguments provided, but call = false"
        else:
            return str(await proxy.describe_tool(tool_name))
    elif query:
        if args:
            return "Arguments and query can't be used at once"
        if call_tool:
            return "Call and query can't be used at once"
        return str(await proxy.search_tools(query, max_results))
    elif call_tool:
        return "No tool name to call provided"
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