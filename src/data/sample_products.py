"""
Sample product data for the e-commerce application.
This data is used to populate the vector store and provide product information.

IMPORTANT: Make sure to run generate_vector_store_persistence.py to add these products to the vector store.
"""

products = [
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

