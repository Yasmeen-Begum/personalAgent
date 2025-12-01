# Project Structure

## Files Overview

### Core Application
- **app.py** - Gradio web interface with 4 tabs (Chat, Meal Planning, Shopping, Travel)
- **config.py** - Configuration management and environment variables

### Data Models
- **data_models.py** - All data models with validation:
  - UserProfile, MealPlan, Meal, Ingredient
  - ShoppingList, ShoppingItem
  - TripPlan, DayPlan, Activity, Restaurant, Accommodation
  - AgentState (for pause/resume)

### Memory & State Management
- **memory_bank.py** - Persistent user preferences and feedback storage
- **session_manager.py** - Conversation state and session lifecycle
- **state_persistence.py** - Task pause/resume functionality

### MCP Tools
- **recipe_tool.py** - Recipe database search with dietary filtering
- **pricing_tool.py** - Grocery price estimates with retry logic
- **travel_tool.py** - Accommodation, activity, and restaurant search

### Agents
- **orchestrator_agent.py** - Main coordinator, intent parsing, agent routing
- **meal_planning_agent.py** - Meal plan generation with preferences
- **shopping_agent.py** - Shopping list creation with consolidation
- **travel_agent.py** - Trip planning with itineraries

### Configuration
- **requirements.txt** - Python dependencies
- **.env.example** - Environment variable template
- **.gitignore** - Git ignore rules

### Documentation
- **README.md** - Setup and usage instructions
- **PROJECT_INFO.md** - Project overview and achievements
- **STRUCTURE.md** - This file

### Data Storage
- **app_memory.json/** - User data storage directory
- **demo_memory.json/** - Demo user data

## File Dependencies

```
app.py
├── orchestrator_agent.py
│   ├── meal_planning_agent.py
│   │   ├── data_models.py
│   │   └── recipe_tool.py
│   ├── shopping_agent.py
│   │   ├── data_models.py
│   │   └── pricing_tool.py
│   ├── travel_agent.py
│   │   ├── data_models.py
│   │   └── travel_tool.py
│   ├── session_manager.py
│   └── memory_bank.py
└── config.py
```

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add GOOGLE_API_KEY

# Run the web interface
python app.py
```

## File Sizes (Approximate)

- data_models.py: ~600 lines
- memory_bank.py: ~200 lines
- session_manager.py: ~150 lines
- state_persistence.py: ~180 lines
- recipe_tool.py: ~220 lines
- pricing_tool.py: ~180 lines
- travel_tool.py: ~240 lines
- meal_planning_agent.py: ~200 lines
- shopping_agent.py: ~180 lines
- travel_agent.py: ~170 lines
- orchestrator_agent.py: ~250 lines
- app.py: ~400 lines
- config.py: ~30 lines

**Total**: ~3,000 lines of production code
