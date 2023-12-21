#inport dependencies


#performs a search using the ohel database
def ohel_database_search(query):
  code

ohel_database_function={
    "name": "ohel_search",
    "description": "The first tool used when searching about an item or vendor.",
    "parameters" : {
      "type": "object",
      "properties" : {
        "query" : {
            "type:" : "string",
            "description": "The search query to use. For example: 'What are good specs for a $400 laptop"#fix me: write right description 
        }
      },
      "required": ["query"]
    }
}