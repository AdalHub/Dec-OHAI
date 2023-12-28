import os
import getpass
import time
import json
from openai import OpenAI
import ddg_search
from dotenv import load_dotenv
from faunadb_client import get_fauna_client
from faunadb import query as q


# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
open_ai_key = os.getenv('open_ai_key')

# Set the OpenAI API key in the environment
os.environ["OPENAI_API_KEY"] = open_ai_key

# Initialize FaunaDB client
fauna_client = get_fauna_client()

# Example operation: fetch a document by its reference
result = fauna_client.query(q.get(q.ref(q.collection('Products'), '384967684936171593')))
print(result)

# Initialize OpenAI client
client = OpenAI()

    
#initializes a client, and creates an assistant using the OpenAI API. It then stores the assistant's ID.
assistant = client.beta.assistants.create(
        name="Query Assistant",
        instructions="You are a personal assistant who focuses in getting to know your clients needs and recomends a product accordingly. Use the provided functions to give the user what it wants. some request might not need tools. ",
        tools=[

            {"type": "function",
            "function" : ddg_search.ddg_function
            }
        ],
        model="gpt-3.5-turbo"
    )
assistant_id = assistant.id





#main function THIS IS THE FUNCITON THAT WILL EXECUTE THE PROGRAM
def llm():
    print(f"Assistant ID: {assistant_id}")

    while True:
        user_input = input("Enter your query (or type 'exit' to end): ")
        if user_input.lower() == 'exit':
            print("Exiting the Assistant.")
            break

        use_assistant(user_input)


#handle the status of the run. If the run requires action, it calls submit_tool_outputs
#to process any required tool outputs, then waits for the run to complete.

def wait_for_run_completion(thread_id, run_id):
    while True:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(f"Current run status: {run.status}")
        if run.status in ['completed', 'failed', 'requires_action']:
            return run


#Adal adding the faunadb function
def get_product_info(product_title):
    try:
        product = fauna_client.query(
            q.get(q.match(q.index("products_by_title"), product_title))
        )
        return product['data']
    except Exception as e:
        return {'error': str(e)}

def get_vendor_info(vendor_name):
    try:
        vendor = fauna_client.query(
            q.get(q.match(q.index("vendors_by_name"), vendor_name))
        )
        return vendor['data']
    except Exception as e:
        return {'error': str(e)}

def update_product_info(product_title, updated_data):
    try:
        response = fauna_client.query(
            q.update(q.select("ref", q.get(q.match(q.index("products_by_title"), product_title))),
                     {"data": updated_data})
        )
        return response['data']
    except Exception as e:
        return {'error': str(e)}

def update_vendor_info(vendor_name, updated_data):
    try:
        response = fauna_client.query(
            q.update(q.select("ref", q.get(q.match(q.index("vendors_by_name"), vendor_name))),
                     {"data": updated_data})
        )
        return response['data']
    except Exception as e:
        return {'error': str(e)}

#end of functons added








def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = tool.function.arguments
        
        # Example of checking for product information before searching the web
        if function_name == "get_product_info":
            print("Fetching product information from FaunaDB...")
            product_title = json.loads(function_args)["query"]
            output = get_product_info(product_title)

        elif function_name == "get_vendor_info":
            print("Fetching vendor information from FaunaDB...")
            vendor_name = json.loads(function_args)["query"]
            output = get_vendor_info(vendor_name)

        elif function_name == "update_product_info":
            print("Updating product information in FaunaDB...")
            product_data = json.loads(function_args)
            output = update_product_info(product_data["title"], product_data)

        elif function_name == "update_vendor_info":
            print("Updating vendor information in FaunaDB...")
            vendor_data = json.loads(function_args)
            output = update_vendor_info(vendor_data["name"], vendor_data)

        elif function_name == "duckduckgo_search":
            print("Consulting Duck Duck Go...")
            # Perform web search if no FaunaDB data available
            if not output:
                output = ddg_search.duckduckgo_search(query=json.loads(function_args)["query"])

        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

    print(tool_output_array)

    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )


#function prints messages from a given thread
def print_messages_from_thread(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    for msg in messages:
        print(f"{msg.role}: {msg.content[0].text.value}")


#creates a thread, sends a query, processes the run, and then prints the messages.
def use_assistant(query):
    # Check if the query is about product or vendor information
    # Modify these conditions based on how your queries are structured
    if "product" in query.lower() or "vendor" in query.lower():
        # Extract the last word in the query as the title/name
        # Note: This is a simplistic approach; you may need a more sophisticated method
        title_or_name = query.split()[-1]

        # Check in FaunaDB for product/vendor information
        db_response = None
        if "product" in query.lower():
            db_response = get_product_info(title_or_name)
        elif "vendor" in query.lower():
            db_response = get_vendor_info(title_or_name)

        # If found in FaunaDB, print the response and return
        if db_response and 'error' not in db_response:
            print(f"From FaunaDB: {db_response}")
            return
        else:
            print("Not found in FaunaDB, consulting OpenAI Assistant...")

    # Create a new thread for the OpenAI Assistant
    thread = client.beta.threads.create()

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

    print("Querying OpenAI Assistant Thread.")
    run = wait_for_run_completion(thread.id, run.id)

    # Process required actions if any
    if run.status == 'requires_action':
        run = submit_tool_outputs(thread.id, run.id, run.required_action.submit_tool_outputs.tool_calls)
        run = wait_for_run_completion(thread.id, run.id)

    # Print the messages from the thread
    print_messages_from_thread(thread.id)

  

if __name__ == "__main__":
    llm()
