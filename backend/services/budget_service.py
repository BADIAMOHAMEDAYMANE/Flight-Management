"""
Budget Service
Handles budget calculations and travel cost estimates
"""

import random
from utils.constants import BASE_COSTS, COST_MULTIPLIERS, ATTRACTIONS_DATA


class BudgetService:
    """Service for calculating travel budgets"""
    
    def calculate_travel_budget(self, destination, user_preferences):
        """
        Calculate travel budget based on destination and user preferences.
        
        Args:
            destination (str): Destination name
            user_preferences (dict): User's travel preferences
        
        Returns:
            dict: Budget breakdown with min/max costs for different categories
        """
        # Get the user's budget level, default to mid-range
        budget_level = user_preferences.get("budget_level", "mid-range")
        
        # Get the cost multiplier for this destination
        cost_multiplier = COST_MULTIPLIERS.get(destination.lower(), 1.0)
        
        # Get the base costs for the selected budget level
        base_budget = BASE_COSTS[budget_level]
        
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
        attractions = self.get_destination_attractions(destination)
        budget["specific_attractions"] = attractions
        
        return budget
    
    def get_destination_attractions(self, destination):
        """
        Get specific attractions and costs for a destination.
        
        Args:
            destination (str): Destination name
        
        Returns:
            list: List of attractions with names and costs
        """
        # Return specific attractions or generate generic ones
        return ATTRACTIONS_DATA.get(destination.lower(), [
            {"name": f"{destination.title()} City Tour", "cost": random.randint(15, 40)},
            {"name": f"{destination.title()} Museum", "cost": random.randint(10, 25)},
            {"name": f"{destination.title()} Historic Site", "cost": random.randint(5, 30)}
        ])
    
    def format_budget_response(self, destination, budget_data):
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
    
    def calculate_trip_budget(self, destination, budget_level, duration, travelers, session_id=None):
        """
        Calculate total trip budget with flights and comprehensive breakdown.
        
        Args:
            destination (str): Destination name
            budget_level (str): Budget level (budget, mid-range, luxury)
            duration (int): Trip duration in days
            travelers (int): Number of travelers
            session_id (str): Session ID for user preferences
        
        Returns:
            dict: Comprehensive budget breakdown
        """
        # Create user preferences with provided budget level
        user_prefs = {"budget_level": budget_level}
        
        # Calculate base budget
        budget_info = self.calculate_travel_budget(destination, user_prefs)
        
        # Calculate total trip cost
        daily_min = budget_info["daily_total"]["min"]
        daily_max = budget_info["daily_total"]["max"]
        
        # Account for number of travelers
        daily_min *= travelers
        daily_max *= travelers
        
        # Calculate trip totals
        trip_min = daily_min * duration
        trip_max = daily_max * duration
        
        # Add flight estimates
        flight_costs = {
            "budget": {"min": 300, "max": 600},
            "mid-range": {"min": 600, "max": 1200},
            "luxury": {"min": 1200, "max": 3000}
        }
        
        flight_cost = flight_costs[budget_level]
        flight_total_min = flight_cost["min"] * travelers
        flight_total_max = flight_cost["max"] * travelers
        
        # Adjust flight costs based on destination
        mult = COST_MULTIPLIERS.get(destination.lower(), 1.0)
        flight_total_min = int(flight_total_min * mult)
        flight_total_max = int(flight_total_max * mult)
        
        # Prepare the response
        budget_response = {
            "destination": destination,
            "duration": duration,
            "travelers": travelers,
            "budgetLevel": budget_level,
            "dailyCost": {
                "min": daily_min,
                "max": daily_max
            },
            "accommodation": {
                "min": budget_info["accommodation"]["min"] * travelers,
                "max": budget_info["accommodation"]["max"] * travelers,
                "total": budget_info["accommodation"]["min"] * travelers * duration
            },
            "food": {
                "min": budget_info["food"]["min"] * travelers,
                "max": budget_info["food"]["max"] * travelers,
                "total": budget_info["food"]["min"] * travelers * duration
            },
            "activities": {
                "min": budget_info["activities"]["min"] * travelers,
                "max": budget_info["activities"]["max"] * travelers,
                "total": budget_info["activities"]["min"] * travelers * duration
            },
            "transportation": {
                "min": budget_info["transport"]["min"] * travelers,
                "max": budget_info["transport"]["max"] * travelers,
                "total": budget_info["transport"]["min"] * travelers * duration
            },
            "flights": {
                "min": flight_total_min,
                "max": flight_total_max
            },
            "totalCost": {
                "min": trip_min + flight_total_min,
                "max": trip_max + flight_total_max
            },
            "attractions": budget_info.get("specific_attractions", [])
        }
        
        return budget_response