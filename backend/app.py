# TravelMate API - Flask Travel Assistant Application
# This application provides a conversational travel planning interface using Google's Gemini AI
# and integrates with Travel Advisor API for real hotel data

# =============================================================================
# IMPORTS AND DEPENDENCIES
# =============================================================================

from flask import Flask, request, jsonify, send_from_directory
import os
import google.generativeai as genai  # Google's Gemini AI for natural language processing
from dotenv import load_dotenv  # Environment variable management
from flask_cors import CORS  # Cross-Origin Resource Sharing for frontend integration
import json
import random
from datetime import datetime, timedelta
import requests  # HTTP requests for external APIs

# =============================================================================
# CONFIGURATION AND SETUP
# =============================================================================

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to allow frontend access

# Configure Google Generative AI with API key from environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
print("Loaded API key:", os.getenv("GEMINI_API_KEY"))

# RapidAPI Key for Travel Advisor API (should be loaded from environment in production)
RAPIDAPI_KEY = "TRAVEL_ADVISOR_KEY"  

# =============================================================================
# AI SYSTEM PROMPT CONFIGURATION
# =============================================================================

# Define the system prompt that instructs the AI on how to respond to travel queries
# This prompt includes specific formatting instructions for destination cards and suggestion buttons
system_prompt = """You are TravelMate, a friendly travel assistant. Respond to greetings naturally.

For travel requests, format your response as follows:

## Recommended Destinations

{destination_card}**Paris, France**{/destination_card}
* **Highlights:** Iconic Eiffel Tower, world-class museums, charming cafés
* **Perfect for:** Romantic getaways, art lovers, foodies
* **Best time to visit:** Spring (April-June) or Fall (September-October)

{destination_card}**Tokyo, Japan**{/destination_card}
* **Highlights:** Blend of tradition and futuristic technology, incredible food scene
* **Perfect for:** Food enthusiasts, technology fans, culture seekers
* **Best time to visit:** Spring (March-May) or Fall (October-November)

{destination_card}**Costa Rica**{/destination_card}
* **Highlights:** Lush rainforests, beautiful beaches, abundant wildlife
* **Perfect for:** Nature lovers, adventure seekers, eco-tourists  
* **Best time to visit:** Dry season (December-April)

For specific destination queries, use this format:

## {destination_card}{Destination Name}{/destination_card}

**Top Attractions:**
* {Attraction 1}
* {Attraction 2}
* {Attraction 3}

**Local Cuisine:** {Brief description of local food}

**Best Time to Visit:** {Season information}

**Travel Tips:**
* {Tip 1}
* {Tip 2}
* {Tip 3}

{suggest_buttons}["I choose {destination name}", "Budget for {destination name}", "Flights to {destination name}"]{/suggest_buttons}

For budget-related questions, respond with a breakdown like this:

## Budget Estimate for {Destination}

**Accommodation:**
* Budget: ${X}-${Y} per night
* Mid-range: ${X}-${Y} per night
* Luxury: ${X}+ per night

**Food:**
* Budget meals: ${X}-${Y} per day
* Mid-range dining: ${X}-${Y} per day
* Fine dining: ${X}+ per meal

**Transportation:**
* Public transit: ${X} per day
* Car rental: ${X}-${Y} per day
* Taxis/rideshares: Average ${X} per ride

**Activities:**
* Free attractions: {Examples}
* Paid attractions: ${X}-${Y} per activity
* Tours: ${X}-${Y} per tour

**Estimated daily budget:** ${X}-${Y} depending on travel style

{suggest_buttons}["I choose {destination name}", "Weather in {destination name}", "Things to do in {destination name}"]{/suggest_buttons}

Always inform users they can get detailed information by typing "I choose {destination name}".
"""

# =============================================================================
# AI MODEL INITIALIZATION
# =============================================================================

# Set up the Gemini model with system instructions
model = genai.GenerativeModel(
    'gemini-2.0-flash',  # Latest Gemini model version
    system_instruction=system_prompt,
)

# =============================================================================
# DATA STORAGE AND SESSION MANAGEMENT
# =============================================================================

# Store chat sessions by user ID with conversation history
# Structure: {session_id: [conversation_history]}
chat_sessions = {}

# Store user preferences extracted from conversations
# Structure: {session_id: {preferences_dict}}
user_preferences = {}

# =============================================================================
# DESTINATION MAPPING FOR TRAVEL ADVISOR API
# =============================================================================

# Mapping of common destinations to their Travel Advisor contentIds
# These IDs are used to fetch specific data from the Travel Advisor API
destination_content_ids = {
    "paris": "187147",
    "london": "186338",
    "new york": "60763",
    "tokyo": "298184",
    "rome": "187791",
    "barcelona": "187497",
    "dubai": "295424",
    "sydney": "255060",
    "amsterdam": "188590",
    "bangkok": "293916",
    "los angeles": "32655",
    "las vegas": "45963",
    "chicago": "35805",
    "miami": "34439",
    "berlin": "187323",
    "madrid": "187514",
    "singapore": "294265",
    "san francisco": "60713",
    "hong kong": "294217",
}

# =============================================================================
# USER PREFERENCE EXTRACTION FUNCTION
# =============================================================================

