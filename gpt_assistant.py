import os
import getpass
import time
import json
from openai import OpenAI
import ddg_search
from dotenv import load_dotenv


#start variables needed for functions and environment 
#key kept in .env for secret security  
load_dotenv()
open_ai_key = os.getenv('OPEN_AI_API_KEY')
        
os.environ["OPENAI_API_KEY"] = open_ai_key
client = OpenAI()

thread_id = None

instruction_prompt ="""
You are an advanced personal assistant dedicated to understanding and catering to 
the unique needs of each client. Your goal is to provide tailored recommendations 
and solutions. Utilize the following tools effectively to enhance your responses:

1. DuckDuckGo Search: Deploy this tool for real-time internet searches to find 
   up-to-date information, product recommendations, or answers to queries that 
   require external data. Use it to compare products, check reviews, or gather 
   detailed information.

2. Database Access: Leverage our internal database for accessing historical data, 
   client preferences, past queries, and frequently requested information. This 
   is particularly useful for personalized responses based on the client's history 
   or preferences.

3. Puppeteer Automation: Use Puppeteer for tasks that require interaction with web 
   pages, such as retrieving information from sites that are not easily accessible 
   through standard searches, automating form submissions, or scraping specific 
   data points from web pages.

Always analyze the client's query to determine the most appropriate tool. For 
straightforward requests or general inquiries, direct responses may suffice. However, 
complex or detailed queries might require the combined use of these tools to provide 
the best possible answer. Your response should not only answer the query but also 
anticipate any follow-up questions based on the context, offering a comprehensive 
and thoughtful solution. Remember, the key is to balance efficiency with thoroughness 
to deliver prompt yet insightful responses.
"""

    
#initializes a client, and creates an assistant using the OpenAI API. It then stores the assistant's ID.
assistant = client.beta.assistants.create(
        name="Query Assistant",
        instructions=instruction_prompt,
        tools=[

            {"type": "function",
            "function" : ddg_search.ddg_function
            }
        ],
        model="gpt-3.5-turbo"
    )
assistant_id = assistant.id




#handle the status of the run. If the run requires action, it calls submit_tool_outputs
#to process any required tool outputs, then waits for the run to complete.

def wait_for_run_completion(thread_id, run_id):
    while True:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        print(f"Current run status: {run.status}")
        if run.status in ['completed', 'failed', 'requires_action']:
            return run




def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = tool.function.arguments

        if function_name == "duckduckgo_search":
            print("Consulting Duck Duck Go...")
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
    global thread_id

    if thread_id is None:
        thread = client.beta.threads.create()
        thread_id = thread.id
    else:
        thread = client.beta.threads.retrieve(thread_id=thread_id)

    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=query,
    )
    print("Creating Assistant ")

    run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant_id,
    )
    print(f"Assistant ID: {assistant_id}")

    print("Querying OpenAI Assistant Thread.")

    run = wait_for_run_completion(thread.id, run.id)

    if run.status == 'requires_action':
        run = submit_tool_outputs(thread.id, run.id, run.required_action.submit_tool_outputs.tool_calls)
    run = wait_for_run_completion(thread.id, run.id)

    print_messages_from_thread(thread.id)

    return thread_id
  