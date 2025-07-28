from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid


@dataclass
class UserAction:
    """Represents a single user action within a session."""
    action_type: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserSession:
    """Represents a user session with tracking capabilities."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    user_actions: List[UserAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_action(self, action_type: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a new user action to the session."""
        action = UserAction(
            action_type=action_type,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        self.user_actions.append(action)
        self.last_activity = datetime.utcnow()
    
    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "user_actions": [
                {
                    "action_type": action.action_type,
                    "timestamp": action.timestamp.isoformat(),
                    "metadata": action.metadata
                }
                for action in self.user_actions
            ],
            "metadata": self.metadata
        }


class SessionStore:
    """In-memory session storage. In production, this could be replaced with Redis."""
    
    def __init__(self):
        self._sessions: Dict[str, UserSession] = {}
    
    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> UserSession:
        """Create a new session."""
        session = UserSession(metadata=metadata or {})
        self._sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Retrieve a session by ID."""
        return self._sessions.get(session_id)
    
    def update_session(self, session: UserSession) -> None:
        """Update an existing session."""
        self._sessions[session.session_id] = session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Remove sessions older than max_age_hours. Returns count of removed sessions."""
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        expired_sessions = [
            session_id for session_id, session in self._sessions.items()
            if session.last_activity < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        return len(expired_sessions)
    
    def get_active_session_count(self) -> int:
        """Get the count of active sessions."""
        return len(self._sessions)


# Global session store instance
session_store = SessionStore()