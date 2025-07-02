"""
WhatsApp webhook handler for receiving and processing messages.
"""

from flask import Blueprint, request
import os
import logging
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from src.speech_processing.processor import download_audio_for_sarvam
from src.agents.ecom_agent import compiled_graph

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio credentials
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_client = None

try:
    if account_sid and auth_token:
        twilio_client = Client(account_sid, auth_token)
except Exception as e:
    logger.error(f"Failed to initialize Twilio client: {e}")

whatsapp_blueprint = Blueprint('whatsapp', __name__)

def configure_whatsapp_routes(app):
    """Configure WhatsApp webhook routes."""
    app.register_blueprint(whatsapp_blueprint)

def send_whatsapp_messages(to_number, agent_response):
    """
    Sends text, image, and audio messages separately using Twilio REST API.

    Args:
        to_number: The recipient WhatsApp number (e.g., 'whatsapp:+919xxxxxx').
        agent_response: A dict containing keys like 'text', 'image_url', 'voice_url'.
    """
    logger.info(f"Creating WhatsApp response: {agent_response}")
    
    from_whatsapp_number = 'whatsapp:' + os.environ.get('TWILIO_WHATSAPP_NUMBER')

    if 'text' in agent_response:
        twilio_client.messages.create(
            from_=from_whatsapp_number,
            to=to_number,
            body=agent_response['text']
        )

    if 'image_url' in agent_response:
        twilio_client.messages.create(
            from_=from_whatsapp_number,
            to=to_number,
            media_url=[agent_response['image_url']]
        )

    if 'voice_url' in agent_response:
        twilio_client.messages.create(
            from_=from_whatsapp_number,
            to=to_number,
            media_url=[agent_response['voice_url']]
        )

@whatsapp_blueprint.route('/webhook', methods=['POST'])
def webhook(): 
    """Handle incoming WhatsApp messages."""
    logger.info(f"Received a new WhatsApp message {request.values}")
    
    # Log all incoming data for debugging
    logger.debug(f"Full webhook request values: {request.values}")
    logger.debug(f"Request headers: {request.headers}")
    
    # Get the message data
    incoming_msg = request.values.get('Body', '')
    sender_id = request.values.get('From', '')
    media_url = request.values.get('MediaUrl0', '')
    media_type = request.values.get('MediaContentType0', '')
    
    logger.info(f"Received message from {sender_id}: {incoming_msg[:20]}...")
    
    # Initialize response
    response = MessagingResponse()
    
    if media_url and 'audio' in media_type:
        try:
            logger.info(f"Processing voice message from {sender_id}")
            logger.info(f"Media URL: {media_url}")
            logger.info(f"Media type: {media_type}")
            
            audio_file = download_audio_for_sarvam(media_url)

            agent_response = compiled_graph.invoke({
                "user_id": sender_id, 
                "regional_audio_path": audio_file
            })
            response = send_whatsapp_messages(sender_id, agent_response["response"])

        except Exception as e:
            logger.error(f"Error processing voice message: {e}", exc_info=True)                    
            response.message("Sorry, I had trouble processing your voice message. Could you please try again or send a text message instead?")
    
    return str(response)

