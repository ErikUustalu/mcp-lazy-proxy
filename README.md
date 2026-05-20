# MCP lazy proxy

A lightweight context efficient proxy for MCP servers. Designed to reduce token usage by lazy-loading tools and tool descriptions only when needed.

## Features
- **Lazy loading:** Only fetch and provide the tools list and schemas when the model actually needs them
- **Easy to configure:** Configured with a simple config.json file
- **Lightweight:** Minimal overhead and no bloated features

## Why did I make this
Most standard MCP setups inject all avaliable MCP tool schemas to the model's context. For projects with many tools or general-use chatbots with many features this consumes tens of thousends of unnecessary tokens. MCP lazy proxy acts as a gateway that only gives the model a minimal interface for using the tools while still keeping the full functionality.

## Quick start
### CLI
1. **Clone the repo**
   ```
   git clone https://github.com/ErikUustalu/mcp-lazy-proxy
   cd mcp-lazy-proxy
2. **Configure your servers**
   Rename the config/config.json.example to config.json and add your servers

## Docker Compose
1. **Copy the compose**
   Copy the example [docker-compose.yaml](docker-compose.yaml)
2. **Copy the configuration**
   ```
   mkdir config
   nano config/config.json
   ```
   Copy and edit the configuration from [config/config.json.example](config/config.json.example)
3. **Start the compose**
   ```
   docker compose up -d
   ```

## License
MIT
