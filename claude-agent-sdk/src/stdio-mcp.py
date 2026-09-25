import asyncio
import os
from pathlib import Path
import json
from dataclasses import asdict

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
)

from claude_agent_sdk.types import (
    McpStdioServerConfig
)

msgLogPath = Path("messages/stdio-mcp")

async def main() -> None:

    stdio_mcp = McpStdioServerConfig(
        command = "fastmcp",
        args = [
            "run",
            "src/simple-stdio-mcp-server.py",
            "--transport",
            "stdio",
        ],
    )

    options = ClaudeAgentOptions(
        model="claude-haiku-4-5-20251001",
        system_prompt="You are a file manager who manages file on my drive",
        mcp_servers= {
            "nas_file_manager": stdio_mcp,
        },
        allowed_tools=[
            "Read",
            "mcp__list_resources",
            "mcp__read_resource",
            "mcp__nas_file_manager__*",
        ],
        add_dirs=[
            "./file-sandbox"
        ]
    )

    i:int = 0

    for msgfile in list(msgLogPath.glob("*.json")):
        os.remove(msgfile)

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Please upload ./file-sandbox/abc.txt to my NAS")

        async for message in client.receive_response():
            print(message)

            i = i + 1
            with open(msgLogPath / f"stdio-mcp_{i}_{type(message).__name__}.json", mode="w") as f:
                json.dump(asdict(message), f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())