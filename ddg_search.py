from duckduckgo_search import DDGS

#performs a search using DuckDuckGo
def duckduckgo_search(query):
  with DDGS() as ddgs:
    #retrieve a maximum of five results for the given query. NOTE: decreasing could save costs but damage results
    results = [r for r in ddgs.text(query, max_results=5)]
    return "\n".join(result["body"] for result in results)

ddg_function={
    "name": "duckduckgo_search",
    "description": "Searches for characteristics of an item when provided ambiguous language.",
    "parameters" : {
      "type": "object",
      "properties" : {
        "query" : {
            "type:" : "string",
            "description": "The search query to use. For example: 'What are good specs for a $400 laptop"
        }
      },
      "required": ["query"]
    }
}