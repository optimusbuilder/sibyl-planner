# Setup Guide

Complete step-by-step instructions to get SIBYL running on your machine.

## Prerequisites

### System Requirements
- Python 3.10 or higher
- pip (Python package manager)
- Git

Check your Python version:
```bash
python --version  # Should show 3.10+
```

### Required API Keys

1. **Anthropic API Key**
   - Sign up at https://console.anthropic.com
   - Navigate to API Keys section
   - Create a new key
   - Copy and save it securely

2. **Google Calendar API** (Optional but recommended)
   - Go to https://console.cloud.google.com
   - Create a new project or select existing
   - Enable Google Calendar API. Ensure that when setting up, you allow the API to see, read, add and delete events from your calendar.
   - Create OAuth 2.0 credentials
   - Download `credentials.json`

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/optimusbuilder/sibyl-planner
cd sibyl-planner
```

### 2. Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If you encounter errors:
```bash
# Try installing problem packages individually
pip install langchain langgraph langchain-anthropic
pip install anthropic pydantic python-dotenv
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Optional (for calendar integration)
GOOGLE_CALENDAR_CREDENTIALS=credentials.json
```

### 5. Set Up Google Calendar (Optional)

If you want calendar integration:

1. Place your `credentials.json` in the project root
2. Run the authentication flow:
```python
from src.functions import get_calendar_service

get_calendar_service()
```

3. A browser window will open - grant permissions
4. A `token.json` file will be created (keep this secret!)

## Verification

Test that everything works:
```python
import asyncio
from src.agent import main


asyncio.run(main("[put your query here with the path to your folders]"))
```

Expected output: SIBYL should respond confirming that it has seen the files and it has scanned them.

## Project Structure
```
sibyl-planner/
├── src/
│   ├── agent.py          # Main agent logic
│   ├── functions.py      # Compilation of functions used in the agents
│   ├── mcp_server.py     # MCP server file (Always run this file first) 
│   ├── prompts.py        # System prompts
│   └── structures.py     # Pydantic schemas
├── examples/
│   └── basic_usage.ipynb    # Example scripts
├── .env                  # Your API keys (DO NOT COMMIT)
├── credentials.json      # Google credentials (DO NOT COMMIT)
└── requirements.txt      # Python dependencies
```

## MCP Server Setup

SIBYL uses Model Context Protocol (MCP) for tools. You need to set up MCP servers:

### File System Server
```bash
# Install MCP file system server
npm install -g @modelcontextprotocol/server-filesystem

# Or using uvx (Python)
uvx mcp install filesystem
```

### Google Calendar Server
```bash
# Install MCP Google Calendar server
npm install -g @modelcontextprotocol/server-google-calendar

# Or
uvx mcp install google-calendar
```

### Configure MCP Client

In your code, initialize the MCP client:
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# File system MCP server
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/syllabi"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # Your agent code here
```

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'langchain'`
**Solution:** Make sure your virtual environment is activated and run:
```bash
pip install -r requirements.txt
```

### Issue: `AuthenticationError: Invalid API key`
**Solution:** Check that your `.env` file has the correct Anthropic API key and is in the project root.

### Issue: Google Calendar authentication fails
**Solution:** 
1. Make sure `credentials.json` is in the project root
2. Delete `token.json` and try again
3. Check that Calendar API is enabled in Google Cloud Console

### Issue: `ImportError: cannot import name 'create_react_agent'`
**Solution:** Update LangGraph:
```bash
pip install --upgrade langgraph
```

### Issue: MCP tools not found
**Solution:** 
1. Verify MCP servers are installed: `npm list -g`
2. Check server paths in your code
3. Ensure servers are running: test with `npx @modelcontextprotocol/server-filesystem`

## Testing Your Setup

Run the example script:
```bash
python examples/basic_usage.py
```

This should:
1. ✅ Connect to Anthropic API
2. ✅ Initialize MCP tools
3. ✅ Run SIBYL agent
4. ✅ Display a response

## Next Steps

- Read the [Usage Examples](../examples/)
- Check the [API Documentation](API.md)
- Join our [Discord community](link)

## Getting Help

If you're stuck:
1. Check [Common Issues](#common-issues) above
2. Search [existing issues](https://github.com/yourusername/sibyl-planner/issues)
3. Open a new issue with:
   - Your Python version
   - Full error message
   - Steps to reproduce

## Development Setup

If you want to contribute:
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black .
ruff check . --fix
```

---

**You're all set! 🎉** Head back to the [README](../README.md) for usage instructions.