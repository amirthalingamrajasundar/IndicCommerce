import pandas as pd
import os
import sys
from typing import List, Dict, Any
import logging
import shutil
import csv
from io import StringIO

# Configure logging for clarity
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# --- Start: Inlined or Adapted Code from original project files ---

# From sample_products.py
sample_products = [
    {
        "id": "prod1",
        "name": "Cotton T-Shirt",
        "description": "A comfortable 100% cotton white t-shirt",
        "price": "₹499",
        "category": "apparel",
        "image_url": "https://ts1.mm.bing.net/th?id=OIP.mABUDivU9i-1zhp9NIjGbAHaHa&pid=15.1"
    },
    {
        "id": "prod2",
        "name": "Denim Jeans",
        "description": "Classic blue denim jeans with straight fit",
        "price": "₹1299",
        "category": "apparel",
        "image_url": "https://th.bing.com/th/id/OIP.kg0Uv2Hi0NrQETZKuq7kHQHaLH?w=123&h=184&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod3",
        "name": "Smartphone",
        "description": "Latest Android smartphone with 6.5 inch display and 64MP camera",
        "price": "₹12999",
        "category": "electronics",
        "image_url": "https://th.bing.com/th/id/OIP.0-wtYyzgKxHMWgv9jJQ69gHaD4?w=301&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod4",
        "name": "Running Shoes",
        "description": "Comfortable running shoes with extra cushioning",
        "price": "₹2499",
        "category": "footwear",
        "image_url": "https://th.bing.com/th/id/OIP.W6ymbzx6Hc-OeEEw_8YLgAAAAA?w=181&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod5",
        "name": "Wireless Earbuds",
        "description": "Bluetooth wireless earbuds with noise cancellation",
        "price": "₹1999",
        "category": "electronics",
        "image_url": "https://th.bing.com/th/id/OIP.wRtJLLtZO2HAgZRffpVmkAAAAA?w=180&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod6",
        "name": "Leather Wallet",
        "description": "Genuine leather wallet with RFID protection",
        "price": "₹799",
        "category": "accessories",
        "image_url": "https://th.bing.com/th/id/OIP.WWgt5OE3-Z2O8PUalUWQ3AHaHa?w=181&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7"
    },
    {
        "id": "prod7",
        "name": "Digital Watch",
        "description": "Stylish waterproof digital watch with LED display",
        "price": "₹1599",
        "category": "accessories",
        "image_url": "https://th.bing.com/th/id/OIP.oDdRg5lVoD5RPVaZ5mYOJQHaHa?w=180&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7"
    },
    {
        "id": "prod8",
        "name": "Office Chair",
        "description": "Ergonomic mesh back office chair with adjustable height",
        "price": "₹4999",
        "category": "furniture",
        "image_url": "https://th.bing.com/th/id/OIP.oOonGQkYY5xBh4Wz9sVzLgHaHa?w=180&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7"
    },
    {
        "id": "prod9",
        "name": "Bluetooth Speaker",
        "description": "Portable speaker with deep bass and 12-hour battery life",
        "price": "₹1299",
        "category": "electronics",
        "image_url": "https://th.bing.com/th/id/OIP.XZx0fb5lZz9uOx-jM8BxCAHaHa?w=180&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7"
    },
    {
        "id": "prod10",
        "name": "Laptop Backpack",
        "description": "Water-resistant backpack suitable for laptops up to 15.6 inches",
        "price": "₹1099",
        "category": "accessories",
        "image_url": "https://th.bing.com/th/id/OIP.iTj-Fn2kkHiqJAVX2zdx8gHaHa?w=180&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7"
    },
    {
        "id": "prod11",
        "name": "Cotton Kurti",
        "description": "Ethnic cotton kurti with traditional block prints",
        "price": "₹899",
        "category": "apparel",
        "image_url": "https://th.bing.com/th/id/OIP.z8A4tC0BZkI2zpWzuhJqGwHaJ4?w=133&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7"
    },
    {
        "id": "prod12",
        "name": "Fitness Band",
        "description": "Activity tracker with heart rate and sleep monitor",
        "price": "₹1799",
        "category": "electronics",
        "image_url": "https://th.bing.com/th/id/OIP.YEGCMBUOsmwDtExxas7wNgHaHa?w=180&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7"
    },
    {
        "id": "prod13",
        "name": "Sneakers",
        "description": "Casual sneakers for daily wear with cushioned sole",
        "price": "₹1499",
        "category": "footwear",
        "image_url": "https://th.bing.com/th/id/OIP.yQDYgygfIefT_fZn-UtXVAHaHa?w=181&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7"
    },
    {
        "id": "prod14",
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with adjustable DPI",
        "price": "₹699",
        "category": "electronics",
        "image_url": "https://th.bing.com/th/id/OIP.4lNznh7PQTX9dEpsnvbR6AHaHa?w=181&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7"
    },
    {
        "id": "prod15",
        "name": "Sunglasses",
        "description": "UV-protected unisex sunglasses with stylish frame",
        "price": "₹1199",
        "category": "accessories",
        "image_url": "https://th.bing.com/th/id/OIP.yRnr6XWRT8lRTP3ksBl9vQHaHa?w=181&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7"
    }
]

