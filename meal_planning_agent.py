"""Meal Planning Agent for generating meal plans and recipes."""
import logging
import uuid
from typing import List, Dict, Optional
from datetime import date, timedelta

from data_models import MealPlan, Meal, Ingredient
from recipe_tool import RecipeDatabaseTool

logger = logging.getLogger(__name__)


class MealPlanningAgent:
    """Agent responsible for creating meal plans based on user preferences.
    
    This agent generates meal plans for specified time periods, applies dietary
    restrictions and preferences, and provides detailed recipe information.
    """
    
    def __init__(self, recipe_tool: RecipeDatabaseTool):
        """Initialize the Meal Planning Agent.
        
        Args:
            recipe_tool: MCP tool for accessing recipe database
        """
        self.recipe_tool = recipe_tool
        logger.info("MealPlanningAgent initialized")
    
    async def generate_meal_plan(
        self,
        user_id: str,
        days: int,
        preferences: Optional[Dict] = None
    ) -> MealPlan:
        """Generate a meal plan for the specified number of days.
        
        Args:
            user_id: User identifier
            days: Number of days to plan for
            preferences: Dictionary containing:
                - dietary_restrictions: List of dietary restrictions
                - cuisine_preferences: List of preferred cuisines
                - meals_per_day: Number of meals per day (default: 3)
                
        Returns:
            MealPlan object with meals for the specified period
            
        Raises:
            ValueError: If days is less than 1
        """
        if days < 1:
            raise ValueError("Days must be at least 1")
        
        preferences = preferences or {}
        dietary_restrictions = preferences.get('dietary_restrictions', [])
        cuisine_preferences = preferences.get('cuisine_preferences', [])
        meals_per_day = preferences.get('meals_per_day', 3)
        
        logger.info(f"Generating {days}-day meal plan for user {user_id}")
        logger.info(f"Dietary restrictions: {dietary_restrictions}")
        logger.info(f"Cuisine preferences: {cuisine_preferences}")
        
        # Calculate date range
        start_date = date.today()
        end_date = start_date + timedelta(days=days - 1)
        
        # Generate meals
        meals = []
        meal_types = self._get_meal_types(meals_per_day)
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            for meal_type in meal_types:
                # Search for recipes matching preferences
                cuisine = None
                if cuisine_preferences:
                    # Rotate through cuisine preferences
                    cuisine = cuisine_preferences[len(meals) % len(cuisine_preferences)]
                
                recipes = await self.recipe_tool.search_recipes(
                    cuisine=cuisine,
                    dietary_restrictions=dietary_restrictions,
                    max_results=5
                )
                
                if not recipes:
                    # Fallback: get random recipes
                    recipes = await self.recipe_tool.get_random_recipes(
                        count=5,
                        dietary_restrictions=dietary_restrictions
                    )
                
                if recipes:
                    # Select a recipe (simple selection for now)
                    recipe = recipes[0]
                    meal = self._recipe_to_meal(recipe, meal_type)
                    meals.append(meal)
        
        # Create meal plan
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        unique_recipes = len(set(m.recipe_id for m in meals))
        
        meal_plan = MealPlan(
            plan_id=plan_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            meals=meals,
            total_recipes=unique_recipes
        )
        
        # Validate the meal plan
        meal_plan.validate()
        
        logger.info(f"Generated meal plan {plan_id} with {len(meals)} meals")
        return meal_plan
    
    async def get_recipe_details(self, recipe_id: str) -> Dict:
        """Get detailed information for a specific recipe.
        
        Args:
            recipe_id: Unique recipe identifier
            
        Returns:
            Dictionary with complete recipe details
            
        Raises:
            ValueError: If recipe not found
        """
        logger.info(f"Fetching details for recipe {recipe_id}")
        recipe = await self.recipe_tool.get_recipe_details(recipe_id)
        return recipe
    
    async def apply_dietary_restrictions(
        self,
        recipes: List[Dict],
        restrictions: List[str]
    ) -> List[Dict]:
        """Filter recipes to match dietary restrictions.
        
        Args:
            recipes: List of recipe dictionaries
            restrictions: List of dietary restrictions (e.g., ["vegetarian", "gluten-free"])
            
        Returns:
            Filtered list of recipes matching all restrictions
        """
        if not restrictions:
            return recipes
        
        logger.info(f"Applying dietary restrictions: {restrictions}")
        
        filtered = []
        for recipe in recipes:
            recipe_tags = [tag.lower() for tag in recipe.get('dietary_tags', [])]
            
            # Check if recipe matches all restrictions
            if all(restriction.lower() in recipe_tags for restriction in restrictions):
                filtered.append(recipe)
        
        logger.info(f"Filtered {len(recipes)} recipes to {len(filtered)} matching restrictions")
        return filtered
    
    async def filter_by_cuisine(
        self,
        recipes: List[Dict],
        cuisine: str
    ) -> List[Dict]:
        """Filter recipes by cuisine type.
        
        Args:
            recipes: List of recipe dictionaries
            cuisine: Cuisine type to filter by
            
        Returns:
            Filtered list of recipes matching cuisine
        """
        logger.info(f"Filtering recipes by cuisine: {cuisine}")
        
        filtered = [r for r in recipes if r['cuisine'].lower() == cuisine.lower()]
        
        logger.info(f"Filtered {len(recipes)} recipes to {len(filtered)} matching cuisine")
        return filtered
    
    def _get_meal_types(self, meals_per_day: int) -> List[str]:
        """Get meal types based on meals per day.
        
        Args:
            meals_per_day: Number of meals per day
            
        Returns:
            List of meal type strings
        """
        if meals_per_day == 1:
            return ['dinner']
        elif meals_per_day == 2:
            return ['lunch', 'dinner']
        elif meals_per_day == 3:
            return ['breakfast', 'lunch', 'dinner']
        else:
            # 4+ meals: add snacks
            return ['breakfast', 'lunch', 'snack', 'dinner']
    
    def _recipe_to_meal(self, recipe: Dict, meal_type: str) -> Meal:
        """Convert a recipe dictionary to a Meal object.
        
        Args:
            recipe: Recipe dictionary from recipe tool
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            
        Returns:
            Meal object
        """
        # Convert ingredients
        ingredients = []
        for ing in recipe.get('ingredients', []):
            ingredient = Ingredient(
                name=ing['name'],
                quantity=ing['quantity'],
                unit=ing['unit']
            )
            ingredients.append(ingredient)
        
        # Create meal
        meal = Meal(
            meal_type=meal_type,
            recipe_id=recipe['id'],
            recipe_name=recipe['name'],
            ingredients=ingredients,
            instructions=recipe.get('instructions', ''),
            prep_time=recipe.get('prep_time', 0),
            cook_time=recipe.get('cook_time', 0)
        )
        
        return meal
