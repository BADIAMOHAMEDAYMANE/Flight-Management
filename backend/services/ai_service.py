# services/ai_service.py
import google.generativeai as genai
from config.settings import Config
from utils.constants import SYSTEM_PROMPT

class AIService:
    """Service for handling AI interactions with Google Gemini"""
    
    def __init__(self):
        # Configure Google Generative AI
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            Config.GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
        )
    
    def start_chat(self, history=None):
        """Start a new chat session with optional history"""
        return self.model.start_chat(history=history or [])
    
    def generate_response(self, chat, message):
        """Generate a response using the AI model"""
        try:
            response = chat.send_message(
                message,
                generation_config={
                    "temperature": Config.AI_TEMPERATURE,
                    "max_output_tokens": Config.MAX_OUTPUT_TOKENS
                },
                safety_settings=[]
            )
            return response.text
        except Exception as e:
            raise Exception(f"AI generation error: {str(e)}")
    
    def generate_travel_data(self, destination):
        """Generate travel data for a destination"""
        prompt = f"""Generate realistic travel data for {destination} in JSON format with these sections:
        1. Weather information for {destination} with current conditions and 5-day forecast
        2. Three recommended flights to {destination} from major hubs
        
        Format:
        {{
            "weather": {{
                "temperature": [current temperature in Celsius],
                "condition": [current weather condition],
                "humidity": [humidity percentage],
                "wind": [wind speed],
                "forecast": [Array of 5 days with day, temperature, and condition]
            }},
            "flights": [Array of 3 flights with airline, price, departure/arrival details]
        }}
        
        Return ONLY the JSON with no additional text or explanation."""
        
        try:
            response = self.model.generate_content(prompt)
            return self._extract_json_from_response(response.text)
        except Exception as e:
            raise Exception(f"Travel data generation error: {str(e)}")
    
    def _extract_json_from_response(self, response_text):
        """Extract JSON content from AI response"""
        import json
        
        # Handle potential markdown code block formatting
        if "```json" in response_text:
            start = response_text.find("```json") + len("```json")
            end = response_text.rfind("```")
            json_content = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + len("```")
            end = response_text.rfind("```")
            json_content = response_text[start:end].strip()
        else:
            json_content = response_text
        
        return json.loads(json_content)