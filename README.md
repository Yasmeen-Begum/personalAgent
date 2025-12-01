# Personal Life Automation Agent System

A multi-agent platform designed to help individuals automate and streamline common life management tasks including meal planning, grocery shopping, and travel planning.

## Features

- **Meal Planning**: Generate weekly meal plans based on dietary preferences and restrictions
- **Shopping Lists**: Automatically create organized shopping lists from meal plans
- **Travel Planning**: Plan trips with suggested itineraries and accommodations
- **Memory Bank**: Persistent storage of user preferences and feedback
- **Pause/Resume**: Handle long-running tasks with state persistence

## Architecture

The system uses Google's Agent Development Kit (ADK) with a hierarchical multi-agent pattern:

- **Orchestrator Agent**: Coordinates sub-agents and manages user interactions
- **Meal Planning Agent**: Creates meal plans and provides recipe details
- **Shopping Agent**: Generates and organizes shopping lists
- **Travel Agent**: Plans trips and creates itineraries

## Setup

### Prerequisites

- Python 3.10 or higher
- Google AI API key (for Gemini)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

### Running the Application

```bash
python -m src.main
```

## Development

### Project Structure

```
.
├── data_models.py              # Data models and validation
├── memory_bank.py              # User preferences storage
├── session_manager.py          # Session management
├── state_persistence.py        # Pause/resume functionality
├── recipe_tool.py              # Recipe database MCP tool
├── pricing_tool.py             # Pricing API MCP tool
├── travel_tool.py              # Travel search MCP tool
├── meal_planning_agent.py      # Meal planning agent
├── shopping_agent.py           # Shopping list agent
├── travel_agent.py             # Travel planning agent
├── orchestrator_agent.py       # Main orchestrator
├── config.py                   # Configuration
├── app.py                      # Gradio web interface
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Running the Application

```bash
# Run the Gradio web interface
python app.py
```

The application will start on http://localhost:7860

## License

MIT License
