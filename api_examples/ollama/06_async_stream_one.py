#!/usr/bin/env python
# ↑ Shebang: lets Unix-like systems run this file directly with `./06_async_stream_one.py`.
#   Harmless on Windows (ignored there).

# ── Imports ─────────────────────────────────────────────────────────────────
import asyncio  # Event loop + async/await primitives.
import sys  # Let us tweak Python's module search path at runtime.
import os  # Filesystem path helpers (dirname, abspath, etc.).
import json  # Decode JSON strings into Python dicts.
import httpx  # Async HTTP client that supports streaming responses.

# Add project root to Python's import path so we can `from lib.utils import ...`
# Steps:
#   1) __file__ → path to THIS script
#   2) abspath(__file__) → absolute path (no "..")
#   3) dirname(...) → folder containing this script
#   4) dirname(...) again → parent folder (project root)
#   5) sys.path.append(...) → tell Python to ALSO search here for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Your helpers:
#   • ws_minify(text): collapse whitespace/newlines for a compact prompt.
#   • get_random_ollama_model(): pick a local Ollama model name (string).
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Multiline for readability; ws_minify() compacts it (fewer tokens for the LLM).
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")

# ── API endpoint & model ────────────────────────────────────────────────────
# Ollama streaming endpoint is the same as generation: /api/generate
# (The difference is we set "stream": true in the request body.)
url = "http://localhost:11434/api/generate"

# Choose a local model (e.g., "llama3", "mistral", "qwen2.5", depending on what's pulled).
model = get_random_ollama_model()


# ── Async program (one streaming request) ───────────────────────────────────
# This sends ONE request with stream=True and prints chunks as soon as they arrive.
async def main():
    # Create an async HTTP client. We'll allow slow models by disabling read timeout.
    timeout = httpx.Timeout(connect=10.0, read=None, write=60.0, pool=15.0)

    # Use a single client; "async with" guarantees proper cleanup afterwards.
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Start a streaming POST. Ollama returns **NDJSON** (one JSON object per line).
        # Example lines:
        #   {"response":"Hello", "done":false, ...}
        #   {"response":" world!", "done":false, ...}
        #   {"done":true, ...}
        async with client.stream(
            "POST",
            url,
            json={"model": model, "prompt": user_prompt, "stream": True},
        ) as response:
            # Optional: a header so you know which model is talking.
            print(f"\n=== {model} (streaming) ===\n", flush=True)

            # Iterate over lines as they arrive (non-blocking).
            async for line in response.aiter_lines():
                # Some servers send keep-alive empty lines; skip those.
                if not line:
                    continue

                # Convert the JSON text into a Python dict so we can read fields.
                data = json.loads(line)

                # If the line includes a "response" chunk, print it without a newline.
                # end="" glues chunks together; flush=True makes it appear immediately.
                if "response" in data:
                    print(data["response"], end="", flush=True)

                # When Ollama signals completion with {"done": true}, add a blank line
                # to keep the terminal tidy and then break.
                if data.get("done"):
                    print("\n\n", flush=True)
                    break


# ── Launch the event loop ───────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
