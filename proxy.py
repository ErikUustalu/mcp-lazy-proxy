import json
import asyncio

from fastmcp import Client

class Proxy:
    def __init__(self, config_path="config.json"):
        with open("config.json", "r") as f:
            self.config = json.load(f)
        self.tools = {}

    async def connect(self):
        for server in self.config["mcp_servers"]:
            client = Client(server["url"])
            await client.__aenter__()
            for tool in await client.list_tools():
                self.tools[tool.name] = {
                    "tool": tool,
                    "client": client
                }

    async def list_tools(self):
        return list(self.tools.keys())
    
    async def describe_tool(self, tool_name):
        if tool_name not in self.tools:
            return f"Tool '{tool_name}' not found"
        else:
            return self.tools[tool_name]["tool"]
        
    async def call_tool(self, tool_name, args):
        if tool_name not in self.tools:
            return f"Tool '{tool_name}' not found"
        else:
            return await self.tools[tool_name]["client"].call_tool(tool_name, args)
        
    async def disconnect(self):
        for server in self.config["mcp_servers"]:
            await server["client"].__aexit__(None, None, None)

if __name__ == "__main__":
    proxy = Proxy()
    asyncio.run(proxy.connect())
    print("Available tools:", asyncio.run(proxy.list_tools()))
    tool_name = input("Enter tool name to describe: ")
    print(asyncio.run(proxy.describe_tool(tool_name)))
    tool_name = input("Enter tool name to call: ")
    args = input("Enter arguments: ")
    print(asyncio.run(proxy.call_tool(tool_name, args)))