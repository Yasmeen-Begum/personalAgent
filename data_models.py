"""Data models for the Personal Life Automation Agent System."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date, datetime
from enum import Enum


class MealType(str, Enum):
    """Enum for meal types."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class TaskStatus(str, Enum):
    """Enum for task status."""
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class UserProfile:
    """User profile with preferences and restrictions."""
    user_id: str
    dietary_restrictions: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    cuisine_preferences: List[str] = field(default_factory=list)
    pantry_items: List[str] = field(default_factory=list)
    budget_preferences: Dict = field(default_factory=dict)
    travel_interests: List[str] = field(default_factory=list)
    
    def validate(self) -> bool:
        """Validate user profile data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.user_id:
            raise ValueError("user_id is required")
        return True


@dataclass
class Ingredient:
    """Ingredient with quantity and unit."""
    name: str
    quantity: float
    unit: str
    
    def validate(self) -> bool:
        """Validate ingredient data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.name:
            raise ValueError("Ingredient name is required")
        if self.quantity <= 0:
            raise ValueError("Ingredient quantity must be positive")
        if not self.unit:
            raise ValueError("Ingredient unit is required")
        return True


@dataclass
class Meal:
    """Meal with recipe details."""
    meal_type: str  # breakfast, lunch, dinner, snack
    recipe_id: str
    recipe_name: str
    ingredients: List[Ingredient]
    instructions: str
    prep_time: int  # minutes
    cook_time: int  # minutes
    
    def validate(self) -> bool:
        """Validate meal data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if self.meal_type not in [mt.value for mt in MealType]:
            raise ValueError(f"Invalid meal_type: {self.meal_type}")
        if not self.recipe_id:
            raise ValueError("recipe_id is required")
        if not self.recipe_name:
            raise ValueError("recipe_name is required")
        if not self.ingredients:
            raise ValueError("Meal must have at least one ingredient")
        if not self.instructions:
            raise ValueError("instructions are required")
        if self.prep_time < 0:
            raise ValueError("prep_time must be non-negative")
        if self.cook_time < 0:
            raise ValueError("cook_time must be non-negative")
        
        # Validate all ingredients
        for ingredient in self.ingredients:
            ingredient.validate()
        
        return True
    
    def total_time(self) -> int:
        """Calculate total cooking time.
        
        Returns:
            Total time in minutes
        """
        return self.prep_time + self.cook_time


@dataclass
class MealPlan:
    """Meal plan for a time period."""
    plan_id: str
    user_id: str
    start_date: date
    end_date: date
    meals: List[Meal]
    total_recipes: int
    
    def validate(self) -> bool:
        """Validate meal plan data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.plan_id:
            raise ValueError("plan_id is required")
        if not self.user_id:
            raise ValueError("user_id is required")
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")
        if not self.meals:
            raise ValueError("Meal plan must have at least one meal")
        if self.total_recipes != len(set(m.recipe_id for m in self.meals)):
            raise ValueError("total_recipes must match unique recipe count")
        
        # Validate all meals
        for meal in self.meals:
            meal.validate()
        
        return True
    
    def duration_days(self) -> int:
        """Calculate duration in days.
        
        Returns:
            Number of days in the meal plan
        """
        return (self.end_date - self.start_date).days + 1


@dataclass
class ShoppingItem:
    """Shopping list item."""
    name: str
    quantity: float
    unit: str
    category: str
    estimated_price: float = 0.0
    
    def validate(self) -> bool:
        """Validate shopping item data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.name:
            raise ValueError("Item name is required")
        if self.quantity <= 0:
            raise ValueError("Item quantity must be positive")
        if not self.unit:
            raise ValueError("Item unit is required")
        if not self.category:
            raise ValueError("Item category is required")
        if self.estimated_price < 0:
            raise ValueError("estimated_price must be non-negative")
        return True


@dataclass
class ShoppingList:
    """Shopping list with categorized items."""
    list_id: str
    user_id: str
    created_date: date
    items: List[ShoppingItem]
    categories: Dict[str, List[ShoppingItem]]
    estimated_total: float
    
    def validate(self) -> bool:
        """Validate shopping list data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.list_id:
            raise ValueError("list_id is required")
        if not self.user_id:
            raise ValueError("user_id is required")
        if not self.items:
            raise ValueError("Shopping list must have at least one item")
        if self.estimated_total < 0:
            raise ValueError("estimated_total must be non-negative")
        
        # Validate all items
        for item in self.items:
            item.validate()
        
        # Validate categories contain all items
        categorized_items = []
        for category_items in self.categories.values():
            categorized_items.extend(category_items)
        
        if len(categorized_items) != len(self.items):
            raise ValueError("All items must be categorized")
        
        return True
    
    def item_count(self) -> int:
        """Get total number of items.
        
        Returns:
            Number of items in the list
        """
        return len(self.items)


