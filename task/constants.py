import os

DEFAULT_SYSTEM_PROMPT = "You are an assistant who answers concisely and informatively."
DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_KEY = os.getenv('DIAL_API_KEY', '')
MODEL_ID = 'gpt-5-mini-2025-08-07'
STREAM_RESPONSE = True

## Working out how to do sync call initially - work back through error in terminal below and go fromthere.