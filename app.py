"""Gradio web interface for the Personal Life Automation Agent System."""
import gradio as gr
import asyncio
import logging
from datetime import date, timedelta
import json

from meal_planning_agent import MealPlanningAgent
from shopping_agent import ShoppingAgent
from travel_agent import TravelAgent
from orchestrator_agent import OrchestratorAgent
from memory_bank import MemoryBank
from session_manager import SessionManager, InMemorySessionService
from recipe_tool import RecipeDatabaseTool
from pricing_tool import PricingAPITool
from travel_tool import TravelSearchTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize all components
recipe_tool = RecipeDatabaseTool()
pricing_tool = PricingAPITool()
travel_tool = TravelSearchTool()

meal_agent = MealPlanningAgent(recipe_tool)
shopping_agent = ShoppingAgent(pricing_tool)
travel_agent = TravelAgent(travel_tool)

memory_bank = MemoryBank("app_memory.json")
session_service = InMemorySessionService()
session_manager = SessionManager(session_service, memory_bank)

orchestrator = OrchestratorAgent(
    meal_agent=meal_agent,
    shopping_agent=shopping_agent,
    travel_agent=travel_agent,
    session_manager=session_manager,
    memory_bank=memory_bank
)

# Store session IDs per user
user_sessions = {}


async def chat_with_agent(message, user_id="default_user"):
    """Process a chat message with the orchestrator agent."""
    try:
        # Get or create session for user
        session_id = user_sessions.get(user_id)
        
        response = await orchestrator.process_message(
            user_id=user_id,
            message=message,
            session_id=session_id
        )
        
        # Store session ID
        user_sessions[user_id] = response['session_id']
        
        return response['response']
    except Exception as e:
        return f"Error: {str(e)}"


async def generate_meal_plan(days, dietary_restrictions, cuisine_preferences, meals_per_day):
    """Generate a meal plan."""
    try:
        restrictions = [r.strip() for r in dietary_restrictions.split(',')] if dietary_restrictions else []
        cuisines = [c.strip() for c in cuisine_preferences.split(',')] if cuisine_preferences else []
        
        preferences = {
            'dietary_restrictions': restrictions,
            'cuisine_preferences': cuisines,
            'meals_per_day': int(meals_per_day)
        }
        
        meal_plan = await meal_agent.generate_meal_plan(
            user_id='gradio_user',
            days=int(days),
            preferences=preferences
        )
        
        # Format output
        output = f"# Meal Plan: {meal_plan.plan_id}\n\n"
        output += f"**Duration:** {meal_plan.duration_days()} days\n"
        output += f"**Total Meals:** {len(meal_plan.meals)}\n"
        output += f"**Unique Recipes:** {meal_plan.total_recipes}\n\n"
        output += "## Meals:\n\n"
        
        current_day = 1
        for i, meal in enumerate(meal_plan.meals):
            if i % int(meals_per_day) == 0:
                output += f"\n### Day {current_day}\n"
                current_day += 1
            
            output += f"- **{meal.meal_type.title()}:** {meal.recipe_name}\n"
            output += f"  - Prep: {meal.prep_time}min, Cook: {meal.cook_time}min\n"
            output += f"  - Ingredients: {len(meal.ingredients)}\n"
        
        return output
    except Exception as e:
        return f"Error generating meal plan: {str(e)}"


async def generate_shopping_list(days, dietary_restrictions, pantry_items):
    """Generate a shopping list from a meal plan."""
    try:
        restrictions = [r.strip() for r in dietary_restrictions.split(',')] if dietary_restrictions else []
        pantry = [p.strip() for p in pantry_items.split(',')] if pantry_items else []
        
        # First generate meal plan
        preferences = {
            'dietary_restrictions': restrictions,
            'cuisine_preferences': [],
            'meals_per_day': 3
        }
        
        logger.info(f"Generating meal plan for {days} days with preferences: {preferences}")
        
        meal_plan = await meal_agent.generate_meal_plan(
            user_id='gradio_user',
            days=int(days),
            preferences=preferences
        )
        
        logger.info(f"Meal plan generated with {len(meal_plan.meals)} meals")
        
        # Generate shopping list
        shopping_list = await shopping_agent.generate_shopping_list(
            user_id='gradio_user',
            meal_plan=meal_plan,
            pantry=pantry
        )
        
        # Format output
        output = f"# Shopping List: {shopping_list.list_id}\n\n"
        output += f"**Generated from:** {days}-day meal plan\n"
        output += f"**Total Items:** {len(shopping_list.items)}\n"
        output += f"**Categories:** {len(shopping_list.categories)}\n"
        output += f"**Estimated Total:** ${shopping_list.estimated_total:.2f}\n\n"
        
        for category, items in shopping_list.categories.items():
            output += f"\n## {category}\n"
            for item in items:
                output += f"- {item.name}: {item.quantity} {item.unit} (${item.estimated_price:.2f})\n"
        
        return output
    except Exception as e:
        logger.error(f"Error generating shopping list: {str(e)}", exc_info=True)
        return f"Error generating shopping list: {str(e)}\n\nPlease try again or check the logs for more details."


