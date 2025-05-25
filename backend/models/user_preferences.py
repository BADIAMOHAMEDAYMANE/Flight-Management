# models/user_preferences.py

class UserPreferences:
    """Model for user travel preferences"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.preferred_destinations = []
        self.travel_interests = []
        self.budget_level = None
        self.travel_type = None
        self.travel_duration = None
    
    def to_dict(self):
        """Convert preferences to dictionary"""
        return {
            "preferred_destinations": self.preferred_destinations,
            "travel_interests": self.travel_interests,
            "budget_level": self.budget_level,
            "travel_type": self.travel_type,
            "travel_duration": self.travel_duration
        }
    
    def update_from_dict(self, data):
        """Update preferences from dictionary"""
        if "preferred_destinations" in data:
            self.preferred_destinations = data["preferred_destinations"]
        if "travel_interests" in data:
            self.travel_interests = data["travel_interests"]
        if "budget_level" in data:
            self.budget_level = data["budget_level"]
        if "travel_type" in data:
            self.travel_type = data["travel_type"]
        if "travel_duration" in data:
            self.travel_duration = data["travel_duration"]

class UserPreferencesManager:
    """Manager for handling user preferences"""
    
    def __init__(self):
        self.preferences = {}
    
    def get_preferences(self, session_id):
        """Get or create user preferences"""
        if session_id not in self.preferences:
            self.preferences[session_id] = UserPreferences(session_id)
        return self.preferences[session_id]
    
    def update_preferences(self, session_id, preferences_dict):
        """Update user preferences"""
        prefs = self.get_preferences(session_id)
        prefs.update_from_dict(preferences_dict)
        return prefs
    
    def remove_preferences(self, session_id):
        """Remove user preferences"""
        if session_id in self.preferences:
            del self.preferences[session_id]