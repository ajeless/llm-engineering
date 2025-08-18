#!/usr/bin/env python

import sys
import os
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import ws_minify, get_random_ollama_model


user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")

url = "http://localhost:11434/v1"
api_key = "ollama"
model = get_random_ollama_model()
messages = [{"role": "user", "content": user_prompt}]

client = OpenAI(base_url=url, api_key=api_key)

response = client.chat.completions.create(model=model, messages=messages)
print(response.choices[0].message.content)
print("\n\n")
