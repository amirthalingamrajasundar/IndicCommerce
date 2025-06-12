# Agentic Ecommerce Application with WhatsApp Voice Interface

## Overview
This project is an agentic ecommerce application that enables users to interact with a shopping assistant via WhatsApp using voice messages in regional Indian languages. The app leverages Sarvam AI for speech processing, LangGraph for agent workflow, and Twilio for WhatsApp integration. It supports product search, shopping cart management, and checkout, all through natural language voice input.

## Features

- **WhatsApp Integration**: Receive and respond to user messages (including audio) via WhatsApp using Twilio.
- **Voice Input in Indian Languages**: Users can send voice messages in their preferred regional language.
- **Speech-to-Text & Text-to-Speech**: Uses Sarvam AI APIs for accurate speech recognition and synthesis.
- **Retrieval-Augmented Generation (RAG)**: Identifies product requirements and fetches relevant product information.
- **Shopping Cart & Checkout**: Manages cart state and handles checkout via conversational flow.
- **Modular Agent Design**: Built with LangGraph for extensible, maintainable agent workflows.
- **Robust Error Handling**: Handles audio conversion, API errors, and user feedback gracefully.

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

## Development Best Practices
- **Python Code Style**: Use `snake_case` for functions/variables, `CapWords` for classes, and type hints throughout.
- **Modularity**: Keep agent nodes, state, and workflow logic in separate modules for maintainability.
- **.gitignore**: The provided `.gitignore` excludes debug, build, environment, and sensitive files. Update as needed for your environment.

## File Structure
- `app.py` — Flask app entry point
- `src/whatsapp/webhook.py` — WhatsApp webhook and Twilio integration
- `src/speech_processing/processor.py` — Audio download, conversion, and Sarvam AI integration
- `src/agents/ecom_agent.py` — LangGraph agent definition and workflow
- `debug_audio/` — Temporary audio files for debugging
- `scripts/` — Test and debug scripts
- `requirements.txt`, `Dockerfile`, `docker-compose.yml` — Environment and dependencies

## Extending the Agent
- Add new nodes to the agent by defining functions and updating the workflow in `ecom_agent.py`.
- Use TypedDict for agent state to ensure type safety and clarity.
- Only return updated keys from node functions to avoid state overwrite.

## Troubleshooting & Debugging
- Check `debug_audio/` for raw and converted audio files.
- Review logs for errors in audio processing or webhook handling.
- Ensure your webhook URL is publicly accessible for Twilio.
- For local testing, use the scripts in `scripts/`.

## Credits & References
- [Sarvam AI](https://sarvam.ai/) — Speech-to-text and text-to-speech APIs
- [LangGraph](https://langgraph.org/) — Agent workflow framework
- [Twilio](https://www.twilio.com/) — WhatsApp messaging API

---
For more details, see code comments and docstrings throughout the project.

## License

[MIT License](LICENSE)

## Contributors

- Amirthalingam Rajasundar (amirthaling1@iisc.ac.in)
- Abhishek Kushary (abhishekkush@iisc.ac.in)
- Nitin Kumar (nitink@iisc.ac.in)
- Vignesh S (vigneshs@iisc.ac.in)
- Preetam Mishra (preetamm@iisc.ac.in)
