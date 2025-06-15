"""
Sample product data for the e-commerce application.
This data is used to populate the vector store and provide product information.
"""
import os
from src.utils.ngrok import get_ngrok_url_with_retry

def get_image_url(image_path):
    """Helper to get an image URL that works in both local and production environments"""
    # Try to get the ngrok URL for production environments
    ngrok_url = get_ngrok_url_with_retry()
    if ngrok_url:
        return f"{ngrok_url}{image_path}"
    # Fall back to relative URL for local development
    return image_path

products = [
    {
        "id": "prod1",
        "name": "Cotton T-Shirt",
        "description": "A comfortable 100% cotton white t-shirt",
        "price": "₹499",
        "category": "apparel",
        "image_url": get_image_url("/static/products/tshirt.jpg")
    },
    {
        "id": "prod2",
        "name": "Denim Jeans",
        "description": "Classic blue denim jeans with straight fit",
        "price": "₹1299",
        "category": "apparel",
        "image_url": get_image_url("/static/products/jeans.jpg")
    },
    {
        "id": "prod3",
        "name": "Smartphone",
        "description": "Latest Android smartphone with 6.5 inch display and 64MP camera",
        "price": "₹12999",
        "category": "electronics",
        "image_url": get_image_url("/static/products/phone.jpg")
    },
    {
        "id": "prod4",
        "name": "Running Shoes",
        "description": "Comfortable running shoes with extra cushioning",
        "price": "₹2499",
        "category": "footwear",
        "image_url": get_image_url("/static/products/shoe.jpg")
    },
    {
        "id": "prod5",
        "name": "Wireless Earbuds",
        "description": "Bluetooth wireless earbuds with noise cancellation",
        "price": "₹1999",
        "category": "electronics",
        "image_url": get_image_url("/static/products/ear_buds.jpg")
    }
]