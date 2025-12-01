# Personal Life Automation Agent System
## Google ADK Capstone Project

## Overview

A multi-agent system built with Google's Agent Development Kit (ADK) that automates personal life management tasks including meal planning, grocery shopping, and travel planning.

## Key Features

- **Meal Planning**: Generate customized meal plans based on dietary restrictions and cuisine preferences
- **Shopping Lists**: Automatically create organized shopping lists with price estimates
- **Travel Planning**: Plan complete trips with accommodations, itineraries, and activity recommendations
- **Memory Bank**: Persistent storage of user preferences across sessions
- **Multi-Agent Coordination**: Hierarchical agent system with specialized sub-agents

## Architecture

### Agents
1. **Orchestrator Agent** - Coordinates all sub-agents and manages user interactions
2. **Meal Planning Agent** - Creates meal plans and provides recipe details
3. **Shopping Agent** - Generates and organizes shopping lists
4. **Travel Agent** - Plans trips and creates day-by-day itineraries

### MCP Tools
- **Recipe Database Tool** - Searches recipes with dietary filtering
- **Pricing API Tool** - Provides price estimates for grocery items
- **Travel Search Tool** - Searches accommodations, activities, and restaurants

### Memory & State
- **Memory Bank** - Stores user preferences, dietary restrictions, and feedback
- **Session Manager** - Maintains conversation context
- **State Persistence** - Enables pause/resume for long-running tasks

## Technology Stack

- **Framework**: Google ADK (Python)
- **LLM**: Gemini (configured for Google AI Studio or Vertex AI)
- **UI**: Gradio web interface
- **Data**: JSON-based persistence
- **Language**: Python 3.10+

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
```

3. Run the application:
```bash
python app.py
```

4. Open browser to http://localhost:7860

## Project Files

- `data_models.py` - Data models with validation
- `memory_bank.py` - User preference storage
- `session_manager.py` - Session management
- `state_persistence.py` - Pause/resume functionality
- `recipe_tool.py` - Recipe database MCP tool
- `pricing_tool.py` - Pricing API MCP tool
- `travel_tool.py` - Travel search MCP tool
- `meal_planning_agent.py` - Meal planning agent
- `shopping_agent.py` - Shopping list agent
- `travel_agent.py` - Travel planning agent
- `orchestrator_agent.py` - Main orchestrator
- `config.py` - Configuration management
- `app.py` - Gradio web interface

## Code Statistics

- **Total Code**: ~3,500 lines of Python
- **Agents**: 4 (1 orchestrator + 3 specialists)
- **MCP Tools**: 3 custom implementations
- **Data Models**: 15+ validated dataclasses
- **UI Tabs**: 4 (Chat, Meal Planning, Shopping, Travel)

## Key Achievements

✓ Multi-agent coordination with hierarchical architecture
✓ MCP tool integration with retry logic and error handling
✓ Persistent memory and session management
✓ Natural language interface with intent parsing
✓ Comprehensive data validation
✓ Production-ready error handling

## Future Enhancements

- Real Gemini API integration for intelligent conversation
- Production API connections for recipes, pricing, and travel
- Vector database for semantic search
- Collaborative planning for families
- Mobile-responsive PWA
- Voice interface integration

## License

MIT License

## Author

Google ADK Capstone Project
