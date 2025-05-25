"""
Chat Controller - Handles chat-related endpoints
"""

from flask import Blueprint, request, jsonify, current_app
from services.ai_service import AIService
from services.budget_service import BudgetService
from services.preference_service import PreferenceService
from utils.response_processor import ResponseProcessor
from datetime import datetime
import traceback

# Create Blueprint
chat_bp = Blueprint('chat', __name__)

# Initialize services
ai_service = AIService()
budget_service = BudgetService()
preference_service = PreferenceService()
response_processor = ResponseProcessor()
@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for conversational travel assistance.
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
        user_message = data.get('message', '').strip()
        session_id = data.get('sessionId')
        
        # Validate input
        if not user_message:
            return jsonify({"error": "No message provided"}), 400, response_headers

        # Get or create chat session
        chat_session = current_app.chat_session_manager.get_session(session_id)
        
        # Get current preferences from session or initialize new ones
        current_preferences = getattr(chat_session, 'preferences', {
            "preferred_destinations": [],
            "travel_interests": [],
            "budget_level": None,
            "travel_type": None,
            "travel_duration": None
        })
        
        # Update user preferences based on the message
        current_preferences = preference_service.extract_preferences_from_message(
            user_message, 
            current_preferences
        )
        
        # Save updated preferences back to session
        chat_session.preferences = current_preferences
        
        # Add user message to history
        chat_session.add_message("user", user_message)
        
        # Check for special requests
        budget_request = "budget" in user_message.lower()
        destination_for_budget = preference_service._extract_destinations(
            user_message.lower(), 
            {"preferred_destinations": []}
        )["preferred_destinations"]
        destination_for_budget = destination_for_budget[0] if destination_for_budget else None
        
        # Handle budget requests with specific destination
        if budget_request and destination_for_budget:
            budget_data = budget_service.calculate_travel_budget(destination_for_budget, current_preferences)
            response_text = budget_service.format_budget_response(destination_for_budget, budget_data)
        else:
            # Create formatted history with the expected structure
            formatted_history = [
                {
                    "parts": [{"text": msg["parts"][0]["text"]}],
                    "role": msg["role"]
                } 
                for msg in chat_session.get_history()
            ]
            # Start a new chat session and generate response from AI service
            chat = ai_service.start_chat(formatted_history)  # Start a new chat session
            response_text = ai_service.generate_response(chat, user_message)  # Pass the chat object
        
        # Process response to detect special formatting markers
        processed_response = response_processor.process_bot_response(response_text)
        
        # Add model response to history
        chat_session.add_message("assistant", response_text)
        
        return jsonify({
            "response": response_text,
            "processed_response": processed_response,
            "userPreferences": current_preferences,
            "sessionId": chat_session.session_id
        }), 200, response_headers
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Chat error: {str(e)}"}), 500, response_headers