async def plan_trip(destination, days, budget, interests, accommodation_type):
    """Plan a trip."""
    try:
        start_date = date.today() + timedelta(days=30)
        end_date = start_date + timedelta(days=int(days) - 1)
        
        interest_list = [i.strip() for i in interests.split(',')] if interests else []
        
        preferences = {
            'interests': interest_list,
            'accommodation_type': accommodation_type if accommodation_type != "Any" else None,
            'budget_per_night': float(budget) / int(days) if budget else None
        }
        
        trip_plan = await travel_agent.plan_trip(
            user_id='gradio_user',
            destination=destination,
            dates=(start_date.isoformat(), end_date.isoformat()),
            budget=float(budget),
            preferences=preferences
        )
        
        # Format output
        output = f"# Trip Plan: {trip_plan.trip_id}\n\n"
        output += f"**Destination:** {trip_plan.destination}\n"
        output += f"**Duration:** {trip_plan.duration_days()} days\n"
        output += f"**Dates:** {trip_plan.start_date} to {trip_plan.end_date}\n\n"
        
        output += f"## Accommodation\n"
        output += f"**{trip_plan.accommodation.name}** ({trip_plan.accommodation.type})\n"
        output += f"- Location: {trip_plan.accommodation.location}\n"
        output += f"- Cost per night: ${trip_plan.accommodation.cost_per_night:.2f}\n"
        output += f"- Total: ${trip_plan.accommodation.total_cost:.2f}\n"
        output += f"- Amenities: {', '.join(trip_plan.accommodation.amenities)}\n\n"
        
        output += f"## Daily Itinerary\n\n"
        for day in trip_plan.itinerary:
            output += f"### Day {day.day_number} - {day.date}\n"
            
            output += f"\n**Activities:**\n"
            for activity in day.activities:
                output += f"- {activity.name} ({activity.duration}min, ${activity.estimated_cost:.2f})\n"
                output += f"  {activity.description}\n"
            
            output += f"\n**Dining:**\n"
            for restaurant in day.meals:
                output += f"- {restaurant.name} ({restaurant.cuisine_type}, ${restaurant.estimated_cost:.2f})\n"
            
            output += f"\n**Daily Cost:** ${day.total_estimated_cost():.2f}\n\n"
        
        output += f"\n## Total Estimated Cost: ${trip_plan.estimated_cost:.2f}\n"
        
        return output
    except Exception as e:
        return f"Error planning trip: {str(e)}"


async def save_preferences(dietary, cuisine, budget_daily, budget_accommodation, travel_interests):
    """Save user preferences."""
    try:
        user_id = 'gradio_user'
        
        if dietary:
            await memory_bank.save_preference(
                user_id, 
                'dietary_restrictions', 
                [d.strip() for d in dietary.split(',')]
            )
        
        if cuisine:
            await memory_bank.save_preference(
                user_id,
                'cuisine_preferences',
                [c.strip() for c in cuisine.split(',')]
            )
        
        if budget_daily or budget_accommodation:
            budget_prefs = {}
            if budget_daily:
                budget_prefs['daily'] = float(budget_daily)
            if budget_accommodation:
                budget_prefs['accommodation'] = float(budget_accommodation)
            await memory_bank.save_preference(user_id, 'budget_preferences', budget_prefs)
        
        if travel_interests:
            await memory_bank.save_preference(
                user_id,
                'travel_interests',
                [t.strip() for t in travel_interests.split(',')]
            )
        
        return "Preferences saved successfully!"
    except Exception as e:
        return f"Error saving preferences: {str(e)}"


