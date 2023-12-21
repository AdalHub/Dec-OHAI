import openai

class UserInteractionAgent:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        openai.api_key = self.openai_api_key

    def get_user_input(self):
        # Prompt the user for input
        return input("Could you please describe the product you're looking for, including any specific preferences or requirements? ")

    def analyze_input(self, user_input):
        try:
            # Using OpenAI's GPT model to analyze the user input
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Analyze this user input for detail level: '{user_input}'\n",
                max_tokens=50
            )
            analysis = response.choices[0].text.strip()

            # Determine if the response is detailed or vague
            if 'detailed' in analysis.lower():
                return 'detailed'
            else:
                return 'vague'
        except Exception as e:
            print(f"An error occurred: {e}")
            return 'error'

    def prompt_user(self):
        user_input = self.get_user_input()
        analysis_result = self.analyze_input(user_input)
        return analysis_result
