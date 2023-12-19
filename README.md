Dependencies
pip install python-dotenv
pip install langchain openai tiktoken cohere arxiv duckduckgo-search langchainhub -qU

if using homebrew environment:
    /opt/homebrew/bin/python3 -m pip install openai
    /opt/homebrew/bin/python3 -m pip install duckduckgo_search



to give llm new tool..
1.create new tool function
2.create new tool dictionary (this is what the llm understand. the llm doesn't have acces to the actual funciton)
See example in ddg_search.py
3.add tool to assistant
4.add if statement to "submit_tool_outputs" function 
5.
