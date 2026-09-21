import logging
import asyncio
from contextlib import asynccontextmanager
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
from geopy.location import Location
from typing import Any

from dataclasses import asdict
import json

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server
)

from claude_agent_sdk.types import (
    McpHttpServerConfig
)

class GeoLocator:

    @staticmethod
    @asynccontextmanager
    async def get_instance():
        async with Nominatim(
            user_agent="my-agent",
            adapter_factory=AioHTTPAdapter,
        ) as nominatim:
            locator = GeoLocator(nominatim)
            yield locator

    def __init__(self, nominatim:Nominatim) -> None:
        self._locator:Nominatim = nominatim

    async def get_current_location(self) -> Location:
        """
        This function convert the given address into geo location
        """
        return await self._locator.geocode("London")
    
    async def get_geo_location(self, address:str) -> Location:
        """
        This function convert the given address into geo location
        """
        return await self._locator.geocode(address)

class GeoLocatorWrapper:

    def __init__(self, geolocator:GeoLocator) -> None:
        self._locator = geolocator

    async def get_current_location(self, args: dict[str, Any]) -> dict[str, Any]:
        location = await self._locator.get_current_location()

        result = {
            "altitude": location.altitude,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "address": location.address
        }
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result)
                }
            ],
            "structuredContent": location
        }

    async def get_geo_location(self, args: dict[str, Any]) -> dict[str, Any]:
        location = await self._locator.get_geo_location(args["address"])

        result = {
            "altitude": location.altitude,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "address": location.address
        }
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result)
                }
            ],
            "structuredContent": location
        }

async def main() -> None:
    async with GeoLocator.get_instance() as locator:

        location = await locator.get_current_location()
        print(type(location))
        print(location)

        location = await locator.get_geo_location("London")
        print(type(location))
        print(location)

        wrapper = GeoLocatorWrapper(locator)

        tool1 = tool(
                name="get_current_location",
                description="Get my current geo location information",
                input_schema={}
            )(wrapper.get_current_location)

        tool2 = tool(
                name="address_to_geo_location",
                description="This function convert the given address into geo location",
                input_schema={"address":str}
            )(wrapper.get_geo_location)
        
        location_mcp = create_sdk_mcp_server(
            name="location",
            version="1.0.0",
            tools=[
                tool1,
                tool2
            ]
        )

        weather_mcp = McpHttpServerConfig(
            type="http",
            url="http://localhost:8080/mcp"
        )

        options = ClaudeAgentOptions(
            model="claude-haiku-4-5-20251001",
            system_prompt="You are a travel expert who helps to plan itinerary",
            mcp_servers= {
                "location": location_mcp,
                "weather": weather_mcp
            },
            allowed_tools=[
                "mcp__list_resources",
                "mcp__read_resource",
                "mcp__location__*",
                "mcp__weather__*"
            ]
        )

        i:int = 0
        async for message in query(
            prompt="Please check the local weather and plan my schedule for next few hours",
            options=options
        ): 
            print(message)

            i = i + 1
            with open(f"messages/openweather-mcp/open_weather_{i}_{type(message).__name__}.json", mode="w") as f:
                json.dump(asdict(message), f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())