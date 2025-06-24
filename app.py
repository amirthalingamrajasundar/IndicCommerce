"""
Main application entry point for the Agentic Ecommerce application.
This file initializes all components and starts the Flask server.
"""

import os
from flask import Flask, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import components
from src.whatsapp.webhook import configure_whatsapp_routes
from src.speech_processing.processor import configure_speech_processing
from src.llm.sarvam import configure_llm
from src.data.sample_products import products as sample_products
from src.utils.vector_store import get_vector_store

# Create Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://amirth.dev",
            "https://www.amirth.dev",
            "https://showstack-six.vercel.app",
            "http://localhost:3000",
        ],
        "supports_credentials": True,
        "methods": ["*"],
        "allow_headers": ["*"]
    }
})

def initialize_app():
    """Initialize all application components."""
    if not os.environ.get('ENV') == 'dev' and not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        raise EnvironmentError("GOOGLE_APPLICATION_CREDENTIALS environment variable must be set to run the app in dev environment.")

    # Configure components
    configure_whatsapp_routes(app)
    configure_speech_processing()
    configure_llm()
    
    @app.route('/get_config')
    def get_config():
        """API endpoint to retrieve configuration information."""
        config = {
            "whatsapp_number": os.environ.get('TWILIO_WHATSAPP_NUMBER'),
            "join_code": os.environ.get('JOIN_CODE'),
            "products": sample_products,
        }
        return {"config": config}
    
    @app.route('/get_products')
    def get_products():
        """API endpoint to retrieve product information."""
        search_query = request.args.get('query', '').lower()
        if search_query:
            vector_store = get_vector_store()
            results = vector_store.search(query=search_query, limit=10)
        else:
            results = sample_products
        return {"products": results}

    return app

if __name__ == "__main__":
    app = initialize_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
