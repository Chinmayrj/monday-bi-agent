import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

MONDAY_API_URL = "https://api.monday.com/v2"
MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")

if not MONDAY_API_TOKEN:
    raise ValueError("MONDAY_API_TOKEN not found. Check your .env file.")

headers = {
    "Authorization": MONDAY_API_TOKEN,
    "Content-Type": "application/json"
}

query = """
query {
  boards {
    id
    name
  }
}
"""

response = requests.post(
    MONDAY_API_URL,
    headers=headers,
    json={"query": query}
)

print(json.dumps(response.json(), indent=2))