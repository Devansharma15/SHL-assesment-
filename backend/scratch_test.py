import httpx
import json

payload = {
    "messages": [
        {"role": "user", "content": "I need an assessment for a Python developer"}
    ]
}

try:
    response = httpx.post("http://localhost:8000/chat", json=payload, timeout=60.0)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
