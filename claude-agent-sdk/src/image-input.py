import asyncio
import os
from pathlib import Path
import json
from dataclasses import asdict
import base64

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
)
from claude_agent_sdk.types import (
    StreamEvent,
    AssistantMessage,
    ResultMessage,
)

from pydantic import BaseModel, Field
from typing import List, Annotated

class StockQuote(BaseModel):
    ticker: Annotated[str, Field(description="Stock ticker")]
    company_name: Annotated[str, Field(description="Company Name")]
    price: Annotated[float, Field(description="Stock spot price")]

class StockQuoteList(BaseModel):
    quote: List[StockQuote]

i:int = 0
msgLogPath = Path("messages/image-input")

async def main() -> None:
    for msgfile in list(msgLogPath.glob("image_input_*.json")):
        os.remove(msgfile)

    async def query_generator():
        with open("stock-price.jpg", "rb") as image:
            image_base64 = base64.b64encode(image.read()).decode()

        print(f"image-base64:{image_base64}")
    
        yield {
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all stock prices in the image embedded into the message. The image is not from a file so please don't read my local drive."
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }
        }

    options = ClaudeAgentOptions(
        model="claude-haiku-4-5-20251001",
        system_prompt="You are a stock markrt analyst.",
        output_format={
            "type": "json_schema",
            "schema": StockQuoteList.model_json_schema(),
        }
    )

    async with ClaudeSDKClient(options) as client:
        await client.query(query_generator())

        async for message in client.receive_response():
            print_message(message)

            if isinstance(message, ResultMessage):
                quotes = StockQuoteList.model_validate(message.structured_output)
                print(quotes.model_dump_json(indent=4))

def print_message(message):

    global i
    print(message)

    i = i + 1
    with open(msgLogPath / f"image_input_{i}_{type(message).__name__}.json", mode="w") as f:
        json.dump(asdict(message), f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())