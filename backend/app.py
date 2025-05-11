from flask import Flask, request, jsonify, send_from_directory
import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
import json
import random
from datetime import datetime, timedelta
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
print("Loaded API key:", os.getenv("GEMINI_API_KEY"))

# RapidAPI Key
RAPIDAPI_KEY = "TRAVEL_ADVISOR_KEY"  

# Define the system prompt
system_prompt = """You are TravelMate, a friendly travel assistant. Respond to greetings naturally, 
and for travel requests provide:
## Recommended Destinations:

1. **{Destination Name}**
   * **Highlights:** {Brief description of main attractions}
   * **Perfect for:** {Type of travelers}
   * **Best time to visit:** {Best season}

2. **{Destination Name}**
   * **Highlights:** {Brief description of main attractions}
   * **Perfect for:** {Type of travelers}
   * **Best time to visit:** {Best season}

3. **{Destination Name}**
   * **Highlights:** {Brief description of main attractions}
   * **Perfect for:** {Type of travelers}
   * **Best time to visit:** {Best season}

If someone asks about a specific destination, provide information in this format:

## {Destination Name}

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

Remember to inform users they can get detailed information by typing "I choose {destination name}"."""

# Set up the model
model = genai.GenerativeModel(
    'gemini-2.0-flash',
    system_instruction=system_prompt,
)

# Store chat sessions by user (in a real app, you'd use a database)
chat_sessions = {}

# Mapping of common destinations to their Travel Advisor contentIds
# This is a simplified approach - in a real app, you'd use a search API to find the destination ID
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

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Add CORS headers to the response
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type"
        }
        
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('sessionId', 'default')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400


        # Create a chat session if it doesn't exist yet
        if session_id not in chat_sessions:
            chat_sessions[session_id] = []
        
        # Get the current chat history
        chat_history = chat_sessions[session_id]
        
        # Add user message to history
        chat_history.append({"role": "user", "parts": [{"text": user_message}]})
        
        # Create chat instance with system prompt
        chat = model.start_chat(history=chat_history)
        
        # Generate response
        response = chat.send_message(
            user_message,
            generation_config={"temperature": 0.7, "max_output_tokens": 800},
            safety_settings=[]
        )
        
        # Add model response to history
        response_text = response.text
        chat_history.append({"role": "model", "parts": [{"text": response_text}]})
        
        # Keep chat history to a reasonable size (last 10 exchanges)
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]
        
        # Update the session
        chat_sessions[session_id] = chat_history
        
        return jsonify({"response": response_text}), 200, response_headers
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500, response_headers

def get_hotel_content_id(destination):
    """Get a content ID for a destination to use in the Travel Advisor API"""
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
    # In a real app, you'd use a search API to find the correct ID
    print(f"No content ID found for {destination}, using default")
    return "60763"  # New York

def fetch_hotels(destination):
    """Fetch hotel data from Travel Advisor API"""
    try:
        # Get content ID for the destination
        content_id = get_hotel_content_id(destination)
        
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

@app.route('/api/destination-details', methods=['POST'])
def destination_details():
    try:
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type"
        }
        
        data = request.json
        destination = data.get('destination', '')
        
        if not destination:
            return jsonify({"error": "No destination provided"}), 400
        
        # Get hotel data from Travel Advisor API
        hotels = fetch_hotels(destination)
        
        # Generate weather and flights data (still mock for this example)
        # In a real app, you would integrate with weather and flight APIs as well
        
        # Generate mock data for Gemini API (in a real app, you'd use real API calls)
        try:
            # Generate realistic data using Gemini
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
            
            response = model.generate_content(prompt)
            
            # Try to extract JSON from the response
            response_text = response.text
            
            # Handle potential markdown code block formatting
            if "```json" in response_text:
                # Extract content between markdown code blocks
                start = response_text.find("```json") + len("```json")
                end = response_text.rfind("```")
                json_content = response_text[start:end].strip()
            elif "```" in response_text:
                # Extract content between generic code blocks
                start = response_text.find("```") + len("```")
                end = response_text.rfind("```")
                json_content = response_text[start:end].strip()
            else:
                # Use the response as is
                json_content = response_text
            
            # Parse the JSON
            destination_data = json.loads(json_content)
            
            # Add our real hotel data to the response
            destination_data["accommodations"] = hotels if hotels else generate_mock_accommodations(destination)
            
            return jsonify(destination_data), 200, response_headers
            
        except Exception as e:
            print(f"Error getting AI generated data: {e}")
            # Fallback to static mock data
            mock_data = generate_mock_data(destination)
            # Replace mock accommodations with real data if available
            if hotels:
                mock_data["accommodations"] = hotels
            return jsonify(mock_data), 200, response_headers
        
    except Exception as e:
        print(f"Error in destination details: {e}")
        return jsonify({"error": str(e)}), 500, response_headers

def generate_mock_accommodations(destination):
    """Generate mock accommodations data for testing"""
    hotel_prefixes = ["Grand", "Royal", "Luxury", "Premium", "Comfort", "Imperial"]
    hotel_types = ["Hotel", "Resort", "Suites", "Inn", "Lodge", "Apartments"]
    amenities_list = ["Free WiFi", "Pool", "Spa", "Restaurant", "Bar", "Gym", "Parking", "Room Service"]
    
    accommodations = []
    for i in range(3):
        hotel_name = f"{random.choice(hotel_prefixes)} {destination} {random.choice(hotel_types)}"
        accommodations.append({
            "name": hotel_name,
            "rating": random.randint(3, 5),
            "price": f"${random.randint(80, 500)}",
            "location": f"{random.choice(['Downtown', 'Central', 'Historic District', 'Beachfront', 'City Center'])} {destination}",
            "amenities": random.sample(amenities_list, random.randint(3, 6))
        })
    
    return accommodations

def generate_mock_data(destination):
    """Generate mock travel data for testing when AI generation fails"""
    
    # Current date for realistic data
    today = datetime.now()
    
    # Mock weather data
    weather = {
        "temperature": random.randint(15, 30),
        "condition": random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Clear"]),
        "humidity": random.randint(40, 90),
        "wind": random.randint(5, 20),
        "forecast": []
    }
    
    # Generate 5-day forecast
    for i in range(5):
        day_date = today + timedelta(days=i+1)
        weather["forecast"].append({
            "day": day_date.strftime("%a"),
            "temperature": random.randint(15, 30),
            "condition": random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Clear"])
        })
    
    # Mock flights data
    airlines = ["Air Travel", "SkyWings", "Global Air", "FastJet", "StarFlight"]
    airports = ["JFK", "LAX", "LHR", "CDG", "DXB", "SIN", "SYD", "HND"]
    
    flights = []
    for i in range(3):
        departure_time = f"{random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}"
        duration_hours = random.randint(1, 14)
        
        departure_dt = datetime.strptime(departure_time, "%H:%M")
        arrival_dt = departure_dt + timedelta(hours=duration_hours)
        arrival_time = arrival_dt.strftime("%H:%M")
        
        flights.append({
            "airline": random.choice(airlines),
            "price": random.randint(200, 1500),
            "departureTime": departure_time,
            "arrivalTime": arrival_time,
            "duration": f"{duration_hours}h {random.choice(['00', '15', '30', '45'])}m",
            "departureAirport": random.choice(airports),
            "arrivalAirport": f"{destination[:3].upper()}"
        })
    
    # Use the separate function for accommodations
    accommodations = generate_mock_accommodations(destination)
    
    return {
        "weather": weather,
        "flights": flights,
        "accommodations": accommodations
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)