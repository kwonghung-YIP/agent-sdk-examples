# How to start the OpenWeather MCP Server
```bash
# create the .env file and add the OpenWeather API Key into the file
# OPEN_WEATHER_APIKEY=<< paste_your_apikey_here >>
uv init
source .venv/bin/activate
uv run --env-file .env src/openweather-api.py

# or #
uv run fastmcp run src/openweather-api.py --no-banner --reload
```

# How to run fastMCP MCP inspector
```bash
# install nodejs with nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
nvm ls-remote
nvm install node

# start MCP inspector
fastmcp dev inspector src/openweather-api.py
```

# Reference
- [FastMCP - Quickstart](https://openweathermap.org/full-price) 
- [OpenWeather - Free Tier Plan](https://openweathermap.org/full-price)
- [OpenWeather - Current Weather Data API Reference](https://openweathermap.org/api/current?collection=current_forecast)
- [Node Version Manager (nvm)](https://github.com/nvm-sh/nvm#installing-and-updating)