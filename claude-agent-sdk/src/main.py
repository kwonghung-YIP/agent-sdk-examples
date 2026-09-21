import asyncio
from dataclasses import asdict
import json
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage
)

async def main():
    print("main")
    i:int = 0
    async for message in query(
        prompt="Review the best budget CPU for running local AI",
        options=ClaudeAgentOptions(
            # model="haiku", # model alias
            model="claude-haiku-4-5-20251001",
            system_prompt="You are a Gaming PC Expert who helps to review different products",
            allowed_tools=["WebSearch"],
            max_turns=10,
            thinking={ "type":"enabled", "budget_tokens": 500, "display": "summarized" }
        )
    ):
        with open(f"message_{i}.json", mode="w") as f:
            f.write(json.dumps(asdict(message), indent=4))

        if isinstance(message, ResultMessage):
            print(message)

if __name__ == "__main__":
    asyncio.run(main())