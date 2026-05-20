import json
import asyncio

from fastmcp import Client

class Proxy:
    def __init__(self, config_path="config.json"):
        with open("config.json", "r") as f:
            self.config = json.load(f)
        self.tools = {}
        self.clients = []

    async def connect(self):
        for server in self.config["mcp_servers"]:
            client = Client(server["url"])
            await client.__aenter__()
            self.clients.append(client)
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
        for client in self.clients:
            await client.__aexit__(None, None, None)

async def main():
    proxy = Proxy()
    await proxy.connect()
    
    while True:
        task = input("list(1), describe(2), call(3), exit(4): ")
        if task == "1":
            tools = await proxy.list_tools()
            for i in range(len(tools)):
                print(f"[{i}] {tools[i]}")

        elif task == "2":
            tool_name = input("Tool name: ")
            if tool_name.isdigit():
                tool_name = (await proxy.list_tools())[int(tool_name)]
            print(await proxy.describe_tool(tool_name))

        elif task == "3":
            tool_name = input("Tool name: ")
            if tool_name.isdigit():
                tool_name = (await proxy.list_tools())[int(tool_name)]
            args = input("Arguments: ")
            if args == "":
                args = "{}"
            print(await proxy.call_tool(tool_name, json.loads(args)))

        elif task == "4":
            await proxy.disconnect()
            break

        else:
            print("Invalid command")

if __name__ == "__main__":
    asyncio.run(main())