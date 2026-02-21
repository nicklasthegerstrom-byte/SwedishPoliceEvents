from dotenv import load_dotenv
import os
import requests

load_dotenv()  # läser .env i denna mapp

url = os.getenv("SLACK_WEBHOOK")
assert url, "Hittar inte SLACK_WEBHOOK i .env"

requests.post(url, json={"text": "🚓 Test från Polishändelser"}, timeout=10)
print("Skickat.")