"""Travel Search MCP Tool for trip planning."""
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TravelSearchTool:
    """MCP tool interface for accessing travel search APIs.
    
    This is a stub implementation with mock data for development.
    In production, this would connect to real travel APIs via MCP protocol.
    """
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        """Initialize the travel search tool.
        
        Args:
            api_key: API key for travel service (optional for mock)
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.call_count = 0  # For testing tool invocation
        logger.info("TravelSearchTool initialized")
    
    async def search_accommodations(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int = 2,
        max_budget: Optional[float] = None,
        accommodation_type: Optional[str] = None
    ) -> List[Dict]:
        """Search for accommodations at destination.
        
        Args:
            destination: Destination city or location
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            guests: Number of guests
            max_budget: Maximum budget per night
            accommodation_type: Type filter (hotel, airbnb, hostel, etc.)
            
        Returns:
            List of accommodation dictionaries
            
        Raises:
            Exception: If API call fails after retries
        """
        self.call_count += 1
        logger.info(f"Searching accommodations in {destination} for {guests} guests")
        
        # Simulate API call with retry logic
        for attempt in range(self.max_retries):
            try:
                accommodations = self._get_mock_accommodations(destination)
                
                # Filter by type
                if accommodation_type:
                    accommodations = [a for a in accommodations if a['type'].lower() == accommodation_type.lower()]
                
                # Filter by budget
                if max_budget:
                    accommodations = [a for a in accommodations if a['cost_per_night'] <= max_budget]
                
                # Calculate total cost
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d')
                nights = (check_out_date - check_in_date).days
                
                for acc in accommodations:
                    acc['nights'] = nights
                    acc['total_cost'] = acc['cost_per_night'] * nights
                    acc['check_in'] = check_in
                    acc['check_out'] = check_out
                
                return accommodations
                
            except Exception as e:
                logger.warning(f"Accommodation search attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Accommodation search failed after all retries")
                    raise
    
    async def search_activities(
        self,
        destination: str,
        interests: Optional[List[str]] = None,
        max_budget: Optional[float] = None
    ) -> List[Dict]:
        """Search for activities at destination.
        
        Args:
            destination: Destination city or location
            interests: List of interest categories (e.g., ["museums", "outdoor"])
            max_budget: Maximum budget per activity
            
        Returns:
            List of activity dictionaries
        """
        self.call_count += 1
        logger.info(f"Searching activities in {destination}")
        
        activities = self._get_mock_activities(destination)
        
        # Filter by interests
        if interests:
            activities = [a for a in activities if any(i.lower() in a['category'].lower() for i in interests)]
        
        # Filter by budget
        if max_budget:
            activities = [a for a in activities if a['estimated_cost'] <= max_budget]
        
        return activities
    
    async def search_restaurants(
        self,
        destination: str,
        cuisine_type: Optional[str] = None,
        price_range: Optional[str] = None
    ) -> List[Dict]:
        """Search for restaurants at destination.
        
        Args:
            destination: Destination city or location
            cuisine_type: Type of cuisine (e.g., "italian", "japanese")
            price_range: Price range ($, $$, $$$, $$$$)
            
        Returns:
            List of restaurant dictionaries
        """
        self.call_count += 1
        logger.info(f"Searching restaurants in {destination}")
        
        restaurants = self._get_mock_restaurants(destination)
        
        # Filter by cuisine
        if cuisine_type:
            restaurants = [r for r in restaurants if r['cuisine_type'].lower() == cuisine_type.lower()]
        
        # Filter by price range
        if price_range:
            restaurants = [r for r in restaurants if r['price_range'] == price_range]
        
        return restaurants
    
    async def get_destination_info(self, destination: str) -> Dict:
        """Get general information about a destination.
        
        Args:
            destination: Destination city or location
            
        Returns:
            Dictionary with destination information
        """
        self.call_count += 1
        logger.info(f"Getting info for destination: {destination}")
        
        # Mock destination data
        destinations = {
            'paris': {
                'name': 'Paris',
                'country': 'France',
                'description': 'The City of Light, known for art, fashion, and culture',
                'best_time_to_visit': 'April to June, September to October',
                'currency': 'EUR',
                'language': 'French',
                'timezone': 'CET',
                'popular_areas': ['Eiffel Tower', 'Louvre Museum', 'Notre-Dame', 'Champs-Élysées']
            },
            'tokyo': {
                'name': 'Tokyo',
                'country': 'Japan',
                'description': 'A vibrant metropolis blending tradition and modernity',
                'best_time_to_visit': 'March to May, September to November',
                'currency': 'JPY',
                'language': 'Japanese',
                'timezone': 'JST',
                'popular_areas': ['Shibuya', 'Shinjuku', 'Asakusa', 'Akihabara']
            },
            'new york': {
                'name': 'New York City',
                'country': 'USA',
                'description': 'The city that never sleeps, a global hub of culture and commerce',
                'best_time_to_visit': 'April to June, September to November',
                'currency': 'USD',
                'language': 'English',
                'timezone': 'EST',
                'popular_areas': ['Times Square', 'Central Park', 'Statue of Liberty', 'Brooklyn Bridge']
            }
        }
        
        dest_lower = destination.lower()
        for key, info in destinations.items():
            if key in dest_lower:
                return info
        
        # Default fallback
        return {
            'name': destination,
            'country': 'Unknown',
            'description': f'A wonderful destination: {destination}',
            'best_time_to_visit': 'Year-round',
            'currency': 'USD',
            'language': 'English',
            'timezone': 'UTC',
            'popular_areas': []
        }
    
    def _get_mock_accommodations(self, destination: str) -> List[Dict]:
        """Get mock accommodation data.
        
        Args:
            destination: Destination name
            
        Returns:
            List of mock accommodations
        """
        return [
            {
                'id': 'acc_001',
                'name': f'Grand Hotel {destination}',
                'type': 'hotel',
                'location': f'Downtown {destination}',
                'cost_per_night': 150.0,
                'rating': 4.5,
                'amenities': ['wifi', 'breakfast', 'gym', 'pool'],
                'description': 'Luxury hotel in the heart of the city'
            },
            {
                'id': 'acc_002',
                'name': f'Cozy Apartment {destination}',
                'type': 'airbnb',
                'location': f'City Center {destination}',
                'cost_per_night': 80.0,
                'rating': 4.7,
                'amenities': ['wifi', 'kitchen', 'washer'],
                'description': 'Modern apartment with great views'
            },
            {
                'id': 'acc_003',
                'name': f'Budget Hostel {destination}',
                'type': 'hostel',
                'location': f'Near Station {destination}',
                'cost_per_night': 35.0,
                'rating': 4.2,
                'amenities': ['wifi', 'shared kitchen', 'lounge'],
                'description': 'Affordable accommodation for backpackers'
            },
            {
                'id': 'acc_004',
                'name': f'Boutique Inn {destination}',
                'type': 'hotel',
                'location': f'Historic District {destination}',
                'cost_per_night': 120.0,
                'rating': 4.8,
                'amenities': ['wifi', 'breakfast', 'spa'],
                'description': 'Charming boutique hotel with personalized service'
            }
        ]
    
    def _get_mock_activities(self, destination: str) -> List[Dict]:
        """Get mock activity data.
        
        Args:
            destination: Destination name
            
        Returns:
            List of mock activities
        """
        return [
            {
                'id': 'act_001',
                'name': f'{destination} City Tour',
                'category': 'sightseeing',
                'description': 'Guided tour of major landmarks',
                'duration': 180,  # minutes
                'estimated_cost': 45.0,
                'rating': 4.6
            },
            {
                'id': 'act_002',
                'name': f'{destination} Museum Visit',
                'category': 'museums',
                'description': 'Explore world-class art and history',
                'duration': 120,
                'estimated_cost': 25.0,
                'rating': 4.7
            },
            {
                'id': 'act_003',
                'name': f'{destination} Food Tour',
                'category': 'food',
                'description': 'Taste local cuisine and specialties',
                'duration': 150,
                'estimated_cost': 65.0,
                'rating': 4.9
            },
            {
                'id': 'act_004',
                'name': f'{destination} Park Walk',
                'category': 'outdoor',
                'description': 'Relaxing walk through scenic parks',
                'duration': 90,
                'estimated_cost': 0.0,
                'rating': 4.5
            },
            {
                'id': 'act_005',
                'name': f'{destination} Shopping District',
                'category': 'shopping',
                'description': 'Browse local shops and boutiques',
                'duration': 120,
                'estimated_cost': 0.0,
                'rating': 4.3
            }
        ]
    
    def _get_mock_restaurants(self, destination: str) -> List[Dict]:
        """Get mock restaurant data.
        
        Args:
            destination: Destination name
            
        Returns:
            List of mock restaurants
        """
        return [
            {
                'id': 'rest_001',
                'name': f'Le Bistro {destination}',
                'cuisine_type': 'French',
                'price_range': '$$$',
                'estimated_cost': 50.0,
                'rating': 4.6,
                'location': f'Downtown {destination}',
                'description': 'Classic French cuisine in elegant setting'
            },
            {
                'id': 'rest_002',
                'name': f'Sushi Bar {destination}',
                'cuisine_type': 'Japanese',
                'price_range': '$$',
                'estimated_cost': 35.0,
                'rating': 4.7,
                'location': f'City Center {destination}',
                'description': 'Fresh sushi and authentic Japanese dishes'
            },
            {
                'id': 'rest_003',
                'name': f'Pizza Place {destination}',
                'cuisine_type': 'Italian',
                'price_range': '$',
                'estimated_cost': 20.0,
                'rating': 4.4,
                'location': f'Near Station {destination}',
                'description': 'Casual Italian pizzeria with great value'
            },
            {
                'id': 'rest_004',
                'name': f'Steakhouse {destination}',
                'cuisine_type': 'American',
                'price_range': '$$$$',
                'estimated_cost': 75.0,
                'rating': 4.8,
                'location': f'Uptown {destination}',
                'description': 'Premium steaks and fine dining experience'
            }
        ]
