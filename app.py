"""
Main application entry point for the Agentic Ecommerce application.
This file initializes all components and starts the Flask server.
"""

import os
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import components
from src.whatsapp.webhook import configure_whatsapp_routes
from src.speech_processing.processor import configure_speech_processing

# Create Flask app
app = Flask(__name__)

def initialize_app():
    """Initialize all application components."""
    # Configure components
    configure_whatsapp_routes(app)
    configure_speech_processing()
    
    # Set up test routes
    @app.route('/')
    def index():
        """Home page for testing."""
        return """
        <html>
            <head>
                <title>WhatsApp Agentic Ecommerce</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                    h1 { color: #4285f4; }
                    .card { border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <h1>WhatsApp Agentic Ecommerce</h1>
                <div class="card">
                    <h2>WhatsApp Webhook</h2>
                    <p>Send 'join lips-swam' to +14155238886</p>
                </div>
            </body>
        </html>
        """
    return app

if __name__ == "__main__":
    app = initialize_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
