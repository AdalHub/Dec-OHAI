import requests
from elasticsearch import Elasticsearch

# Initialize the Elasticsearch client
client = Elasticsearch(
    "https://6a08a4951dff4c61a75fd673075afa86.us-central1.gcp.cloud.es.io:443",
    api_key="SU9MZHg0d0JiNlRXeGpHZ2Z6Nk86RlY1MjVrVGNUZW0yNVR4OXVXY056UQ=="
)

# Categories to fetch bestsellers from
categories = [
    "Amazon Devices & Accessories", "Amazon Renewed", "Appliances", "Apps & Games",
    "Arts, Crafts & Sewing", "Audible Books & Originals", "Automotive", "Baby",
    "Beauty & Personal Care", "Books", "Camera & Photo Products", "CDs & Vinyl",
    "Cell Phones & Accessories", "Climate Pledge Friendly", "Clothing, Shoes & Jewelry",
    "Collectible Coins", "Computers & Accessories", "Digital Educational Resources",
    "Digital Music", "Electronics", "Entertainment Collectibles", "Gift Cards",
    "Grocery & Gourmet Food", "Handmade Products", "Health & Household", "Home & Kitchen",
    "Industrial & Scientific", "Kindle Store", "Kitchen & Dining", "Movies & TV",
    "Musical Instruments", "Office Products", "Patio, Lawn & Garden", "Pet Supplies",
    "Software", "Sports & Outdoors", "Sports Collectibles", "Tools & Home Improvement",
    "Toys & Games", "Unique Finds", "Video Games"
]


# Rainforest API key
api_key = '962BFCBC3E9C47E982C8FBF6DC793414'

# Function to fetch bestsellers for a category
def fetch_bestsellers(category_id):
    params = {
        'api_key': api_key,
        'type': 'bestsellers',
        'amazon_domain': 'amazon.com',
        'category_id': category_id
    }
    response = requests.get('https://api.rainforestapi.com/request', params)
    return response.json()

# Function to index products to Elasticsearch
def index_to_elasticsearch(products):
    for product in products:
        try:
            # Modify the indexing logic as per your Elasticsearch schema
            client.index(index="search-product-vendor", document=product)
        except Exception as e:
            print(f"Error indexing product: {e}")

# Main function
def main():
    for category in categories:
        print(f"Fetching bestsellers for category: {category}")
        bestsellers_data = fetch_bestsellers(category)
        if 'bestsellers' in bestsellers_data:
            index_to_elasticsearch(bestsellers_data['bestsellers'])
        else:
            print(f"No bestsellers data found for category: {category}")

# Run the main function
if __name__ == "__main__":
    main()
