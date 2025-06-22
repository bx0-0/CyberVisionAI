import random
import time
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

if stopwords.words('english'):
    print("Stopwords already downloaded.")
else:
    nltk.download('punkt_tab')
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)


stop_words = set(stopwords.words('english'))

def clean_text(text):
    """Clean the extracted text by removing stopwords and non-alphanumeric words."""
    word_tokens = word_tokenize(text.lower())
    filtered_text = [word for word in word_tokens if word.isalnum() and word not in stop_words]
    return " ".join(filtered_text)

def is_valid_text(text, min_word_count=5):
    """Check if the cleaned text meets the minimum word count requirement."""
    return len(word_tokenize(text)) >= min_word_count 


def extract_text(urls, max_paragraphs=10):
    """Extract text from the given URLs, handling 403 errors gracefully."""
    texts = []
    headers_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36',
        
    ]
    success = 0
    for url in urls:
        retries = 3  
        for attempt in range(retries):
            try:
                
                headers = {'User-Agent': random.choice(headers_list)}
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    success += 1
                    soup = BeautifulSoup(response.content, 'html.parser')
                    paragraphs = soup.find_all('p')[3:]
                    extracted_text = "  ".join([para.get_text() for para in paragraphs[:max_paragraphs]])
                    cleaned_text = clean_text(extracted_text)

                    if is_valid_text(cleaned_text):
                        texts.append(f"Source: {url}, (Content: {cleaned_text})")
                    break  
                elif response.status_code == 403:
                    print(f"Access denied for {url} (403). Moving on.")
                    break  
                else:
                    print(f"HTTP error {response.status_code} for {url}. Moving on.")
                    break  
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed for {url}: {e}")
                if attempt < retries - 1:  
                    wait_time = random.uniform(1, 3)  
                    print(f"Retrying {url} in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"All attempts failed for {url}. Moving on.")

        
        time.sleep(random.uniform(1, 3))  
    if success ==0:
        texts = ["no results found"]
    elif success == 6:
        texts = texts[:4] 
       
    return texts

