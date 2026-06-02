# Multi-Server MCP Application

This project demonstrates a small but complete Model Context Protocol (MCP) application with multiple MCP servers and an AI client that can discover and use their tools.

It includes:

- A local math MCP server that runs over `stdio`.
- A weather MCP server that runs over `streamable-http`.
- A LangGraph ReAct agent that connects to both servers through `langchain-mcp-adapters`.
- A Groq-hosted LLaMA model that decides which MCP tool to call for each user request.

The main idea is simple: the language model does not need to know how to calculate or fetch weather directly. It receives tool definitions from MCP servers, chooses the right tool, calls it, and uses the result in its final response.

## Project Structure

```text
.
├── client.py          # LangGraph/LangChain client that connects to both MCP servers
├── maths.py           # MCP server exposing math tools over stdio
├── weather.py         # MCP server exposing weather lookup over streamable HTTP
├── main.py            # Small starter entry point
├── requirements.txt   # Python dependencies
├── .GITIGNORE         # Local files ignored by Git
└── README.md          # Project documentation
```

## How the Pieces Work Together

### `maths.py`

`maths.py` creates a FastMCP server named `Math`.

It exposes two tools:

- `add(a: int, b: int) -> int`: adds two integers.
- `multiple(a: int, b: int) -> int`: multiplies two integers.

This server runs with the `stdio` transport:

```python
mcp.run(transport="stdio")
```

Because it uses standard input/output, the client can start it as a subprocess. You do not need to manually run `maths.py` before running the client.

### `weather.py`

`weather.py` creates a FastMCP server named `Weather`.

It exposes one async tool:

- `get_weather(location: str) -> str`: fetches current weather for a given location using the OpenWeatherMap API.

This server runs with the `streamable-http` transport:

```python
mcp.run(transport="streamable-http")
```

The client expects this server to be available at:

```text
http://localhost:8000/mcp
```

Because this is an HTTP server, it must be started separately before running `client.py`.

### `client.py`

`client.py` is the AI client. It uses:

- `MultiServerMCPClient` to connect to multiple MCP servers.
- `create_react_agent` from LangGraph to create a tool-using agent.
- `ChatGroq` with the `llama-3.1-8b-instant` model.

The client connects to two MCP servers:

```python
client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            "args": ["maths.py"],
            "transport": "stdio",
        },
        "weather": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        },
    }
)
```

After connecting, it retrieves the available tools and gives them to the LangGraph agent:

```python
tools = await client.get_tools()
model = ChatGroq(model="llama-3.1-8b-instant")
agent = create_react_agent(model, tools)
```

## Prerequisites

Before running the project, make sure you have:

- Python 3.10 or newer.
- A Groq API key.
- An OpenWeatherMap API key.
- A terminal that can run multiple sessions at the same time.

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

These values are loaded with `python-dotenv`.

The `.GITIGNORE` file already ignores `.env`, virtual environments, Python bytecode files, and `__pycache__`, which helps keep secrets and generated files out of Git.

## How to Run

This project uses two transports, so it needs two terminal sessions.

### Terminal 1: Start the Weather MCP Server

Activate the virtual environment, then start the weather server:

```bash
.\venv\Scripts\Activate.ps1
python weather.py
```

Leave this terminal running. The weather server will listen on `localhost:8000` and expose the MCP endpoint at `/mcp`.

### Terminal 2: Run the AI Client

Open a second terminal, activate the virtual environment, and run:

```bash
.\venv\Scripts\Activate.ps1
python client.py
```

The client will:

1. Start `maths.py` automatically through `stdio`.
2. Connect to the running weather server over HTTP.
3. Discover all tools from both MCP servers.
4. Create a ReAct agent using Groq.
5. Ask one math question and one weather question.

## Example Flow

The math prompt in `client.py` asks:

```text
what's (3 + 5) x 12? Please use the add tool first to calculate 3+5, and then pass that result to the multiple tool.
```

The expected tool flow is:

1. Call `add(3, 5)` and receive `8`.
2. Call `multiple(8, 12)` and receive `96`.
3. Return a final natural-language answer.

The weather prompt asks:

```text
what is the weather in California?
```

The expected tool flow is:

1. Call `get_weather("California")`.
2. Fetch weather data from OpenWeatherMap.
3. Return the current temperature and weather description.

## Dependencies

The project uses the following Python packages:

- `mcp`: MCP server utilities, including FastMCP.
- `langchain-mcp-adapters`: connects LangChain/LangGraph clients to MCP servers.
- `langgraph`: builds the ReAct agent.
- `langchain-groq`: connects the agent to Groq-hosted models.
- `httpx`: performs async HTTP requests for weather data.

## Troubleshooting

### `OPENWEATHER_API_KEY` is not configured

Make sure your `.env` file exists and includes:

```env
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

Then restart `weather.py`.

### `GROQ_API_KEY` is missing

Make sure your `.env` file includes:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Then rerun `client.py`.

### The client cannot connect to the weather server

Check that `weather.py` is running before starting `client.py`.

The client expects this URL:

```text
http://localhost:8000/mcp
```

If the weather server is running on another host or port, update the `weather` entry in `client.py`.

### Weather lookup returns an unknown location error

OpenWeatherMap may not recognize the location string. Try a more specific value, such as:

```text
California,US
London,UK
Delhi,IN
```

### The math server does not need a separate terminal

`maths.py` uses `stdio`, so `client.py` starts it automatically. Only `weather.py` needs to be started manually.

## Development Notes

When adding a new MCP tool:

1. Add the function to the relevant server file.
2. Decorate it with `@mcp.tool()`.
3. Use clear type hints for inputs and outputs.
4. Write a docstring that explains what the tool does.
5. Restart the server so the client can discover the new tool.

For example:

```python
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b
```

If the tool belongs to the HTTP weather server, restart `weather.py`. If it belongs to the stdio math server, rerun `client.py`.

## Security Notes

- Do not commit `.env` or API keys.
- Keep tool inputs validated with type hints and explicit checks where needed.
- Be careful before adding tools that read files, write files, run shell commands, or call paid APIs.
- Avoid returning sensitive data in tool responses.
- Keep API errors helpful, but do not expose secrets or full internal traces.

## Future Improvements

Useful next steps for this project could include:

- Add a `.env.example` file with placeholder variables.
- Add tests for `maths.py` tools.
- Improve `weather.py` error handling for network failures.
- Add support for more weather details, such as humidity, wind speed, and country code.
- Make `client.py` interactive instead of using two hard-coded prompts.
- Add a third MCP server to demonstrate another transport or tool category.

## License

Add a license if you plan to share or publish this project.
