#! /usr/bin/env python
import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import ws_minify, get_random_ollama_model


user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")

url = "http://localhost:11434/api/generate"
model = get_random_ollama_model()

response = requests.post(
    url, json={"model": model, "prompt": user_prompt, "stream": False}
)

print(response.json()["response"].strip())
print("\n\n")
