import json
import asyncio
import logging

from fastmcp import Client
from collections import defaultdict

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
                tool_name = f"{tool.name}_{server_name}"
                self.tools[tool_name] = {
                    "tool": tool,
                    "client": client,
                    "server": server_name
                }

    async def list_tools(self):
        output = defaultdict(list)
        for tool in self.tools.keys():
            output[self.tools[tool]["server"].lower().replace(" ", "_")].append(tool)
        return output
    
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
        
    async def search_tools(self, query):
        matches = []
        for tool in self.tools.keys():
            if query.lower() in tool.lower():
                matches.append(tool)
            if query.lower() in str(self.tools[tool]).lower():
                matches.append(tool)
        return matches

    async def disconnect(self):
        for client in self.clients:
            await client.__aexit__(None, None, None)

async def main():
    proxy = Proxy()
    await proxy.connect()

    tool_map = []
    for key in (await proxy.list_tools()).keys():
        for tool in (await proxy.list_tools())[key]:
            tool_map.append(tool)
    
    while True:
        task = input("list(1), describe(2), call(3), search(4), exit(5): ")
        if task == "1":
            tools = await proxy.list_tools()
            keys = tools.keys()
            for key in keys:
                print(f"{key}:")
                for tool in tools[key]:
                    print(f"\t[{tool_map.index(tool)}] {tool}")

        elif task == "2":
            tool_name = input("Tool name: ")
            if tool_name.isdigit():
                tool_name = tool_map[int(tool_name)]
            print(await proxy.describe_tool(tool_name))

        elif task == "3":
            tool_name = input("Tool name: ")
            if tool_name.isdigit():
                tool_name = tool_map[int(tool_name)]
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