# models/chat_session.py
from datetime import datetime
import uuid
from typing import Dict, List

class ChatSession:
    """Model for managing chat sessions with enhanced features"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.history: List[Dict] = []
        self.max_history = 20  # Maximum messages to retain in history
        self.metadata = {}  # Additional session metadata storage
    
    def add_message(self, role: str, message: str) -> None:
        """Add a message to the chat history with timestamp"""
        self.last_accessed = datetime.now()
        self.history.append({
            "role": role,
            "parts": [{"text": message}],
            "timestamp": datetime.now().isoformat()
        })
        
        # Maintain history size limit
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_history(self, formatted: bool = False) -> List[Dict]:
        """Get the chat history in either raw or formatted format"""
        self.last_accessed = datetime.now()
        if formatted:
            return [{"role": msg["role"], "content": msg["parts"][0]["text"]} for msg in self.history]
        return self.history
    
    def clear_history(self) -> None:
        """Clear the chat history while maintaining session"""
        self.history = []
    
    def update_metadata(self, key: str, value: any) -> None:
        """Update session metadata"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str = None) -> any:
        """Get specific metadata or all metadata if no key provided"""
        return self.metadata.get(key) if key else self.metadata

class ChatSessionManager:
    """Manager for handling multiple chat sessions with cleanup"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout = 3600  # 1 hour in seconds
    
    def get_session(self, session_id: str = None) -> ChatSession:
        """Get or create a chat session with optional session timeout handling"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatSession(session_id)
        else:
            # Update last accessed time for existing session
            self.sessions[session_id].last_accessed = datetime.now()
        
        return self.sessions[session_id]
    
    def remove_session(self, session_id: str) -> bool:
        """Remove a chat session and return success status"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_inactive_sessions(self) -> int:
        """Remove inactive sessions older than timeout period and return count removed"""
        now = datetime.now()
        to_remove = [
            session_id for session_id, session in self.sessions.items()
            if (now - session.last_accessed).total_seconds() > self.session_timeout
        ]
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        return len(to_remove)
    
    def get_active_sessions_count(self) -> int:
        """Get the number of active sessions"""
        return len(self.sessions)
    
    def get_session_ids(self) -> List[str]:
        """Get list of all active session IDs"""
        return list(self.sessions.keys())