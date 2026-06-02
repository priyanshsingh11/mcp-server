import os
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp=FastMCP("Weather")

@mcp.tool()
async def get_weather(location:str)->str:
    """Get the current weather for a specific location."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "OpenWeatherMap API key is not configured."
        
    async with httpx.AsyncClient() as client:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        resp = await client.get(url)
        data = resp.json()
        
        if data.get("cod") != 200 and data.get("cod") != "200":
            return f"Could not find weather for location: {location}. Error: {data.get('message', 'Unknown error')}"
            
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        name = data["name"]
        
        return f"The current weather in {name} is {temp}°C with {desc}."

if __name__=="__main__":
    mcp.run(transport="streamable-http")