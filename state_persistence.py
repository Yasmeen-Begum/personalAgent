"""State Persistence implementation for pause/resume functionality."""
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


class StatePersistence:
    """Manages persistent storage of agent execution state for pause/resume."""
    
    def __init__(self, storage_path: Path):
        """Initialize State Persistence with storage path.
        
        Args:
            storage_path: Directory path for storing state files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_state_file(self, task_id: str) -> Path:
        """Get the file path for a task's state.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Path to task's state JSON file
        """
        return self.storage_path / f"{task_id}.json"
    
    def _get_user_index_file(self, user_id: str) -> Path:
        """Get the index file path for a user's tasks.
        
        Args:
            user_id: User identifier
            
        Returns:
            Path to user's task index file
        """
        return self.storage_path / f"user_{user_id}_index.json"
    
    def _load_user_index(self, user_id: str) -> Dict[str, Any]:
        """Load user's task index.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary mapping task_id to task metadata
        """
        index_file = self._get_user_index_file(user_id)
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_user_index(self, user_id: str, index: Dict[str, Any]) -> None:
        """Save user's task index.
        
        Args:
            user_id: User identifier
            index: Dictionary mapping task_id to task metadata
        """
        index_file = self._get_user_index_file(user_id)
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    async def save_state(self, task_id: str, state: Dict[str, Any]) -> None:
        """Save agent execution state for a task.
        
        Args:
            task_id: Task identifier
            state: Dictionary containing task state (must include 'user_id')
        """
        if 'user_id' not in state:
            raise ValueError("State must include 'user_id' field")
        
        # Add metadata
        state_with_metadata = {
            **state,
            'task_id': task_id,
            'saved_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Save state file
        state_file = self._get_state_file(task_id)
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_with_metadata, f, indent=2, ensure_ascii=False)
        
        # Update user index
        user_id = state['user_id']
        index = self._load_user_index(user_id)
        index[task_id] = {
            'task_id': task_id,
            'agent_type': state.get('agent_type', 'unknown'),
            'status': state.get('status', 'paused'),
            'saved_at': state_with_metadata['saved_at']
        }
        self._save_user_index(user_id, index)
    
    async def load_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load agent execution state for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Dictionary containing task state, or None if not found
        """
        state_file = self._get_state_file(task_id)
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    async def delete_state(self, task_id: str) -> None:
        """Delete agent execution state for a task.
        
        Args:
            task_id: Task identifier
        """
        # Load state to get user_id before deleting
        state = await self.load_state(task_id)
        
        # Delete state file
        state_file = self._get_state_file(task_id)
        if state_file.exists():
            state_file.unlink()
        
        # Update user index if we have user_id
        if state and 'user_id' in state:
            user_id = state['user_id']
            index = self._load_user_index(user_id)
            if task_id in index:
                del index[task_id]
                self._save_user_index(user_id, index)
    
    async def list_paused_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """List all paused tasks for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of task metadata dictionaries
        """
        index = self._load_user_index(user_id)
        return list(index.values())
    
    async def task_exists(self, task_id: str) -> bool:
        """Check if a task state exists.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if task state exists, False otherwise
        """
        state_file = self._get_state_file(task_id)
        return state_file.exists()
    
    async def update_task_status(self, task_id: str, status: str) -> None:
        """Update the status of a paused task.
        
        Args:
            task_id: Task identifier
            status: New status (e.g., 'paused', 'running', 'completed', 'failed')
        """
        state = await self.load_state(task_id)
        if state:
            state['status'] = status
            state['updated_at'] = datetime.now(timezone.utc).isoformat()
            await self.save_state(task_id, state)
