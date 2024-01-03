# tools.py
tools_list = [
    {
        "type": "function",
        "function": {
            "name": "elasticsearch_lookup",
            "description": "Query the ElasticSearch database to retrieve product information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for the product"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "duckduckgo_search",
            "description": "Perform a web search using DuckDuckGo to find product information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for the web"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_fauna_db",
            "description": "Post new information to the FaunaDB",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "The data to be updated in the database"
                    }
                },
                "required": ["data"]
            }
        }
    }
]
