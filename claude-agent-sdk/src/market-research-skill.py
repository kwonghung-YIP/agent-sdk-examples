import logging
import asyncio
import json
from pathlib import Path
import os

from dataclasses import asdict
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions
)


async def main() -> None:
    options = ClaudeAgentOptions(
        model="claude-haiku-4-5-20251001",
        system_prompt="You are a technical consuming product expert",
        cwd=os.getcwd(),
        setting_sources=["project"],
        skills="all",
        allowed_tools=[
            "Read",
            "Write",
            "Bash",
            "WebSearch",
        ]
    )

    msgLogPath = Path("messages/market-research-skill")
    for msgfile in list(msgLogPath.glob("market-research_*.json")):
        os.remove(msgfile)

    i:int = 0
    async for message in query(
        prompt="I am considering to buy a new PC monitor and would like to have a research first. I want a 4K monitor most of time for coding, the budget is below 700 pounds and will consider dual monitor if possible",
        options=options
    ): 
        print(message)

        i = i + 1
        with open(f"messages/market-research-skill/market-research_{i}_{type(message).__name__}.json", mode="w") as f:
            json.dump(asdict(message), f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())