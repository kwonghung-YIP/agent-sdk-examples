# How to start the OpenWeather MCP Server
```bash
# create the .env file and add the OpenWeather API Key into the file
# OPEN_WEATHER_APIKEY=<< paste_your_apikey_here >>
uv init
source .venv/bin/activate
uv run --env-file .env src/openweather-api.py
```

# Reference
- [FastMCP - Quickstart](https://openweathermap.org/full-price) 
- [OpenWeather - Free Tier Plan](https://openweathermap.org/full-price)
- [OpenWeather - Current Weather Data API Reference](https://openweathermap.org/api/current?collection=current_forecast)