"""Pricing API MCP Tool for shopping list price estimates."""
import logging
import time
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class PricingAPITool:
    """MCP tool interface for accessing grocery pricing APIs.
    
    This is a stub implementation with mock data for development.
    In production, this would connect to a real pricing API via MCP protocol.
    """
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        """Initialize the pricing API tool.
        
        Args:
            api_key: API key for pricing service (optional for mock)
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.call_count = 0  # For testing tool invocation
        self.rate_limit_count = 0  # For testing rate limit handling
        logger.info("PricingAPITool initialized")
    
    async def get_item_price(
        self,
        item_name: str,
        quantity: float = 1.0,
        unit: str = "unit",
        store: Optional[str] = None
    ) -> Dict:
        """Get price estimate for a single item.
        
        Args:
            item_name: Name of the grocery item
            quantity: Quantity needed
            unit: Unit of measurement
            store: Optional store preference
            
        Returns:
            Dictionary with item_name, quantity, unit, price_per_unit, total_price
            
        Raises:
            Exception: If API call fails after retries
        """
        self.call_count += 1
        logger.info(f"Getting price for: {item_name} ({quantity} {unit})")
        
        # Simulate API call with retry logic
        for attempt in range(self.max_retries):
            try:
                # Simulate rate limiting occasionally
                if self.rate_limit_count > 0:
                    self.rate_limit_count -= 1
                    raise Exception("Rate limit exceeded")
                
                price_per_unit = self._get_mock_price(item_name)
                total_price = price_per_unit * quantity
                
                return {
                    'item_name': item_name,
                    'quantity': quantity,
                    'unit': unit,
                    'price_per_unit': price_per_unit,
                    'total_price': round(total_price, 2),
                    'store': store or 'Generic Store',
                    'currency': 'USD'
                }
                
            except Exception as e:
                logger.warning(f"Price lookup attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Price lookup failed after all retries")
                    # Return fallback price instead of failing
                    return {
                        'item_name': item_name,
                        'quantity': quantity,
                        'unit': unit,
                        'price_per_unit': 5.0,  # Fallback price
                        'total_price': round(5.0 * quantity, 2),
                        'store': 'Estimated',
                        'currency': 'USD',
                        'note': 'Estimated price - API unavailable'
                    }
    
    async def get_bulk_prices(
        self,
        items: List[Dict],
        store: Optional[str] = None
    ) -> List[Dict]:
        """Get price estimates for multiple items.
        
        Args:
            items: List of item dictionaries with name, quantity, unit
            store: Optional store preference
            
        Returns:
            List of price dictionaries
        """
        self.call_count += 1
        logger.info(f"Getting bulk prices for {len(items)} items")
        
        results = []
        for item in items:
            price_info = await self.get_item_price(
                item_name=item['name'],
                quantity=item.get('quantity', 1.0),
                unit=item.get('unit', 'unit'),
                store=store
            )
            results.append(price_info)
        
        return results
    
    async def compare_stores(
        self,
        item_name: str,
        quantity: float = 1.0,
        unit: str = "unit"
    ) -> List[Dict]:
        """Compare prices across different stores.
        
        Args:
            item_name: Name of the grocery item
            quantity: Quantity needed
            unit: Unit of measurement
            
        Returns:
            List of price dictionaries from different stores
        """
        self.call_count += 1
        logger.info(f"Comparing prices for: {item_name}")
        
        stores = ['Walmart', 'Target', 'Whole Foods', 'Kroger']
        results = []
        
        base_price = self._get_mock_price(item_name)
        
        for store in stores:
            # Add some variation to prices
            import random
            variation = random.uniform(0.9, 1.1)
            price_per_unit = round(base_price * variation, 2)
            
            results.append({
                'item_name': item_name,
                'quantity': quantity,
                'unit': unit,
                'price_per_unit': price_per_unit,
                'total_price': round(price_per_unit * quantity, 2),
                'store': store,
                'currency': 'USD'
            })
        
        # Sort by total price
        results.sort(key=lambda x: x['total_price'])
        return results
    
    def simulate_rate_limit(self, count: int = 1):
        """Simulate rate limiting for testing.
        
        Args:
            count: Number of requests to fail with rate limit
        """
        self.rate_limit_count = count
        logger.info(f"Simulating rate limit for next {count} requests")
    
    def _get_mock_price(self, item_name: str) -> float:
        """Get mock price for an item.
        
        Args:
            item_name: Name of the item
            
        Returns:
            Mock price per unit
        """
        # Mock price database
        prices = {
            'pasta': 2.99,
            'bell peppers': 1.49,
            'zucchini': 1.99,
            'olive oil': 8.99,
            'parmesan cheese': 6.99,
            'chicken breast': 5.99,
            'corn tortillas': 3.49,
            'avocado': 1.99,
            'lime': 0.49,
            'cilantro': 1.99,
            'quinoa': 4.99,
            'chickpeas': 1.49,
            'sweet potato': 1.29,
            'kale': 2.99,
            'tahini': 7.99,
            'ground beef': 6.99,
            'burger buns': 3.99,
            'lettuce': 2.49,
            'tomato': 1.99,
            'cheddar cheese': 5.99,
            'mixed greens': 3.99,
            'cucumber': 1.49,
            'cherry tomatoes': 3.99,
            'feta cheese': 6.99,
            'olives': 4.99,
            'salmon fillets': 12.99,
            'teriyaki sauce': 4.99,
            'rice': 3.99,
            'broccoli': 2.99,
            'sesame seeds': 3.49,
            'eggs': 4.99,
            'milk': 3.99,
            'bread': 2.99,
            'butter': 4.99,
            'onion': 0.99,
            'garlic': 0.79,
            'carrots': 1.99,
            'potatoes': 2.99,
        }
        
        # Return price if found, otherwise estimate based on name length
        item_lower = item_name.lower()
        for key, price in prices.items():
            if key in item_lower:
                return price
        
        # Default fallback price
        return 3.99
