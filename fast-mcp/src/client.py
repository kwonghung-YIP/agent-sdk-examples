import asyncio
from fastmcp import Client

client = Client("http://localhost:8080/mcp")

async def call_tool():
    async with client:
        tools = await client.list_tools()
        for tool in tools:
            print(tool)
        params = { "lat": 51.5099, "lon": 0.1181 }
        result = await client.call_tool("get_current", arguments=params)
        print(result)

if __name__ == "__main__":
    asyncio.run(call_tool())