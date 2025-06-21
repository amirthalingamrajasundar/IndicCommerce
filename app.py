"""
Main application entry point for the Agentic Ecommerce application.
This file initializes all components and starts the Flask server.
"""

import os
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import components
from src.whatsapp.webhook import configure_whatsapp_routes
from src.speech_processing.processor import configure_speech_processing
from src.llm.sarvam import configure_llm
from src.data.sample_products import products as sample_products

# Create Flask app
app = Flask(__name__)

def initialize_app():
    """Initialize all application components."""
    # Configure components
    configure_whatsapp_routes(app)
    configure_speech_processing()
    configure_llm()
    
    # Set up routes
    @app.route('/')
    def index():
        """Home page with modern UI and WhatsApp link."""
        whatsapp_number = os.environ.get('TWILIO_WHATSAPP_NUMBER', '+14155238886').replace('+', '')
        join_code = 'join lips-swam'
        return render_template('index.html', whatsapp_number=whatsapp_number, join_code=join_code)
    
    @app.route('/products')
    def products():
        """Products page with search functionality."""
        # Get WhatsApp number from environment or use default
        whatsapp_number = os.environ.get('TWILIO_WHATSAPP_NUMBER', '+14155238886')
        
        # Get search parameters
        search_query = request.args.get('search', '').lower()
        category = request.args.get('category', '')
        
        # Filter products based on search and category
        filtered_products = []
        for product in sample_products:
            # Apply category filter if specified
            if category and product['category'] != category:
                continue
                
            # Apply search filter if specified
            if search_query and search_query not in product['name'].lower() and search_query not in product['description'].lower():
                continue
            
            # Add product to filtered list
            filtered_products.append(product)
        
        return render_template(
            'products.html',
            products=filtered_products,
            search_query=search_query,
            category=category,
            whatsapp_number=whatsapp_number.replace("+", "")
        )
    
    return app

if __name__ == "__main__":
    app = initialize_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