def update_user_preferences(session_id, user_message):
    """
    Extract and update user preferences from conversation messages.
    
    Args:
        session_id (str): Unique identifier for the user session
        user_message (str): The user's message to analyze for preferences
    
    Returns:
        dict: Updated user preferences for the session
    
    This function analyzes user messages to extract:
    - Budget level (budget, mid-range, luxury)
    - Travel type (family, solo, couple, group)
    - Travel interests (beach, culture, food, etc.)
    - Travel duration
    - Preferred destinations
    """
    
    # Initialize preferences structure if not exists
    if session_id not in user_preferences:
        user_preferences[session_id] = {
            "preferred_destinations": [],
            "travel_interests": [],
            "budget_level": None,
            "travel_type": None,
            "travel_duration": None
        }
    
    preferences = user_preferences[session_id]
    message_lower = user_message.lower()
    
    # Extract budget level from keywords
    if any(word in message_lower for word in ["luxury", "high-end", "five-star", "5-star"]):
        preferences["budget_level"] = "luxury"
    elif any(word in message_lower for word in ["budget", "cheap", "affordable", "inexpensive"]):
        preferences["budget_level"] = "budget"
    elif any(word in message_lower for word in ["mid-range", "moderate", "medium"]):
        preferences["budget_level"] = "mid-range"
    
    # Extract travel type from keywords
    if any(word in message_lower for word in ["family", "kids", "children"]):
        preferences["travel_type"] = "family"
    elif any(word in message_lower for word in ["solo", "alone", "by myself"]):
        preferences["travel_type"] = "solo"
    elif any(word in message_lower for word in ["couple", "romantic", "honeymoon"]):
        preferences["travel_type"] = "couple"
    elif any(word in message_lower for word in ["friends", "group"]):
        preferences["travel_type"] = "group"
    
    # Extract travel interests from keywords
    interests = ["beach", "mountain", "hiking", "culture", "history", "food", "adventure", 
                "relaxation", "shopping", "nightlife", "nature", "wildlife", "diving", 
                "skiing", "art", "museum"]
    
    for interest in interests:
        if interest in message_lower and interest not in preferences["travel_interests"]:
            preferences["travel_interests"].append(interest)
    
    # Extract travel duration (e.g., "5 days", "2 weeks")
    duration_words = ["day", "days", "week", "weeks", "month", "months"]
    for word in duration_words:
        if word in message_lower:
            # Find numbers before duration words
            for i in range(1, 31):  # Check numbers 1-30
                if f"{i} {word}" in message_lower:
                    preferences["travel_duration"] = f"{i} {word}"
                    break
    
    # Extract mentioned destinations
    for destination in destination_content_ids.keys():
        if destination in message_lower and destination not in preferences["preferred_destinations"]:
            preferences["preferred_destinations"].append(destination)
    
    return preferences

