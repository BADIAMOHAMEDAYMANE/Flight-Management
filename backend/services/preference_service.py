# services/preference_service.py
from utils.constants import DESTINATION_CONTENT_IDS

class PreferenceService:
    """Service for extracting and managing user preferences"""
    
    @staticmethod
    def extract_preferences_from_message(user_message, current_preferences=None):
        """
        Extract user preferences from a message
        """
        if current_preferences is None:
            current_preferences = {
                "preferred_destinations": [],
                "travel_interests": [],
                "budget_level": None,
                "travel_type": None,
                "travel_duration": None
            }
        
        message_lower = user_message.lower()
        
        # Extract budget level
        current_preferences = PreferenceService._extract_budget_level(
            message_lower, current_preferences
        )
        
        # Extract travel type
        current_preferences = PreferenceService._extract_travel_type(
            message_lower, current_preferences
        )
        
        # Extract travel interests
        current_preferences = PreferenceService._extract_travel_interests(
            message_lower, current_preferences
        )
        
        # Extract travel duration
        current_preferences = PreferenceService._extract_travel_duration(
            message_lower, current_preferences
        )
        
        # Extract destinations
        current_preferences = PreferenceService._extract_destinations(
            message_lower, current_preferences
        )
        
        return current_preferences
    
    @staticmethod
    def _extract_budget_level(message_lower, preferences):
        """Extract budget level from message"""
        if any(word in message_lower for word in ["luxury", "high-end", "five-star", "5-star"]):
            preferences["budget_level"] = "luxury"
        elif any(word in message_lower for word in ["budget", "cheap", "affordable", "inexpensive"]):
            preferences["budget_level"] = "budget"
        elif any(word in message_lower for word in ["mid-range", "moderate", "medium"]):
            preferences["budget_level"] = "mid-range"
        return preferences
    
    @staticmethod
    def _extract_travel_type(message_lower, preferences):
        """Extract travel type from message"""
        if any(word in message_lower for word in ["family", "kids", "children"]):
            preferences["travel_type"] = "family"
        elif any(word in message_lower for word in ["solo", "alone", "by myself"]):
            preferences["travel_type"] = "solo"
        elif any(word in message_lower for word in ["couple", "romantic", "honeymoon"]):
            preferences["travel_type"] = "couple"
        elif any(word in message_lower for word in ["friends", "group"]):
            preferences["travel_type"] = "group"
        return preferences
    
    @staticmethod
    def _extract_travel_interests(message_lower, preferences):
        """Extract travel interests from message"""
        interests = [
            "beach", "mountain", "hiking", "culture", "history", "food", 
            "adventure", "relaxation", "shopping", "nightlife", "nature", 
            "wildlife", "diving", "skiing", "art", "museum"
        ]
        
        for interest in interests:
            if interest in message_lower and interest not in preferences["travel_interests"]:
                preferences["travel_interests"].append(interest)
        return preferences
    
    @staticmethod
    def _extract_travel_duration(message_lower, preferences):
        """Extract travel duration from message"""
        duration_words = ["day", "days", "week", "weeks", "month", "months"]
        
        for word in duration_words:
            if word in message_lower:
                for i in range(1, 31):
                    if f"{i} {word}" in message_lower:
                        preferences["travel_duration"] = f"{i} {word}"
                        break
        return preferences
    
    @staticmethod
    def _extract_destinations(message_lower, preferences):
        """Extract mentioned destinations from message"""
        for destination in DESTINATION_CONTENT_IDS.keys():
            if (destination.lower() in message_lower and 
                destination not in preferences["preferred_destinations"]):
                preferences["preferred_destinations"].append(destination)
        return preferences