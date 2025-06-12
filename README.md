# Agentic Ecommerce Application with WhatsApp Voice Interface

This application enables voice-based ecommerce interactions through WhatsApp, supporting regional Indian languages. Users can search for products, manage their cart, and complete purchases entirely through voice commands in their preferred language.

## Features

- **Multilingual Voice Input**: Accept voice commands in multiple regional Indian languages
- **Natural Language Understanding**: Extract product requests, quantities, and other details
- **Retrieval Augmented Generation**: Intelligent product recommendations using RAG
- **Interactive Shopping Cart**: Build and manage cart throughout the conversation
- **Voice Responses**: Return responses in the user's language with text and audio
- **Checkout Process**: Complete transactions within the WhatsApp conversation

## Architecture

The system consists of the following components:

1. **WhatsApp Integration**: Handles incoming and outgoing WhatsApp messages using the Twilio API
2. **Speech Processing**: Transcribes voice messages to text using Sarvam AI's speech-to-text API
3. **Product Catalog**: Manages product information and provides RAG-based search functionality
4. **Cart Management**: Tracks user shopping carts throughout the conversation
5. **Payment Processing**: Handles checkout and payment via Razorpay integration
6. **Response Generation**: Creates appropriate responses to user queries using RAG
7. **Text-to-Speech**: Converts text responses back to audio using Sarvam AI

## Project Structure

```
agentic-ecom/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker-compose setup for development
├── config/                         # Configuration files
│   └── .env.example                # Example environment variables
├── docs/                           # Documentation
├── src/                            # Source code
│   ├── whatsapp/                   # WhatsApp integration
│   │   └── webhook.py              # WhatsApp webhook handler
│   ├── speech_processing/          # Voice processing and intent recognition
│   │   └── processor.py            # Speech-to-text and intent extraction
│   ├── product_catalog/            # Product database and search
│   │   └── catalog.py              # Product management and RAG search
│   ├── cart/                       # Shopping cart functionality
│   │   └── manager.py              # Cart operations
│   ├── payment/                    # Payment processing
│   │   └── gateway.py              # Payment gateway integration
│   └── response_generation/        # Response generation using RAG
│       ├── generator.py            # Text response generation
│       └── tts.py                  # Text-to-speech conversion
└── tests/                          # Test cases
    ├── run_tests.py                # Test runner
    └── test_webhook.py             # WhatsApp webhook tests
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (recommended for development)
- Sarvam AI API key
- Twilio account with WhatsApp Business API access
- Razorpay account (for payment processing)
- ngrok or similar tunneling service for local development

### Environment Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/agentic-ecom.git
   cd agentic-ecom
   ```

2. Copy the example environment file and fill in your API keys:
   ```
   copy config\.env.example .env
   ```

3. Edit the `.env` file with your API keys:
   ```
   SARVAM_API_KEY=your_sarvam_api_key
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_WHATSAPP_NUMBER=your_whatsapp_number
   RAZORPAY_KEY_ID=your_razorpay_key_id
   RAZORPAY_KEY_SECRET=your_razorpay_secret
   NGROK_AUTH_TOKEN=your_ngrok_auth_token
   ```

### Running with Docker (Recommended)

1. Build and start the containers:
   ```
   docker-compose up --build
   ```

2. The application will be available at `http://localhost:5000`
3. ngrok will create a public URL accessible at `http://localhost:4040`

### Running without Docker

1. Create a virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Expose your local server using ngrok:
   ```
   ngrok http 5000
   ```

## WhatsApp Business API Setup

1. Create a Twilio account and set up a WhatsApp Sandbox
2. Configure the sandbox webhook URL to point to your ngrok URL + `/webhook`, e.g., `https://your-ngrok-url.ngrok.io/webhook`
3. Test the integration by sending a message to your WhatsApp sandbox number

## User Flow

1. **User Sends Voice Message**: User sends a voice message in their preferred language asking for products
2. **Speech-to-Text**: The system transcribes the voice message using Sarvam AI
3. **Intent Recognition**: The system identifies what the user is looking for
4. **Product Search**: RAG is used to find relevant products
5. **Response Generation**: The system generates an appropriate response
6. **Text-to-Speech**: The response is converted to audio in the user's language
7. **WhatsApp Response**: Both text and audio responses are sent back to the user
8. **Conversation Continues**: The user can ask for more details, add products to their cart, etc.
9. **Checkout**: When ready, the user can complete their purchase via a payment link

## Development Guide

### Testing the Application

1. Run the local development server
2. Visit `http://localhost:5000` to access the testing interface
3. Use the product search form to test the RAG system
4. Upload audio files to test the voice processing

### Running Tests

```
python tests/run_tests.py
```

### Adding New Products

Modify the `load_product_data` function in `src/product_catalog/catalog.py` to add or modify products.

### Extending the System

- **Adding Languages**: Update the speech processing module to support additional languages
- **Custom Intent Recognition**: Enhance the intent extraction in `speech_processing/processor.py`
- **New Product Categories**: Add new product types to the catalog
- **Enhanced RAG**: Improve the retrieval system in `product_catalog/catalog.py`

## Deployment

For production deployment:

1. Set up a proper database for product catalog and cart storage
2. Use a production-ready web server with Gunicorn:
   ```
   gunicorn -w 4 -b 0.0.0.0:5000 "app:initialize_app()"
   ```
3. Set up SSL for secure communications
4. Use a proper media storage service for audio files
5. Implement proper authentication and security measures

## Team Assignments

For the 10-day implementation with 5 team members:

- **Team Member 1**: WhatsApp Integration & Project Setup
- **Team Member 2**: Speech Processing & Intent Recognition
- **Team Member 3**: Product Catalog & RAG Implementation
- **Team Member 4**: Cart Management & Payment Processing
- **Team Member 5**: Response Generation & Text-to-Speech

## License

[MIT License](LICENSE)

## Contributors

- Your Team Member Names Here