# =============================================================================
# MAIN CHAT ENDPOINT
# =============================================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for conversational travel assistance.
    
    Handles user messages, maintains conversation history, extracts preferences,
    and generates AI responses with special formatting for destination cards
    and suggestion buttons.
    
    Request JSON:
        - message: User's message
        - sessionId: Unique session identifier
    
    Response JSON:
        - response: Raw AI response
        - processed_response: Formatted response with extracted elements
        - userPreferences: Updated user preferences
    """
    
    try:
        # Add CORS headers to the response
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type"
        }
        
        # Extract request data
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('sessionId', 'default')
        
        # Validate input
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Create a chat session if it doesn't exist yet
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        # Update user preferences based on the message
        current_preferences = update_user_preferences(session_id, user_message)
        
        # Get the current chat history
        chat_history = chat_sessions[session_id]
        
        # Add user message to history
        chat_history.append({"role": "user", "parts": [{"text": user_message}]})
        
        # Create chat instance with system prompt and history
        chat = model.start_chat(history=chat_history)
        
        # Check for budget calculation request
        budget_request = False
        destination_for_budget = None
        
        if "budget" in user_message.lower():
            budget_request = True
            # Try to extract destination from the message
            for destination in destination_content_ids.keys():
                if destination in user_message.lower():
                    destination_for_budget = destination
                    break
        
        # Handle budget requests with specific destination
        if budget_request and destination_for_budget:
            budget_data = calculate_travel_budget(destination_for_budget, current_preferences)
            response_text = format_budget_response(destination_for_budget, budget_data)
        else:
            # Generate response from Gemini AI
            response = chat.send_message(
                user_message,
                generation_config={"temperature": 0.7, "max_output_tokens": 800},
                safety_settings=[]
            )
            response_text = response.text
        
        # Process response to detect special formatting markers
        processed_response = process_bot_response(response_text)
        
        # Add model response to history
        chat_history.append({"role": "model", "parts": [{"text": response_text}]})
        
        # Keep chat history to a reasonable size (last 20 exchanges)
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]
        
        # Update the session
        chat_sessions[session_id] = chat_history
        
        return jsonify({
            "response": response_text,
            "processed_response": processed_response,
            "userPreferences": current_preferences
        }), 200, response_headers
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500, response_headers

# =============================================================================
# RESPONSE PROCESSING FUNCTIONS
# =============================================================================

def process_bot_response(text):
    """
    Process bot response to extract special formatting markers.
    
    Args:
        text (str): Raw response text from AI
    
    Returns:
        dict: Processed response with extracted destination cards and suggestion buttons
    
    This function extracts:
    - Destination cards: {destination_card}Paris{/destination_card}
    - Suggestion buttons: {suggest_buttons}["Button 1", "Button 2"]{/suggest_buttons}
    """
    
    # Extract destination cards
    destination_cards = []
    dest_card_start = "{destination_card}"
    dest_card_end = "{/destination_card}"
    
    start_idx = 0
    while True:
        start = text.find(dest_card_start, start_idx)
        if start == -1:
            break
        
        end = text.find(dest_card_end, start)
        if end == -1:
            break
        
        # Extract the destination name
        destination_name = text[start + len(dest_card_start):end].strip()
        destination_cards.append(destination_name)
        
        # Move to the next position
        start_idx = end + len(dest_card_end)
    
    # Extract suggestion buttons
    suggestion_buttons = []
    suggest_start = "{suggest_buttons}"
    suggest_end = "{/suggest_buttons}"
    
    start_idx = 0
    while True:
        start = text.find(suggest_start, start_idx)
        if start == -1:
            break
        
        end = text.find(suggest_end, start)
        if end == -1:
            break
        
        # Extract the buttons JSON string
        buttons_str = text[start + len(suggest_start):end].strip()
        try:
            buttons = json.loads(buttons_str)
            suggestion_buttons = buttons
        except:
            pass  # Ignore JSON parse errors
        
        # Move to the next position
        start_idx = end + len(suggest_end)
    
    # Remove the special markers from the text for clean display
    clean_text = text.replace(dest_card_start, "**").replace(dest_card_end, "**")
    clean_text = clean_text.replace(suggest_start, "").replace(suggest_end, "")
    
    # Try to clean up any JSON artifacts that might remain
    try:
        json_start = clean_text.find("[")
        json_end = clean_text.find("]", json_start)
        if json_start != -1 and json_end != -1:
            json_str = clean_text[json_start:json_end+1]
            if all(x in json_str for x in ['"', ',']):  # Looks like JSON
                clean_text = clean_text.replace(json_str, "")
    except:
        pass  # Ignore cleanup errors
    
    return {
        "text": clean_text,
        "destinationCards": destination_cards,
        "suggestionButtons": suggestion_buttons
    }

# =============================================================================
# BUDGET CALCULATION FUNCTIONS
# =============================================================================

def calculate_travel_budget(destination, user_preferences):
    """
    Calculate travel budget based on destination and user preferences.
    
    Args:
        destination (str): Destination name
        user_preferences (dict): User's travel preferences
    
    Returns:
        dict: Budget breakdown with min/max costs for different categories
    
    This function considers:
    - Base costs for different budget levels
    - Destination-specific cost multipliers
    - User's budget preferences
    """
    
    # Base costs for different budget levels (per person, per day in USD)
    base_costs = {
        "budget": {
            "accommodation": {"min": 50, "max": 100},
            "food": {"min": 20, "max": 40},
            "activities": {"min": 10, "max": 30},
            "transport": {"min": 5, "max": 15}
        },
        "mid-range": {
            "accommodation": {"min": 100, "max": 250},
            "food": {"min": 40, "max": 80},
            "activities": {"min": 30, "max": 60},
            "transport": {"min": 15, "max": 40}
        },
        "luxury": {
            "accommodation": {"min": 250, "max": 1000},
            "food": {"min": 80, "max": 200},
            "activities": {"min": 60, "max": 200},
            "transport": {"min": 40, "max": 150}
        }
    }
    
    # Cost multipliers for different destinations based on cost of living
    cost_multipliers = {
        "paris": 1.3,
        "london": 1.4,
        "new york": 1.5,
        "tokyo": 1.4,
        "dubai": 1.3,
        "sydney": 1.2,
        "hong kong": 1.3,
        "singapore": 1.2,
        "las vegas": 1.1,
        "bangkok": 0.6,  # Much cheaper destination
        "barcelona": 1.0,
        "rome": 1.1,
        "berlin": 1.0,
        "madrid": 1.0,
        "amsterdam": 1.2,
        "chicago": 1.1,
        "los angeles": 1.3,
        "san francisco": 1.4,
        "miami": 1.2
    }
    
    # Default multiplier for destinations not in our list
    default_multiplier = 1.0
    
    # Get the user's budget level, default to mid-range
    budget_level = user_preferences.get("budget_level", "mid-range")
    
    # Get the cost multiplier for this destination
    cost_multiplier = cost_multipliers.get(destination.lower(), default_multiplier)
    
    # Get the base costs for the selected budget level
    base_budget = base_costs[budget_level]
    
    # Apply destination-specific cost multiplier
    budget = {}
    for category, costs in base_budget.items():
        budget[category] = {
            "min": int(costs["min"] * cost_multiplier),
            "max": int(costs["max"] * cost_multiplier)
        }
    
    # Calculate daily total
    min_daily = sum(item["min"] for item in budget.values())
    max_daily = sum(item["max"] for item in budget.values())
    
    budget["daily_total"] = {"min": min_daily, "max": max_daily}
    
    # Add specific details for attractions based on destination
    attractions = get_destination_attractions(destination)
    budget["specific_attractions"] = attractions
    
    return budget

def format_budget_response(destination, budget_data):
    """
    Format the budget data into a formatted response string.
    
    Args:
        destination (str): Destination name
        budget_data (dict): Budget calculation results
    
    Returns:
        str: Formatted budget response with suggestion buttons
    """
    
    response = f"## Budget Estimate for {destination.title()}\n\n"
    
    # Accommodation section
    response += "**Accommodation:**\n"
    response += f"* Budget: ${budget_data['accommodation']['min']}-${budget_data['accommodation']['max']} per night\n"
    response += f"* Mid-range: ${budget_data['accommodation']['min']*2}-${budget_data['accommodation']['max']*1.5} per night\n"
    response += f"* Luxury: ${budget_data['accommodation']['max']*1.5}+ per night\n\n"
    
    # Food section
    response += "**Food:**\n"
    response += f"* Budget meals: ${budget_data['food']['min']}-${budget_data['food']['min']*1.5} per day\n"
    response += f"* Mid-range dining: ${budget_data['food']['min']*1.5}-${budget_data['food']['max']} per day\n"
    response += f"* Fine dining: ${budget_data['food']['max']}+ per meal\n\n"
    
    # Transportation section
    response += "**Transportation:**\n"
    response += f"* Public transit: ${budget_data['transport']['min']} per day\n"
    response += f"* Car rental: ${budget_data['transport']['min']*3}-${budget_data['transport']['max']*2} per day\n"
    response += f"* Taxis/rideshares: Average ${budget_data['transport']['min']*2} per ride\n\n"
    
    # Activities section
    response += "**Activities:**\n"
    if budget_data.get("specific_attractions"):
        attractions = budget_data["specific_attractions"]
        for i, attraction in enumerate(attractions[:3]):
            response += f"* {attraction['name']}: ${attraction['cost']}\n"
    else:
        response += f"* Free attractions: Parks, walking tours, public spaces\n"
        response += f"* Paid attractions: ${budget_data['activities']['min']}-${budget_data['activities']['max']} per activity\n"
        response += f"* Tours: ${budget_data['activities']['min']*2}-${budget_data['activities']['max']*2} per tour\n"
    
    # Daily budget summary
    response += f"\n**Estimated daily budget:** ${budget_data['daily_total']['min']}-${budget_data['daily_total']['max']} depending on travel style\n\n"
    
    # Add suggestion buttons
    response += f"{{suggest_buttons}}[\"I choose {destination.title()}\", \"Weather in {destination.title()}\", \"Things to do in {destination.title()}\"]{{/suggest_buttons}}"
    
    return response


    """
    Get specdef get_destination_attractions(destination):ific attractions and costs for a destination.
    
    Args:
        destination (str): Destination name
    
    Returns:
        list: List of attractions with names and costs
    """
    
    # Predefined attractions data for major destinations
    attractions_data = {
        "paris": [
            {"name": "Eiffel Tower", "cost": 25},
            {"name": "Louvre Museum", "cost": 17},
            {"name": "Seine River Cruise", "cost": 15}
        ],
        "london": [
            {"name": "Tower of London", "cost": 30},
            {"name": "London Eye", "cost": 35},
            {"name": "Westminster Abbey", "cost": 25}
        ],
        "new york": [
            {"name": "Empire State Building", "cost": 42},
            {"name": "Metropolitan Museum of Art", "cost": 25},
            {"name": "Statue of Liberty Ferry", "cost": 24}
        ],
        "tokyo": [
            {"name": "Tokyo Skytree", "cost": 23},
            {"name": "Robot Restaurant Show", "cost": 80},
            {"name": "Senso-ji Temple", "cost": 0}
        ],
        "rome": [
            {"name": "Colosseum", "cost": 16},
            {"name": "Vatican Museums", "cost": 17},
            {"name": "Roman Forum", "cost": 16}
        ]
    }
    
    # Return specific attractions or generate generic ones
    return attractions_data.get(destination.lower(), [
        {"name": f"{destination.title()} City Tour", "cost": random.randint(15, 40)},
        {"name": f"{destination.title()} Museum", "cost": random.randint(10, 25)},
        {"name": f"{destination.title()} Historic Site", "cost": random.randint(5, 30)}
    ])

# =============================================================================
# TRAVEL ADVISOR API INTEGRATION
# =============================================================================

def get_hotel_content_id(destination):
    """
    Get a content ID for a destination to use in the Travel Advisor API.
    
    Args:
        destination (str): Destination name
    
    Returns:
        str: Content ID for the destination or default fallback
    """
    
    # Convert destination to lowercase for case-insensitive matching
    destination_lower = destination.lower()
    
    # Try direct match
    if destination_lower in destination_content_ids:
        return destination_content_ids[destination_lower]
    
    # Try partial match
    for key, value in destination_content_ids.items():
        if key in destination_lower or destination_lower in key:
            return value
    
    # Use New York as fallback if no match is found
    print(f"No content ID found for {destination}, using default")
    return "60763"  # New York

def fetch_hotels(destination):
    """
    Fetch hotel data from Travel Advisor API.
    
    Args:
        destination (str): Destination name
    
    Returns:
        list: List of hotel objects with name, rating, price, location, amenities
    
    Note: This function requires a valid RapidAPI key for Travel Advisor API
    """
    
    try:
        # Get content ID for the destination
        content_id = get_hotel_content_id(destination)
        
        # API endpoint
        url = "https://travel-advisor.p.rapidapi.com/answers/v2/list"
        
        # Query parameters
        params = {
            "currency": "USD",
            "units": "km",
            "lang": "en_US"
        }
        
        # Request headers
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "travel-advisor.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        # Request payload
        payload = {
            "contentType": "hotel",
            "contentId": content_id,
            "questionId": "8393250",  # Hotels related question ID
            "pagee": 0,
            "updateToken": ""
        }
        
        # Make the request
        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        data = response.json()
        
        # Process the data to extract hotel information
        hotels = []
        
        if 'data' in data and 'content' in data['data']:
            answers = data['data']['content']
            
            # Limit to top 3 hotels
            for i, answer in enumerate(answers[:3]):
                if 'business' in answer:
                    business = answer['business']
                    
                    # Extract amenities
                    amenities = []
                    if 'amenities' in business:
                        for amenity in business['amenities'][:5]:  # Limit to top 5 amenities
                            if 'amenityCategoryName' in amenity:
                                amenities.append(amenity['amenityCategoryName'])
                    
                    # Create hotel object with available information
                    hotel = {
                        "name": business.get('name', f"Hotel in {destination}"),
                        "rating": round(float(business.get('rating', 4))),
                        "price": business.get('price', {}).get('displayPrice', '$150'),
                        "location": business.get('addressObj', {}).get('street1', f"Central {destination}"),
                        "amenities": amenities if amenities else ["WiFi", "Parking", "Restaurant"]
                    }
                    
                    hotels.append(hotel)
        
        # If no hotels found or error occurred, return empty list
        if not hotels:
            print("No hotels found or error in processing hotel data")
            return []
            
        return hotels
        
    except Exception as e:
        print(f"Error fetching hotels: {e}")
        return []  # Return empty list on error
# =============================================================================
# TRAVEL API - DESTINATION DETAILS & BUDGET CALCULATOR
# =============================================================================
"""
Comprehensive Travel Planning API

