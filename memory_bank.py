"""Memory Bank implementation for persistent user preferences and feedback."""
import json
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timezone


class MemoryBank:
    """Manages persistent storage of user preferences, feedback, and pantry inventory."""
    
    def __init__(self, storage_path: Path):
        """Initialize Memory Bank with storage path.
        
        Args:
            storage_path: Directory path for storing user data files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_user_file(self, user_id: str) -> Path:
        """Get the file path for a user's data.
        
        Args:
            user_id: User identifier
            
        Returns:
            Path to user's JSON data file
        """
        return self.storage_path / f"{user_id}.json"
    
    def _load_user_data(self, user_id: str) -> dict:
        """Load user data from file.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary containing user data, or empty dict if file doesn't exist
        """
        user_file = self._get_user_file(user_id)
        if user_file.exists():
            with open(user_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "preferences": {},
            "feedback": [],
            "pantry": []
        }
    
    def _save_user_data(self, user_id: str, data: dict) -> None:
        """Save user data to file.
        
        Args:
            user_id: User identifier
            data: Dictionary containing user data to save
        """
        user_file = self._get_user_file(user_id)
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    async def save_preference(self, user_id: str, key: str, value: Any) -> None:
        """Save a user preference.
        
        Args:
            user_id: User identifier
            key: Preference key (e.g., 'dietary_restrictions', 'cuisine_preferences')
            value: Preference value (can be any JSON-serializable type)
        """
        data = self._load_user_data(user_id)
        data["preferences"][key] = value
        self._save_user_data(user_id, data)
    
    async def get_preference(self, user_id: str, key: str) -> Optional[Any]:
        """Retrieve a user preference.
        
        Args:
            user_id: User identifier
            key: Preference key
            
        Returns:
            Preference value, or None if not found
        """
        data = self._load_user_data(user_id)
        return data["preferences"].get(key)
    
    async def get_all_preferences(self, user_id: str) -> dict:
        """Retrieve all preferences for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of all user preferences
        """
        data = self._load_user_data(user_id)
        return data["preferences"]
    
    async def update_feedback(self, user_id: str, item_id: str, rating: float) -> None:
        """Store user feedback/rating for an item.
        
        Args:
            user_id: User identifier
            item_id: Identifier for the rated item (e.g., recipe_id, trip_id)
            rating: Rating value (typically 1-5)
        """
        data = self._load_user_data(user_id)
        
        feedback_entry = {
            "item_id": item_id,
            "rating": rating,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        data["feedback"].append(feedback_entry)
        self._save_user_data(user_id, data)
    
    async def get_feedback_history(self, user_id: str) -> list:
        """Retrieve all feedback history for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of feedback entries with item_id, rating, and timestamp
        """
        data = self._load_user_data(user_id)
        return data["feedback"]
    
    async def save_pantry_items(self, user_id: str, items: list[str]) -> None:
        """Save pantry inventory for a user.
        
        Args:
            user_id: User identifier
            items: List of pantry item names
        """
        data = self._load_user_data(user_id)
        data["pantry"] = items
        self._save_user_data(user_id, data)
    
    async def get_pantry_items(self, user_id: str) -> list[str]:
        """Retrieve pantry inventory for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of pantry item names
        """
        data = self._load_user_data(user_id)
        return data["pantry"]
    
    async def add_pantry_item(self, user_id: str, item: str) -> None:
        """Add a single item to user's pantry.
        
        Args:
            user_id: User identifier
            item: Pantry item name to add
        """
        data = self._load_user_data(user_id)
        if item not in data["pantry"]:
            data["pantry"].append(item)
            self._save_user_data(user_id, data)
    
    async def remove_pantry_item(self, user_id: str, item: str) -> None:
        """Remove a single item from user's pantry.
        
        Args:
            user_id: User identifier
            item: Pantry item name to remove
        """
        data = self._load_user_data(user_id)
        if item in data["pantry"]:
            data["pantry"].remove(item)
            self._save_user_data(user_id, data)
