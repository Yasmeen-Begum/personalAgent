"""Session Manager implementation for conversation state management."""
import uuid
from typing import Optional, Dict, List
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
import json


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Session:
    """Represents a user session with conversation history."""
    session_id: str
    user_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "messages": [asdict(msg) for msg in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create session from dictionary."""
        messages = [Message(**msg) for msg in data.get("messages", [])]
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            messages=messages,
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            metadata=data.get("metadata", {})
        )


class InMemorySessionService:
    """In-memory storage for sessions."""
    
    def __init__(self):
        """Initialize in-memory session storage."""
        self._sessions: Dict[str, Session] = {}
    
    def save(self, session: Session) -> None:
        """Save a session to memory."""
        self._sessions[session.session_id] = session
    
    def get(self, session_id: str) -> Optional[Session]:
        """Retrieve a session from memory."""
        return self._sessions.get(session_id)
    
    def delete(self, session_id: str) -> None:
        """Delete a session from memory."""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def list_by_user(self, user_id: str) -> List[Session]:
        """List all sessions for a user."""
        return [s for s in self._sessions.values() if s.user_id == user_id]


class SessionManager:
    """Manages user sessions and conversation history."""
    
    def __init__(self, session_service: InMemorySessionService, memory_bank=None):
        """Initialize Session Manager.
        
        Args:
            session_service: Service for storing/retrieving sessions
            memory_bank: Optional MemoryBank for loading user preferences
        """
        self.session_service = session_service
        self.memory_bank = memory_bank
    
    async def create_session(self, user_id: str) -> str:
        """Create a new session for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id, user_id=user_id)
        
        # Load user preferences if memory bank is available
        if self.memory_bank:
            preferences = await self.memory_bank.get_all_preferences(user_id)
            session.metadata["preferences"] = preferences
        
        self.session_service.save(session)
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object or None if not found
        """
        return self.session_service.get(session_id)
    
    async def update_session(self, session_id: str, messages: List[Message]) -> None:
        """Update session with new messages.
        
        Args:
            session_id: Session identifier
            messages: List of messages to add to the session
        """
        session = self.session_service.get(session_id)
        if session:
            session.messages.extend(messages)
            session.updated_at = datetime.now(timezone.utc).isoformat()
            self.session_service.save(session)
    
    async def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a single message to a session.
        
        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        message = Message(role=role, content=content)
        await self.update_session(session_id, [message])
    
    async def close_session(self, session_id: str) -> None:
        """Close and delete a session.
        
        Args:
            session_id: Session identifier
        """
        self.session_service.delete(session_id)
    
    async def get_conversation_history(self, session_id: str) -> List[Message]:
        """Get conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages in the session
        """
        session = self.session_service.get(session_id)
        return session.messages if session else []
    
    async def list_user_sessions(self, user_id: str) -> List[Session]:
        """List all sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of sessions for the user
        """
        return self.session_service.list_by_user(user_id)
    
    async def update_session_metadata(self, session_id: str, key: str, value: any) -> None:
        """Update session metadata.
        
        Args:
            session_id: Session identifier
            key: Metadata key
            value: Metadata value
        """
        session = self.session_service.get(session_id)
        if session:
            session.metadata[key] = value
            session.updated_at = datetime.now(timezone.utc).isoformat()
            self.session_service.save(session)
