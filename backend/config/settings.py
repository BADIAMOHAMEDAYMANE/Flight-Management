# config/settings.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Flask settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "TRAVEL_ADVISOR_KEY")
    
    # AI Model settings
    GEMINI_MODEL = "gemini-2.0-flash"
    AI_TEMPERATURE = 0.7
    MAX_OUTPUT_TOKENS = 800
    
    # Session settings
    MAX_CHAT_HISTORY = 20
    
    # CORS settings
    CORS_ORIGINS = "*"
    
    # Travel Advisor API settings
    TRAVEL_ADVISOR_BASE_URL = "https://travel-advisor.p.rapidapi.com"
    TRAVEL_ADVISOR_HOST = "travel-advisor.p.rapidapi.com"
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        
        print(f"Loaded API key: {cls.GEMINI_API_KEY}")
        return True