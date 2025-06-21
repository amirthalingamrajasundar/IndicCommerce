"""
WhatsApp webhook handler for receiving and processing messages.
"""

from flask import Blueprint, request, Response
import json
import os
import logging
from twilio.rest import Client
from twilio.twiml.messaging_response import Body, Media, Message, MessagingResponse

from src.speech_processing.processor import download_audio_for_sarvam
from src.agents.ecom_agent import process_text_message, process_voice_message

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

# def create_whatsapp_response(agent_response):
#     """
#     Create a WhatsApp response message based on the agent's response.
    
#     Args:
#         agent_response: The response from the agent.
        
#     Returns:
#         MessagingResponse: The Twilio MessagingResponse object.
#     """
#     response = MessagingResponse()

#     logger.info(f"Creating WhatsApp response: {agent_response}")

#     if 'voice_url' in agent_response:
#         audio_message = Message()
#         audio_message.media(agent_response['voice_url'])
#         response.append(audio_message)
    
#     if 'text' in agent_response:
#         text_message = Message()
#         text_message.body(agent_response['text'])
#         response.append(text_message)
    
#     if 'image_url' in agent_response:
#         image_message = Message()
#         image_message.media(agent_response['image_url'])
#         response.append(image_message)

#     logger.info(f"WhatsApp response created: {response}")

#     return response

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
            
            # Download the audio file from Twilio's URL
            audio_file = download_audio_for_sarvam(media_url)
            logger.info(f"Audio downloaded to: {audio_file}")
            
            # Process the voice message - this will ensure audio is only sent to Sarvam AI
            # The modified process_voice_message function now handles Sarvam AI speech-to-text directly
            agent_response = process_voice_message(audio_file)
            logger.info(f"Voice processing complete, response: {agent_response}")
            
            if isinstance(agent_response, dict) and "text" in agent_response:
                logger.info(f"Creating WhatsApp response with text: {agent_response['text'][:30]}...")
                response = create_whatsapp_response(agent_response)
            else:
                default_response = {"text": "We have received your voice message, but there was an issue processing it. Please try asking a specific product question."}
                response = create_whatsapp_response(default_response)

        except Exception as e:
            logger.error(f"Error processing voice message: {e}", exc_info=True)                    
            response.message("Sorry, I had trouble processing your voice message. Could you please try again or send a text message instead?")
    else:
        try:
            logger.info(f"Processing text message from {sender_id}")
            logger.info(f"Text: {incoming_msg[:20]}...")
            
            sender_language = request.values.get('Language', 'auto')
            logger.info(f"Detected language setting for sender: {sender_language}")
            
            agent_response = process_text_message(incoming_msg, sender_language)
            logger.info(f"Text processing complete, agent response keys: {agent_response.keys() if isinstance(agent_response, dict) else 'not a dict'}")
            
            # Extract response from different possible structures
            if isinstance(agent_response, dict):
                if "text" in agent_response:
                    response = create_whatsapp_response(agent_response)
                elif "response" in agent_response:
                    response = create_whatsapp_response(agent_response["response"])
                elif "messages" in agent_response and len(agent_response["messages"]) > 0:
                    assistant_messages = [msg for msg in agent_response["messages"] if msg.get("role") == "assistant"]
                    if assistant_messages:
                        last_message = assistant_messages[-1]
                        text_response = {"text": last_message.get("content", "")}
                        logger.info(f"Extracted response from messages: {text_response}")
                        response = create_whatsapp_response(text_response)
                    else:
                        default_response = {"text": "We received your message but couldn't generate a proper response. Our system handles over 1,00,000 queries monthly from customers across India. Please try asking about our products directly."}
                        response = create_whatsapp_response(default_response)
                else:
                    default_response = {"text": "We have received your text message, but had trouble processing it. Please try asking a specific product question."}
                    response = create_whatsapp_response(default_response)
            else:
                default_response = {"text": "We have received your text message, but had trouble processing it. Please try again with clearer wording."}
                response = create_whatsapp_response(default_response)
        except Exception as e:
            logger.error(f"Error processing text message: {e}", exc_info=True)
            response.message("Sorry, I had trouble processing your text message. Could you please try again or send a voice message instead?")
    
    return str(response)




