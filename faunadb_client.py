from faunadb import query as q
from faunadb.client import FaunaClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch your FaunaDB secret key from the environment variable
FAUNADB_SECRET = os.getenv('FAUNADB_SECRET')

# Initialize the FaunaDB client
fauna_client = FaunaClient(secret=FAUNADB_SECRET)

# Export the FaunaDB client for use in other files
def get_fauna_client():
    return fauna_client
