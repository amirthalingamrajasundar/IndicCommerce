"""
Speech processor using Sarvam AI for speech-to-text conversion and language detection.
"""

import os
import requests
import tempfile
import logging
from sarvamai import SarvamAI
import shutil
import time
import mimetypes
from pydub import AudioSegment

# Initialize Sarvam AI client
sarvam_api_key = os.environ.get("SARVAM_API_KEY")
sarvam_client = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_audio_format(file_path, content_type=None):
    """
    Detect audio format using file extension and content type
    
    Args:
        file_path: Path to the audio file
        content_type: HTTP Content-Type header (optional)
        
    Returns:
        tuple: (format_name, extension)
    """
    # Common audio format mapping
    format_map = {
        'audio/ogg': ('ogg', '.ogg'),
        'audio/opus': ('ogg', '.opus'),
        'audio/mpeg': ('mp3', '.mp3'),
        'audio/mp3': ('mp3', '.mp3'),
        'audio/wav': ('wav', '.wav'),
        'audio/wave': ('wav', '.wav'),
        'audio/x-wav': ('wav', '.wav'),
        'audio/aac': ('aac', '.aac'),
        'audio/mp4': ('mp4', '.m4a'),
        'audio/x-m4a': ('mp4', '.m4a'),
        'audio/webm': ('webm', '.webm')
    }
    
    # Try to determine format from content type
    if content_type and content_type in format_map:
        return format_map[content_type]
    
    # Try to determine from file extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.ogg' or ext == '.oga':
        return 'ogg', ext
    elif ext == '.opus':
        return 'ogg', ext  # opus uses ogg container format
    elif ext == '.mp3':
        return 'mp3', ext
    elif ext == '.wav':
        return 'wav', ext
    elif ext == '.m4a':
        return 'mp4', ext
    elif ext == '.aac':
        return 'aac', ext
    elif ext == '.webm':
        return 'webm', ext
        
    # Default to ogg for WhatsApp audio (most likely)
    logger.warning(f"Unknown audio format for {file_path} with content type {content_type}, defaulting to ogg")
    return 'ogg', '.ogg'

def configure_speech_processing():
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


def download_audio_for_sarvam(media_url):
    """
    Download audio file from URL and convert it to WAV format if needed.
    
    Args:
        media_url: URL to the audio file
        
    Returns:
        str: Path to the downloaded and converted audio file in WAV format
    """    # Download the audio file
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    response = requests.get(media_url, auth=(account_sid, auth_token))
    
    if response.status_code != 200:
        logger.error(f"Failed to download audio: {response.status_code}, {response.text[:100]}")
        raise ValueError(f"Failed to download audio: {response.status_code}")
    
    # Get content type for format detection
    content_type = response.headers.get('Content-Type', '')
    logger.info(f"Content-Type from response headers: {content_type}")
    
    # Create a temporary file with a generic extension
    with tempfile.NamedTemporaryFile(delete=False, suffix='.audio') as temp_file:
        temp_file.write(response.content)
        original_path = temp_file.name
    
    # Detect the audio format
    audio_format, extension = detect_audio_format(original_path, content_type)
    logger.info(f"Detected audio format: {audio_format}, extension: {extension}")
    
    # Rename the file with the correct extension
    new_path = original_path.replace('.audio', extension)
    os.rename(original_path, new_path)
    original_path = new_path
    
    # Save a copy to a persistent location for debugging
    debug_dir = "/app/debug_audio"
    os.makedirs(debug_dir, exist_ok=True)
    debug_file = f"{debug_dir}/audio_original_{int(time.time())}{extension}"
    shutil.copy(original_path, debug_file)
    logger.info(f"Original audio saved to: {debug_file}")

    # Convert to WAV if not already in WAV format
    if audio_format != 'wav':
        logger.info(f"Converting {audio_format} audio to WAV format")
        try:
            # Ensure we have enough debug information to diagnose any issues
            file_size = os.path.getsize(original_path)
            logger.info(f"Original file size before conversion: {file_size} bytes")
            
            # For OGG files from WhatsApp, we may need to try different approaches
            if audio_format == 'ogg':
                # Try with both OGG and Opus decoders since WhatsApp can use either
                try:
                    # First try as OGG Vorbis
                    audio = AudioSegment.from_file(original_path, format="ogg")
                except Exception as inner_e:
                    logger.warning(f"Failed with OGG format, trying as Opus: {inner_e}")
                    # If that fails, try as Opus in OGG container
                    audio = AudioSegment.from_file(original_path, format="opus")
            else:
                # For other formats use the detected format
                audio = AudioSegment.from_file(original_path, format=audio_format)
            
            # Export to WAV format
            wav_path = original_path.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_path, format="wav")
            
            # Verify the WAV file was created successfully
            if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
                raise Exception("Converted WAV file is empty or doesn't exist")
            
            # Save a debug copy of the converted WAV file
            debug_wav = f"{debug_dir}/audio_converted_{int(time.time())}.wav"
            shutil.copy(wav_path, debug_wav)
            logger.info(f"Converted WAV audio saved to: {debug_wav} (size: {os.path.getsize(wav_path)} bytes)")
            
            # Remove the original temporary file
            os.unlink(original_path)
            
            return wav_path
        except Exception as e:
            raise ValueError(f"Error converting audio: {e}")
    else:
        logger.info(f"Audio already in WAV format, no conversion needed")
        return original_path

