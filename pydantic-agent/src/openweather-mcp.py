import asyncio

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import MCP

from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
from geopy.location import Location
from typing_extensions import TypedDict, Any

class MyLocation(TypedDict):
    latitude: float
    longitude: float
    address: str

agent = Agent(
    name="personal schedule assistant",
    model="openai:gpt-5-nano",
    system_prompt="""
    # Role
    You are a personal schedule assistant manage my schedule.
    
    # Rules
    - please check the weather before you arrange an event.
    """,
    capabilities=[
        MCP(
            id="open-weather-mcp",
            url="http://localhost:8080/mcp",
            description="OpenWeather MCP Server"
        )
    ]
)

@agent.tool
async def get_current_location(ctx:RunContext[Any]) -> MyLocation:
    """
    Use this function to get your current geo location
    """
    async with Nominatim(
        user_agent="my-geo-agent",
        adapter_factory=AioHTTPAdapter,
    ) as locator:
        location:Location = await locator.geocode("London")
        result = MyLocation(
            latitude=location.latitude,
            longitude=location.longitude,
            address=location.address,
        )
        return result

async def main() -> None:
    result = await agent.run(
        user_prompt="""
        Should we go out to have a BBQ party now?
        """
    )
    print(result.output)

if __name__ == "__main__":
    asyncio.run(main())