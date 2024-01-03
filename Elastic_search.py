from elasticsearch import Elasticsearch

# Initialize the Elasticsearch client
client = Elasticsearch(
    "https://6a08a4951dff4c61a75fd673075afa86.us-central1.gcp.cloud.es.io:443",
    api_key="SU9MZHg0d0JiNlRXeGpHZ2Z6Nk86RlY1MjVrVGNUZW0yNVR4OXVXY056UQ=="
)

# Test the connection
try:
    info = client.info()
    print("Connection Successful:", info)
except Exception as e:
    print("Error Connecting to Elasticsearch:", e)

# Ingest data
documents = [
    {"index": {"_index": "search-product-vendor", "_id": "9780553351927"}},
    {"name": "Snow Crash", "author": "Neal Stephenson", "release_date": "1992-06-01", "page_count": 470},
    {"index": {"_index": "search-product-vendor", "_id": "9780441017225"}},
    {"name": "Revelation Space", "author": "Alastair Reynolds", "release_date": "2000-03-15", "page_count": 585},
    # ... Add more documents as needed
]

# Perform bulk ingestion
try:
    client.bulk(operations=documents)
    print("Data ingestion successful")
except Exception as e:
    print("Error ingesting data:", e)

# Perform a basic search query
try:
    search_response = client.search(index="search-product-vendor", q="snow")
    print("Search Results:", search_response)
except Exception as e:
    print("Error performing search query:", e)
