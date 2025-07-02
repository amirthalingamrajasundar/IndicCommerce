"""
Chat Completion using Sarvam AI.
"""

import os
import logging
from sarvamai import SarvamAI

# Initialize Sarvam AI client
sarvam_api_key = os.environ.get("SARVAM_API_KEY")
sarvam_client = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configure_llm():
    """Configure speech processing components."""
    global sarvam_client
    
    if not sarvam_api_key:
        logger.error("SARVAM_API_KEY environment variable is not set")
        raise ValueError("SARVAM_API_KEY environment variable is not set")
    
    logger.info("Initializing Sarvam AI client")
    sarvam_client = SarvamAI(
        api_subscription_key=sarvam_api_key,
    )
    logger.info("Sarvam AI client initialized successfully")

def chat_completion(prompt: str, model: str = "sarvam-m", temperature: float = 0.2):
    """
    Generate chat completion using Sarvam AI.

    Args:
        prompt (str): The input prompt for the chat model.
        model (str): The model to use for chat completion.
        temperature (float): Sampling temperature for response generation.

    Returns:
        str: The generated response from the model.
    """
    if not sarvam_client:
        configure_llm()
    
    logger.info(f"Generating chat completion with model: {model}")
    
    try:
        response = sarvam_client.chat.completions(messages=[
            {
                "role": "system", 
                "content": (
                    "You are a helpful salesperson." 
                    "Answer questions about products and provide recommendations based only on the context provided."
                    "Do not make thing up if you don't know the answer. Try to be helpful and upsell products when possible."
                    "Make sure to return no more than 900 characters in your response."
                )
            },
            {
                "role": "user", 
                "content": prompt
            }
        ])
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"Error generating chat completion: {e}")
        raise