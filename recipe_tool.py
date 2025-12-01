"""Recipe Database MCP Tool for meal planning."""
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RecipeDatabaseTool:
    """MCP tool interface for accessing recipe databases.
    
    This is a stub implementation with mock data for development.
    In production, this would connect to a real recipe API via MCP protocol.
    """
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        """Initialize the recipe database tool.
        
        Args:
            api_key: API key for recipe service (optional for mock)
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.call_count = 0  # For testing tool invocation
        logger.info("RecipeDatabaseTool initialized")
    
    async def search_recipes(
        self,
        query: str = "",
        cuisine: Optional[str] = None,
        dietary_restrictions: Optional[List[str]] = None,
        max_results: int = 10
    ) -> List[Dict]:
        """Search for recipes matching criteria.
        
        Args:
            query: Search query string
            cuisine: Cuisine type filter (e.g., "italian", "mexican")
            dietary_restrictions: List of dietary restrictions (e.g., ["vegetarian", "gluten-free"])
            max_results: Maximum number of results to return
            
        Returns:
            List of recipe dictionaries with id, name, cuisine, ingredients, etc.
            
        Raises:
            Exception: If API call fails after retries
        """
        self.call_count += 1
        logger.info(f"Searching recipes: query='{query}', cuisine={cuisine}, restrictions={dietary_restrictions}")
        
        # Simulate API call with retry logic
        for attempt in range(self.max_retries):
            try:
                # Mock recipe data
                recipes = self._get_mock_recipes()
                
                # Filter by cuisine
                if cuisine:
                    cuisine_filtered = [r for r in recipes if r['cuisine'].lower() == cuisine.lower()]
                    if cuisine_filtered:
                        recipes = cuisine_filtered
                
                # Filter by dietary restrictions (flexible matching)
                if dietary_restrictions:
                    filtered = [r for r in recipes if self._matches_restrictions(r, dietary_restrictions)]
                    # If no exact matches, return all recipes (flexible fallback)
                    if filtered:
                        recipes = filtered
                    else:
                        logger.warning(f"No recipes match restrictions {dietary_restrictions}, returning all available")
                
                # Filter by query
                if query:
                    query_filtered = [r for r in recipes if query.lower() in r['name'].lower()]
                    if query_filtered:
                        recipes = query_filtered
                
                return recipes[:max_results]
                
            except Exception as e:
                logger.warning(f"Recipe search attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Recipe search failed after all retries")
                    raise
    
    async def get_recipe_details(self, recipe_id: str) -> Dict:
        """Get detailed information for a specific recipe.
        
        Args:
            recipe_id: Unique recipe identifier
            
        Returns:
            Recipe dictionary with complete details including instructions
            
        Raises:
            ValueError: If recipe not found
            Exception: If API call fails
        """
        self.call_count += 1
        logger.info(f"Fetching recipe details for: {recipe_id}")
        
        recipes = self._get_mock_recipes()
        recipe = next((r for r in recipes if r['id'] == recipe_id), None)
        
        if not recipe:
            raise ValueError(f"Recipe not found: {recipe_id}")
        
        return recipe
    
    async def get_random_recipes(
        self,
        count: int = 5,
        cuisine: Optional[str] = None,
        dietary_restrictions: Optional[List[str]] = None
    ) -> List[Dict]:
        """Get random recipes matching criteria.
        
        Args:
            count: Number of random recipes to return
            cuisine: Optional cuisine filter
            dietary_restrictions: Optional dietary restriction filters
            
        Returns:
            List of random recipe dictionaries
        """
        self.call_count += 1
        logger.info(f"Getting {count} random recipes")
        
        import random
        recipes = self._get_mock_recipes()
        
        # Apply filters (flexible matching)
        if cuisine:
            cuisine_filtered = [r for r in recipes if r['cuisine'].lower() == cuisine.lower()]
            if cuisine_filtered:
                recipes = cuisine_filtered
        
        if dietary_restrictions:
            filtered = [r for r in recipes if self._matches_restrictions(r, dietary_restrictions)]
            # If no exact matches, use all recipes (flexible fallback)
            if filtered:
                recipes = filtered
            else:
                logger.warning(f"No recipes match restrictions {dietary_restrictions}, using all available")
        
        # Return random selection
        return random.sample(recipes, min(count, len(recipes)))
    
    def _matches_restrictions(self, recipe: Dict, restrictions: List[str]) -> bool:
        """Check if recipe matches dietary restrictions.
        
        Args:
            recipe: Recipe dictionary
            restrictions: List of dietary restrictions
            
        Returns:
            True if recipe matches all restrictions
        """
        recipe_tags = [tag.lower() for tag in recipe.get('dietary_tags', [])]
        return all(restriction.lower() in recipe_tags for restriction in restrictions)
    
    def _get_mock_recipes(self) -> List[Dict]:
        """Get mock recipe data for development.
        
        Returns:
            List of mock recipe dictionaries
        """
        return [
            {
                'id': 'recipe_001',
                'name': 'Vegetarian Pasta Primavera',
                'cuisine': 'Italian',
                'dietary_tags': ['vegetarian', 'dairy'],
                'prep_time': 15,
                'cook_time': 20,
                'servings': 4,
                'ingredients': [
                    {'name': 'pasta', 'quantity': 1, 'unit': 'lb'},
                    {'name': 'bell peppers', 'quantity': 2, 'unit': 'whole'},
                    {'name': 'zucchini', 'quantity': 1, 'unit': 'whole'},
                    {'name': 'olive oil', 'quantity': 2, 'unit': 'tbsp'},
                    {'name': 'parmesan cheese', 'quantity': 0.5, 'unit': 'cup'},
                ],
                'instructions': '1. Cook pasta according to package. 2. Sauté vegetables in olive oil. 3. Combine pasta and vegetables. 4. Top with parmesan.',
                'rating': 4.5
            },
            {
                'id': 'recipe_002',
                'name': 'Grilled Chicken Tacos',
                'cuisine': 'Mexican',
                'dietary_tags': ['gluten-free'],
                'prep_time': 20,
                'cook_time': 15,
                'servings': 4,
                'ingredients': [
                    {'name': 'chicken breast', 'quantity': 1.5, 'unit': 'lb'},
                    {'name': 'corn tortillas', 'quantity': 12, 'unit': 'whole'},
                    {'name': 'avocado', 'quantity': 2, 'unit': 'whole'},
                    {'name': 'lime', 'quantity': 2, 'unit': 'whole'},
                    {'name': 'cilantro', 'quantity': 0.5, 'unit': 'cup'},
                ],
                'instructions': '1. Season and grill chicken. 2. Warm tortillas. 3. Slice chicken and avocado. 4. Assemble tacos with toppings.',
                'rating': 4.7
            },
            {
                'id': 'recipe_003',
                'name': 'Vegan Buddha Bowl',
                'cuisine': 'Asian',
                'dietary_tags': ['vegan', 'gluten-free'],
                'prep_time': 25,
                'cook_time': 30,
                'servings': 2,
                'ingredients': [
                    {'name': 'quinoa', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'chickpeas', 'quantity': 1, 'unit': 'can'},
                    {'name': 'sweet potato', 'quantity': 1, 'unit': 'whole'},
                    {'name': 'kale', 'quantity': 2, 'unit': 'cups'},
                    {'name': 'tahini', 'quantity': 0.25, 'unit': 'cup'},
                ],
                'instructions': '1. Cook quinoa. 2. Roast sweet potato and chickpeas. 3. Massage kale. 4. Assemble bowl and drizzle with tahini.',
                'rating': 4.8
            },
            {
                'id': 'recipe_004',
                'name': 'Classic Beef Burger',
                'cuisine': 'American',
                'dietary_tags': [],
                'prep_time': 10,
                'cook_time': 15,
                'servings': 4,
                'ingredients': [
                    {'name': 'ground beef', 'quantity': 1.5, 'unit': 'lb'},
                    {'name': 'burger buns', 'quantity': 4, 'unit': 'whole'},
                    {'name': 'lettuce', 'quantity': 4, 'unit': 'leaves'},
                    {'name': 'tomato', 'quantity': 1, 'unit': 'whole'},
                    {'name': 'cheddar cheese', 'quantity': 4, 'unit': 'slices'},
                ],
                'instructions': '1. Form beef into patties. 2. Grill burgers to desired doneness. 3. Toast buns. 4. Assemble burgers with toppings.',
                'rating': 4.6
            },
            {
                'id': 'recipe_005',
                'name': 'Mediterranean Salad',
                'cuisine': 'Mediterranean',
                'dietary_tags': ['vegetarian', 'gluten-free'],
                'prep_time': 15,
                'cook_time': 0,
                'servings': 4,
                'ingredients': [
                    {'name': 'mixed greens', 'quantity': 6, 'unit': 'cups'},
                    {'name': 'cucumber', 'quantity': 1, 'unit': 'whole'},
                    {'name': 'cherry tomatoes', 'quantity': 2, 'unit': 'cups'},
                    {'name': 'feta cheese', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'olives', 'quantity': 0.5, 'unit': 'cup'},
                    {'name': 'olive oil', 'quantity': 3, 'unit': 'tbsp'},
                ],
                'instructions': '1. Chop vegetables. 2. Combine all ingredients in bowl. 3. Drizzle with olive oil and lemon juice. 4. Toss and serve.',
                'rating': 4.4
            },
            {
                'id': 'recipe_006',
                'name': 'Teriyaki Salmon',
                'cuisine': 'Japanese',
                'dietary_tags': ['gluten-free', 'pescatarian'],
                'prep_time': 10,
                'cook_time': 20,
                'servings': 2,
                'ingredients': [
                    {'name': 'salmon fillets', 'quantity': 2, 'unit': 'whole'},
                    {'name': 'teriyaki sauce', 'quantity': 0.25, 'unit': 'cup'},
                    {'name': 'rice', 'quantity': 1, 'unit': 'cup'},
                    {'name': 'broccoli', 'quantity': 2, 'unit': 'cups'},
                    {'name': 'sesame seeds', 'quantity': 1, 'unit': 'tbsp'},
                ],
                'instructions': '1. Marinate salmon in teriyaki. 2. Cook rice. 3. Bake salmon at 400°F for 15 min. 4. Steam broccoli. 5. Serve with sesame seeds.',
                'rating': 4.9
            }
        ]