async def load_preferences():
    """Load user preferences."""
    try:
        prefs = await memory_bank.get_all_preferences('gradio_user')
        
        output = "# Your Preferences\n\n"
        
        if prefs.get('dietary_restrictions'):
            output += f"**Dietary Restrictions:** {', '.join(prefs['dietary_restrictions'])}\n"
        
        if prefs.get('cuisine_preferences'):
            output += f"**Cuisine Preferences:** {', '.join(prefs['cuisine_preferences'])}\n"
        
        if prefs.get('budget_preferences'):
            budget = prefs['budget_preferences']
            output += f"**Budget Preferences:**\n"
            if 'daily' in budget:
                output += f"  - Daily: ${budget['daily']:.2f}\n"
            if 'accommodation' in budget:
                output += f"  - Accommodation: ${budget['accommodation']:.2f}\n"
        
        if prefs.get('travel_interests'):
            output += f"**Travel Interests:** {', '.join(prefs['travel_interests'])}\n"
        
        if not prefs:
            output += "*No preferences saved yet.*\n"
        
        return output
    except Exception as e:
        return f"Error loading preferences: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Personal Life Automation Agent") as app:
    gr.Markdown("""
    # Personal Life Automation Agent System
    ### Google ADK Capstone Project
    
    An intelligent multi-agent system to help you with meal planning, shopping lists, and travel planning.
    """)
    
    with gr.Tabs():
        # Chat Tab
        with gr.Tab("Chat with Agent"):
            gr.Markdown("### Natural Language Interface")
            gr.Markdown("Ask me anything! I can help with meal planning, shopping lists, or travel planning.")
            
            chat_input = gr.Textbox(
                label="Your Message",
                placeholder="e.g., 'Create a 5-day vegetarian meal plan' or 'Plan a trip to Paris'",
                lines=2
            )
            chat_output = gr.Textbox(label="Agent Response", lines=10)
            chat_btn = gr.Button("Send Message", variant="primary")
            
            chat_btn.click(
                fn=lambda msg: asyncio.run(chat_with_agent(msg)),
                inputs=[chat_input],
                outputs=[chat_output]
            )
            
            gr.Examples(
                examples=[
                    ["Create a 3-day meal plan with vegetarian options"],
                    ["Plan a trip to Tokyo for 5 days"],
                    ["I need a shopping list for this week"],
                    ["What can you help me with?"]
                ],
                inputs=[chat_input]
            )
        
        # Meal Planning Tab
        with gr.Tab("Meal Planning"):
            gr.Markdown("### Generate Custom Meal Plans")
            
            with gr.Row():
                meal_days = gr.Slider(1, 14, value=7, step=1, label="Number of Days")
                meal_per_day = gr.Slider(1, 4, value=3, step=1, label="Meals per Day")
            
            meal_dietary = gr.Textbox(
                label="Dietary Restrictions (comma-separated)",
                placeholder="e.g., vegetarian, gluten-free, vegan"
            )
            meal_cuisine = gr.Textbox(
                label="Cuisine Preferences (comma-separated)",
                placeholder="e.g., Italian, Mexican, Japanese"
            )
            
            meal_output = gr.Markdown(label="Meal Plan")
            meal_btn = gr.Button("Generate Meal Plan", variant="primary")
            
            meal_btn.click(
                fn=lambda d, dr, cp, mpd: asyncio.run(generate_meal_plan(d, dr, cp, mpd)),
                inputs=[meal_days, meal_dietary, meal_cuisine, meal_per_day],
                outputs=[meal_output]
            )
        
        # Shopping Tab
        with gr.Tab("Shopping Lists"):
            gr.Markdown("### Generate Shopping Lists from Meal Plans")
            
            shop_days = gr.Slider(1, 7, value=3, step=1, label="Days of Meals")
            shop_dietary = gr.Textbox(
                label="Dietary Restrictions (comma-separated)",
                placeholder="e.g., vegetarian, gluten-free"
            )
            shop_pantry = gr.Textbox(
                label="Pantry Items to Exclude (comma-separated)",
                placeholder="e.g., salt, pepper, olive oil"
            )
            
            shop_output = gr.Markdown(label="Shopping List")
            shop_btn = gr.Button("Generate Shopping List", variant="primary")
            
            shop_btn.click(
                fn=lambda d, dr, p: asyncio.run(generate_shopping_list(d, dr, p)),
                inputs=[shop_days, shop_dietary, shop_pantry],
                outputs=[shop_output]
            )
        
        # Travel Tab
        with gr.Tab("Travel Planning"):
            gr.Markdown("### Plan Your Next Trip")
            
            with gr.Row():
                travel_dest = gr.Textbox(label="Destination", placeholder="e.g., Paris, Tokyo, New York")
                travel_days = gr.Slider(1, 14, value=5, step=1, label="Number of Days")
            
            with gr.Row():
                travel_budget = gr.Number(label="Total Budget ($)", value=2000)
                travel_accommodation = gr.Dropdown(
                    choices=["Any", "hotel", "airbnb", "hostel"],
                    value="Any",
                    label="Accommodation Type"
                )
            
            travel_interests = gr.Textbox(
                label="Interests (comma-separated)",
                placeholder="e.g., museums, food, outdoor, shopping"
            )
            
            travel_output = gr.Markdown(label="Trip Plan")
            travel_btn = gr.Button("Plan Trip", variant="primary")
            
            travel_btn.click(
                fn=lambda dest, days, budget, interests, acc: asyncio.run(
                    plan_trip(dest, days, budget, interests, acc)
                ),
                inputs=[travel_dest, travel_days, travel_budget, travel_interests, travel_accommodation],
                outputs=[travel_output]
            )
    
   

if __name__ == "__main__":
    print("Starting Personal Life Automation Agent System...")
    print("Opening Gradio interface...")
    app.launch(share=False, server_name="0.0.0.0", server_port=7860)
