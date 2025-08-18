#! /usr/bin/env python
import asyncio
import sys
import os
import httpx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import ws_minify, get_random_ollama_model


user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")

url = "http://localhost:11434/api/generate"
models = [get_random_ollama_model() for _ in range(2)]


async def one(client, model):
    response = await client.post(
        url, json={"model": model, "prompt": user_prompt, "stream": False}
    )
    print(model, "→", response.json()["response"])
    print("\n\n")


async def main():
    async with httpx.AsyncClient(timeout=None) as client:
        await asyncio.gather(*(one(client, model) for model in models))


asyncio.run(main())
