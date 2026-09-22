import asyncio
import base64

from pydantic import BaseModel, Field
from typing import List, Annotated

from agents import Agent, Runner, trace

class StockQuote(BaseModel):
    ticker: Annotated[str, Field(description="Stock ticker")]
    company_name: Annotated[str, Field(description="Company Name")]
    price: Annotated[float, Field(description="Stock spot price")]

class StockQuoteList(BaseModel):
    quote: List[StockQuote]

agent = Agent(
    name="Vision Agent",
    model="gpt-5-nano",
    instructions="""
    Extract user requested information from the input image.
    """,
    output_type=StockQuoteList
)

async def main() -> None:
    with trace("image-input"):
        with open("stock-price.jpg", "rb") as image:
            image_base64 = base64.b64encode(image.read()).decode()

        result = await Runner.run(
            agent,
            input = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "detail": "auto",
                            "image_url": f"data:image/jpeg;base64,{image_base64}",
                        },
                        {
                            "type": "input_text",
                            "text": """
                            Extract all stock prices in the image embedded into the message. 
                            """
                        }
                    ]
                }
            ]
        )

        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())