#!/usr/bin/env python
# ↑ Shebang: allows Unix-like systems to run this file directly with `./05_async_many.py`.
#   Harmless on Windows.

# ── Imports ─────────────────────────────────────────────────────────────────
import asyncio  # Event loop & async/await primitives.
import sys  # For modifying Python's import search path.
import os  # Filesystem helpers (dirname, abspath, etc.).
import httpx  # Async HTTP client for making concurrent API calls.

# Add project root to Python’s import path so `lib.utils` can be imported.
# Steps:
#   1) __file__ → path of THIS script
#   2) abspath(__file__) → full absolute path
#   3) dirname(...) → containing folder
#   4) dirname(...) again → parent folder (project root)
#   5) sys.path.append(...) → tell Python to also search here for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Helper functions from your repo:
#   • ws_minify(text): trims whitespace/newlines (efficient prompt).
#   • get_random_ollama_model(): returns a random local Ollama model name.
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")

# ── API endpoint & model list ───────────────────────────────────────────────
url = "http://localhost:11434/api/generate"

# Choose multiple random models — here we’ll run 3 requests in parallel.
models = [get_random_ollama_model() for _ in range(3)]


# ── Task: one request per model ─────────────────────────────────────────────
# Each task will send a POST request for a single model and print the reply.
async def one(client, model):
    # Send request to Ollama and wait for the full response.
    response = await client.post(
        url,
        json={
            "model": model,
            "prompt": user_prompt,
            "stream": False,  # wait for complete output, no streaming
        },
    )

    # Print which model responded + its generated text.
    print(f"\n=== {model} ===")
    print(response.json()["response"].strip())
    print("\n\n")  # spacing between outputs


# ── Main program: launch all tasks concurrently ─────────────────────────────
async def main():
    # Create one shared AsyncClient (connection pooling = more efficient).
    async with httpx.AsyncClient(timeout=None) as client:
        # asyncio.gather(...) runs multiple coroutines in parallel.
        # The starred expression *(...) expands into one task per model.
        await asyncio.gather(*(one(client, model) for model in models))


# ── Run the async event loop ────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
