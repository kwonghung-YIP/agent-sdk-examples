import asyncio

from agents import Agent, Runner, trace, function_tool
from agents.mcp import MCPServerStreamableHttp

from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
from geopy.location import Location
from typing_extensions import TypedDict

class MyLocation(TypedDict):
    latitude: float
    longitude: float
    address: str

@function_tool
async def get_current_location() -> MyLocation:
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
    with trace("openweather-mcp"):
        async with MCPServerStreamableHttp(
            name="OpenWeather MCP Server",
            params={
                "url": "http://localhost:8080/mcp",
                "timeout": 30,
            }
        ) as mcp_server:
            agent = Agent(
                name="personal schedule assistant",
                model="gpt-5-nano",
                instructions="""
                # Role
                You are a personal schedule assistant manage my schedule.
                
                # Rules
                - please check the weather before you arrange an event.
                """,
                mcp_servers=[mcp_server],
                tools=[get_current_location],
            )

            result = await Runner.run(
                agent,
                input="""
                Should we go out to have a BBQ party now?
                """
            )
            print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())