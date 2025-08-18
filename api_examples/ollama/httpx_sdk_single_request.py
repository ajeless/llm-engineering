#! /usr/bin/env python
# ↑ Shebang line: lets you run this script directly on Unix-like systems with `./script.py`.
#   On Windows this line is ignored, so it’s safe to leave in.

# ── Imports ────────────────────────────────────────────────────────────────
import asyncio  # Python’s built-in library for writing async (non-blocking) code.
import sys  # Lets us manipulate Python’s runtime environment (like sys.path).
import os  # Functions for working with filesystem paths.
import httpx  # Third-party HTTP client library that supports async requests.

# Add the parent directory of this file to Python’s import search path.
# This lets us import your own helper functions when running the script directly.
# Step by step:
#   1. __file__ → this script’s path
#   2. abspath(__file__) → full absolute path to this script
#   3. dirname(...) → the directory containing this script
#   4. dirname(...) again → the parent directory
#   5. sys.path.append(...) → tell Python "also search here when importing"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import helper utilities you wrote elsewhere:
#   • ws_minify(text): compresses whitespace/newlines so prompts are shorter.
#   • get_random_ollama_model(): returns the name of a random Ollama model.
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Triple-quoted string → easy to write multi-line prompts.
# ws_minify(...) → cleans it up to a single neat line (fewer tokens for the LLM).
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")


# ── API endpoint & model selection ──────────────────────────────────────────
# Default Ollama REST API endpoint for text generation.
url = "http://localhost:11434/api/generate"

# Pick one random model installed locally (e.g., "llama3", "mistral", etc.).
model = get_random_ollama_model()


# ── Define the async main program ───────────────────────────────────────────
# Async functions (declared with `async def`) let Python *pause* at "await" points,
# so while one request is waiting on the network, other tasks could run.
async def main():
    # Create a single AsyncClient session for making HTTP requests.
    #   • timeout=None → no time limit; useful for slow local models.
    #   • "async with" ensures the client is closed cleanly afterwards.
    async with httpx.AsyncClient(timeout=None) as client:
        # Send a POST request to Ollama’s /api/generate endpoint.
        # Arguments:
        #   – url: endpoint string
        #   – json={...}: Python dict → auto-encoded to JSON body
        #       • "model": which Ollama model to run
        #       • "prompt": our user input
        #       • "stream": False → wait for the entire response before returning
        response = await client.post(
            url, json={"model": model, "prompt": user_prompt, "stream": False}
        )

        # Parse the HTTP response body as JSON into a Python dict.
        # Example Ollama reply: {"response":"Hello!", "done":true, ...}
        # Extract the "response" field (the generated text).
        print(response.json()["response"])

        # Print a couple of newlines for cleaner terminal formatting.
        print("\n\n")


# ── Run the async program ───────────────────────────────────────────────────
# asyncio.run(...) creates an event loop, runs main(), and then shuts down.
# This is the standard way to launch async code in a normal Python script.
asyncio.run(main())