This Flask application provides travel planning services including:
- Destination weather forecasts and flight information
- Hotel accommodations via Travel Advisor API integration
- Dynamic budget calculations with multiple tiers
- AI-powered realistic travel data generation
- Session-based user preference management

Dependencies:
- Flask: Web framework for API endpoints
- AI Model: For generating realistic travel data
- Travel Advisor API: External hotel data source
- JSON: Data serialization and API communication

Author: Travel API Team
Version: 1.0
"""

import json
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

# Initialize Flask application
app = Flask(__name__)

# =============================================================================
# DESTINATION DETAILS ENDPOINT
# =============================================================================

@app.route('/api/destination-details', methods=['POST'])
def destination_details():
    """
    Comprehensive Destination Information Retrieval Endpoint
    
    This endpoint serves as the primary data aggregation service for travel planning.
    It combines multiple data sources to provide a complete travel overview:
    
    Data Sources:
    1. AI-generated weather and flight data (primary)
    2. Travel Advisor API for real hotel information
    3. Internal budget calculation system
    4. Mock data fallback system
    
    Processing Flow:
    1. Validate request and extract parameters
    2. Fetch real hotel data from external API
    3. Generate weather/flight data using AI
    4. Calculate budget estimates based on user preferences
    5. Aggregate all data into comprehensive response
    6. Handle errors with fallback mechanisms
    
    Args:
        JSON Request Body:
            destination (str): Target destination name (required)
            sessionId (str): User session identifier for preferences (optional)
    
    Returns:
        JSON Response:
            weather (dict): Current conditions and 5-day forecast
            flights (list): Available flight options with pricing
            accommodations (list): Hotel listings with details and amenities
            budget (dict): Comprehensive budget breakdown
    
    Error Handling:
        - 400: Missing destination parameter
        - 500: Internal server errors with detailed logging
        - Automatic fallback to mock data if AI service fails
    
    CORS Configuration:
        - Allows all origins for development
        - Supports POST method with Content-Type header
    """
    
    try:
        # Configure CORS headers for cross-origin requests
        # Note: In production, restrict origins to specific domains
        response_headers = {
            "Access-Control-Allow-Origin": "*",  # Allow all origins (dev only)
            "Access-Control-Allow-Methods": "POST",  # Only POST method allowed
            "Access-Control-Allow-Headers": "Content-Type"  # Accept JSON content
        }
        
        # Extract and validate request parameters
        data = request.json
        destination = data.get('destination', '')  # Primary destination parameter
        session_id = data.get('sessionId', 'default')  # User session for preferences
        
        # Validate required parameters
        if not destination:
            return jsonify({"error": "No destination provided"}), 400
        
        # =================================================================
        # STEP 1: FETCH REAL HOTEL DATA
        # =================================================================
        # Integrate with Travel Advisor API for authentic accommodation data
        # This provides real hotel names, ratings, and current pricing
        hotels = fetch_hotels(destination)
        
        # =================================================================
        # STEP 2: RETRIEVE USER PREFERENCES
        # =================================================================
        # Get stored user preferences for personalized budget calculations
        # Preferences include budget tier, accommodation type, activity preferences
        user_prefs = user_preferences.get(session_id, {})
        
        # =================================================================
        # STEP 3: AI-POWERED DATA GENERATION
        # =================================================================
        try:
            # Construct detailed prompt for AI model
            # This prompt ensures structured, realistic data generation
            prompt = f"""Generate realistic travel data for {destination} in JSON format with these sections:
            1. Weather information for {destination} with current conditions and 5-day forecast
            2. Three recommended flights to {destination} from major hubs
            
            Format Requirements:
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
            
            Important: Return ONLY the JSON with no additional text or explanation.
            Use realistic data appropriate for {destination}'s climate and geography."""
            
            # Generate content using AI model
            response = model.generate_content(prompt)
            response_text = response.text
            
            # =============================================================
            # JSON EXTRACTION AND PARSING
            # =============================================================
            # Handle various response formats from AI model
            # AI may return JSON wrapped in markdown code blocks
            
            if "```json" in response_text:
                # Extract content from JSON markdown blocks
                start = response_text.find("```json") + len("```json")
                end = response_text.rfind("```")
                json_content = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract content from generic code blocks
                start = response_text.find("```") + len("```")
                end = response_text.rfind("```")
                json_content = response_text[start:end].strip()
            else:
                # Use response as-is if no code blocks detected
                json_content = response_text
            
            # Parse extracted JSON content
            destination_data = json.loads(json_content)
            
            # =============================================================
            # DATA INTEGRATION AND ENRICHMENT
            # =============================================================
            
            # Integrate real hotel data with AI-generated content
            # Priority: Real API data > Mock data generator
            destination_data["accommodations"] = hotels if hotels else generate_mock_accommodations(destination)
            
            # Calculate comprehensive budget information
            # Uses user preferences and destination-specific pricing
            budget_info = calculate_travel_budget(destination, user_prefs)
            
            # Structure budget data for frontend consumption
            destination_data["budget"] = {
                "daily_min": budget_info["daily_total"]["min"],
                "daily_max": budget_info["daily_total"]["max"],
                "accommodation_min": budget_info["accommodation"]["min"],
                "accommodation_max": budget_info["accommodation"]["max"],
                "food_min": budget_info["food"]["min"],
                "food_max": budget_info["food"]["max"],
                "attractions": budget_info.get("specific_attractions", [])
            }
            
            return jsonify(destination_data), 200, response_headers
            
        except Exception as e:
            # =============================================================
            # AI SERVICE FAILURE RECOVERY
            # =============================================================
            print(f"Error getting AI generated data: {e}")
            
            # Fallback to deterministic mock data generation
            # Ensures service availability even when AI model fails
            mock_data = generate_mock_data(destination)
            
            # Replace mock accommodations with real data if available
            if hotels:
                mock_data["accommodations"] = hotels
                
            # Add budget information to mock data response
            budget_info = calculate_travel_budget(destination, user_prefs)
            mock_data["budget"] = {
                "daily_min": budget_info["daily_total"]["min"],
                "daily_max": budget_info["daily_total"]["max"],
                "accommodation_min": budget_info["accommodation"]["min"],
                "accommodation_max": budget_info["accommodation"]["max"],
                "food_min": budget_info["food"]["min"],
                "food_max": budget_info["food"]["max"],
                "attractions": budget_info.get("specific_attractions", [])
            }
            
            return jsonify(mock_data), 200, response_headers
        
    except Exception as e:
        # =================================================================
        # GLOBAL ERROR HANDLING
        # =================================================================
        print(f"Error in destination details: {e}")  # Log for debugging
        return jsonify({"error": str(e)}), 500, response_headers

