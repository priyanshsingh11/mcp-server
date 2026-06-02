# Multi-Server MCP Application

This project is a demonstration of a fully functioning, multi-tool, multi-transport Model Context Protocol (MCP) application. It features two separate MCP servers providing distinct tools, and a LangGraph-powered AI client that orchestrates them using LLaMA models.

## Project Structure

- **`maths.py`**: A locally-run MCP server that communicates over standard input/output (`stdio`). It provides basic mathematical tools:
  - `add`: Adds two integers together.
  - `multiple`: Multiplies two integers.
- **`weather.py`**: A persistent MCP server that communicates over an HTTP stream (`streamable-http`). It securely uses an OpenWeatherMap API key to fetch real-world weather data for any location.
  - `get_weather`: Takes a location string and returns the current temperature and weather conditions.
- **`client.py`**: The AI Agent application built using LangChain, LangGraph, and LangChain MCP Adapters. It dynamically discovers tools from both the Math and Weather MCP servers and exposes them to a `llama-3.1-8b-instant` model hosted on Groq.

## Prerequisites

1. Python 3.10+
2. A Groq API Key (for the LLM)
3. An OpenWeatherMap API Key (for the weather server)

## Installation

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   
   # For Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   
   # For Mac/Linux:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your `.env` file with your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

## How to Run

Because this architecture uses an HTTP-based MCP server (`weather.py`), you need to run the application using two separate terminals.

### Terminal 1: Start the Weather MCP Server
Start the weather server and leave it running in the background. It will host the weather tool on `localhost:8000`.
```bash
.\venv\Scripts\activate
python weather.py
```

### Terminal 2: Run the AI Client
In a new terminal window, start the AI client. It will automatically spawn the math server internally via `stdio` and connect to your running weather server via HTTP.
```bash
.\venv\Scripts\activate
python client.py
```

## How it Works

When you run `client.py`, the ReAct agent takes your natural language prompts and decides which MCP server to query:
- For `"what's (3 + 5) x 12?"`, it queries the `maths.py` MCP server.
- For `"what is the weather in California?"`, it queries the `weather.py` MCP server over HTTP.

This demonstrates the core power of MCP: The LLM client doesn't need to know *how* to calculate math or fetch weather; it just asks the standardized MCP servers to do the heavy lifting!
