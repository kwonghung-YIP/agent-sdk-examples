import asyncio
from typing_extensions import TypedDict, Any

from agents import Agent, Runner, RunContextWrapper, trace
from agents.decorators import tool, function_tool

class OnlineShopOrder(TypedDict):
    memberId: str
    success: bool
    total_amount: float

@function_tool
async def current_location() -> str:
    """
    Fetch the current geo location of the caller
    """
    return "London"

@function_tool
async def weather_info(location:str) -> str:
    """
    Fetch the weather info of the given location
    
    Args:
        location: e.g. London, Paris
    """
    return f"{location} is sunny!"

@tool
async def place_order(ctx: RunContextWrapper[Any], item:str, qty:int) -> OnlineShopOrder:
    """
    The function place order to online shopping order to the nearby supermarket,
    it return an order instance.

    Args:
        item: the item you want to order. (e.g. beer, hot dog)
        qty: no of item you want to order. 
    """
    return OnlineShopOrder(memberId=ctx.context["memberId"], success=True, total_amount=99.99)


agent = Agent(
    name="tool_calling",
    instructions="You are an assistant for arranging user schedule",
    model="gpt-5-nano",
    tools=[current_location, weather_info, place_order]
)

async def main() -> None:
    with trace("tool-calling"):
        result = await Runner.run(
            agent,
            input="""
            Please check the weather, should we go out to have a BBQ party?
            If it is good for BBQ, please order 2 dozen beers for the party.
            """,
            context={"memberId":"member-001"})

        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())

