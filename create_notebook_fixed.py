"""
Create a self-contained Jupyter notebook with all code inline (no imports between cells)
"""
import json

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

# Title
notebook["cells"].append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# Personal Life Automation Agent System\\n",
        "## Google ADK Capstone Project\\n",
        "\\n",
        "**Complete Self-Contained Implementation**\\n",
        "\\n",
        "Run all cells sequentially to launch the Gradio interface!\\n",
        "\\n",
        "### Features:\\n",
        "- 🍽️ Meal Planning\\n",
        "- 🛒 Shopping Lists\\n",
        "- ✈️ Travel Planning\\n",
        "- 🤖 Multi-Agent System"
    ]
})

# Install
notebook["cells"].append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": ["!pip install gradio python-dotenv -q"]
})

# Read and combine all files in correct order
files_in_order = [
    ('data_models.py', 'Data Models', True),
    ('memory_bank.py', 'Memory Bank', True),
    ('session_manager.py', 'Session Manager', True),
    ('state_persistence.py', 'State Persistence', True),
    ('recipe_tool.py', 'Recipe Tool', True),
    ('pricing_tool.py', 'Pricing Tool', True),
    ('travel_tool.py', 'Travel Tool', True),
    ('meal_planning_agent.py', 'Meal Planning Agent', True),
    ('shopping_agent.py', 'Shopping Agent', True),
    ('travel_agent.py', 'Travel Agent', True),
    ('orchestrator_agent.py', 'Orchestrator Agent', True),
    ('app.py', 'Gradio Interface', False),  # Don't remove imports from app.py
]

def remove_imports(code, filename):
    """Remove import statements that reference other project files"""
    lines = code.split('\\n')
    filtered_lines = []
    
    for line in lines:
        # Skip imports from our own modules
        if line.strip().startswith('from data_models import'):
            continue
        elif line.strip().startswith('from memory_bank import'):
            continue
        elif line.strip().startswith('from session_manager import'):
            continue
        elif line.strip().startswith('from state_persistence import'):
            continue
        elif line.strip().startswith('from recipe_tool import'):
            continue
        elif line.strip().startswith('from pricing_tool import'):
            continue
        elif line.strip().startswith('from travel_tool import'):
            continue
        elif line.strip().startswith('from meal_planning_agent import'):
            continue
        elif line.strip().startswith('from shopping_agent import'):
            continue
        elif line.strip().startswith('from travel_agent import'):
            continue
        elif line.strip().startswith('from orchestrator_agent import'):
            continue
        elif line.strip().startswith('from config import'):
            continue
        else:
            filtered_lines.append(line)
    
    return '\\n'.join(filtered_lines)

for filename, title, remove_internal_imports in files_in_order:
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [f"## {title}"]
    })
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        if remove_internal_imports:
            code = remove_imports(code, filename)
        
        notebook["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [code]
        })
    except FileNotFoundError:
        print(f"Warning: {filename} not found")

# Final cell
notebook["cells"].append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 🎉 Application Launched!\\n",
        "\\n",
        "The Gradio interface is now running!\\n",
        "Click the link above to access it.\\n",
        "\\n",
        "### Available Features:\\n",
        "1. **Chat Tab** - Natural language interface\\n",
        "2. **Meal Planning Tab** - Generate meal plans\\n",
        "3. **Shopping Lists Tab** - Create shopping lists\\n",
        "4. **Travel Planning Tab** - Plan trips"
    ]
})

with open('PersonalLifeAgent.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2)

print("✅ Fixed notebook created: PersonalLifeAgent.ipynb")
print(f"📊 Total cells: {len(notebook['cells'])}")
