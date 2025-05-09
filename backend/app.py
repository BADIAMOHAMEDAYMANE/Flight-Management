from flask import Flask, request, jsonify, send_from_directory
import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
print("Loaded API key:", os.getenv("GEMINI_API_KEY"))


# Define the system prompt
system_prompt = """You are TravelMate, a friendly travel assistant. Respond to greetings naturally, 
and for travel requests provide:
1. 1-3 location suggestions
2. Each as a bullet point with:
   - **Place**: Brief highlight
   - Best for: [type of travelers]
   - When: [best season]"""

# Set up the model
model = genai.GenerativeModel(
    'gemini-1.5-pro-latest', 
    system_instruction=system_prompt
)

# Store chat sessions by user (in a real app, you'd use a database)
chat_sessions = {}

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


if __name__ == '__main__':
    app.run(debug=True, port=5000)