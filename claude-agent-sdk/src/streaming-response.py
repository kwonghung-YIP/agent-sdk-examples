import asyncio
import os
from pathlib import Path
import json
from dataclasses import asdict


from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
)
from claude_agent_sdk.types import (
    StreamEvent,
    AssistantMessage,
    ResultMessage,
)

i:int = 0
msgLogPath = Path("messages/streaming-response")

async def main() -> None:
    for msgfile in list(msgLogPath.glob("streaming_response_*.json")):
        os.remove(msgfile)

    options = ClaudeAgentOptions(
        model="claude-haiku-4-5-20251001",
        system_prompt="You are a stand-up comedians",
        include_partial_messages=True,
    )

    async for message in query(
        prompt="Tell me a 3 minutes joke about a junior developer first production release in night shift",
        options=options,
    ):
        print_message(message)

        if isinstance(message, StreamEvent):
            event = message.event
            if event.get("type") == "message_start":
                msg = event.get("message")
                print(f"event.type:{event["type"]}, message.id:{msg["id"]}")
            elif event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    print(f"event.type:{event["type"]}, delta.type:{delta["type"]}", delta.get("text"))
                elif delta.get("type") == "thinking_delta":
                    print(f"event.type:{event["type"]}, delta.type:{delta["type"]}", delta.get("thinking"))
                else:
                    print(f"event.type:{event["type"]}, delta.type:{delta["type"]}")
            else:
                print(f"event.type:{event["type"]}")
        elif isinstance(message, AssistantMessage):
            print(f"AssistantMessage: message_id:{message.message_id}, content:{message.content}")
        elif isinstance(message, ResultMessage):
            print(f"ResultMessage: result:{message.result}")



def print_message(message):

    global i
    #print(message)

    i = i + 1
    with open(msgLogPath / f"streaming_response_{i}_{type(message).__name__}.json", mode="w") as f:
        json.dump(asdict(message), f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())