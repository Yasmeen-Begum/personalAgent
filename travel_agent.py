"""Travel Agent for planning trips and creating itineraries."""
import logging
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import date, timedelta

from data_models import (
    TripPlan, DayPlan, Activity, Restaurant, Accommodation
)
from travel_tool import TravelSearchTool

logger = logging.getLogger(__name__)


class TravelAgent:
    """Agent responsible for planning trips and creating itineraries.
    
    This agent gathers trip requirements, searches accommodations, creates
    day-by-day itineraries, and recommends activities and restaurants.
    """
    
    def __init__(self, travel_tool: TravelSearchTool):
        """Initialize the Travel Agent.
        
        Args:
            travel_tool: MCP tool for accessing travel search APIs
        """
        self.travel_tool = travel_tool
        logger.info("TravelAgent initialized")
    
    async def plan_trip(
        self,
        user_id: str,
        destination: str,
        dates: Tuple[str, str],
        budget: float,
        preferences: Optional[Dict] = None
    ) -> TripPlan:
        """Plan a complete trip with accommodation and itinerary.
        
        Args:
            user_id: User identifier
            destination: Destination city or location
            dates: Tuple of (start_date, end_date) in YYYY-MM-DD format
            budget: Total budget for the trip
            preferences: Dictionary containing:
                - accommodation_type: Preferred type (hotel, airbnb, hostel)
                - interests: List of interests (museums, outdoor, food, etc.)
                - budget_per_night: Maximum budget per night for accommodation
                
        Returns:
            TripPlan object with accommodation and daily itinerary
            
        Raises:
            ValueError: If dates are invalid or budget is negative
        """
        if budget < 0:
            raise ValueError("Budget must be non-negative")
        
        start_date_str, end_date_str = dates
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
        
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")
        
        preferences = preferences or {}
        accommodation_type = preferences.get('accommodation_type')
        interests = preferences.get('interests', [])
        budget_per_night = preferences.get('budget_per_night')
        
        logger.info(f"Planning trip to {destination} from {start_date} to {end_date}")
        logger.info(f"Budget: ${budget}, Interests: {interests}")
        
        # Calculate trip duration
        nights = (end_date - start_date).days
        days = nights + 1
        
        # Search for accommodations
        accommodations = await self.search_accommodations(
            destination=destination,
            check_in=start_date_str,
            check_out=end_date_str,
            max_budget=budget_per_night,
            accommodation_type=accommodation_type
        )
        
        if not accommodations:
            raise ValueError(f"No accommodations found in {destination} within budget")
        
        # Select best accommodation (first one, sorted by rating in tool)
        selected_accommodation = accommodations[0]
        
        # Create itinerary
        itinerary = await self.create_itinerary(
            destination=destination,
            start_date=start_date,
            days=days,
            interests=interests,
            daily_budget=(budget - selected_accommodation['total_cost']) / days if days > 0 else 0
        )
        
        # Convert accommodation dict to Accommodation object
        accommodation_obj = Accommodation(
            name=selected_accommodation['name'],
            type=selected_accommodation['type'],
            location=selected_accommodation['location'],
            cost_per_night=selected_accommodation['cost_per_night'],
            total_cost=selected_accommodation['total_cost'],
            amenities=selected_accommodation.get('amenities', [])
        )
        
        # Calculate total estimated cost
        accommodation_cost = selected_accommodation['total_cost']
        activities_cost = sum(
            sum(a.estimated_cost for a in day.activities)
            for day in itinerary
        )
        meals_cost = sum(
            sum(r.estimated_cost for r in day.meals)
            for day in itinerary
        )
        estimated_cost = accommodation_cost + activities_cost + meals_cost
        
        # Create trip plan
        trip_id = f"trip_{uuid.uuid4().hex[:8]}"
        trip_plan = TripPlan(
            trip_id=trip_id,
            user_id=user_id,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            accommodation=accommodation_obj,
            itinerary=itinerary,
            estimated_cost=round(estimated_cost, 2)
        )
        
        # Validate
        trip_plan.validate()
        
        logger.info(f"Created trip plan {trip_id} for {days} days, estimated cost: ${estimated_cost:.2f}")
        return trip_plan
    
    async def search_accommodations(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        max_budget: Optional[float] = None,
        accommodation_type: Optional[str] = None
    ) -> List[Dict]:
        """Search for accommodations at destination.
        
        Args:
            destination: Destination city or location
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            max_budget: Maximum budget per night
            accommodation_type: Type filter (hotel, airbnb, hostel)
            
        Returns:
            List of accommodation dictionaries
        """
        logger.info(f"Searching accommodations in {destination}")
        
        accommodations = await self.travel_tool.search_accommodations(
            destination=destination,
            check_in=check_in,
            check_out=check_out,
            guests=2,
            max_budget=max_budget,
            accommodation_type=accommodation_type
        )
        
        # Filter by budget if specified
        if max_budget:
            accommodations = [a for a in accommodations if a['cost_per_night'] <= max_budget]
        
        logger.info(f"Found {len(accommodations)} accommodations")
        return accommodations
    
    async def create_itinerary(
        self,
        destination: str,
        start_date: date,
        days: int,
        interests: Optional[List[str]] = None,
        daily_budget: float = 100.0
    ) -> List[DayPlan]:
        """Create a day-by-day itinerary for the trip.
        
        Args:
            destination: Destination city or location
            start_date: Start date of the trip
            days: Number of days
            interests: List of interest categories
            daily_budget: Budget per day for activities and meals
            
        Returns:
            List of DayPlan objects
        """
        logger.info(f"Creating {days}-day itinerary for {destination}")
        
        interests = interests or []
        
        # Get activities and restaurants
        activities = await self.suggest_activities(destination, interests)
        restaurants = await self.travel_tool.search_restaurants(destination)
        
        itinerary = []
        
        for day_num in range(1, days + 1):
            current_date = start_date + timedelta(days=day_num - 1)
            
            # Select 2-3 activities per day
            day_activities = []
            activities_per_day = min(3, len(activities))
            
            for i in range(activities_per_day):
                # Rotate through available activities
                activity_data = activities[(day_num - 1 + i) % len(activities)]
                
                activity = Activity(
                    name=activity_data['name'],
                    description=activity_data['description'],
                    duration=activity_data['duration'],
                    estimated_cost=activity_data['estimated_cost'],
                    location=activity_data.get('location', destination)
                )
                day_activities.append(activity)
            
            # Select 2-3 restaurants per day (breakfast, lunch, dinner)
            day_restaurants = []
            meals_per_day = min(3, len(restaurants))
            
            for i in range(meals_per_day):
                # Rotate through available restaurants
                restaurant_data = restaurants[(day_num - 1 + i) % len(restaurants)]
                
                restaurant = Restaurant(
                    name=restaurant_data['name'],
                    cuisine_type=restaurant_data['cuisine_type'],
                    estimated_cost=restaurant_data['estimated_cost'],
                    location=restaurant_data.get('location', destination)
                )
                day_restaurants.append(restaurant)
            
            # Create day plan
            day_plan = DayPlan(
                day_number=day_num,
                date=current_date,
                activities=day_activities,
                meals=day_restaurants,
                notes=f"Day {day_num} in {destination}"
            )
            
            itinerary.append(day_plan)
        
        logger.info(f"Created itinerary with {len(itinerary)} days")
        return itinerary
    
    async def suggest_activities(
        self,
        destination: str,
        interests: List[str]
    ) -> List[Dict]:
        """Suggest activities based on interests.
        
        Args:
            destination: Destination city or location
            interests: List of interest categories
            
        Returns:
            List of activity dictionaries
        """
        logger.info(f"Suggesting activities for {destination} with interests: {interests}")
        
        activities = await self.travel_tool.search_activities(
            destination=destination,
            interests=interests if interests else None
        )
        
        logger.info(f"Found {len(activities)} activities")
        return activities
