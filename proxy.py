import json
import asyncio
import logging
import os
import time

from fastmcp import Client
from collections import defaultdict
from rapidfuzz import fuzz

logging.basicConfig(level=logging.WARN, format="%(asctime)s - %(levelname)s - %(message)s")

class Proxy:
    def __init__(self, config_path="config/config.json", auto_reload=True, check_interval=1):
        self.config_path = config_path
        self.config = None
        self.auto_reload_enabled = auto_reload
        self.check_interval = check_interval
        self.tools = {}
        self.clients = []

    async def start(self):
        await self.load_config()
        if self.auto_reload_enabled:
            asyncio.create_task(self.auto_reload())

    async def auto_reload(self):
        last_modified = os.path.getmtime(self.config_path)
        while True:
            current_modified = os.path.getmtime(self.config_path)
            if current_modified != last_modified:
                await self.load_config()
                last_modified = current_modified
            await asyncio.sleep(self.check_interval)

    async def load_config(self):
        with open(self.config_path, "r") as f:
            try:
                self.config = json.load(f)
            except:
                logging.warning("Invalid json. Skipping reload")
                return
        tools = {}
        clients = []
        for server in self.config["mcp_servers"]:
            try:
                if server["auth"]:
                    client = Client(server["url"], auth=server["token"])
                else:
                    client = Client(server["url"])
                await client.__aenter__()
            except Exception as e:
                logging.warning(f"Failed to connect to {server['name']} at {server['url']} - Skipping")
                continue
            clients.append(client)
            for tool in await client.list_tools():
                server_name = server["name"].lower().replace(" ", "_")
                tool_name = f"{server_name}_{tool.name}"
                tool.name = tool_name
                tools[tool_name] = {
                    "tool": tool,
                    "client": client,
                    "server": server_name
                }
        self.tools = tools
        self.clients = clients

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
        
    async def search_tools(self, query, max_results=10, return_description=True):
        tools = {}
        query_words = query.split()

        for tool in self.tools.keys():
            name_ratio = 0
            desc_ratio = 0
            for word in query_words:
                name_ratio += fuzz.partial_ratio(tool.lower(), word.lower()) * 3
                desc_ratio += fuzz.partial_ratio(self.tools[tool]["tool"].description.lower(), word.lower())

            name_ratio /= len(query_words)
            desc_ratio /= len(query_words)
            tools[tool] = name_ratio + desc_ratio

        tools = sorted(tools, key=tools.get, reverse=True)
        tools = tools[:max_results]

        matches = []

        if return_description:
            for tool in tools:
                matches.append(str(self.tools[tool]["tool"]))
        else:
            matches = tools
            
        return matches

    async def disconnect(self):
        for client in self.clients:
            await client.__aexit__(None, None, None)

async def main():
    proxy = Proxy(auto_reload=False)
    await proxy.load_config()
    
    while True:
        task = input("list(1), describe(2), call(3), search(4), reload(5), exit(6): ")
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
            max_results = int(input("Max results: "))
            return_description = input("Return description ([y]/n): ")
            if return_description == "" or return_description == "y":
                return_description = True
            else:
                return_description = False

            print(await proxy.search_tools(query, max_results=max_results, return_description=return_description))

        elif task == "5":
            await proxy.load_config()

        elif task == "6":
            await proxy.disconnect()
            break

        else:
            print("Invalid command")

if __name__ == "__main__":
    asyncio.run(main())