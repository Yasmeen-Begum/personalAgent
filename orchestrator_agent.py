"""Orchestrator Agent for coordinating specialized agents."""
import logging
import re
from typing import Dict, Optional, Any
from datetime import date, timedelta

from meal_planning_agent import MealPlanningAgent
from shopping_agent import ShoppingAgent
from travel_agent import TravelAgent
from session_manager import SessionManager
from memory_bank import MemoryBank

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Main orchestrator agent that coordinates specialized sub-agents.
    
    This agent parses user intent, routes to appropriate sub-agents,
    maintains conversation context, and manages session lifecycle.
    """
    
    def __init__(
        self,
        meal_agent: MealPlanningAgent,
        shopping_agent: ShoppingAgent,
        travel_agent: TravelAgent,
        session_manager: SessionManager,
        memory_bank: MemoryBank
    ):
        """Initialize the Orchestrator Agent.
        
        Args:
            meal_agent: Meal planning agent instance
            shopping_agent: Shopping agent instance
            travel_agent: Travel agent instance
            session_manager: Session manager for conversation state
            memory_bank: Memory bank for user preferences
        """
        self.meal_agent = meal_agent
        self.shopping_agent = shopping_agent
        self.travel_agent = travel_agent
        self.session_manager = session_manager
        self.memory_bank = memory_bank
        logger.info("OrchestratorAgent initialized")
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user message and route to appropriate agent.
        
        Args:
            user_id: User identifier
            message: User message text
            session_id: Optional session ID (creates new if not provided)
            
        Returns:
            Dictionary with response, intent, and any generated data
        """
        logger.info(f"Processing message from user {user_id}: {message[:50]}...")
        
        # Get or create session
        if not session_id:
            session_id = await self.session_manager.create_session(user_id)
            logger.info(f"Created new session: {session_id}")
        
        # Load user preferences
        preferences = await self.memory_bank.get_all_preferences(user_id)
        
        # Parse intent
        intent = self._parse_intent(message)
        logger.info(f"Detected intent: {intent}")
        
        # Check for ambiguity
        if intent == 'ambiguous':
            return {
                'response': self._generate_clarifying_questions(message),
                'intent': 'ambiguous',
                'requires_clarification': True
            }
        
        # Route to appropriate agent
        context = {
            'user_id': user_id,
            'session_id': session_id,
            'preferences': preferences,
            'message': message
        }
        
        result = await self.route_to_agent(intent, context)
        
        # Generate summary
        summary = self._generate_summary(intent, result)
        
        # Update session
        await self.session_manager.update_session(
            session_id,
            [{'role': 'user', 'content': message}, {'role': 'assistant', 'content': summary}]
        )
        
        return {
            'response': summary,
            'intent': intent,
            'data': result.get('data'),
            'session_id': session_id
        }
    
    async def route_to_agent(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request to appropriate specialized agent.
        
        Args:
            intent: Detected intent (meal_planning, shopping, travel, etc.)
            context: Context dictionary with user info and preferences
            
        Returns:
            Dictionary with agent response and generated data
        """
        logger.info(f"Routing to agent for intent: {intent}")
        
        user_id = context['user_id']
        preferences = context.get('preferences', {})
        message = context.get('message', '')
        
        try:
            if intent == 'meal_planning':
                # Extract parameters from message
                days = self._extract_days(message) or 7
                
                meal_plan = await self.meal_agent.generate_meal_plan(
                    user_id=user_id,
                    days=days,
                    preferences=preferences
                )
                
                return {
                    'success': True,
                    'data': meal_plan,
                    'message': f'Generated {days}-day meal plan'
                }
            
            elif intent == 'shopping':
                # For shopping, we need a meal plan
                # In a real implementation, this would retrieve from context
                return {
                    'success': False,
                    'message': 'Please generate a meal plan first before creating a shopping list'
                }
            
            elif intent == 'travel':
                # Extract travel parameters
                destination = self._extract_destination(message)
                if not destination:
                    return {
                        'success': False,
                        'message': 'Please specify a destination for your trip'
                    }
                
                # Use default dates if not specified
                start_date = date.today() + timedelta(days=30)
                end_date = start_date + timedelta(days=7)
                budget = 2000.0
                
                trip_plan = await self.travel_agent.plan_trip(
                    user_id=user_id,
                    destination=destination,
                    dates=(start_date.isoformat(), end_date.isoformat()),
                    budget=budget,
                    preferences=preferences
                )
                
                return {
                    'success': True,
                    'data': trip_plan,
                    'message': f'Created trip plan for {destination}'
                }
            
            elif intent == 'multi_domain':
                # Handle multi-domain requests sequentially
                results = []
                
                if 'meal' in message.lower():
                    meal_result = await self.route_to_agent('meal_planning', context)
                    results.append(meal_result)
                
                if 'shop' in message.lower():
                    shop_result = await self.route_to_agent('shopping', context)
                    results.append(shop_result)
                
                if 'travel' in message.lower() or 'trip' in message.lower():
                    travel_result = await self.route_to_agent('travel', context)
                    results.append(travel_result)
                
                return {
                    'success': True,
                    'data': results,
                    'message': 'Completed multi-domain request'
                }
            
            else:
                return {
                    'success': False,
                    'message': f'Unknown intent: {intent}'
                }
        
        except Exception as e:
            logger.error(f"Error routing to agent: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Error processing request: {str(e)}'
            }
    
    def _parse_intent(self, message: str) -> str:
        """Parse user intent from message.
        
        Args:
            message: User message text
            
        Returns:
            Intent string (meal_planning, shopping, travel, multi_domain, ambiguous)
        """
        message_lower = message.lower()
        
        # Count domain indicators
        domains = []
        
        if any(word in message_lower for word in ['meal', 'recipe', 'cook', 'eat', 'food', 'dinner', 'lunch', 'breakfast']):
            domains.append('meal_planning')
        
        if any(word in message_lower for word in ['shop', 'grocery', 'groceries', 'buy', 'ingredient', 'store']):
            domains.append('shopping')
        
        if any(word in message_lower for word in ['travel', 'trip', 'vacation', 'visit', 'hotel', 'flight']):
            domains.append('travel')
        
        # Determine intent
        if len(domains) == 0:
            return 'ambiguous'
        elif len(domains) == 1:
            return domains[0]
        else:
            return 'multi_domain'
    
    def _generate_clarifying_questions(self, message: str) -> str:
        """Generate clarifying questions for ambiguous input.
        
        Args:
            message: User message text
            
        Returns:
            Clarifying question string
        """
        return (
            "I'm not sure what you'd like help with. "
            "I can assist with:\n"
            "- Meal planning (creating weekly meal plans)\n"
            "- Shopping lists (generating grocery lists)\n"
            "- Travel planning (planning trips and itineraries)\n\n"
            "What would you like to do?"
        )
    
    def _generate_summary(self, intent: str, result: Dict[str, Any]) -> str:
        """Generate a summary of actions taken.
        
        Args:
            intent: Detected intent
            result: Result from agent execution
            
        Returns:
            Summary string
        """
        if not result.get('success'):
            return result.get('message', 'Failed to process request')
        
        if intent == 'meal_planning':
            meal_plan = result.get('data')
            if meal_plan:
                return (
                    f"✓ Created a {meal_plan.duration_days()}-day meal plan with "
                    f"{len(meal_plan.meals)} meals using {meal_plan.total_recipes} recipes."
                )
        
        elif intent == 'shopping':
            shopping_list = result.get('data')
            if shopping_list:
                return (
                    f"✓ Generated shopping list with {len(shopping_list.items)} items "
                    f"across {len(shopping_list.categories)} categories. "
                    f"Estimated total: ${shopping_list.estimated_total:.2f}"
                )
        
        elif intent == 'travel':
            trip_plan = result.get('data')
            if trip_plan:
                return (
                    f"✓ Planned {trip_plan.duration_days()}-day trip to {trip_plan.destination}. "
                    f"Accommodation: {trip_plan.accommodation.name}. "
                    f"Estimated cost: ${trip_plan.estimated_cost:.2f}"
                )
        
        elif intent == 'multi_domain':
            results = result.get('data', [])
            summaries = []
            for r in results:
                if r.get('success'):
                    summaries.append(r.get('message', ''))
            return "✓ Completed multiple tasks:\n" + "\n".join(f"  - {s}" for s in summaries)
        
        return result.get('message', 'Task completed')
    
    def _extract_days(self, message: str) -> Optional[int]:
        """Extract number of days from message.
        
        Args:
            message: User message text
            
        Returns:
            Number of days or None
        """
        # Look for patterns like "3 days", "5-day", "week" (7 days)
        patterns = [
            r'(\d+)\s*days?',
            r'(\d+)-day',
            r'for\s+(\d+)\s+days?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return int(match.group(1))
        
        if 'week' in message.lower():
            return 7
        
        return None
    
    def _extract_destination(self, message: str) -> Optional[str]:
        """Extract destination from message.
        
        Args:
            message: User message text
            
        Returns:
            Destination string or None
        """
        # Look for patterns like "to Paris", "visit Tokyo", "trip to New York"
        patterns = [
            r'to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'visit\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'trip\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        
        return None
