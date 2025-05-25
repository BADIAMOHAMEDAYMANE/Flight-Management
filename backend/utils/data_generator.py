"""
Data Generator Utilities
Generates mock data for testing and fallback scenarios
"""

import random
from datetime import datetime, timedelta


class DataGenerator:
    """Utility class for generating mock travel data"""
    
    @staticmethod
    def generate_mock_accommodations(destination):
        """
        Generate mock accommodations data for testing.
        
        Args:
            destination (str): Destination name
        
        Returns:
            list: List of mock hotel objects
        """
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
    
    @staticmethod
    def generate_mock_weather():
        """
        Generate mock weather data.
        
        Returns:
            dict: Mock weather data with current conditions and forecast
        """
        today = datetime.now()
        
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
        
        return weather
    
    @staticmethod
    def generate_mock_flights():
        """
        Generate mock flight data.
        
        Returns:
            list: List of mock flight objects
        """
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
                "arrivalAirport": f"DST"  # Generic destination airport
            })
        
        return flights
    
    @staticmethod
    def generate_mock_data(destination):
        """
        Generate comprehensive mock travel data for testing.
        
        Args:
            destination (str): Destination name
        
        Returns:
            dict: Complete mock travel data including weather, flights, accommodations
        """
        return {
            "weather": DataGenerator.generate_mock_weather(),
            "flights": DataGenerator.generate_mock_flights(),
            "accommodations": DataGenerator.generate_mock_accommodations(destination)
        }