import ollama
import re

def get_assistant_response(bug_info,report_stricture, model="X"):

    sys = "Before providing an answer, analyze the task deeply, ensure you understand each part using the <thinking> format. Develop a structured approach for your response, detailing each step involved. It’s crucial to validate that every step of your solution is accurate and correctly applied using <thinking> framework. Only after thorough verification and accurate application of your steps should you present your final answer."
    q = f"Create a detailed pentesting report based on the following information: {bug_info},Do not modify any of the provided information; include it exactly as it is in the report, the report must following this structure: {report_stricture}"
    question = f"system message: {sys}, user task is: {q}"
    ans = ""
    print(model)
    if model == "X-mini":
        print('enter x-mini')
        q = report_stricture


        
    message = [{'role': 'user','content': question}]

    stream = ollama.chat(model='X-mini', messages=message, stream=True )
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
        ans += chunk['message']['content']
        

    return clean_report_content(ans)



def clean_report_content(response):
    """
    Cleans the report content by extracting the content between <output> and </output> tags,
    removing introductory sentences and unnecessary sections like "Related concepts".

    Args:
    - response (str): The original response string from the model.

    Returns:
    - str: The cleaned report content with only the necessary sections.
    """
    # Extract content between <output> and </output> tags
    match = re.search(r'<output>(.*?)</output>', response, re.DOTALL)
    
    if match:
        # Get the content inside <output> tags
        content = match.group(1).strip()
        
        # Remove introductory sentences using a general pattern
        content = re.sub(r'^(Here.*?:|This is.*?:|Below is.*?:|.*?report for.*?:)', '', content, flags=re.IGNORECASE).strip()
        
        # Remove any sections starting with "Related concepts"
        content = re.sub(r'Related concepts.*', '', content, flags=re.DOTALL).strip()
        
        return content

    # If no <output> tags are found, return the original response
    return response.strip()
