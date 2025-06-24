"""
Sample product data for the e-commerce application.
This data is used to populate the vector store and provide product information.

IMPORTANT: Make sure to run generate_vector_store_persistence.py to add these products to the vector store.
"""

products = [
    {
        "id": "prod1",
        "name": "Cotton T-Shirt",
        "description": "A comfortable 100 percent cotton white t-shirt",
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
        "image_url": "https://th.bing.com/th/id/OIP.SvJhQLhZ6tUDihv6-PwxqAHaHa?w=209&h=209&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod7",
        "name": "Digital Watch",
        "description": "Stylish waterproof digital watch with LED display",
        "price": "₹1599",
        "category": "accessories",
        "image_url": "https://th.bing.com/th/id/OIP.ZDoda3B5d8FQvOuvu6WZWgHaHa?w=182&h=195&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod8",
        "name": "Office Chair",
        "description": "Ergonomic mesh back office chair with adjustable height",
        "price": "₹4999",
        "category": "furniture",
        "image_url": "https://th.bing.com/th/id/OIP.OZ-_kHNifKKp53Qt9PY7WwAAAA?w=185&h=204&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod9",
        "name": "Bluetooth Speaker",
        "description": "Portable speaker with deep bass and 12-hour battery life",
        "price": "₹1299",
        "category": "electronics",
        "image_url": "https://th.bing.com/th/id/OIP.UyIzEfCEpxFLAUGdVXuh6QHaFk?w=238&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod10",
        "name": "Laptop Backpack",
        "description": "Water-resistant backpack suitable for laptops up to 15.6 inches",
        "price": "₹1099",
        "category": "accessories",
        "image_url": "https://th.bing.com/th/id/OIP.QMoPOJlcZx70APsTKnC5_AHaI7?w=175&h=211&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod11",
        "name": "Cotton Kurti",
        "description": "Ethnic cotton kurti with traditional block prints",
        "price": "₹899",
        "category": "apparel",
        "image_url": "https://th.bing.com/th/id/OIP.zLeRSerSHA9Nu0BSh9OH4QHaHS?w=208&h=206&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod12",
        "name": "Fitness Band",
        "description": "Activity tracker with heart rate and sleep monitor",
        "price": "₹1799",
        "category": "electronics",
        "image_url": "https://th.bing.com/th/id/OIP._j2JUdn1PhefJ7H2UK0cYgHaHa?w=177&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod13",
        "name": "Sneakers",
        "description": "Casual sneakers for daily wear with cushioned sole",
        "price": "₹1499",
        "category": "footwear",
        "image_url": "https://th.bing.com/th/id/OIP.ue8cZS7HNFPc26J7E7dFdgHaHa?w=168&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod14",
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with adjustable DPI",
        "price": "₹699",
        "category": "electronics",
        "image_url": "https://th.bing.com/th/id/OIP._eSPBe46DobbGbyPnmnzDwHaHa?w=178&h=180&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod15",
        "name": "Sunglasses",
        "description": "UV-protected unisex sunglasses with stylish frame",
        "price": "₹1199",
        "category": "accessories",
        "image_url": "https://th.bing.com/th/id/OIP.9XOAN43qTSpwZv5DoATisAHaHa?w=217&h=217&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
    {
        "id": "prod16",
        "name": "Striped Cotton T-Shirt",
        "description": "A comfortable 100 percent cotton t-shirt with stripes",
        "price": "₹499",
        "category": "apparel",
        "image_url": "https://th.bing.com/th/id/OIP.nG3Ntl-V7cQIo1oSxXb0XAHaJ4?w=154&h=205&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3"
    },
]

