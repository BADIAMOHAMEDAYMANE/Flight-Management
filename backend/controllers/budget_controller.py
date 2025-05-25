"""
Budget Controller - Handles budget calculation endpoints
"""

from flask import Blueprint, request, jsonify
from services.budget_service import BudgetService
from models.user_preferences import UserPreferences

budget_bp = Blueprint('budget', __name__)

# Initialize services
budget_service = BudgetService()

@budget_bp.route('/budget-calculator', methods=['POST'])
def budget_calculator():
    """
    Calculate detailed budget for a destination and trip parameters.
    
    Request JSON:
        - destination: Destination name
        - budgetLevel: Budget level (budget, mid-range, luxury)
        - duration: Trip duration in days
        - travelers: Number of travelers
        - sessionId: User session ID
    
    Response JSON:
        - Detailed budget breakdown with totals and per-category costs
    """
    
    try:
        response_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type"
        }
        
        data = request.json
        destination = data.get('destination', '')
        budget_level = data.get('budgetLevel', 'mid-range')
        duration = data.get('duration', 7)
        travelers = data.get('travelers', 1)
        session_id = data.get('sessionId', 'default')
        
        if not destination:
            return jsonify({"error": "No destination provided"}), 400
        
        # Get user preferences if available
        user_prefs = UserPreferences.get_preferences(session_id)
        
        # Override with provided budget level
        user_prefs["budget_level"] = budget_level
        
        # Calculate base budget
        budget_info = budget_service.calculate_travel_budget(destination, user_prefs)
        
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
        flight_costs = budget_service.get_flight_costs(budget_level, destination, travelers)
        
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
            "flights": flight_costs,
            "totalCost": {
                "min": trip_min + flight_costs["min"],
                "max": trip_max + flight_costs["max"]
            },
            "attractions": budget_info.get("specific_attractions", [])
        }
        
        return jsonify(budget_response), 200, response_headers
        
    except Exception as e:
        print(f"Error in budget calculator: {e}")
        return jsonify({"error": str(e)}), 500, response_headers