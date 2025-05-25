"""
Travel Advisor API Service
Handles integration with Travel Advisor API for hotel data
"""

import requests
import random
from utils.constants import DESTINATION_CONTENT_IDS
from config.settings import Config


class TravelAdvisorService:
    """Service for interacting with Travel Advisor API"""
    
    def __init__(self):
        self.api_key = Config.RAPIDAPI_KEY
        self.base_url = "https://travel-advisor.p.rapidapi.com"
    
    def get_hotel_content_id(self, destination):
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
        if destination_lower in DESTINATION_CONTENT_IDS:
            return DESTINATION_CONTENT_IDS[destination_lower]
        
        # Try partial match
        for key, value in DESTINATION_CONTENT_IDS.items():
            if key in destination_lower or destination_lower in key:
                return value
        
        # Use New York as fallback if no match is found
        print(f"No content ID found for {destination}, using default")
        return "60763"  # New York
    
    def fetch_hotels(self, destination):
        """
        Fetch hotel data from Travel Advisor API.
        
        Args:
            destination (str): Destination name
        
        Returns:
            list: List of hotel objects with name, rating, price, location, amenities
        """
        try:
            # Get content ID for the destination
            content_id = self.get_hotel_content_id(destination)
            
            # API endpoint
            url = f"{self.base_url}/answers/v2/list"
            
            # Query parameters
            params = {
                "currency": "USD",
                "units": "km",
                "lang": "en_US"
            }
            
            # Request headers
            headers = {
                "x-rapidapi-key": self.api_key,
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
            response.raise_for_status()
            
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
                            for amenity in business['amenities'][:5]:
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
            return []