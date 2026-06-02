import httpx
from mcp.server.fastmcp import FastMCP

mcp=FastMCP("Weather")

@mcp.tool()
async def get_weather(location:str)->str:
    """Get the current weather for a specific location."""
    async with httpx.AsyncClient() as client:
        # First get the latitude and longitude from the location name
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        geo_resp = await client.get(geo_url)
        geo_data = geo_resp.json()
        
        if not geo_data.get("results"):
            return f"Could not find the location: {location}"
            
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        name = geo_data["results"][0]["name"]
        
        # Then get the current weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
        weather_resp = await client.get(weather_url)
        weather_data = weather_resp.json()
        
        temp = weather_data["current"]["temperature_2m"]
        wind = weather_data["current"]["wind_speed_10m"]
        
        return f"The current weather in {name} is {temp}°C with a wind speed of {wind} km/h."

if __name__=="__main__":
    mcp.run(transport="streamable-http")