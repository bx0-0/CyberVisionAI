import re
import ollama
from  utils import extract_urls
import json_repair
from spiders import extract_text
from duckduckgo_search import DDGS
from  rich.console import Console
from  rich.markdown import Markdown

conversation_history = []
sys="Dont answer the question directly and instead Before answering, analyze the task thoroughly using <thinking>. Outline each step in a structured approach, and verify each step's accuracy and application. Present your answer only after this careful process. Use Markdown formatting (headers, lists, code blocks) where appropriate to ensure clarity."

def AgentTOImproveSearchQuery(query):
  q = """
  You are a AI Agent. Your task is to extract the key points from the user's query and gave a more specific and relevant search query your search  query will  use directly to  search in  the web so that you can get more accurate results.
  ### role:
  - Analyze the query components.
  - Identify key elements and intent.
  - Refine the query to be more specific and relevant.
  -Gave only one query that can be used directly to search in the web, to make a detailed report that  contains more accurate results.
  -do not change the meaning of the user's query in any way the query will  use to  generate a detail report .
  -dont gave a report your role is just gave an improved query in json format.
  -do not change the user's query in any way or change any  word in the query.
  -The search results will be used to generate a detailed report that answers the user's question comprehensively.
  -extract the main  key  point from  the user query and use them  to generate a more accurate search query dont add any other words.
  -dont change any word in the query ,  the user will  gave you word in  correct  spell.
  -Gave the query in json format as shown below.
  -if the search  contains programming code dont add this code just refer the link  or give the link of the programming code.
  ### json structure:
  ```json
  {
    "improved_query": "",
  }
  ### dont forget to include the improved query in the json format.
  ### dont change any word in the query just extract the main  key  point from  the user query and use them  to generate a more accurate search query dont add any other words.
  ```
   """+"### Here is the user's query: " + query
  messages = [{'role': 'user', 'content': f"system message: {sys}, user task is {q}"}]
  stream = ollama.chat(model='x', messages=messages, stream=True)
  return stream

def AgentToSummarizeText(text,query):
  q = f"""
  You are a AI Agent. Your task is to analyze the text provided and summarize the key points and insights based on the user's query.
  ### role:
  - Analyze the text content.
  - Identify key points and insights.
  - Summarize the text in a concise manner.
  - Use Markdown formatting (headers, lists, code blocks) to structure your response.
  - Ensure the summary captures the main points and insights from the text.
  - Provide a well-structured summary that is easy to understand.
  - the summary should answer the user's question comprehensively.
  ### Here is the text content:
  {text}
  ### Here is the user's query:
  {query}
  """
  messages = [{'role': 'user', 'content': f"system message: {sys}, user task is {q}"}]
  stream = ollama.chat(model='x', messages=messages, stream=True)
  return stream


def AgentTOGetFullReportFormSearchResults(query,search_results,resources):
  q = f"""
  You are an AI Agent. Your task is to analyze the search results and generate a comprehensive, well-structured, and highly detailed report for the user.

  ## Role:
  - Structure the response using **Markdown formatting** (headers, subheaders, lists, tables, and code blocks where appropriate).
  - Provide **detailed explanations** under relevant subheadings.
  - Include **tables** where applicable to present data clearly.
  - Mention and integrate relevant links from the search results as supporting references.
  - Avoid directly copying text from the search results; instead, rephrase and organize the information effectively.
  - Ensure the final report is **well-structured, easy to read, and highly informative**.
  -dont forget  to  use the markdown formatting in your response.
  -the report should be longer as possible to answer the user's question comprehensively.

  ## Search Results:
  {"\n".join(search_results)}

  ## Additional Resources:
  {"\n".join(resources)}

  ## User's Question:
  {query}

### report structure:
  - **Introduction**: Briefly introduce the topic and the purpose of the report.
  - **Search Results**: Present the search results in a structured format, highlighting key points and relevant information.
  - **Additional Resources**: List any additional resources or references that were found during the search.
  - ** Table of Contents**: Include a table of contents for easy navigation.
  - **User's Question**: Restate the user's question and provide a detailed answer based on the search results.
  - **Conclusion**: Summarize the key findings and provide a final thought or recommendation.
  - **References**: Cite any external sources or references used in the report.
  - **Appendices**: Include any additional information or data that supports the report.
  - **Glossary**: Define any technical terms or jargon used in the report.
  - **Index**: Provide an index for quick reference.
  - **Acknowledgments**: Acknowledge any contributors or sources of information.
  - **Appendices**: Include any additional information or data that supports the report.

  Make sure to follow the structure and guidelines provided above to create a comprehensive and well-organized report and use markdown formatting in your response.
"""

  messages = [{'role': 'user', 'content': f"system message: {sys}, user task is {q}"}]
  stream = ollama.chat(model='x', messages=messages,stream=True)
  return stream

def StreamText(stream):
    text_accumulated = ""  
    text_accumulated = ""
    for chunk in stream:
        if 'message' in chunk and 'content' in chunk['message']:
            text = chunk['message']['content']
            print(text, end="", flush=True)  
            text_accumulated += text  

    return text_accumulated    
    

if __name__ == "__main__":
  full_response = ""
  num_results=20
  query = input("Enter your query: ")
  print("Improving the search query...\n")
  stream = AgentTOImproveSearchQuery(query)
  improved_query = StreamText(stream)
  full_response += improved_query
  query = json_repair.loads(improved_query)
  if type(query) == dict:
    query1 = query['improved_query']
  else:
    query1 = query[0]['improved_query']
  print("\n\n")
  print("Improved Search Query: ", query1)
  print("\n\n")
  print("Start searching for relevant resources...\n")
  start_search = results = DDGS().text(query1, max_results=3)
  search_resources,t = extract_urls(query1, num_results)
  summary = []
  for i  in  range(num_results//6):
    full_summary  = ""
    search_content = search_resources[i*6:(i+1)*6]
    print("Summarizing search results...\n")
    search_content  = extract_text(search_content)
    search_content =  "\n\n".join([result['body'] + result['title'] for result in start_search]) + "\n\n" + "\n\n".join(search_content)
    stream = AgentToSummarizeText(search_content, query)
    res = StreamText(stream)
    full_summary += res
  
  
    # extract  text from  <output> and </output>
    match = re.search(r'<output>(.*?)</output>', full_summary, re.DOTALL)
    if match:
      summary.append(match.group(1))
    else:
      summary.append(full_summary)
    print("\n\n")
  report = AgentTOGetFullReportFormSearchResults(query,summary,search_resources)
  report = StreamText(report)
  match = re.search(r'<output>(.*?)</output>', report, re.DOTALL)
  if match:
     print('report:\n\n')
     # print markdown  report in terminal
     console  = Console()
     console.print(Markdown(match.group(1)))







        