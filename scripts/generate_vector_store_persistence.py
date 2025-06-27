import sys
import os
from dotenv import load_dotenv
import logging

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.utils.vector_store import get_vector_store

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Generating vector store persistence...")

try:
    vector_store = get_vector_store()
    vector_store.add_test_products()
except Exception as e:
    logger.error(f"Error initializing vector store: {e}")
