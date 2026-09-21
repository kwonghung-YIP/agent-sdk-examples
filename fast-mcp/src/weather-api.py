from fastmcp import FastMCP

mcp = FastMCP("Weather MCP Server")

@mcp.tool
def current_location() -> str:
    """
    Get my current location
    """
    return "London"

@mcp.tool
def get_weather(location:str) -> float:
    """
    Get weather info by location

    Args:
        location: Weather info of the given location
    """
    return 39.9

if __name__ == "__main__":
    mcp.run()