@dataclass
class Activity:
    """Activity for a trip itinerary."""
    name: str
    description: str
    duration: int  # minutes
    estimated_cost: float = 0.0
    location: str = ""
    
    def validate(self) -> bool:
        """Validate activity data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.name:
            raise ValueError("Activity name is required")
        if self.duration <= 0:
            raise ValueError("Activity duration must be positive")
        if self.estimated_cost < 0:
            raise ValueError("estimated_cost must be non-negative")
        return True


@dataclass
class Restaurant:
    """Restaurant recommendation."""
    name: str
    cuisine_type: str
    estimated_cost: float
    location: str = ""
    
    def validate(self) -> bool:
        """Validate restaurant data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.name:
            raise ValueError("Restaurant name is required")
        if not self.cuisine_type:
            raise ValueError("cuisine_type is required")
        if self.estimated_cost < 0:
            raise ValueError("estimated_cost must be non-negative")
        return True


@dataclass
class Accommodation:
    """Accommodation details."""
    name: str
    type: str  # hotel, airbnb, hostel, etc.
    location: str
    cost_per_night: float
    total_cost: float
    amenities: List[str] = field(default_factory=list)
    
    def validate(self) -> bool:
        """Validate accommodation data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.name:
            raise ValueError("Accommodation name is required")
        if not self.type:
            raise ValueError("Accommodation type is required")
        if not self.location:
            raise ValueError("Accommodation location is required")
        if self.cost_per_night < 0:
            raise ValueError("cost_per_night must be non-negative")
        if self.total_cost < 0:
            raise ValueError("total_cost must be non-negative")
        return True


@dataclass
class DayPlan:
    """Daily itinerary for a trip."""
    day_number: int
    date: date
    activities: List[Activity]
    meals: List[Restaurant]
    notes: str = ""
    
    def validate(self) -> bool:
        """Validate day plan data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if self.day_number <= 0:
            raise ValueError("day_number must be positive")
        
        # Validate all activities
        for activity in self.activities:
            activity.validate()
        
        # Validate all restaurants
        for restaurant in self.meals:
            restaurant.validate()
        
        return True
    
    def total_estimated_cost(self) -> float:
        """Calculate total estimated cost for the day.
        
        Returns:
            Total cost including activities and meals
        """
        activity_cost = sum(a.estimated_cost for a in self.activities)
        meal_cost = sum(m.estimated_cost for m in self.meals)
        return activity_cost + meal_cost


@dataclass
class TripPlan:
    """Complete trip plan with itinerary."""
    trip_id: str
    user_id: str
    destination: str
    start_date: date
    end_date: date
    accommodation: Accommodation
    itinerary: List[DayPlan]
    estimated_cost: float
    
    def validate(self) -> bool:
        """Validate trip plan data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.trip_id:
            raise ValueError("trip_id is required")
        if not self.user_id:
            raise ValueError("user_id is required")
        if not self.destination:
            raise ValueError("destination is required")
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")
        if not self.itinerary:
            raise ValueError("Trip must have at least one day plan")
        if self.estimated_cost < 0:
            raise ValueError("estimated_cost must be non-negative")
        
        # Validate accommodation
        self.accommodation.validate()
        
        # Validate all day plans
        for day_plan in self.itinerary:
            day_plan.validate()
        
        return True
    
    def duration_days(self) -> int:
        """Calculate trip duration in days.
        
        Returns:
            Number of days in the trip
        """
        return (self.end_date - self.start_date).days + 1


@dataclass
class AgentState:
    """Agent execution state for pause/resume."""
    task_id: str
    agent_type: str
    status: str  # running, paused, completed, failed
    current_step: int
    total_steps: int
    context: Dict
    created_at: datetime
    updated_at: datetime
    
    def validate(self) -> bool:
        """Validate agent state data.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.agent_type:
            raise ValueError("agent_type is required")
        if self.status not in [s.value for s in TaskStatus]:
            raise ValueError(f"Invalid status: {self.status}")
        if self.current_step < 0:
            raise ValueError("current_step must be non-negative")
        if self.total_steps <= 0:
            raise ValueError("total_steps must be positive")
        if self.current_step > self.total_steps:
            raise ValueError("current_step cannot exceed total_steps")
        return True
    
    def progress_percentage(self) -> float:
        """Calculate progress percentage.
        
        Returns:
            Progress as a percentage (0-100)
        """
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100