def is_valid_audio_file(file_path):
    """
    Check if the file is a valid audio file.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        bool: True if valid audio file, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False
    
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith('audio'):
        # Check if the file extension is supported by Sarvam AI
        _, file_ext = os.path.splitext(file_path)
        if file_ext.lower() not in ['.wav', '.mp3']:
            logger.error(f"File format {file_ext} is not supported by Sarvam AI.")
            return False
        return True
    
    logger.error(f"File is not a valid audio file: {file_path} (MIME type: {mime_type})")
    return False

def translate_audio(audio_file_path):
    """
    Translate regional audio to English text using Sarvam AI.
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        str: Translated text
    """
    logger.info(f"Translating audio file at: {audio_file_path}")
    # Get file info for debugging
    file_size = os.path.getsize(audio_file_path)
    logger.info(f"Audio file size: {file_size} bytes")

    try:
        if (is_valid_audio_file(audio_file_path)):
            with open(audio_file_path, "rb") as audio_file:
                logger.info(f"Sending audio file to Sarvam AI for translation")
                response = sarvam_client.speech_to_text.translate(
                    file=audio_file,
                    model="saaras:v2"
                )
            logger.info(f"Translation response: {response}")
            return [
                response.transcript,
                response.language_code
            ]
    except Exception as e:
        logger.error(f"Error translating audio: {e}")
        return ["Sorry, I couldn't translate the audio."]

def text_to_speech(text, language_code=None, speaker_gender='Female'):
    """
    Convert text to speech using Sarvam AI.
    
    Args:
        text: Text to convert
        language_code: Target language code (e.g., 'hi-IN')
        speaker_gender: Speaker gender ('Male' or 'Female')
        
    Returns:
        str: Path to the generated audio file, or None if failed
    """
    logger.info(f"Converting text to speech: {text}, language: {language_code}")

    try:
        # Call Sarvam AI TTS API
        logger.info(f"Calling text to speech sarvam API")
        response = sarvam_client.text_to_speech.convert(
            text=text,
            target_language_code=language_code,
            speaker_gender=speaker_gender
        )
        logger.info(f"TTS response {response}")
        
        # Save the audio to a temporary file
        audio_data = response.audios[0]
        if audio_data:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                return temp_file.name
        
        return None
        
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

def translate_and_speak(text, source_language_code='auto', target_language_code='ta-IN', speaker_gender='Female'):
    """
    Translate text and convert to speech.
    
    Args:
        text: Text to translate and convert
        source_language_code: Source language code
        target_language_code: Target language code
        speaker_gender: Speaker gender
        
    Returns:
        tuple: (translated_text, audio_file_path)
    """
    try:
        # First translate the text
        translation_response = sarvam_client.text.translate(
            input=text,
            source_language_code=source_language_code,
            target_language_code=target_language_code,
            speaker_gender=speaker_gender
        )

        logger.info(f"Translation response: {translation_response}")
        
        translated_text = translation_response.translated_text
        
        # Then convert to speech
        audio_path = text_to_speech(translated_text, target_language_code, speaker_gender)
        
        return (translated_text, audio_path)
        
    except Exception as e:
        print(f"Error translating and generating speech: {e}")
        return (text, None)


