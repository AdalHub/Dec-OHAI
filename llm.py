import os
import getpass
import time
import re
import json
from openai import OpenAI
import ddg_search
from dotenv import load_dotenv
from faunadb_client import get_fauna_client
from faunadb import query as q
from tools import tools_list
from elasticsearch import Elasticsearch

# Load environment variables from .env file
load_dotenv()


# Retrieve OpenAI API key from environment variables
open_ai_key = os.getenv('open_ai_key')

# Set the OpenAI API key in the environment
os.environ["OPENAI_API_KEY"] = open_ai_key


# Retrieve variables from .env file
elasticsearch_url = os.getenv('ELASTICSEARCH_URL')
elasticsearch_api_key = os.getenv('ELASTICSEARCH_API_KEY')
if not elasticsearch_url or not elasticsearch_api_key:
    raise ValueError("Elasticsearch URL or API key missing in environment variables.")


# Initialize the Elasticsearch client with variables from .env
es_client = Elasticsearch(elasticsearch_url, api_key=elasticsearch_api_key)


# Initialize FaunaDB client
fauna_client = get_fauna_client()

# Example operation: fetch a document by its reference from the fauna db
result = fauna_client.query(q.get(q.ref(q.collection('Products'), '384967684936171593')))
print(result)




# Placeholder for Elasticsearch lookup tool
def elasticsearch_lookup(search_term, search_field):
    if not search_term or not search_field:
        print("Empty search term or field")
        return []

    try:
        index_name = "search-product-vendor"
        print("SEARCHING " + search_term + " OR " + search_field)
        search_body = {
            "query": {
                "match": {
                    search_field: search_term
                }
            }
        }

        response = es_client.search(index=index_name, body=search_body)

        if response["hits"]["hits"]:
            results_text = "Search Results:\n"
            for hit in response["hits"]["hits"]:
                item = hit["_source"]
                # Format each result as a string
                results_text += f"Name: {item.get('name')}, Author: {item.get('author')}, Release Date: {item.get('release_date')}, Page Count: {item.get('page_count')}\n"
        else:
            results_text = "No results found"

        return results_text

    except Exception as e:
        print(f"An error occurred during Elasticsearch search: {e}")
        return '[]'  # Return empty JSON array as a string





def duckduckgo_search(query):
    try:
        # If ddg_search has a function named 'search'
        results = ddg_search.search(query)
        # Convert results to string if necessary
        return json.dumps(results) if results else 'No results found'
    except AttributeError:
        print("Error: 'search' function not found in ddg_search module")
        return '[]'  # Return empty JSON array as string


# Placeholder for FaunaDB update tool
def update_fauna_db(data):
    try:
        update_result = fauna_client.query(
            q.create(q.collection('YourCollection'), {"data": data})
        )
        return json.dumps(update_result)  # Convert result to JSON string
    except Exception as e:
        print(f"An error occurred: {e}")
        return '{}'  # Return empty JSON object as string






# Initialize OpenAI client
client = OpenAI()

#initializes a client, and creates an assistant using the OpenAI API. It then stores the assistant's ID.
# Instructions modified for clarity in extracting arguments from user queries
assistant = client.beta.assistants.create(
    name="Shopping Expert Assistant",
    #instructions="You are an intelligent personal assistant dedicated to understanding and fulfilling your clients' specific needs. Your primary goal is to recommend products that align closely with the client's requests. When a client specifies a product, your first step is to consult the FaunaDB database to check for detailed information on that item. If the database lacks sufficient details or if the item is not found, you are then required to utilize web search tools to find the product online, focusing on the best price or other specified criteria. Ensure accuracy and relevance in your responses, and prioritize client satisfaction in every interaction.",
    instructions="You are an intelligent assistant. For product queries, identify the product name and any specific detail like 'author', 'price', or 'description'. Use the elasticsearch_lookup function with 'search_term' as the product name and 'search_field' as the detail. For general web searches, use the duckduckgo_search function with the full user query.",
    tools=tools_list,
    model="gpt-3.5-turbo",
)

assistant_id = assistant.id
    # Create a new thread for the OpenAI Assistant
thread = client.beta.threads.create()

query = input("Please enter your query: ")
    # Create a new message in the thread
message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=query,
    )

print("Creating Assistant ")
print(f"Assistant ID: {assistant_id}")

    # Create a new run in the thread
run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

#print("Querying OpenAI Assistant Thread.")
print(f"Assistant ID: {assistant_id}")
  
# Polling for Assistant's response
while True:
    # Wait for a few seconds before checking the run status
    time.sleep(5)

    # Retrieve the run status
    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

    # Check if run is completed
    if run_status.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Loop through messages and print content based on role
        for msg in messages.data:
            role = msg.role
            content = msg.content[0].text.value
            print(f"{role.capitalize()}: {content}")
        break
    elif run_status.status == 'requires_action':
        print("Function Calling")
        required_actions = run_status.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for action in required_actions:
            func_name = action.function.name
            print("USING FUNCTION " + func_name)
            arguments = json.loads(action.function.arguments)

            if func_name == "elasticsearch_lookup":
                search_term = arguments.get('search_term')
                search_field = arguments.get('search_field')
                query_result = elasticsearch_lookup(search_term, search_field)
                # Ensure the output is in string format
                #output_str = json.dumps(query_result) if query_result else 'No results found'
                output_str = elasticsearch_lookup(search_term, search_field)
                tool_outputs.append({
                    "tool_call_id": action.id,
                    "output": output_str
                })


            elif func_name == "duckduckgo_search":
                search_query = arguments.get('query')
                search_results = duckduckgo_search(search_query)
                tool_outputs.append({
                    "tool_call_id": action.id,
                    "output": search_results
                })

            elif func_name == "update_fauna_db":
                data = arguments.get('data')
                update_status = update_fauna_db(data)
                tool_outputs.append({
                    "tool_call_id": action.id,
                    "output": update_status
                })

    # Submit tool outputs back to the Assistant
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
    else:
        print("Waiting for the Assistant to process...")




