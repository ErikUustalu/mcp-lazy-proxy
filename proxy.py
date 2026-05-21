import json
import asyncio
import logging

from fastmcp import Client
from collections import defaultdict
from rapidfuzz import fuzz

logging.basicConfig(level=logging.WARN, format="%(asctime)s - %(levelname)s - %(message)s")

class Proxy:
    def __init__(self, config_path="config/config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.tools = {}
        self.clients = []

    async def connect(self):
        for server in self.config["mcp_servers"]:
            try:
                if server["auth"]:
                    client = Client(server["url"], auth=server["token"])
                else:
                    client = Client(server["url"])
                await client.__aenter__()
            except Exception as e:
                logging.warning(f"Failed to connect to {server['name']} at {server['url']}: {e} - Skipping")
                continue
            self.clients.append(client)
            for tool in await client.list_tools():
                server_name = server["name"].lower().replace(" ", "_")
                tool_name = f"{server_name}_{tool.name}"
                tool.name = tool_name
                self.tools[tool_name] = {
                    "tool": tool,
                    "client": client,
                    "server": server_name
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
            server_tool_name = tool_name.replace(self.tools[tool_name]["server"] + "_", "")
            return await self.tools[tool_name]["client"].call_tool(server_tool_name, args)
        
    async def search_tools(self, query, max_results=10):
        tools = {}
        for tool in self.tools.keys():
            name_ratio = fuzz.partial_ratio(tool.lower(), query.lower()) * 3
            desc_ratio = fuzz.partial_ratio(self.tools[tool]["tool"].description.lower(), query.lower())
            tools[tool] = name_ratio + desc_ratio

        matches = sorted(tools, key=tools.get, reverse=True)
        matches = matches[:max_results]
            
        return matches

    async def disconnect(self):
        for client in self.clients:
            await client.__aexit__(None, None, None)

async def main():
    proxy = Proxy()
    await proxy.connect()
    
    while True:
        task = input("list(1), describe(2), call(3), search(4), exit(5): ")
        if task == "1":
            tools = await proxy.list_tools()
            for i in range(len(tools)):
                print(f"[{i}] {tools[i]}")

        elif task == "2":
            tool_name = input("Tool name: ")
            if tool_name.isdigit():
                tool_name = list(await proxy.list_tools())[int(tool_name)]
            print(await proxy.describe_tool(tool_name))

        elif task == "3":
            tool_name = input("Tool name: ")
            if tool_name.isdigit():
                tool_name = list(await proxy.list_tools())[int(tool_name)]
            args = input("Arguments: ")
            if args == "":
                args = "{}"
            print(await proxy.call_tool(tool_name, json.loads(args)))

        elif task == "4":
            query = input("Query: ")
            print(await proxy.search_tools(query))

        elif task == "5":
            await proxy.disconnect()
            break

        else:
            print("Invalid command")

if __name__ == "__main__":
    asyncio.run(main())