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

# Initialize FaunaDB client
fauna_client = get_fauna_client()

# Example operation: fetch a document by its reference from the fauna db
result = fauna_client.query(q.get(q.ref(q.collection('Products'), '384967684936171593')))
print(result)



# Initialize ElasticSearch client
elastic_search_endpoint = os.getenv('ELASTIC_SEARCH_ENDPOINT')
elastic_client = Elasticsearch(hosts=[elastic_search_endpoint])

# Placeholder for FaunaDB lookup tool
def fauna_db_lookup(query):
    try:
        response = elastic_client.search(index="your_elastic_index", body={
            "query": {
                "match": {
                    "field_to_search": query  # Adjust as per your ElasticSearch schema
                }
            }
        })
        return [hit["_source"] for hit in response["hits"]["hits"]]
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

# Placeholder for DuckDuckGo web search tool
def duckduckgo_search(query):
    # Implement your DuckDuckGo search logic here
    return ddg_search.search(query)

# Placeholder for FaunaDB update tool
def update_fauna_db(data):
    try:
        update_result = fauna_client.query(
            q.create(q.collection('YourCollection'), {"data": data})
        )
        return update_result
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}







# Initialize OpenAI client
client = OpenAI()

#initializes a client, and creates an assistant using the OpenAI API. It then stores the assistant's ID.
assistant = client.beta.assistants.create(
    name="Shopping Expert Assistant",
    instructions="You are an intelligent personal assistant dedicated to understanding and fulfilling your clients' specific needs. Your primary goal is to recommend products that align closely with the client's requests. When a client specifies a product, your first step is to consult the FaunaDB database to check for detailed information on that item. If the database lacks sufficient details or if the item is not found, you are then required to utilize web search tools to find the product online, focusing on the best price or other specified criteria. Ensure accuracy and relevance in your responses, and prioritize client satisfaction in every interaction.",
    tools= tools_list,
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
        # Handle required actions for custom tools
        print("Function Calling")
        required_actions = run_status.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for action in required_actions:
            func_name = action['function']['name']
            arguments = json.loads(action['function']['arguments'])

            if func_name == "fauna_db_lookup":
                # Create query for ElasticSearch and execute
                query_result = fauna_db_lookup(arguments['query'])
                tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": query_result
                })

            elif func_name == "duckduckgo_search":
                # Execute web search and get results
                search_results = duckduckgo_search(arguments['query'])
                tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": search_results
                })

            elif func_name == "update_fauna_db":
                # Update FaunaDB with new information
                update_status = update_fauna_db(arguments['data'])
                tool_outputs.append({
                    "tool_call_id": action['id'],
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




