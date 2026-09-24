import asyncio
from dataclasses import dataclass
from pathlib import Path
import json

from pydantic import BaseModel, Field
from typing import List, Annotated

from pydantic_ai import Agent, RunContext
from pydantic_ai_harness.playwright import PlaywrightBrowser

output_path = Path("output/playwright-capabilities")

class Product(BaseModel):
    category: Annotated[str, Field(description="Product Category requested by user")]
    brand: str
    model_no: str
    url: Annotated[str|None,Field(description="The URL for the product page")]
    price: float

class ProductList(BaseModel):
    category: Annotated[str, Field(description="Product Category requested by user")]
    page: Annotated[int, Field(description="Total no of page in the website")]
    products: Annotated[List[Product], Field(description="Product full list found by the research")]    
    error: Annotated[str|None, Field(description="If any error while browsing the page, report the error here.")]
@dataclass
class ProductResearchInput:
    url: str
    product: str
    brand: str

agent = Agent(
    name="Market Research Assistant",
    model="openai:gpt-5-nano",
    deps_type=ProductResearchInput,
    output_type=ProductList,
    capabilities=[PlaywrightBrowser(
        cdp_url='http://localhost:9222'
    )],
)

@agent.system_prompt
async def fetch_system_prompt(ctx:RunContext[ProductResearchInput]) -> str:
    return f"""
        # Role
        You are a Market Research Assistant expertise in the "{ctx.deps.product}".

        # Workflow
        1. User provide an URL for a product page: {ctx.deps.url}.
        2. Find out the total number of page in "Page XX of NN" near the footer in the page.
        3. You should found a list of product in the page if it loaded successfully, otherwise wait for 5 second and reload and try again.
        4. For each page, extract the information that the user requested for.
        5. Open next page if it is available, then extract the requested information again.
        6. After go through all pages and extracted all information, return the user expected output.

        # Hints
        - Use the provided tools to browse the product page.
        - Accept all cookie.
        """
    
async def main():
    result = await agent.run(
        deps=ProductResearchInput(
            product="PC Monitor",
            brand="Dell",
            url="https://www.dell.com/en-gb/shop/computer-monitors/ar/all-monitors",
        ),
        user_prompt="""
        # Objective
        - Extract all available PC Monitor models in the Dell Website.
        - For each model, extract the below information: 
          - model no
          - price
          - product link (the hyperlink attached with the Model No)
        """,
    )
    print(result.output.model_dump_json(indent=3))
    with open(output_path / "dell-pc-monitors.json", mode="w") as f:
        f.write(result.output.model_dump_json(indent=3))
    #with open(output_path / "dell-pc-monitors-usage.json", mode="w") as f:
    #    json.dump(result.usage, f, indent=3)

if __name__ == "__main__":
    asyncio.run(main())