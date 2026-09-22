import logging
import asyncio
import os
import dotenv
import httpx2
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Annotated

from fastmcp import FastMCP
from fastmcp.tools import tool

logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG
)

dotenv.load_dotenv(verbose=True)

mcp = FastMCP("OpenWeather API MCP Server")

class Coordination(BaseModel):
    """Geographic coordinates"""
    lon: Annotated[float, Field(description="Longitude of the location")]
    lat: Annotated[float, Field(description="Latitude of the location")]

class Weather(BaseModel):
    id: Annotated[int, Field(description="Weather condition id")]
    main: Annotated[str, Field(description="Group of weather parameters (Rain, Snow, Clouds etc.)")]
    description: Annotated[str, Field(description="Weather condition within the group")]
    icon: Annotated[str, Field(description="Weather icon id")]

class Main(BaseModel):
    temp: Annotated[float, Field(description="Temperture. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit")]
    feels_like: Annotated[float, Field(description="Temperature. This temperature parameter accounts for the human perception of weather. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit")]
    pressure: Annotated[int, Field(description="Atmospheric pressure on the sea level, hPa")]
    humidity: Annotated[int, Field(description="Humidity, %")]
    temp_min: Annotated[float, Field(description="Minimum temperature at the moment. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit")]
    temp_max: Annotated[float, Field(description="Maximum temperature at the moment. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit")]
    sea_level: Annotated[int, Field(description="Atmospheric pressure on the sea level, hPa")]
    grnd_level: Annotated[int, Field(description="Atmospheric pressure on the ground level, hPa")]

class Wind(BaseModel):
    """Wind information"""
    speed: Annotated[float, Field(description="Wind speed. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour")]
    deg: Annotated[int, Field(description="Wind direction, degrees (meteorological)")]
    gust: Annotated[float|None, Field(default=None, description="Wind gust. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour")]

class Clouds(BaseModel):
    """Cloudiness infomation"""
    all: Annotated[int, Field(description="Cloudiness, %.")]

class Rain(BaseModel):
    """Rain volume"""
    one_hour: Annotated[float|None, Field(alias="1h", description="Rain volume for the last 1 hour, mm.")]

class Snow(BaseModel):
    """Snow volume"""
    one_hour: Annotated[float|None, Field(alias="1h", description="Snow volume for the last 1 hour, mm.")]

class Sys(BaseModel):
    type: Annotated[int|None, Field(description="Internal parameter")]
    id: Annotated[int|None, Field(description="Internal parameter")]
    message: Annotated[str|None, Field(default=None, description="Internal parameter")]
    country: Annotated[str|None, Field(description="Country Code")]
    sunrise: Annotated[int|None, Field(description="Sunrise time, Unix, UTC.")]
    sunset: Annotated[int|None, Field(description="Sunset time, Unix, UTC.")]

class CurrentWeatherData(BaseModel):
    coord: Coordination
    weather: List[Weather]
    base: Annotated[str, Field(description="Internal parameter")]
    main: Main
    visibility: Annotated[int, Field(description="Visibility, meter. The maximum value of the visibility is 10 km")]
    wind: Wind
    clouds: Clouds
    rain: Rain|None = None
    snow: Snow|None = None
    dt: Annotated[int, Field(description="Time of data calculation, unix, UTC")]
    sys: Sys
    timezone: Annotated[int, Field(description="Shift in seconds from UTC")]
    id: Annotated[int, Field(description="City ID")]
    name: Annotated[str, Field(description="City Name")]
    cod: Annotated[int, Field(description="Internal parameter")]

    model_config = ConfigDict(extra='ignore')

class OpenWeatherClient:
    """
    OpenWeather API Client implementation
    """

    def __init__(
        self,
        baseUrl:str = "https://api.openweathermap.org/data",
        version:str = "2.5"
    ) -> None:
        self._apikey:str = os.getenv("OPEN_WEATHER_APIKEY")

        headers = {
            "Accept": "application/json",
        }

        params = {
            "appid": self._apikey,
            "lang": "en",
        }

        self._client = httpx2.AsyncClient(
            base_url=f"{baseUrl}/{version}",
            headers=headers,
            params=params,
            http2=True,
            follow_redirects=True,
        )

    async def __aenter__(self):
        print("create httpx2 async client...")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        print("close httpx2 async client...")
        await self._client.aclose()

    @tool(name="get_current")
    async def get_current(self, lat:float, lon:float) -> CurrentWeatherData:
        """
        Get Current Weather Data (v2.5)
        reference: https://openweathermap.org/api/current?collection=current_forecast
        """

        params = {
            "lat": lat,
            "lon": lon,
        }
        response = await self._client.get(url="/weather", params=params)
        #print(response.url)
        print(response.json())

        data = CurrentWeatherData.model_validate(response.json())

        return data

client = OpenWeatherClient()
mcp.tool(client.get_current)

async def main() -> None:
    
    #await mcp.run_http_async(
    #    stateless_http=True,
    #    json_response=True,
    #    transport="http", host="localhost", port=8080
    #)
    await client._client.aclose()

if __name__ == "__main__":
    #asyncio.run(main())
    mcp.run(
        transport="http", host="localhost", port=8080, json_response=True
    )