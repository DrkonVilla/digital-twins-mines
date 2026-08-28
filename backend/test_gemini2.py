import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print('No API key found in environment variables')
    exit(1)

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Say "Hello World!"'
    )
    print('SUCCESS:', response.text)
except Exception as e:
    print('ERROR:', str(e))
