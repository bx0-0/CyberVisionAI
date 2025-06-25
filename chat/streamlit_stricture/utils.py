from datetime import datetime
import os
import random
from io import StringIO
import time
import PyPDF2
import docx
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from duckduckgo_search import DDGS
from spiders import extract_text
import datetime  
import requests
import streamlit as st
from auth import generate_temporary_token_and_timestamp
import html
from nltk.tokenize import sent_tokenize
import whisper
import tempfile

@st.cache_resource
def get_formatted_date():
    return datetime.now().strftime("%B %d, %Y")

@st.cache_resource
def get_random_icon():
    icons = ['smart_toy:', 'precision_manufacturing:', 'robot_2:', 'robot:']
    return random.choice(icons)

@st.cache_resource
def process_file(uploaded_file, pages_per_summary=3, min_text_length=100, min_pages=0):
    """
    Process uploaded file and return its cleaned content if small, or summarize if large.
    """
    if uploaded_file:
        validation_message = validate_file(uploaded_file)
        if validation_message != "File is valid.":
            return validation_message  

    file_type = uploaded_file.name.split('.')[-1].lower()
    all_summaries = []

    if file_type == 'pdf':
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        total_pages = len(pdf_reader.pages)
        
        if total_pages < min_pages:
            cleaned_text = "\n".join([pdf_reader.pages[page_num].extract_text() for page_num in range(total_pages)])
            return "The file is too small to summarize. Returning the cleaned content:\n" + clean_text(cleaned_text)

        for start_page in range(0, total_pages, pages_per_summary):
            page_text = ""
            for page_num in range(start_page, min(start_page + pages_per_summary, total_pages)):
                page = pdf_reader.pages[page_num]
                page_text += page.extract_text() + " "  
            
            if len(page_text.strip()) < min_text_length:
                all_summaries.append(clean_text(page_text.strip()))
            else:
                summary = extract_important_sentences(page_text, num_sentences=1)
                summary += "\n"
                all_summaries.append(summary)

        return '\n'.join(all_summaries)

    elif file_type == 'txt':
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        string_data = stringio.read()
        
        if len(string_data.strip()) < min_text_length:
            return "The file is too small to summarize. Returning the cleaned content:\n" + clean_text(string_data.strip())
        
        return extract_important_sentences(string_data)

    elif file_type == 'docx':
        doc = docx.Document(uploaded_file)
        all_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        
        if len(all_text.strip()) < min_text_length:
            return "The file is too small to summarize. Returning the cleaned content:\n" + clean_text(all_text.strip())
        
        return extract_important_sentences(all_text)

    else:
        return "Unsupported file type."

def clean_text(text):
    """
    Cleans the input text by removing unnecessary whitespace and symbols.

    Args:
        text (str): Text to clean.

    Returns:
        str: Cleaned text.
    """
    text = re.sub(r'[^\w\s\.\?\!]', '', text)  
    text = re.sub(r'\s+', ' ', text).strip()   
    return text

def validate_file(uploaded_file, max_size_mb=3):
    file_size_mb = uploaded_file.size / (1024 * 1024)  
    if file_size_mb > max_size_mb:
        return f"Error: File size exceeds the maximum limit of {max_size_mb} MB. Current size: {file_size_mb:.2f} MB."

    return "File is valid."

def extract_important_sentences(text: str, num_sentences=6, min_sentence_length=30, max_sentence_length=200):
    """
    Extracts the most important sentences from a given text with control over the summary length.

    Args:
        text (str): Input text to analyze.
        num_sentences (int): Number of important sentences to return.
        min_sentence_length (int): Minimum length of sentences to consider (in characters).
        max_sentence_length (int): Maximum length of sentences to consider (in characters).

    Returns:
        str: Important sentences separated by newline.
    """
    
    text = re.sub(r'[^\w\s\.\?\!]', '', text)  
    text = re.sub(r'\s+', ' ', text).strip()   
    
    
    sentences = sent_tokenize(text)
    
    
    processed_sentences = [
        ' '.join(re.findall(r'\w+', sentence.lower())) 
        for sentence in sentences 
        if min_sentence_length <= len(sentence) <= max_sentence_length
    ]
    
    if not processed_sentences:
        return ""

    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(processed_sentences)
    sentence_scores = tfidf_matrix.sum(axis=1).A1  
    
    
    scored_sentences = [
        (score, i, sentences[i]) 
        for i, score in enumerate(sentence_scores)
    ]
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    
    
    important_sentences = sorted(scored_sentences[:num_sentences], key=lambda x: x[1])
    
    
    return '\n'.join(sentence.strip() for _, _, sentence in important_sentences)



def extract_urls(query, num_results=6):
    """Extract URLs using DuckDuckGo search."""
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=num_results)
        current_datetime = datetime.datetime.now()
        urls = [result['href'] for result in results]
        return urls,current_datetime
    except Exception as e:
        print(e)
        st.warning("Network error occurred. please ask your question agin")

def internet_access(query):
    res = ''
    links,current_datetime = extract_urls(query)
    results = extract_text(links[2:])
    print(results)
   
    print("rest"+ res)
    return results,current_datetime,links

