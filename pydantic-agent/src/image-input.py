import asyncio

from pydantic import BaseModel, Field
from typing import List, Annotated

from pydantic_ai import Agent, RunContext, BinaryImage

class StockQuote(BaseModel):
    ticker: Annotated[str, Field(description="Stock ticker")]
    company_name: Annotated[str, Field(description="Company Name")]
    price: Annotated[float, Field(description="Stock spot price")]

class StockQuoteList(BaseModel):
    quote: List[StockQuote]

agent = Agent(
    name="Vision Agent",
    model="openai:gpt-5-nano",
    system_prompt="""
    Extract user requested information from the input image.
    """,
    output_type=StockQuoteList
)

async def main() -> None:
    with open("stock-price.jpg", "rb") as image:
        image_binary = image.read()

    result = await agent.run(
        user_prompt=[
            BinaryImage(data=image_binary, media_type="image/jpeg"),
            "Extract all stock prices in the image embedded into the message."
        ]
    )

    print(result.all_messages_json())
    print(result.output)

if __name__ == "__main__":
    asyncio.run(main())