# From vector_store.py (simplified for testing, focusing on core search logic)
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

class VectorStore:
    """Simplified Vector store for product search using LangChain-Chroma for testing."""

    def __init__(self, persist_directory: str = None):
        """Initialize the Chroma vector store. Persist directory is optional for in-memory testing."""
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        # Use a temporary directory for Chroma DB persistence for testing
        self.persist_directory = persist_directory if persist_directory else os.path.join(os.getcwd(), "test_chroma_db")
        
        self.initialized = False
        self.initialize_collection() # Initialize immediately for testing

    def initialize_collection(self, collection_name: str = "products_test"):
        """Initialize or get the collection."""
        try:
            # Delete old persistence directory to ensure a fresh start for testing
            if os.path.exists(self.persist_directory) and os.path.isdir(self.persist_directory):
                shutil.rmtree(self.persist_directory)
                logger.info(f"Cleaned up old persistence directory: {self.persist_directory}")

            logger.info(f"Initializing Chroma collection '{collection_name}' with persistence directory '{self.persist_directory}'...")
            
            self.vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
            self.initialized = True
            logger.info(f"LangChain-Chroma collection '{collection_name}' initialized.")
            return True
        except Exception as e:
            logger.error(f"Error initializing LangChain-Chroma collection: {e}")
            self.initialized = False
            return False
    
    def add_products(self, products: List[Dict[str, Any]]):
        """
        Add products to the vector store.
        """
        if not self.initialized:
            logger.error("Vector store not initialized. Call initialize_collection first.")
            return False
        
        try:
            documents = []
            for product in products:
                doc = Document(
                    page_content=f"{product['name']}: {product['description']}",
                    metadata=product
                )
                documents.append(doc)
            
            self.vector_store.add_documents(documents)
            logger.info(f"Added {len(products)} products to the vector store.")
            return True
        except Exception as e:
            logger.error(f"Error adding products to vector store: {e}")
            return False
    
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search for products using a text query.
        
        Args:
            query: The text query to search with
            limit: Maximum number of results to return
            
        Returns:
            List of matching products
        """
        if not self.initialized:
            logger.error("Vector store not initialized.")
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=limit)
            if results:
                return [doc.metadata for doc in results]
            return []
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []

# --- End: Inlined or Adapted Code ---

def calculate_precision_recall_f1(retrieved_items: List[str], relevant_items: List[str]):
    """
    Calculates Precision, Recall, and F1 Score for a single query.

    Args:
        retrieved_items: A list of IDs of items retrieved by the system (should be at most 1 for this script).
        relevant_items: A list of IDs of truly relevant items (should be exactly 1 for this script).

    Returns:
        A tuple (precision, recall, f1_score).
    """
    if not relevant_items:
        precision = 1.0 if not retrieved_items else 0.0
        recall = 0.0
        f1_score = 0.0
        return precision, recall, f1_score

    true_positives = len(set(retrieved_items) & set(relevant_items))
    false_positives = len(set(retrieved_items) - set(relevant_items))
    false_negatives = len(set(relevant_items) - set(retrieved_items))

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0

    if precision + recall == 0:
        f1_score = 0.0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)

    return precision, recall, f1_score

def run_rag_evaluation(queries_csv_content: str) -> str:
    """
    Runs the RAG evaluation to calculate F1 score for product search queries
    and returns the results in an HTML-formatted table.

    Args:
        queries_csv_content: A string containing the CSV data of test queries.
    
    Returns:
        An HTML string containing the evaluation results.
    """
    # Load queries from the CSV content string
    try:
        queries_df = pd.read_csv(StringIO(queries_csv_content), quotechar='"', doublequote=True)
        if 'Query' not in queries_df.columns:
            logger.error(f"Error: 'Query' column not found in CSV content.")
            return "<p style='color:red;'>Error: 'Query' column not found in CSV data. Please ensure the CSV has a 'Query' header.</p>"
        queries_from_csv = queries_df['Query'].tolist()
    except Exception as e:
        logger.error(f"Error reading queries CSV content: {e}")
        return f"<p style='color:red;'>Error parsing queries CSV content: {e}</p>"

    # --- Define Ground Truth (Explicitly defined for exactly one relevant product) ---
    # This dictionary maps query strings to a list of product IDs that are
    # considered *truly relevant* for that query. Each query here MUST have exactly one relevant product.
    ground_truth_map = {
        "I'm searching for an apparel item that is white and costs less than five hundred rupees.": ["prod1"],
        "Are there any ergonomic furniture pieces that are also aesthetically pleasing and made of wood?": ["prod8"],
        "Show me cotton shirts in yellow with a relaxed fit.": ["prod1"],
        "Browse your home goods, focusing on items that are both decorative and functional.": ["prod8"],
        "I'm interested in accessories that protect against RFID, like wallets, in a classic leather finish.": ["prod6"],
        "I want a comfortable white t-shirt suitable for everyday wear, possibly with a subtle print.": ["prod1"],
        "Suggest a portable speaker with deep bass and a battery life of over 10 hours.": ["prod9"],
        "I need orange running shoes with advanced cushioning technology for long distances.": ["prod4"],
        "Can you show me blue denim jeans with a straight cut that are pre-shrunk?": ["prod2"],
        "I'm looking for an office chair with lumbar support and adjustable armrests.": ["prod8"],
        "Find me an inexpensive gray wallet with multiple card slots.": ["prod6"],
        "Suggest tablet computers with at least 64GB storage and a high-resolution display.": ["prod3"],
        "I need a white men's shirt that is wrinkle-resistant and priced under eight hundred.": ["prod1"],
        "Do you have cameras with optical zoom and high-definition video recording?": ["prod3"],
        "Show me men's clothing suitable for a semi-formal occasion.": ["prod2"],
        "Can you suggest black casual sneakers that are easy to slip on and off?": ["prod13"],
        "What wearable tech gadgets are available for fitness tracking beyond basic steps?": ["prod12"],
        "What sports products are currently popular for outdoor activities?": ["prod4"],
        "Show me running shoes in blue that provide arch support.": ["prod4"],
        "I need a white blouse with a V-neck design.": ["prod1"],
        "Are there any affordable noise-cancelling headphones that are over-ear?": ["prod5"],
        "Show me everything from the furniture section that is made of solid wood.": ["prod8"],
        "Find Bluetooth earbuds that offer clear call quality and are sweat-resistant.": ["prod5"],
        "Show me a black polo shirt made of pique cotton, priced up to twelve hundred.": ["prod1"],
        "Suggest smart home devices that can be integrated with voice assistants.": ["prod9"],
        "Can you find a blue shirt that is stain-resistant and within fifteen hundred?": ["prod11"],
        "What computer components are available for upgrading a desktop PC?": ["prod14"],
        "I want a yellow casual shirt that is easy to care for and doesn't require ironing.": ["prod1"],
        "What outerwear is available that is both windproof and water-resistant?": ["prod10"],
        "I'm looking for white apparel with subtle embroidery or detailing, maximum ₹2500.": ["prod1"],
        "I need a black wallet with a minimalist design, not more than ₹1000.": ["prod6"],
        "Can you suggest green casual sneakers for women?": ["prod13"],
        "I'm looking for purple canvas shoes that are slip-on style.": ["prod13"],
        "Find speakers that offer 360-degree sound and are waterproof.": ["prod9"],
        "What office wear for women combines comfort with professional style?": ["prod11"],
        "Suggest wearable technology that monitors heart rate continuously.": ["prod12"],
        "What ethnic wear kurtis are available with contemporary designs?": ["prod11"],
        "Do you have any smart phones with a large screen?": ["prod3"],
        "Tell me about your denim pants.": ["prod2"],
        "Show me earbuds that are wireless.": ["prod5"],
        "Looking for a wallet that is genuine leather.": ["prod6"],
        "What kind of digital watches do you sell?": ["prod7"],
        "Is there an office chair with adjustable features?": ["prod8"],
        "I'm interested in portable Bluetooth speakers.": ["prod9"],
        "Do you have any backpacks for laptops?": ["prod10"],
        "Show me traditional kurtis for women.": ["prod11"],
        "Looking for a fitness tracker with heart rate monitoring.": ["prod12"],
        "What are your casual sneakers like?": ["prod13"],
        "I need a wireless computer mouse.": ["prod14"],
        "Show me sunglasses with UV protection.": ["prod15"],
        "Jeans for everyday wear.": ["prod2"],
        "Phones with high-resolution cameras.": ["prod3"],
        "Headphones with noise cancellation.": ["prod5"],
        "Accessories with RFID blocking.": ["prod6"],
        "Watches that are waterproof.": ["prod7"],
        "Ergonomic chairs for office use.": ["prod8"],
        "Speakers with long battery life.": ["prod9"],
        "Backpacks for carrying a laptop.": ["prod10"],
        "Kurtis with traditional prints.": ["prod11"],
        "Bands that track activity.": ["prod12"],
        "Sneakers for casual outings.": ["prod13"],
        "Mice that are wireless.": ["prod14"],
        "Eyewear that protects from UV rays.": ["prod15"],
        "Any white t-shirts?": ["prod1"],
        "Blue jeans.": ["prod2"],
        "Smartphones with large displays.": ["prod3"],
        "Running shoes with cushioning.": ["prod4"],
        "Wireless earbuds for audio.": ["prod5"],
        "Leather wallets.": ["prod6"],
        "Digital watches.": ["prod7"],
        "Office chairs.": ["prod8"],
        "Bluetooth speakers.": ["prod9"],
        "Laptop bags.": ["prod10"],
        "Cotton kurtis.": ["prod11"],
        "Fitness bands.": ["prod12"],
        "Casual sneakers.": ["prod13"],
        "Wireless mice.": ["prod14"],
        "Sunglasses.": ["prod15"],
        "Can I find a comfortable t-shirt for daily wear?": ["prod1"],
        "Looking for durable jeans.": ["prod2"],
        "Show me latest smartphones.": ["prod3"],
        "Need good running shoes.": ["prod4"],
        "Wallets with security features.": ["prod6"],
        "Stylish digital watches.": ["prod7"],
        "Ergonomic seating for my office.": ["prod8"],
        "Speakers for music on the go.": ["prod9"],
        "Bags for laptops.": ["prod10"],
        "Traditional Indian apparel.": ["prod11"],
        "Health monitoring bands.": ["prod12"],
        "Everyday sneakers.": ["prod13"],
        "Computer pointing devices.": ["prod14"],
        "Eyewear for sun protection.": ["prod15"],
        "White top made of cotton.": ["prod1"],
        "Denim trousers.": ["prod2"],
        "Mobile phones.": ["prod3"],
        "Earbuds.": ["prod5"],
        "Wallets.": ["prod6"],
        "Chairs.": ["prod8"],
        "Speakers.": ["prod9"],
        "Backpacks.": ["prod10"],
        "Kurtis.": ["prod11"],
        "Fitness devices.": ["prod12"],
        "Footwear for casual use.": ["prod13"],
        "Computer mouse.": ["prod14"],
        "Goggles.": ["prod15"],
        "Basic white t-shirt.": ["prod1"],
        "Classic blue jeans.": ["prod2"],
        "New smartphones.": ["prod3"],
        "Noise-cancelling earbuds.": ["prod5"],
        "RFID wallets.": ["prod6"],
        "Waterproof digital watches.": ["prod7"],
        "Adjustable office chairs.": ["prod8"],
        "Portable Bluetooth speakers.": ["prod9"],
        "Laptop backpacks.": ["prod10"],
        "Printed cotton kurtis.": ["prod11"],
        "Heart rate monitors.": ["prod12"],
        "Comfortable casual sneakers.": ["prod13"],
        "Wireless optical mouse.": ["prod14"],
        "Unisex sunglasses.": ["prod15"],
        "Furniture for home office.": ["prod8"],
        "Watches with LED display.": ["prod7"],
        "Speakers with deep bass.": ["prod9"],
        "Bags for books and laptops.": ["prod10"],
        "Kurtis for festive occasions.": ["prod11"],
        "Bands for tracking activity.": ["prod12"],
        "Slip-on sneakers.": ["prod13"],
        "Mice with adjustable DPI.": ["prod14"],
        "Trendy sunglasses.": ["prod15"],
        "T-shirts.": ["prod1"],
        "Jeans.": ["prod2"],
        "Smartphones.": ["prod3"],
        "Running shoes.": ["prod4"],
        "Earbuds.": ["prod5"],
        "Wallets.": ["prod6"],
        "Watches.": ["prod7"],
        "Office chairs.": ["prod8"],
        "Bluetooth speakers.": ["prod9"],
        "Backpacks.": ["prod10"],
        "Kurtis.": ["prod11"],
        "Fitness bands.": ["prod12"],
        "Sneakers.": ["prod13"],
        "Mice.": ["prod14"],
        "Sunglasses.": ["prod15"],
        # Additional single GT queries
        "A white short-sleeved cotton top.": ["prod1"],
        "Comfortable basic tee.": ["prod1"],
        "Plain white cotton shirt.": ["prod1"],
        "T-shirt made of 100% cotton.": ["prod1"],
        "Casual white top for everyday.": ["prod1"],
        "Classic blue trousers made of denim.": ["prod2"],
        "Straight fit denim pants.": ["prod2"],
        "Durable blue jeans.": ["prod2"],
        "Everyday denim bottom wear.": ["prod2"],
        "Standard blue denim.": ["prod2"],
        "Latest model Android phone.": ["prod3"],
        "Mobile with a 6.5-inch screen.": ["prod3"],
        "Phone with a 64MP camera.": ["prod3"],
        "New smartphone release.": ["prod3"],
        "High-resolution display phone.": ["prod3"],
        "Shoes designed for running comfort.": ["prod4"],
        "Athletic footwear with extra cushioning.": ["prod4"],
        "Sports shoes for long distances.": ["prod4"],
        "Cushioned running footwear.": ["prod4"],
        "Comfortable shoes for jogging.": ["prod4"],
        "Bluetooth noise-cancelling earphones.": ["prod5"],
        "Wireless in-ear headphones.": ["prod5"],
        "Earbuds with active noise cancellation.": ["prod5"],
        "Portable wireless audio device.": ["prod5"],
        "Headphones without wires.": ["prod5"],
        "Genuine leather wallet with card slots.": ["prod6"],
        "Wallet with RFID blocking technology.": ["prod6"],
        "Compact leather billfold.": ["prod6"],
        "Security wallet.": ["prod6"],
        "Brown leather wallet.": ["prod6"],
        "Waterproof digital wrist watch.": ["prod7"],
        "Stylish watch with LED display.": ["prod7"],
        "Modern digital timepiece.": ["prod7"],
        "Sporty waterproof watch.": ["prod7"],
        "Digital watch for men/women.": ["prod7"],
        "Ergonomic chair for long office hours.": ["prod8"],
        "Mesh back chair with adjustable height.": ["prod8"],
        "Comfortable seating for workspace.": ["prod8"],
        "Adjustable office chair.": ["prod8"],
        "Chair for computer desk.": ["prod8"],
        "Portable speaker with powerful bass.": ["prod9"],
        "Speaker with 12-hour playback.": ["prod9"],
        "Wireless speaker for outdoor use.": ["prod9"],
        "Deep bass Bluetooth speaker.": ["prod9"],
        "Long battery life portable speaker.": ["prod9"],
        "Water-resistant backpack for laptops.": ["prod10"],
        "Bag suitable for 15.6-inch laptop.": ["prod10"],
        "Durable laptop bag.": ["prod10"],
        "Backpack for work or travel.": ["prod10"],
        "Waterproof laptop carrier.": ["prod10"],
        "Ethnic kurti with traditional designs.": ["prod11"],
        "Cotton kurti for women.": ["prod11"],
        "Block print kurti.": ["prod11"], # Corrected from dict entry
        "Traditional Indian top.": ["prod11"],
        "Comfortable ethnic wear.": ["prod11"],
        "Activity tracker with heart rate monitor.": ["prod12"],
        "Fitness band for sleep tracking.": ["prod12"],
        "Wearable health tracker.": ["prod12"],
        "Smart band for activity.": ["prod12"],
        "Monitor heart rate activity band.": ["prod12"],
        "Casual sneakers with cushioned sole.": ["prod13"],
        "Sneakers for daily walking.": ["prod13"],
        "Comfortable casual footwear.": ["prod13"],
        "Slip-on casual sneakers.": ["prod13"],
        "Everyday use sneakers.": ["prod13"],
        "Ergonomic mouse for computer.": ["prod14"],
        "Wireless optical mouse.": ["prod14"],
        "Mouse with adjustable DPI.": ["prod14"], # Corrected from dict entry
        "Computer mouse without cable.": ["prod14"],
        "Comfortable wireless pointing device.": ["prod14"],
        "UV-protected unisex sunglasses.": ["prod15"],
        "Stylish eyewear for sun.": ["prod15"],
        "Fashionable sun goggles.": ["prod15"],
        "Sunglasses with eye protection.": ["prod15"],
        "Trendy sunglasses.": ["prod15"],
    }

    # Filter ground truth: Keep only queries with exactly one relevant product ID
    ground_truth = {}
    for query, relevant_ids in ground_truth_map.items():
        if len(relevant_ids) == 1:
            ground_truth[query] = relevant_ids
    
    # Filter the 'queries_from_csv' list to only include those that made it into the filtered 'ground_truth'
    queries_to_evaluate = [query for query in queries_from_csv if query in ground_truth]
    queries_to_evaluate.sort() # Sort for consistent report order

    if len(queries_to_evaluate) < 100:
        logger.warning(f"Only {len(queries_to_evaluate)} queries with a single ground truth product found. Aiming for 100+.")


    # Initialize the vector store and add products
    logger.info("Initializing vector store and adding sample products...")
    temp_persist_dir = os.path.join(os.getcwd(), "test_chroma_db")
    vector_store_instance = VectorStore(persist_directory=temp_persist_dir)
    if not vector_store_instance.add_products(sample_products):
        logger.error("Failed to add products to vector store. Exiting.")
        if os.path.exists(temp_persist_dir) and os.path.isdir(temp_persist_dir):
            shutil.rmtree(temp_persist_dir)
        return "<p style='color:red;'>Failed to initialize vector store or add products. Check logs for details.</p>"

    all_precision = []
    all_recall = []
    all_f1 = []
    
    html_output = []
    html_output.append("<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='UTF-8'>\n<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n<title>RAG Evaluation Report</title>\n<style>\n  body { font-family: sans-serif; margin: 20px; }\n  table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }\n  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n  th { background-color: #f2f2f2; }\n  h2, h3 { color: #333; }\n  p { color: #555; }\n</style>\n</head>\n<body>")
    html_output.append("<h2>RAG Evaluation Results</h2>")
    html_output.append("<h3>Detailed Query Results</h3>")
    html_output.append("<table>")
    html_output.append("<thead><tr>")
    html_output.append("<th>Query</th>")
    html_output.append("<th>Retrieved Product ID (Top 1)</th>")
    html_output.append("<th>Relevant Product ID (Ground Truth)</th>")
    html_output.append("<th>Precision</th>")
    html_output.append("<th>Recall</th>")
    html_output.append("<th>F1-Score</th>")
    html_output.append("</tr></thead><tbody>")

    for query in queries_to_evaluate:
        relevant_product_ids_for_query = ground_truth.get(query, [])
        
        # This check ensures we only process queries that definitively have one GT.
        if not relevant_product_ids_for_query or len(relevant_product_ids_for_query) != 1:
            logger.error(f"Internal Error: Query '{query}' should have exactly one ground truth but has {len(relevant_product_ids_for_query)}. Skipping.")
            continue

        # Perform RAG search with limit=1 to get only the top predicted product
        retrieved_products = vector_store_instance.search(query=query, limit=1)
        
        top_retrieved_product_id = retrieved_products[0]['id'] if retrieved_products else "N/A"
        retrieved_product_ids_for_f1 = [p['id'] for p in retrieved_products]

        precision, recall, f1 = calculate_precision_recall_f1(retrieved_product_ids_for_f1, relevant_product_ids_for_query)
        
        all_precision.append(precision)
        all_recall.append(recall)
        all_f1.append(f1)

        html_output.append("<tr>")
        html_output.append(f"<td>{query}</td>")
        html_output.append(f"<td>{top_retrieved_product_id}</td>")
        html_output.append(f"<td>{relevant_product_ids_for_query[0]}</td>")
        html_output.append(f"<td>{precision:.4f}</td>")
        html_output.append(f"<td>{recall:.4f}</td>")
        html_output.append(f"<td>{f1:.4f}</td>")
        html_output.append("</tr>")

    html_output.append("</tbody></table>")

    avg_precision = sum(all_precision) / len(all_precision) if all_precision else 0.0
    avg_recall = sum(all_recall) / len(all_recall) if all_recall else 0.0
    avg_f1 = sum(all_f1) / len(all_f1) if all_f1 else 0.0

    html_output.append("<h3>Evaluation Summary</h3>")
    html_output.append(f"<p>Total queries evaluated: {len(all_f1)}</p>")
    html_output.append(f"<p>Average Precision: {avg_precision:.4f}</p>")
    html_output.append(f"<p>Average Recall: {avg_recall:.4f}</p>")
    html_output.append(f"<p>Average F1-Score: {avg_f1:.4f}</p>")
    html_output.append("<p style='font-style: italic; color: #555;'>Note: Only queries with exactly one ground truth product were included in this report.</p>")
    html_output.append("<p style='font-style: italic; color: #555;'>The accuracy of these metrics depends entirely on the correctness of the 'ground_truth' dictionary and the relevance of the sample products.</p>")
    html_output.append("</body>\n</html>")
    
    if os.path.exists(temp_persist_dir) and os.path.isdir(temp_persist_dir):
        shutil.rmtree(temp_persist_dir)
        logger.info(f"Cleaned up temporary persistence directory: {temp_persist_dir}")
    
    return "\n".join(html_output)

if __name__ == "__main__":
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY environment variable not set. Please set it to run the evaluation.")
        logger.error("You can set it in your terminal: export OPENAI_API_KEY='your_api_key_here'")
    else:
        # Define the full set of queries and their ground truths.
        # The script will internally filter for queries with exactly one ground truth.
        # This list ensures that the CSV content matches the ground_truth_map keys.
        all_possible_queries = [
            "I'm searching for an apparel item that is white and costs less than five hundred rupees.",
            "Are there any ergonomic furniture pieces that are also aesthetically pleasing and made of wood?",
            "Show me cotton shirts in yellow with a relaxed fit.",
            "Browse your home goods, focusing on items that are both decorative and functional.",
            "I'm interested in accessories that protect against RFID, like wallets, in a classic leather finish.",
            "I want a comfortable white t-shirt suitable for everyday wear, possibly with a subtle print.",
            "Suggest a portable speaker with deep bass and a battery life of over 10 hours.",
            "I need orange running shoes with advanced cushioning technology for long distances.",
            "Can you show me blue denim jeans with a straight cut that are pre-shrunk?",
            "I'm looking for an office chair with lumbar support and adjustable armrests.",
            "Find me an inexpensive gray wallet with multiple card slots.",
            "Suggest tablet computers with at least 64GB storage and a high-resolution display.",
            "I need a white men's shirt that is wrinkle-resistant and priced under eight hundred.",
            "Do you have cameras with optical zoom and high-definition video recording?",
            "Show me men's clothing suitable for a semi-formal occasion.",
            "Can you suggest black casual sneakers that are easy to slip on and off?",
            "What wearable tech gadgets are available for fitness tracking beyond basic steps?",
            "What sports products are currently popular for outdoor activities?",
            "Show me running shoes in blue that provide arch support.",
            "I need a white blouse with a V-neck design.",
            "Are there any affordable noise-cancelling headphones that are over-ear?",
            "Show me everything from the furniture section that is made of solid wood.",
            "Find Bluetooth earbuds that offer clear call quality and are sweat-resistant.",
            "Show me a black polo shirt made of pique cotton, priced up to twelve hundred.",
            "Suggest smart home devices that can be integrated with voice assistants.",
            "Can you find a blue shirt that is stain-resistant and within fifteen hundred?",
            "What computer components are available for upgrading a desktop PC?",
            "I want a yellow casual shirt that is easy to care for and doesn't require ironing.",
            "What outerwear is available that is both windproof and water-resistant?",
            "I'm looking for white apparel with subtle embroidery or detailing, maximum ₹2500.",
            "I need a black wallet with a minimalist design, not more than ₹1000.",
            "Can you suggest green casual sneakers for women?",
            "I'm looking for purple canvas shoes that are slip-on style.",
            "Find speakers that offer 360-degree sound and are waterproof.",
            "What office wear for women combines comfort with professional style?",
            "Suggest wearable technology that monitors heart rate continuously.",
            "What ethnic wear kurtis are available with contemporary designs?",
            "Do you have any smart phones with a large screen?",
            "Tell me about your denim pants.",
            "Show me earbuds that are wireless.",
            "Looking for a wallet that is genuine leather.",
            "What kind of digital watches do you sell?",
            "Is there an office chair with adjustable features?",
            "I'm interested in portable Bluetooth speakers.",
            "Do you have any backpacks for laptops?",
            "Show me traditional kurtis for women.",
            "Looking for a fitness tracker with heart rate monitoring.",
            "What are your casual sneakers like?",
            "I need a wireless computer mouse.",
            "Show me sunglasses with UV protection.",
            "Jeans for everyday wear.",
            "Phones with high-resolution cameras.",
            "Headphones with noise cancellation.",
            "Accessories with RFID blocking.",
            "Watches that are waterproof.",
            "Ergonomic chairs for office use.",
            "Speakers with long battery life.",
            "Backpacks for carrying a laptop.",
            "Kurtis with traditional prints.",
            "Bands that track activity.",
            "Sneakers for casual outings.",
            "Mice that are wireless.",
            "Eyewear that protects from UV rays.",
            "Any white t-shirts?",
            "Blue jeans.",
            "Smartphones with large displays.",
            "Running shoes with cushioning.",
            "Wireless earbuds for audio.",
            "Leather wallets.",
            "Digital watches.",
            "Office chairs.",
            "Bluetooth speakers.",
            "Laptop bags.",
            "Cotton kurtis.",
            "Fitness bands.",
            "Casual sneakers.",
            "Wireless mice.",
            "Sunglasses.",
            "Can I find a comfortable t-shirt for daily wear?",
            "Looking for durable jeans.",
            "Show me latest smartphones.",
            "Need good running shoes.",
            "Wallets with security features.",
            "Stylish digital watches.",
            "Ergonomic seating for my office.",
            "Speakers for music on the go.",
            "Bags for laptops.",
            "Traditional Indian apparel.",
            "Health monitoring bands.",
            "Everyday sneakers.",
            "Computer pointing devices.",
            "Eyewear for sun protection.",
            "White top made of cotton.",
            "Denim trousers.",
            "Mobile phones.",
            "Earbuds.",
            "Wallets.",
            "Chairs.",
            "Speakers.",
            "Backpacks.",
            "Kurtis.",
            "Fitness devices.",
            "Footwear for casual use.",
            "Computer mouse.",
            "Goggles.",
            "Basic white t-shirt.",
            "Classic blue jeans.",
            "New smartphones.",
            "Noise-cancelling earbuds.",
            "RFID wallets.",
            "Waterproof digital watches.",
            "Adjustable office chairs.",
            "Portable Bluetooth speakers.",
            "Laptop backpacks.",
            "Printed cotton kurtis.",
            "Heart rate monitors.",
            "Comfortable casual sneakers.",
            "Wireless optical mouse.",
            "Unisex sunglasses.",
            "Furniture for home office.",
            "Watches with LED display.",
            "Speakers with deep bass.",
            "Bags for books and laptops.",
            "Kurtis for festive occasions.",
            "Bands for tracking activity.",
            "Slip-on sneakers.",
            "Mice with adjustable DPI.",
            "Trendy sunglasses.",
            "T-shirts.",
            "Jeans.",
            "Smartphones.",
            "Running shoes.",
            "Earbuds.",
            "Wallets.",
            "Watches.",
            "Office chairs.",
            "Bluetooth speakers.",
            "Backpacks.",
            "Kurtis.",
            "Fitness bands.",
            "Sneakers.",
            "Mice.",
            "Sunglasses.",
            "A white short-sleeved cotton top.",
            "Comfortable basic tee.",
            "Plain white cotton shirt.",
            "T-shirt made of 100% cotton.",
            "Casual white top for everyday.",
            "Classic blue trousers made of denim.",
            "Straight fit denim pants.",
            "Durable blue jeans.",
            "Everyday denim bottom wear.",
            "Standard blue denim.",
            "Latest model Android phone.",
            "Mobile with a 6.5-inch screen.",
            "Phone with a 64MP camera.",
            "New smartphone release.",
            "High-resolution display phone.",
            "Shoes designed for running comfort.",
            "Athletic footwear with extra cushioning.",
            "Sports shoes for long distances.",
            "Cushioned running footwear.",
            "Comfortable shoes for jogging.",
            "Bluetooth noise-cancelling earphones.",
            "Wireless in-ear headphones.",
            "Earbuds with active noise cancellation.",
            "Portable wireless audio device.",
            "Headphones without wires.",
            "Genuine leather wallet with card slots.",
            "Wallet with RFID blocking technology.",
            "Compact leather billfold.",
            "Security wallet.",
            "Brown leather wallet.",
            "Waterproof digital wrist watch.",
            "Stylish watch with LED display.",
            "Modern digital timepiece.",
            "Sporty waterproof watch.",
            "Digital watch for men/women.",
            "Ergonomic chair for long office hours.",
            "Mesh back chair with adjustable height.",
            "Comfortable seating for workspace.",
            "Adjustable office chair.",
            "Chair for computer desk.",
            "Portable speaker with powerful bass.",
            "Speaker with 12-hour playback.",
            "Wireless speaker for outdoor use.",
            "Deep bass Bluetooth speaker.",
            "Long battery life portable speaker.",
            "Water-resistant backpack for laptops.",
            "Bag suitable for 15.6-inch laptop.",
            "Durable laptop bag.",
            "Backpack for work or travel.",
            "Waterproof laptop carrier.",
            "Ethnic kurti with traditional designs.",
            "Cotton kurti for women.",
            "Block print kurti.",
            "Traditional Indian top.",
            "Comfortable ethnic wear.",
            "Activity tracker with heart rate monitor.",
            "Fitness band for sleep tracking.",
            "Wearable health tracker.",
            "Smart band for activity.",
            "Monitor heart rate activity band.",
            "Casual sneakers with cushioned sole.",
            "Sneakers for daily walking.",
            "Comfortable casual footwear.",
            "Slip-on casual sneakers.",
            "Everyday use sneakers.",
            "Ergonomic mouse for computer.",
            "Wireless optical mouse.",
            "Mouse with adjustable DPI.",
            "Computer mouse without cable.",
            "Comfortable wireless pointing device.",
            "UV-protected unisex sunglasses.",
            "Stylish eyewear for sun.",
            "Fashionable sun goggles.",
            "Sunglasses with eye protection.",
            "Trendy sunglasses.",
        ]

        # Generate CSV content based on all_possible_queries
        selected_queries_csv_content = '"Query"\n' + '\n'.join([f'"{q}"' for q in all_possible_queries])

        html_results = run_rag_evaluation(selected_queries_csv_content)
        
        report_filename = "rag_report.html"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(html_results)
        print(f"RAG evaluation report generated: {report_filename}")