def use_external_ais(prompt):
    prompt += " make sure your answer is short" 
    try:
        gpt_respone =DDGS().chat(prompt, model="gpt-4o-mini")
        time.sleep(4)
    except Exception:  
        gpt_respone = ""
    try:
        claude_response = DDGS().chat(prompt, model="claude-3-haiku")
        time.sleep(4)
    except Exception:  
        claude_response =""
    try:
        llama_respone = DDGS().chat(prompt, model="llama-3.1-70b")
        time.sleep(4)
    except Exception:  
        llama_respone =""

    res = f"gpt-40-mini response: {gpt_respone}\n\n\nclaude-3-haiku response: {claude_response}\n\n\nllama-3.1-70b response: {llama_respone}"
    return res

def extract_mind_map_content(text):
    match = re.search(r'<output>(.*?)</output>', text, re.DOTALL)
    if match:
        return match.group(1).replace("<strong style='color: #888;'>🧠 Answer:...</strong><br>",'\n').replace('Related concepts:','### Related concepts:').strip()

    return None

def send_mindMap_to_dj(text):
    url = "http://127.0.0.1:8000/chat/create_mind_map/"
    token, timestamp, signature = generate_temporary_token_and_timestamp(st.session_state.api_key)
    payload = {
        "api_key": st.session_state.api_key,
        "timestamp": timestamp,
        "signature": signature,
        "text": html.escape(text),  
    }
    with st.spinner("Creating  your Mind Map..."):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  

            file_url = response.json().get('file_url')
            if file_url:
                st.success("Mind map created successfully!")
                st.write(f"Access your mind map [here]({file_url})")
            else:
                st.error("Mind map creation failed. Please try again.")
        
        except requests.exceptions.RequestException:
            st.error("Failed to create mind map. Please try to ask X again.")

@st.cache_resource
def snow_animation():
    st.snow()

def save_conversation():
    url = "http://127.0.0.1:8000/chat/save_chat/"
    messages = st.session_state.messages
    api_kay = st.session_state.api_key
    token, timestamp, signature = generate_temporary_token_and_timestamp(api_kay)

    payload = {
        "api_key": api_kay,
        "timestamp": timestamp,
        "signature": signature,
        "conversation": messages
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  
        st.success("Chat saved successfully!", icon=":material/check:")
        st.session_state.save_success_conversation = True
        st.stop()
    except requests.exceptions.RequestException:
        st.error("Failed to save chat. Please try again.")

    
    print(messages)

def clear_text_after_convert_to_audio(text: str):
    """
    Clear the text after converting to audio.
    remove emotions and other tags.

    """
    
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    
    text = text.replace('*',' ').replace('#',' ')
    

    statments = [', see code in the converstion. ',', you can  see the code is in the converstion. ',', the code is in the chat. ',', see code in the chat. ']

    
    text = re.sub(r'```[^`]*```', lambda match: statments[random.randint(0, 3)], text)

    start_tag = "<output>"
    end_tag = "</output>"
    if '<output>' in text:
        start_index = text.find(start_tag) + len(start_tag)
        end_index = text.find(end_tag)
        text = text[start_index:end_index].strip()
    
    if 'saber' in text.lower():
        text = text.replace('Saber','Saaber').replace('saber','saaber')
        

    return text

def save_audio_to_tempfile(audio_bytes):
    temp_folder = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(temp_folder, exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=temp_folder) as temp_file:
        temp_file.write(audio_bytes)  
        temp_file_path = temp_file.name  

    return temp_file_path

st.cache_data and st.cache_resource()
def extract_text_from_audio(audio_bytes):
    model_size = "base"  

    model = whisper.load_model(model_size)

    temp_file_path = save_audio_to_tempfile(audio_bytes)

    initial_prompt = (
        "This is a chat between a user and an AI model named X. The conversation is focused on technology, cybersecurity, vulnerabilities, exploits, and related topics. Common terms include: AI, machine learning, encryption, firewall, malware, phishing, cloud computing, blockchain, IoT, data privacy, XSS (Cross-Site Scripting), CSRF (Cross-Site Request Forgery), SQLi (SQL Injection), payloads, and other security-related concepts. The AI model should provide accurate, detailed, and helpful information about cybersecurity, vulnerabilities, exploitation techniques, and best practices for securing systems. The AI should also be aware of common attack vectors such as XSS, CSRF, SQLi,python,c,c++, and others, and explain them in a clear and understandable way. The AI should assist the user in understanding how to identify, prevent, and mitigate these vulnerabilities."
    )

    try:
        result = model.transcribe(
            temp_file_path, 
            language="en",  
            initial_prompt=initial_prompt,  
            beam_size=1,  
            temperature=0  
        )
        recognized_text = result["text"]
    except RuntimeError as e:
        print(f"Error processing audio: {e}")
        recognized_text = ""
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return recognized_text.strip()

def get_RAG_content_from_DJ(query):
    url = "http://127.0.0.1:8000/RAGManger/get_RAG_content/"
    data = {
        "query":query,
        "api_key":st.session_state.api_key,
        "number_data_retrav":st.session_state.RAG_result_number
    }
    with st.spinner('Data Retrieving...'):
        try:
            result = requests.post(url=url,json=data)
            result.raise_for_status()
            if result.json().get('status') == 'no_content':
                st.info('You dont upload any  vontent for X.. to trian for it...')
            else:
                return result.json().get('result')
        except Exception as e:
            st.error(e)
            st.error('error ocueear try  agin')
