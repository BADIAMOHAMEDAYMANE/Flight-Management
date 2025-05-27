"""
Destination Controller - Handles destination-related endpoints
"""

from flask import Blueprint, request, jsonify
from services.travel_advisor_service import TravelAdvisorService
from services.budget_service import BudgetService
from services.ai_service import AIService
from models.user_preferences import UserPreferences
from utils.data_generator import DataGenerator
import json

destination_bp = Blueprint('destination', __name__)

# Initialize services
travel_service = TravelAdvisorService()
budget_service = BudgetService()
ai_service = AIService()
data_generator = DataGenerator()

@destination_bp.route('/destination-details', methods=['POST', 'OPTIONS'])
def destination_details():
    """
    Retrieve comprehensive information about a specific destination.
    
    Provides weather, flights, accommodations, and budget information.
    Uses AI to generate realistic data and integrates with Travel Advisor API for hotels.
    """
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        destination = data.get('destination', '')
        session_id = data.get('sessionId', 'default')
        
        if not destination:
            return jsonify({"error": "No destination provided"}), 400
        
        print(f"Processing destination details request for: {destination}")
        
        # Get hotel data from Travel Advisor API
        try:
            hotels = travel_service.fetch_hotels(destination)
        except Exception as e:
            print(f"Error fetching hotels: {e}")
            hotels = []
        
        # Get user preferences if available
        try:
            user_prefs = UserPreferences.get_preferences(session_id)
        except Exception as e:
            print(f"Error getting user preferences: {e}")
            user_prefs = None
        
        # Generate weather and flights data using AI
        try:
            # Create prompt for AI to generate realistic travel data
            prompt = f"""Generate realistic travel data for {destination} in JSON format with these sections:
            1. Weather information for {destination} with current conditions and 5-day forecast
            2. Three recommended flights to {destination} from major hubs
            
            Format:
            {{
                "weather": {{
                    "temperature": [current temperature in Celsius],
                    "condition": "[current weather condition]",
                    "humidity": [humidity percentage],
                    "wind": [wind speed],
                    "forecast": [
                        {{"day": "Mon", "temperature": [temp], "condition": "[condition]"}},
                        {{"day": "Tue", "temperature": [temp], "condition": "[condition]"}},
                        {{"day": "Wed", "temperature": [temp], "condition": "[condition]"}},
                        {{"day": "Thu", "temperature": [temp], "condition": "[condition]"}},
                        {{"day": "Fri", "temperature": [temp], "condition": "[condition]"}}
                    ]
                }},
                "flights": [
                    {{
                        "airline": "[Airline Name]",
                        "price": [price_number],
                        "departureTime": "[HH:MM]",
                        "departureAirport": "[Airport Code]",
                        "arrivalTime": "[HH:MM]",
                        "arrivalAirport": "[Airport Code]",
                        "duration": "[duration like 2h 30m]"
                    }}
                ]
            }}
            
            Return ONLY the JSON with no additional text or explanation."""
            
            response = ai_service.generate_content(prompt)
            
            # Try to extract JSON from the response
            response_text = response
            
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
            
            # Parse the JSON
            destination_data = json.loads(json_content)
            
            # Add our real hotel data to the response
            destination_data["accommodations"] = hotels if hotels else data_generator.generate_mock_accommodations(destination)
            
            # Add budget information
            try:
                budget_info = budget_service.calculate_travel_budget(destination, user_prefs)
                destination_data["budget"] = {
                    "daily_min": budget_info["daily_total"]["min"],
                    "daily_max": budget_info["daily_total"]["max"],
                    "accommodation_min": budget_info["accommodation"]["min"],
                    "accommodation_max": budget_info["accommodation"]["max"],
                    "food_min": budget_info["food"]["min"],
                    "food_max": budget_info["food"]["max"],
                    "attractions": budget_info.get("specific_attractions", [])
                }
            except Exception as e:
                print(f"Error calculating budget: {e}")
                destination_data["budget"] = {}
            
            print(f"Successfully generated destination data for {destination}")
            return jsonify(destination_data), 200
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw AI response: {response_text}")
            # Fallback to static mock data
            return _get_fallback_data(destination, hotels, user_prefs)
            
        except Exception as e:
            print(f"Error getting AI generated data: {e}")
            # Fallback to static mock data
            return _get_fallback_data(destination, hotels, user_prefs)
        
    except Exception as e:
        print(f"Error in destination details: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

def _get_fallback_data(destination, hotels, user_prefs):
    """Generate fallback mock data when AI service fails"""
    try:
        mock_data = data_generator.generate_mock_data(destination)
        # Replace mock accommodations with real data if available
        if hotels:
            mock_data["accommodations"] = hotels
            
        # Add budget information to mock data
        try:
            budget_info = budget_service.calculate_travel_budget(destination, user_prefs)
            mock_data["budget"] = {
                "daily_min": budget_info["daily_total"]["min"],
                "daily_max": budget_info["daily_total"]["max"],
                "accommodation_min": budget_info["accommodation"]["min"],
                "accommodation_max": budget_info["accommodation"]["max"],
                "food_min": budget_info["food"]["min"],
                "food_max": budget_info["food"]["max"],
                "attractions": budget_info.get("specific_attractions", [])
            }
        except Exception as e:
            print(f"Error in fallback budget calculation: {e}")
            mock_data["budget"] = {}
        
        return jsonify(mock_data), 200
    except Exception as e:
        print(f"Error generating fallback data: {e}")
        return jsonify({"error": "Unable to generate destination data"}), 500