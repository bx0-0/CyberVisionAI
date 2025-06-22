import json
from channels.generic.websocket import AsyncWebsocketConsumer
from ollama import AsyncClient
import json_repair

sys="Dont answer the question directly and instead Before answering, analyze the task thoroughly using <thinking>. Outline each step in a structured approach, and verify each step's accuracy and application. Present your answer only after this careful process. Use Markdown formatting (headers, lists, code blocks) where appropriate to ensure clarity."

async def AgentTOImproveSearchQuery(query):
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
  -dont change any word in the query.
  -Gave the query in json format as shown below.
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
  async for part in await AsyncClient().chat(model='x', messages=messages, stream=True):

        yield part['message']['content']
async def AgentToSummarizeText(text, query):
  q = f"""
  You are a AI Agent. Your task is to analyze the text provided and summarize the key points and insights based on the user's query.
  ### role:
  - Analyze the text content.
  - Identify key points and insights.
  - Summarize the text in a concise manner.
  - Use Markdown formatting (headers, lists, code blocks) to structure your response.
  - Ensure the summary captures the main points and insights from the text.
  - Provide a well-structured summary that is easy to understand.
  ### Here is the text content:
  {text}
  ### Here is the user's query:
  {query}
  """
  messages = [{'role': 'user', 'content': f"system message: {sys}, user task is {q}"}]
  async for part in await AsyncClient().chat(model='x', messages=messages, stream=True):
    yield part['message']['content']


async def AgentTOGetFullReportFormSearchResults(query,search_results,resources):
  q = f"""
  You are a AI Agent. Your task is to analyze the search results and provide a detailed report to the user.
  role:
  - Analyze the search results provided and extract relevant information.
  - Summarize the key points and insights from the search results.
  - Provide a detailed report that answers the user's question comprehensively.
  - Use Markdown formatting (headers, lists, code blocks) to structure your response.
  - Include references and links to the search results where applicable.
  - Mention relevant links from the search results in your response, where applicable, to support your response.
  - Avoid copying text directly from the search results; instead, rephrase and integrate the information naturally.
  - Ensure the response is well-structured and easy to understand for the user.
  ### Here are the search results:
  {"\n".join(search_results)}
  ### Here are the resources:
  {"\n".join(resources)}
  ### Here is the user's question:
  {query}
  """
  messages = [{'role': 'user', 'content': f"system message: {sys}, user task is {q}"}]
  async for part in await AsyncClient().chat(model='x', messages=messages, stream=True):
    yield part['message']['content']

async def AgentTOGetFullReportFormSearchResults(query,search_results,resources):
  q = f"""
  You are a AI Agent. Your task is to analyze the search results and provide a detailed report to the user.
  role:
  - Analyze the search results provided and extract relevant information.
  - Summarize the key points and insights from the search results.
  - Provide a detailed report that answers the user's question comprehensively.
  - Use Markdown formatting (headers, lists, code blocks) to structure your response.
  - Include references and links to the search results where applicable.
  - Mention relevant links from the search results in your response, where applicable, to support your response.
  - Avoid copying text directly from the search results; instead, rephrase and integrate the information naturally.
  - Ensure the response is well-structured and easy to understand for the user.
  ### Here are the search results:
  {"\n".join(search_results)}
  ### Here are the resources:
  {"\n".join(resources)}
  ### Here is the user's question:
  {query}
  """
  messages = [{'role': 'user', 'content': f"system message: {sys}, user task is {q}"}]
  async for part in await AsyncClient().chat(model='x', messages=messages, stream=True):
    yield part['message']['content']



class SearchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        # Handle disconnection if needed
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        query = data.get("query")

        if not query:
            await self.send(text_data=json.dumps({"error": "Query is required"}))
            return
        improved_query = ""
        async for part in AgentTOImproveSearchQuery(query):
            improved_query += part
            await self.send(text_data=json.dumps({"message": part,"agent": "Improved Query"}))

        improved_query = json_repair.loads(improved_query)
        if len(improved_query) ==1:
            improved_query = improved_query['improved_query']
        else:
            improved_query = improved_query[0]['improved_query']

        await self.send(text_data=json.dumps({"message": improved_query,"agent": "improved_query"}))





