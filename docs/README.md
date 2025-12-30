# SIBYL - AI Academic Planner

An intelligent semester planning agent that reads your syllabi and automatically creates an optimized study schedule in Google Calendar.

## Features

- Reads PDF syllabi automatically
- Extracts all assignments, exams, and readings
- Calculates strategic start dates (study 7 days before exams, etc.)
- Syncs directly to Google Calendar
- Prioritizes high-stakes work (exams > assignments > readings)


## Quick Start

### Prerequisites

- Python 3.10+
- Anthropic API key
- Google Calendar API credentials

### Installation
```bash
# Clone the repo
git clone https://github.com/optimusbuilder/sibyl-planner.git
cd sibyl-planner

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Add your API keys to a .env
```

### Usage
```python
from src.agent import main
import asyncio

response = asyncio.run(
    main("Analyze syllabi in ./my_syllabi_folder")
)
print(response)
```

## Configuration

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
GOOGLE_CALENDAR_CREDENTIALS=path/to/credentials.json
```

## How It Works

1. **Reads PDFs**: Uses MCP tools to extract text from syllabus PDFs
2. **Structures Data**: Claude extracts events with dates, types, and priorities
3. **Calculates Strategy**: Automatically determines when to start studying/working
4. **Syncs to Calendar**: Adds events to Google Calendar with smart reminders

## Architecture

- **Agent**: LangGraph ReAct agent powered by Claude Haiku 4.5
- **Tools**: MCP (Model Context Protocol) for file reading and calendar integration
- **Models**: Pydantic for structured data validation

## Contributing

Contributions and critique welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Support for Canvas/Blackboard API integration
- [ ] Multi-calendar support
- [ ] Conflict detection and resolution
- [ ] Mobile app
- [ ] Study time estimation based on course difficulty

## License

MIT License - see [LICENSE](LICENSE) file

## Acknowledgments

- Built with [LangChain](https://langchain.com) and [LangGraph](https://langgraph.com)
- Powered by [Anthropic's Claude](https://anthropic.com)
- Uses [MCP](https://modelcontextprotocol.io) for tool integration

## Support

- 🐛 [Report bugs](https://github.com/optimusbuilder/sibyl-planner/issues)
- 💡 [Request features](https://github.com/optimusbuilder/sibyl-planner/issues)
- 📧 Email: oyeludeferanmi@gmail.com