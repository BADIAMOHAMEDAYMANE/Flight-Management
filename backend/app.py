# TravelMate API - Flask Travel Assistant Application
# Point d'entrée principal de l'application

from flask import Flask
from flask_cors import CORS
from config.settings import Config
from controllers.chat_controller import chat_bp
from controllers.destination_controller import destination_bp
from controllers.budget_controller import budget_bp
from models.chat_session import ChatSessionManager

def create_app():
    """Factory function to create Flask app instance"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Initialize chat session manager
    app.chat_session_manager = ChatSessionManager()
    
    # Register blueprints
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(destination_bp, url_prefix='/api')
    app.register_blueprint(budget_bp, url_prefix='/api')
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)