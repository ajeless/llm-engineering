#!/usr/bin/env python
# ↑ Shebang: lets Unix-like systems run this file directly with `./01_sync_requests.py`.
#   Windows ignores this line, so it’s harmless there.

# ── Imports ─────────────────────────────────────────────────────────────────
import sys  # Lets us interact with the Python runtime (e.g., adjust import paths).
import os  # Handy tools for filesystem paths (dirname, abspath, etc.).
import requests  # Popular HTTP library for making web requests (simple and synchronous).

# Add this project’s parent directory to Python’s module search path.
# Why? So that `from lib.utils import ...` works when running this file directly.
# Steps:
#   1) __file__ → path of this script.
#   2) abspath(__file__) → absolute path (no “..” pieces).
#   3) dirname(...) → folder containing this file.
#   4) dirname(...) again → go UP one directory (the project root, typically).
#   5) sys.path.append(...) → tell Python to ALSO look there when importing modules.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Bring in your helper functions (already in your repo):
# - ws_minify(text): collapses whitespace/newlines so prompts are compact.
# - get_random_ollama_model(): returns the name of a local Ollama model (string).
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Triple-quoted strings allow neat multi-line text in code.
# We immediately pass it through ws_minify to remove extra whitespace.
# Rationale: LLMs tokenize whitespace too; smaller prompts = fewer tokens.
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")


# ── API endpoint & model ────────────────────────────────────────────────────
# Default local Ollama HTTP endpoint for "one-shot" text generation.
# If Ollama is running on a different host/port, change this accordingly.
url = "http://localhost:11434/api/generate"

# Choose a random local model (examples: "llama3", "qwen2.5", "mistral", etc.).
# If you prefer a fixed model, replace this with a hard-coded string.
model = get_random_ollama_model()


# ── Make the request (synchronous / blocking) ───────────────────────────────
# requests.post(...) sends a single HTTP POST and waits for the ENTIRE response.
# Arguments:
#   - url: the API endpoint (string)
#   - json={...}: Python dict that requests will encode to JSON as the body
#     • "model": which Ollama model to run
#     • "prompt": your user text
#     • "stream": False → we do NOT stream partial output; we wait for completion
response = requests.post(
    url,
    json={
        "model": model,
        "prompt": user_prompt,
        "stream": False,
    },
)

# ── Use the response ────────────────────────────────────────────────────────
# The server replies with JSON. Convert it into a Python dict with .json().
# Typical shape: {"model":"...", "response":"...text...", "done":true, ...}
# We print only the generated text under "response".
print(response.json()["response"].strip())

# Extra blank lines for readability in terminal output.
print("\n\n")
