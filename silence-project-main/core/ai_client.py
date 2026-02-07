import os
import json
import requests

# 1. Setup variables
AI_API_URL = os.getenv("AI_API_URL", "https://openrouter.ai/api/v1/chat/completions")
AI_API_KEY = os.getenv("AI_API_KEY", "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")
AI_MODEL = os.getenv("AI_MODEL", "google/gemini-2.0-flash-001")

def generate_insights(prompt: str) -> str:
    if not AI_API_URL or not AI_API_KEY:
        return "AI insights are not configured."

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
        # OpenRouter likes these optional headers to identify your app
        "HTTP-Referer": "http://localhost:3000", 
        "X-Title": "Local Test App"
    }

    # 2. Fix the payload structure
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        # 3. Fix: Use AI_API_URL here, not the key!
        resp = requests.post(AI_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        
        data = resp.json()

        # 4. Fix the parsing logic for OpenRouter
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        
        return f"Response error: {json.dumps(data)}"

    except Exception as e:
        return f"Request failed: {str(e)}"
