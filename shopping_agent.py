"""Shopping Agent for generating and managing shopping lists."""
import logging
import uuid
from typing import List, Dict, Optional
from datetime import date
from collections import defaultdict

from data_models import ShoppingList, ShoppingItem, MealPlan, Ingredient
from pricing_tool import PricingAPITool

logger = logging.getLogger(__name__)


class ShoppingAgent:
    """Agent responsible for generating shopping lists from meal plans.
    
    This agent extracts ingredients, consolidates quantities, organizes by
    category, and integrates with pricing APIs.
    """
    
    # Category mapping for common ingredients
    CATEGORY_MAP = {
        'pasta': 'Grains & Pasta',
        'rice': 'Grains & Pasta',
        'quinoa': 'Grains & Pasta',
        'bread': 'Bakery',
        'burger buns': 'Bakery',
        'corn tortillas': 'Bakery',
        'chicken breast': 'Meat & Poultry',
        'ground beef': 'Meat & Poultry',
        'salmon fillets': 'Seafood',
        'eggs': 'Dairy & Eggs',
        'milk': 'Dairy & Eggs',
        'butter': 'Dairy & Eggs',
        'cheddar cheese': 'Dairy & Eggs',
        'parmesan cheese': 'Dairy & Eggs',
        'feta cheese': 'Dairy & Eggs',
        'bell peppers': 'Produce',
        'zucchini': 'Produce',
        'avocado': 'Produce',
        'lime': 'Produce',
        'cilantro': 'Produce',
        'sweet potato': 'Produce',
        'kale': 'Produce',
        'lettuce': 'Produce',
        'tomato': 'Produce',
        'cucumber': 'Produce',
        'cherry tomatoes': 'Produce',
        'mixed greens': 'Produce',
        'broccoli': 'Produce',
        'onion': 'Produce',
        'garlic': 'Produce',
        'carrots': 'Produce',
        'potatoes': 'Produce',
        'chickpeas': 'Canned Goods',
        'olives': 'Canned Goods',
        'olive oil': 'Oils & Condiments',
        'teriyaki sauce': 'Oils & Condiments',
        'tahini': 'Oils & Condiments',
        'sesame seeds': 'Spices & Seasonings',
    }
    
    def __init__(self, pricing_tool: PricingAPITool):
        """Initialize the Shopping Agent.
        
        Args:
            pricing_tool: MCP tool for accessing pricing information
        """
        self.pricing_tool = pricing_tool
        logger.info("ShoppingAgent initialized")
    
    async def generate_shopping_list(
        self,
        user_id: str,
        meal_plan: MealPlan,
        pantry: Optional[List[str]] = None
    ) -> ShoppingList:
        """Generate a shopping list from a meal plan.
        
        Args:
            user_id: User identifier
            meal_plan: MealPlan object containing meals
            pantry: List of items already in pantry (to exclude)
            
        Returns:
            ShoppingList object with consolidated and categorized items
        """
        pantry = pantry or []
        logger.info(f"Generating shopping list for meal plan {meal_plan.plan_id}")
        logger.info(f"Pantry items to exclude: {pantry}")
        
        # Extract all ingredients from meals
        all_ingredients = []
        for meal in meal_plan.meals:
            all_ingredients.extend(meal.ingredients)
        
        logger.info(f"Extracted {len(all_ingredients)} ingredients from {len(meal_plan.meals)} meals")
        
        # Consolidate duplicate ingredients
        consolidated = await self.consolidate_ingredients(all_ingredients)
        
        # Filter out pantry items
        filtered = [ing for ing in consolidated if ing['name'].lower() not in [p.lower() for p in pantry]]
        logger.info(f"Filtered to {len(filtered)} items after removing pantry items")
        
        # Get price estimates
        prices = await self.get_price_estimates(filtered)
        
        # Create shopping items with categories
        shopping_items = []
        for item_data in filtered:
            price_info = next((p for p in prices if p['item_name'] == item_data['name']), None)
            estimated_price = price_info['total_price'] if price_info else 0.0
            
            category = self._categorize_item(item_data['name'])
            
            shopping_item = ShoppingItem(
                name=item_data['name'],
                quantity=item_data['quantity'],
                unit=item_data['unit'],
                category=category,
                estimated_price=estimated_price
            )
            shopping_items.append(shopping_item)
        
        # Organize by category
        categories = await self.organize_by_category(shopping_items)
        
        # Calculate total
        estimated_total = sum(item.estimated_price for item in shopping_items)
        
        # Create shopping list
        list_id = f"list_{uuid.uuid4().hex[:8]}"
        shopping_list = ShoppingList(
            list_id=list_id,
            user_id=user_id,
            created_date=date.today(),
            items=shopping_items,
            categories=categories,
            estimated_total=round(estimated_total, 2)
        )
        
        # Validate
        shopping_list.validate()
        
        logger.info(f"Generated shopping list {list_id} with {len(shopping_items)} items, total: ${estimated_total:.2f}")
        return shopping_list
    
    async def consolidate_ingredients(
        self,
        ingredients: List[Ingredient]
    ) -> List[Dict]:
        """Consolidate duplicate ingredients with correct quantity summing.
        
        Args:
            ingredients: List of Ingredient objects
            
        Returns:
            List of consolidated ingredient dictionaries
        """
        logger.info(f"Consolidating {len(ingredients)} ingredients")
        
        # Group by name and unit
        grouped = defaultdict(lambda: {'quantity': 0.0, 'unit': '', 'name': ''})
        
        for ing in ingredients:
            key = (ing.name.lower(), ing.unit.lower())
            grouped[key]['name'] = ing.name
            grouped[key]['unit'] = ing.unit
            grouped[key]['quantity'] += ing.quantity
        
        # Convert to list
        consolidated = [
            {
                'name': data['name'],
                'quantity': round(data['quantity'], 2),
                'unit': data['unit']
            }
            for data in grouped.values()
        ]
        
        logger.info(f"Consolidated to {len(consolidated)} unique items")
        return consolidated
    
    async def organize_by_category(
        self,
        items: List[ShoppingItem]
    ) -> Dict[str, List[ShoppingItem]]:
        """Organize shopping items by grocery store category.
        
        Args:
            items: List of ShoppingItem objects
            
        Returns:
            Dictionary mapping category names to lists of items
        """
        logger.info(f"Organizing {len(items)} items by category")
        
        categories = defaultdict(list)
        for item in items:
            categories[item.category].append(item)
        
        # Sort items within each category by name
        for category in categories:
            categories[category].sort(key=lambda x: x.name)
        
        logger.info(f"Organized into {len(categories)} categories")
        return dict(categories)
    
    async def get_price_estimates(
        self,
        items: List[Dict]
    ) -> List[Dict]:
        """Get price estimates for shopping items.
        
        Args:
            items: List of item dictionaries with name, quantity, unit
            
        Returns:
            List of price information dictionaries
        """
        logger.info(f"Getting price estimates for {len(items)} items")
        
        prices = await self.pricing_tool.get_bulk_prices(items)
        
        return prices
    
    def _categorize_item(self, item_name: str) -> str:
        """Categorize an item by name.
        
        Args:
            item_name: Name of the item
            
        Returns:
            Category name
        """
        item_lower = item_name.lower()
        
        # Check exact matches first
        if item_lower in self.CATEGORY_MAP:
            return self.CATEGORY_MAP[item_lower]
        
        # Check partial matches
        for key, category in self.CATEGORY_MAP.items():
            if key in item_lower or item_lower in key:
                return category
        
        # Default category
        return 'Other'