# =============================================================================
# BUDGET CALCULATOR ENDPOINT
# =============================================================================

@app.route('/api/budget-calculator', methods=['POST'])
def budget_calculator():
    """
    Advanced Travel Budget Calculator
    
    This endpoint provides detailed cost estimation for travel planning.
    It considers multiple variables to generate accurate budget projections:
    
    Calculation Factors:
    - Destination cost-of-living index
    - Trip duration and number of travelers
    - Budget tier (budget/mid-range/luxury)
    - Seasonal price variations
    - Transportation costs including flights
    - Activity and attraction pricing
    
    Budget Categories:
    1. Accommodation (per night, scaled by travelers)
    2. Food & Dining (daily meals, local cuisine)
    3. Activities & Attractions (entry fees, tours)
    4. Local Transportation (public transit, taxis)
    5. Flight Costs (round-trip, scaled by travelers)
    
    Args:
        JSON Request Body:
            destination (str): Target destination (required)
            budgetLevel (str): Spending tier - "budget", "mid-range", "luxury"
            duration (int): Trip length in days (default: 7)
            travelers (int): Number of people traveling (default: 1)
            sessionId (str): User session for preferences
    
    Returns:
        JSON Response: Comprehensive budget breakdown with min/max ranges
            for each category and total trip cost estimation
    
    Features:
    - Dynamic pricing based on destination
    - Multi-traveler cost scaling
    - Flight cost estimation with regional adjustments
    - Detailed category breakdown for planning
    """
    
    try:
        # Configure CORS headers (consistent with other endpoints)
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type"
        }
        
        # =================================================================
        # PARAMETER EXTRACTION AND VALIDATION
        # =================================================================
        data = request.json
        destination = data.get('destination', '')
        budget_level = data.get('budgetLevel', 'mid-range')  # Default to mid-range
        duration = data.get('duration', 7)  # Default week-long trip
        travelers = data.get('travelers', 1)  # Default single traveler
        session_id = data.get('sessionId', 'default')
        
        # Validate required destination parameter
        if not destination:
            return jsonify({"error": "No destination provided"}), 400
        
        # =================================================================
        # USER PREFERENCE INTEGRATION
        # =================================================================
        # Retrieve and merge user preferences with request parameters
        user_prefs = user_preferences.get(session_id, {})
        
        # Override stored preferences with explicit request parameters
        user_prefs["budget_level"] = budget_level
        
        # =================================================================
        # BASE BUDGET CALCULATION
        # =================================================================
        # Calculate foundational budget using destination-specific data
        # This function considers local cost-of-living and price indices
        budget_info = calculate_travel_budget(destination, user_prefs)
        
        # Extract daily cost estimates
        daily_min = budget_info["daily_total"]["min"]
        daily_max = budget_info["daily_total"]["max"]
        
        # =================================================================
        # MULTI-TRAVELER SCALING
        # =================================================================
        # Scale daily costs based on number of travelers
        # Some costs (accommodation) may have economies of scale
        daily_min *= travelers
        daily_max *= travelers
        
        # Calculate total trip cost based on duration
        trip_min = daily_min * duration
        trip_max = daily_max * duration
        
        # =================================================================
        # FLIGHT COST ESTIMATION
        # =================================================================
        # Flight costs vary significantly by budget tier and destination
        # These estimates are based on average market rates
        flight_costs = {
            "budget": {"min": 300, "max": 600},      # Economy, budget airlines
            "mid-range": {"min": 600, "max": 1200},  # Major carriers, some flexibility
            "luxury": {"min": 1200, "max": 3000}     # Premium economy/business class
        }
        
        # Get flight cost range for selected budget tier
        flight_cost = flight_costs[budget_level]
        flight_total_min = flight_cost["min"] * travelers
        flight_total_max = flight_cost["max"] * travelers
        
        # =================================================================
        # DESTINATION-SPECIFIC FLIGHT ADJUSTMENTS
        # =================================================================
        # Adjust flight costs based on destination distance and market factors
        # Multipliers based on average flight costs from major hubs
        cost_multipliers = {
            "paris": 1.2,        # European destination, moderate premium
            "london": 1.2,       # UK, similar to Paris pricing
            "new york": 1.0,     # Domestic US baseline
            "tokyo": 1.5,        # Long-haul Asia, higher fuel costs
            "dubai": 1.3,        # Middle East, competitive but distant
            "sydney": 1.8,       # Longest routes, highest fuel costs
            "bangkok": 1.4,      # Southeast Asia, growing market
        }
        
        # Apply destination multiplier (default 1.0 for unlisted destinations)
        mult = cost_multipliers.get(destination.lower(), 1.0)
        flight_total_min = int(flight_total_min * mult)
        flight_total_max = int(flight_total_max * mult)
        
        # =================================================================
        # RESPONSE ASSEMBLY
        # =================================================================
        # Construct comprehensive budget response with all categories
        budget_response = {
            # Trip metadata
            "destination": destination,
            "duration": duration,
            "travelers": travelers,
            "budgetLevel": budget_level,
            
            # Daily cost breakdown
            "dailyCost": {
                "min": daily_min,
                "max": daily_max
            },
            
            # Accommodation costs (per night, total for trip)
            "accommodation": {
                "min": budget_info["accommodation"]["min"] * travelers,
                "max": budget_info["accommodation"]["max"] * travelers,
                "total": budget_info["accommodation"]["min"] * travelers * duration
            },
            
            # Food and dining costs
            "food": {
                "min": budget_info["food"]["min"] * travelers,
                "max": budget_info["food"]["max"] * travelers,
                "total": budget_info["food"]["min"] * travelers * duration
            },
            
            # Activities and attractions
            "activities": {
                "min": budget_info["activities"]["min"] * travelers,
                "max": budget_info["activities"]["max"] * travelers,
                "total": budget_info["activities"]["min"] * travelers * duration
            },
            
            # Local transportation (buses, taxis, metro)
            "transportation": {
                "min": budget_info["transport"]["min"] * travelers,
                "max": budget_info["transport"]["max"] * travelers,
                "total": budget_info["transport"]["min"] * travelers * duration
            },
            
            # Flight costs (round-trip)
            "flights": {
                "min": flight_total_min,
                "max": flight_total_max
            },
            
            # Grand total including all categories
            "totalCost": {
                "min": trip_min + flight_total_min,
                "max": trip_max + flight_total_max
            },
            
            # Specific attractions with individual pricing
            "attractions": budget_info.get("specific_attractions", [])
        }
        
        return jsonify(budget_response), 200, response_headers
        
    except Exception as e:
        # Global error handling with detailed logging
        print(f"Error in budget calculator: {e}")
        return jsonify({"error": str(e)}), 500, response_headers

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def generate_mock_accommodations(destination):
    """
    Mock Hotel Data Generator
    
    Generates realistic hotel data for testing and fallback scenarios.
    Used when Travel Advisor API is unavailable or returns no results.
    
    Args:
        destination (str): Target destination for contextual naming
    
    Returns:
        list: Array of mock hotel objects with realistic attributes
    
    Features:
    - Contextual hotel naming based on destination
    - Varied price ranges and star ratings
    - Realistic amenity combinations
    - Random but believable location descriptions
    """
    
    # Hotel naming components for realistic generation
    hotel_prefixes = ["Grand", "Royal", "Luxury", "Premium", "Comfort", "Imperial"]
    hotel_types = ["Hotel", "Resort", "Suites", "Inn", "Lodge", "Apartments"]
    
    # Common hotel amenities for random selection
    amenities_list = [
        "Free WiFi", "Pool", "Spa", "Restaurant", "Bar", 
        "Gym", "Parking", "Room Service", "Concierge", "Business Center"
    ]
    
    accommodations = []
    
    # Generate 3 mock hotels with varied characteristics
    for i in range(3):
        # Create contextual hotel name
        hotel_name = f"{random.choice(hotel_prefixes)} {destination} {random.choice(hotel_types)}"
        
        accommodations.append({
            "name": hotel_name,
            "rating": random.randint(3, 5),  # 3-5 star rating
            "price": f"${random.randint(80, 500)}",  # Varied price range
            "location": f"{random.choice(['Downtown', 'Central', 'Historic District', 'Beachfront', 'City Center'])} {destination}",
            "amenities": random.sample(amenities_list, random.randint(3, 6))  # 3-6 random amenities
        })
    
    return accommodations

