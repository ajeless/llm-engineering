#!/usr/bin/env python
# ↑ Shebang: lets Unix-like systems run this file directly with `./04_async_one.py`.
#   Harmless on Windows (ignored there).

# ── Imports ─────────────────────────────────────────────────────────────────
import asyncio  # Built-in: event loop, async/await primitives.
import sys  # Lets us tweak Python's import search path at runtime.
import os  # Filesystem helpers (dirname, abspath, etc.).
import httpx  # Async-capable HTTP client (like requests, but with async support).

# Make sure we can import from your project (e.g., lib/utils.py) when running directly.
# Steps:
#   1) __file__ → this script's path
#   2) abspath(__file__) → absolute path (no "..")
#   3) dirname(...) → folder containing this file
#   4) dirname(...) again → go up one directory (project root)
#   5) sys.path.append(...) → tell Python to ALSO search there for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Your helpers:
#   • ws_minify(text): collapses whitespace/newlines (cheaper prompts).
#   • get_random_ollama_model(): returns a local Ollama model name (string).
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Multiline for readability in code; ws_minify() compacts it for the API.
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")

# ── API endpoint & model ────────────────────────────────────────────────────
# Ollama's REST endpoint for one-shot generation.
url = "http://localhost:11434/api/generate"

# Pick a local model (e.g., "llama3", "mistral", "qwen2.5"); replace with a fixed
# string if you want consistent behavior while testing.
model = get_random_ollama_model()


# ── Async program entrypoint ────────────────────────────────────────────────
# Why async here if we're only doing ONE request?
#   • This sets the stage for later steps where we do MANY requests concurrently.
#   • You'll learn the pattern once and reuse it for advanced scripts.
async def main():
    # Create ONE async HTTP client for this script.
    # timeout=None: no per-request deadline (useful for slow local inference).
    # "async with": guarantees the client is closed properly afterwards.
    async with httpx.AsyncClient(timeout=None) as client:
        # Send a POST request to Ollama; await its completion.
        # stream=False → wait for the full response (no partial chunks).
        response = await client.post(
            url,
            json={
                "model": model,
                "prompt": user_prompt,
                "stream": False,
            },
        )

        # Convert JSON body → Python dict and extract the generated text.
        print(response.json()["response"].strip())
        print("\n\n")  # extra spacing in terminal output


# ── Launch the event loop ───────────────────────────────────────────────────
# asyncio.run(...) sets up an event loop, runs main() to completion, and cleans up.
if __name__ == "__main__":
    asyncio.run(main())
