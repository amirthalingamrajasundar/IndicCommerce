"""
Basic test for WhatsApp webhook handler.
"""

import pytest
import json
from app import initialize_app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app = initialize_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

def test_webhook_receives_text_message(client):
    """Test that webhook properly handles a text message."""
    
    with patch('src.whatsapp.webhook.MessagingResponse') as mock_resp:
        mock_msg = MagicMock()
        mock_resp.return_value = mock_msg
        
        response = client.post('/webhook', data={
            'Body': 'Hello',
            'From': 'whatsapp:+1234567890',
            'MediaUrl0': '',
            'MediaContentType0': ''
        })
        
        # Check that we got a successful response
        assert response.status_code == 200
        
        # Check that the response message contains the expected text
        mock_msg.message.assert_called_once()
        call_args = mock_msg.message.call_args[0][0]
        assert "Please send a voice message" in call_args

def test_webhook_receives_voice_message(client):
    """Test that webhook properly handles a voice message."""
    
    with patch('src.whatsapp.webhook.process_voice_message') as mock_process:
        # Set up the mock to return a specific transcription and intent
        mock_process.return_value = ("I want to buy a phone", {
            'intent_type': 'product_search',
            'entities': {
                'product': 'phone',
                'quantity': 1
            }
        })
        
        with patch('src.whatsapp.webhook.MessagingResponse') as mock_resp:
            mock_msg = MagicMock()
            mock_resp.return_value = mock_msg
            
            with patch('src.whatsapp.webhook.get_cart_for_user') as mock_cart:
                mock_cart.return_value = {'items': []}
                
                with patch('src.whatsapp.webhook.generate_response') as mock_gen:
                    mock_gen.return_value = "Here are some phones you might be interested in"
                    
                    response = client.post('/webhook', data={
                        'Body': '',
                        'From': 'whatsapp:+1234567890',
                        'MediaUrl0': 'http://example.com/audio.wav',
                        'MediaContentType0': 'audio/wav'
                    })
                    
                    # Check that we got a successful response
                    assert response.status_code == 200
                    
                    # Check that process_voice_message was called with the correct URL
                    mock_process.assert_called_once_with('http://example.com/audio.wav')
                    
                    # Check that generate_response was called with the correct arguments
                    mock_gen.assert_called_once()
                    
                    # Check that the response message contains the expected text
                    mock_msg.message.assert_called_once_with(
                        "Here are some phones you might be interested in"
                    )
