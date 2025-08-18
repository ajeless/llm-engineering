#! /usr/bin/env python
# ↑ Shebang: allows Unix-like systems to run this script directly with `./script.py`.
#   On Windows this line is ignored.

# ── Imports ────────────────────────────────────────────────────────────────
import asyncio  # For async programming (run multiple tasks without blocking).
import sys  # Lets us work with Python’s runtime (e.g., modify sys.path).
import os  # File system utilities (e.g., dirname, abspath).
import httpx  # Async-friendly HTTP client (like requests, but with async support).

# Add the parent folder of this script to Python’s import search path.
# Why? So we can import your helper functions from lib/utils.py.
# Step by step:
#   1. __file__ = path of this script
#   2. abspath(__file__) → full path (no "..")
#   3. dirname(...) → directory of this script
#   4. dirname(...) again → parent directory
#   5. sys.path.append(...) → tell Python to also search here for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your helper utilities:
#   • ws_minify: trims spaces/newlines (cleaner prompts, fewer tokens).
#   • get_random_ollama_model: returns the name of a random Ollama model.
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Triple-quoted string = easy to write multiline text.
# ws_minify(...) compresses it into a single neat line for efficiency.
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")


# ── API endpoint & model list ───────────────────────────────────────────────
# Ollama’s REST API endpoint for text generation.
url = "http://localhost:11434/api/generate"

# Create a list of models to query.
# Here: pick 2 random models (could be duplicates if random repeats).
models = [get_random_ollama_model() for _ in range(2)]


# ── One request task ───────────────────────────────────────────────────────
# An async function that sends ONE request for ONE model.
# Arguments:
#   • client: shared AsyncClient session
#   • model: the model name (string)
async def one(client, model):
    # Send a POST request to Ollama’s /api/generate endpoint.
    # stream=False → wait until the full response is ready.
    response = await client.post(
        url, json={"model": model, "prompt": user_prompt, "stream": False}
    )

    # Print the model name and its generated response.
    print(model, "→", response.json()["response"])
    print("\n\n")


# ── Main program: run multiple requests concurrently ────────────────────────
async def main():
    # Create one AsyncClient for all requests (connection pooling = faster).
    async with httpx.AsyncClient(timeout=None) as client:
        # asyncio.gather(...) runs multiple coroutines *at the same time*.
        # Here: run one(client, model) for EACH model in models list.
        # The starred generator expression *(...) expands into separate tasks.
        await asyncio.gather(*(one(client, model) for model in models))


# ── Run the async event loop ────────────────────────────────────────────────
# asyncio.run(...) starts an event loop, runs main() until complete, then exits.
asyncio.run(main())
