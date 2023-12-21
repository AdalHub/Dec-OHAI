import openai
import requests  # For making API requests to DuckDuckGo

class SuggestionAgent:
    def __init__(self, openai_api_key, duckduckgo_api_key=None):
        self.openai_api_key = openai_api_key
        openai.api_key = self.openai_api_key
        self.duckduckgo_api_key = duckduckgo_api_key

    def get_suggestions(self, user_input):
        while True:  # Loop to continuously engage with the user
            # Analyze the user's input and decide on the next step
            suggestion_response = self.generate_suggestion(user_input)
            print(suggestion_response)

            # Ask the user if they need more help or if the suggestion is sufficient
            user_response = input("Do you need more help with this? (yes/no) ")
            if user_response.lower() == 'no':
                break  # Exit the loop if the user is satisfied

            # Get further input from the user
            user_input = input("Please provide more details or ask another question: ")

    def generate_suggestion(self, user_query):
        # Here you can use OpenAI's GPT model to generate a suggestion based on the user query
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Generate a product suggestion based on this query: '{user_query}'\n",
                max_tokens=100
            )
            suggestion = response.choices[0].text.strip()
            return suggestion
        except Exception as e:
            return f"An error occurred: {e}"

    def search_duckduckgo(self, query):
        # Implement the DuckDuckGo search here
        # This is a placeholder implementation as the exact details depend on the API's capabilities
        try:
            response = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json")
            return response.json()
        except Exception as e:
            return f"An error occurred during the DuckDuckGo search: {e}"
