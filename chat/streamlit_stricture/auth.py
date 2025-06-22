import hashlib
import hmac
import time
import requests
import streamlit as st
from config import SECRET_KEY

def create_signature(secret_key, token, timestamp):
    message = f"{token}{timestamp}".encode('utf-8')
    return hmac.new(secret_key.encode(), message, hashlib.sha256).hexdigest()

def validate_token(token, timestamp, signature):
    url = 'http://localhost:8000/chat/send_api/' 
    payload = {
        'token': token,
        'timestamp': timestamp,
        'signature': signature
    }
    try:
        response = requests.post(url, json=payload)
        
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException:
        st.error("token not valid")
        return None

def generate_temporary_token_and_timestamp(token):
    timestamp = int(time.time())
    signature = create_signature(SECRET_KEY, token, str(timestamp))
    return token, timestamp, signature