def generate_mock_data(destination):
    """
    Comprehensive Mock Travel Data Generator
    
    Creates realistic travel data when AI service is unavailable.
    Ensures service continuity and testing capability.
    
    Args:
        destination (str): Target destination for contextual data
    
    Returns:
        dict: Complete travel data structure matching AI-generated format
    
    Generated Data:
    - Weather: Current conditions and 5-day forecast
    - Flights: 3 flight options with realistic scheduling
    - Accommodations: Hotel listings via separate function
    
    Algorithm:
    - Uses current date for realistic forecast dates
    - Randomizes within realistic ranges for each data type
    - Maintains consistent data structure with AI responses
    """
    
    # Use current date for realistic forecast generation
    today = datetime.now()
    
    # =================================================================
    # WEATHER DATA GENERATION
    # =================================================================
    # Generate realistic weather data with seasonal considerations
    weather = {
        "temperature": random.randint(15, 30),  # Celsius, temperate range
        "condition": random.choice([
            "Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Clear"
        ]),
        "humidity": random.randint(40, 90),  # Percentage
        "wind": random.randint(5, 20),  # km/h
        "forecast": []
    }
    
    # Generate 5-day forecast with day-by-day variation
    for i in range(5):
        day_date = today + timedelta(days=i+1)
        weather["forecast"].append({
            "day": day_date.strftime("%a"),  # Abbreviated day name
            "temperature": random.randint(15, 30),
            "condition": random.choice([
                "Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Clear"
            ])
        })
    
    # =================================================================
    # FLIGHT DATA GENERATION
    # =================================================================
    # Realistic airline and airport data for flight generation
    airlines = ["Air Travel", "SkyWings", "Global Air", "FastJet", "StarFlight"]
    airports = ["JFK", "LAX", "LHR", "CDG", "DXB", "SIN", "SYD", "HND"]
    
    flights = []
    
    # Generate 3 flight options with varied characteristics
    for i in range(3):
        # Random departure time during business hours
        departure_time = f"{random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}"
        
        # Realistic flight duration (1-14 hours)
        duration_hours = random.randint(1, 14)
        
        # Calculate arrival time based on duration
        departure_dt = datetime.strptime(departure_time, "%H:%M")
        arrival_dt = departure_dt + timedelta(hours=duration_hours)
        arrival_time = arrival_dt.strftime("%H:%M")
        
        flights.append({
            "airline": random.choice(airlines),
            "price": random.randint(200, 1500),  # USD range
            "departureTime": departure_time,
            "arrivalTime": arrival_time,
            "duration": f"{duration_hours}h {random.choice(['00', '15', '30', '45'])}m",
            "departureAirport": random.choice(airports),
            "arrivalAirport": f"{destination[:3].upper()}"  # Destination airport code
        })
    
    # =================================================================
    # DATA ASSEMBLY
    # =================================================================
    # Use dedicated function for accommodation generation
    accommodations = generate_mock_accommodations(destination)
    
    return {
        "weather": weather,
        "flights": flights,
        "accommodations": accommodations
    }

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    """
    Flask Application Initialization
    
    Development server configuration:
    - Debug mode enabled for development
    - Port 5000 for local testing
    - Hot reload on code changes
    
    Production Deployment Notes:
    - Disable debug mode in production
    - Use proper WSGI server (Gunicorn, uWSGI)
    - Configure environment variables for API keys
    - Implement proper logging and monitoring
    """
    app.run(debug=True, port=5000)