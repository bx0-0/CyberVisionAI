from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found. Please set it in a .env file.")
