import asyncio
from typing import Any

from pydantic_ai import Agent, RunContext

agent = Agent(
    name="tool calling agent",
    model='openai:gpt-5-nano',
    system_prompt="""
    # Role
    You are a personal assistant to help manage my personal schedule.
    """,
)

@agent.tool
async def current_location(ctx:RunContext[None]) -> str:
    """
    Fetch the current geo location of the caller
    """
    return "London"

@agent.tool
async def weather_info(ctx:RunContext[str], location:str) -> str:
    """
    Fetch the weather info of the given location
    
    Args:
        location: e.g. London, Paris
    """
    return f"{location} is sunny!"

async def main() -> None:
    result = await agent.run(
        user_prompt="""
        Please check the weather, should we go out to have a BBQ party?
        """
    )
    print(result.output)

if __name__ == "__main__":
    asyncio.run(main())