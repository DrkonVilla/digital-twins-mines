import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print('No API key found in environment variables')
    exit(1)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content('Say "Hello World!"')
    print('SUCCESS:', response.text)
except Exception as e:
    print('ERROR:', str(e))
