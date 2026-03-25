import os
import requests
import sys

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("NO API KEY")
    sys.exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("MODELS THAT SUPPORT GENERATE_CONTENT:")
    for model in data.get("models", []):
        if "generateContent" in model.get("supportedGenerationMethods", []):
            print(model.get("name"))
else:
    print(f"FAILED: {response.status_code}")
    print(response.text)
