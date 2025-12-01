"""
Script to create a comprehensive Jupyter notebook with all code embedded
"""
import json

# Read all source files
files_to_include = {
    'data_models.py': 'Data Models',
    'memory_bank.py': 'Memory Bank',
    'session_manager.py': 'Session Manager', 
    'state_persistence.py': 'State Persistence',
    'recipe_tool.py': 'Recipe MCP Tool',
    'pricing_tool.py': 'Pricing MCP Tool',
    'travel_tool.py': 'Travel MCP Tool',
    'meal_planning_agent.py': 'Meal Planning Agent',
    'shopping_agent.py': 'Shopping Agent',
    'travel_agent.py': 'Travel Agent',
    'orchestrator_agent.py': 'Orchestrator Agent',
    'app.py': 'Gradio Web Interface'
}

notebook = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.10.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

# Title cell
notebook["cells"].append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# Personal Life Automation Agent System\\n",
        "## Google ADK Capstone Project\\n",
        "\\n",
        "**Complete Implementation in One Notebook**\\n",
        "\\n",
        "This notebook contains all the code for the multi-agent system.\\n",
        "Simply run all cells to launch the Gradio interface!\\n",
        "\\n",
        "### Features:\\n",
        "- 🍽️ Meal Planning with dietary restrictions\\n",
        "- 🛒 Shopping List generation with price estimates\\n",
        "- ✈️ Travel Planning with itineraries\\n",
        "- 💾 Persistent memory for user preferences\\n",
        "- 🤖 Multi-agent coordination"
    ]
})

# Install dependencies cell
notebook["cells"].append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": ["!pip install gradio python-dotenv -q"]
})

# Add each source file as a code cell
for filename, title in files_to_include.items():
    # Add markdown header
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [f"## {title}\\n\\nFrom: `{filename}`"]
    })
    
    # Read file content
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Add code cell
        notebook["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [code]
        })
    except FileNotFoundError:
        print(f"Warning: {filename} not found")

# Add final instruction cell
notebook["cells"].append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 🚀 Application Running!\\n",
        "\\n",
        "The Gradio interface should now be running above.\\n",
        "Click the link to open it in your browser!\\n",
        "\\n",
        "### Available Tabs:\\n",
        "1. **Chat** - Natural language interface\\n",
        "2. **Meal Planning** - Generate custom meal plans\\n",
        "3. **Shopping Lists** - Create organized shopping lists\\n",
        "4. **Travel Planning** - Plan complete trips"
    ]
})

# Write notebook
with open('PersonalLifeAgent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2)

print("✅ Notebook created: PersonalLifeAgent.ipynb")
print("📊 Total cells:", len(notebook["cells"]))
