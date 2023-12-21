import sys
import os
from dotenv import load_dotenv

load_dotenv()  # This loads the .env file

openai_api_key = os.getenv('OPENAI_API_KEY')
faunadb_key = os.getenv('FAUNADB_KEY')


# Importing individual agents (to be implemented in separate files)
from user_interaction_agent import UserInteractionAgent
from suggestion_agent import SuggestionAgent
from query_analysis_agent import QueryAnalysisAgent
from database_query_agent import DatabaseQueryAgent
from web_search_agent import WebSearchAgent
from recommendation_agent import RecommendationAgent
from reflection_monitoring_agent import ReflectionMonitoringAgent

class Chatbot:
    def __init__(self):
        self.user_interaction_agent = UserInteractionAgent(openai_api_key)
        self.suggestion_agent = SuggestionAgent()
        self.query_analysis_agent = QueryAnalysisAgent()
        self.database_query_agent = DatabaseQueryAgent()
        self.web_search_agent = WebSearchAgent()
        self.recommendation_agent = RecommendationAgent()
        self.reflection_monitoring_agent = ReflectionMonitoringAgent()

    def start_chat(self):
        # Initial user interaction
        user_query = self.user_interaction_agent.get_input()

        # Processing the query and determining the next step
        if self.user_interaction_agent.is_detailed_query(user_query):
            query_analysis = self.query_analysis_agent.analyze_query(user_query)
            product_options = self.database_query_agent.query_database(query_analysis)
        else:
            suggestion = self.suggestion_agent.get_suggestions()
            query_analysis = self.query_analysis_agent.analyze_query(suggestion)
            product_options = self.database_query_agent.query_database(query_analysis)

        # Checking database results and deciding next action
        if not product_options:
            web_search_results = self.web_search_agent.perform_web_search(query_analysis)
            product_options = web_search_results

        # Generating recommendations
        recommendations = self.recommendation_agent.generate_recommendations(product_options)

        # Handling reflection and monitoring
        self.reflection_monitoring_agent.monitor_agents()

        return recommendations

if __name__ == "__main__":
    chatbot = Chatbot()
    results = chatbot.start_chat()
    print("Product Recommendations:", results)
