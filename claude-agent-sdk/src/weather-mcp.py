import asyncio
from dataclasses import asdict
import json

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
)

from claude_agent_sdk.types import (
    McpHttpServerConfig
)

async def main() -> None:

    weather_mcp = McpHttpServerConfig(
        type="http",
        url="http://localhost:8080/mcp"
    )
    options = ClaudeAgentOptions(
        model="claude-haiku-4-5-20251001",
        system_prompt="You are a weather reporter",
        mcp_servers= {
            "weather": weather_mcp
        },
        allowed_tools=[
            "mcp__weather__current_location",
            "mcp__weather__get_weather"
        ]
    )

    i:int = 0
    async for message in query(
        prompt="Please tell me the weather",
        options=options
    ): 
        print(message)

        i = i + 1
        with open(f"weather_{i}.json", mode="w") as f:
            json.dump(asdict(message), f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())