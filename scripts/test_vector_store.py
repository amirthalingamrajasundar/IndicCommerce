"""
Test script to verify the LangChain-Chroma vector store implementation.
"""
import logging
from src.utils.vector_store import vector_store, initialize_demo_products

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_vector_store():
    """Test the vector store implementation."""
    logger.info("Initializing vector store...")
    initialize_demo_products()
    
    # Test queries
    test_queries = [
        "I need a smartphone",
        "Looking for t-shirts",
        "Need comfortable shoes for running",
        "Wireless earbuds with good bass",
        "Denim pants"
    ]
    
    for query in test_queries:
        logger.info(f"\nSearching for: '{query}'")
        results = vector_store.search(query, limit=2)
        
        if results:
            logger.info(f"Found {len(results)} results:")
            for i, product in enumerate(results, 1):
                logger.info(f"Result {i}: {product['name']} - {product['price']}")
                logger.info(f"Description: {product['description']}")
        else:
            logger.info("No results found.")

if __name__ == "__main__":
    test_vector_store()
