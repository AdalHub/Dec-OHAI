import os
import getpass
import time
import json
from openai import OpenAI
import ddg_search
from dotenv import load_dotenv



#start variables needed for functions and environment 
# load_dotenv()

        # open_ai_key = os.getenv('open_ai_key')
        # os.environ["OPENAI_API_KEY"] = "key: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"
os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")
client = OpenAI()
    
#initializes a client, and creates an assistant using the OpenAI API. It then stores the assistant's ID.
assistant = client.beta.assistants.create(
        name="Query Assistant",
        instructions="You are a personal assistant. Use the provided functions to answer questions.",
        tools=[

            {"type": "function",
            "function" : ddg_search.ddg_function
            }
        ],
        model="gpt-3.5-turbo"
    )
assistant_id = assistant.id






def llm():

    
    print(f"Assistant ID: {assistant_id}")

    use_assistant("what are goods specs for a $400 laptop")



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
  thread = client.beta.threads.create()

  message = client.beta.threads.messages.create(
      thread_id=thread.id,
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
  

if __name__ == "__main__":
    llm()
