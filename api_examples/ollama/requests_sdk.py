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


#! /usr/bin/env python
# ↑ Shebang line: allows Unix-like systems to run this script directly
#   (e.g. `./script.py`) using whichever Python interpreter is first on PATH.
#   On Windows this line is ignored, so it’s harmless there.

# ── Imports ────────────────────────────────────────────────────────────────
import sys  # Lets us work with the Python runtime itself (argv, path, etc.).
import os  # Tools for filesystem paths (dirname, abspath, etc.).
import requests  # Third-party library for making HTTP requests (simpler than httpx).

# Add parent directory of this script to Python’s import search path.
# Why? So we can import `lib.utils` even when running this file directly.
# Step by step:
#   • __file__ → path to THIS script file
#   • os.path.abspath(__file__) → absolute path (resolves ".." pieces)
#   • os.path.dirname(...) → the folder containing this file
#   • wrapping dirname(...) again → go one level UP (the parent folder)
#   • sys.path.append(...) → tell Python "also look here for imports"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import two helper functions from YOUR own utils module:
#   • ws_minify(text): collapses whitespace/newlines (keeps prompts compact).
#   • get_random_ollama_model(): returns a random Ollama model name (string).
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Triple-quoted string: allows clean multi-line text.
# We immediately pass it to ws_minify → removes extra line breaks/spaces.
# Why? Because LLMs tokenize whitespace too; compact prompts = fewer tokens.
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")


# ── Target endpoint & model choice ──────────────────────────────────────────
# URL of your local Ollama server (default port is 11434).
# Endpoint `/api/generate` = one-shot text generation request.
url = "http://localhost:11434/api/generate"

# Pick a random local model to query (e.g., "llama3", "qwen2.5", etc.).
model = get_random_ollama_model()


# ── Send the request ───────────────────────────────────────────────────────
# requests.post(...) makes a synchronous HTTP POST call.
# Arguments:
#   • url: Ollama API endpoint (string)
#   • json={...}: dictionary automatically encoded to JSON
#       – "model": the model name we chose above
#       – "prompt": the text we want the model to answer
#       – "stream": False means "don’t stream partial outputs, wait until done"
#
# The result is a `Response` object containing the server’s reply.
response = requests.post(
    url, json={"model": model, "prompt": user_prompt, "stream": False}
)


# ── Handle the reply ───────────────────────────────────────────────────────
# Ollama’s reply body is JSON → convert it into a Python dict via .json().
# Example: {"response":"Hello world", "done":true, ...}
# We extract the "response" field (the generated text).
# .strip() removes leading/trailing whitespace and newlines.
print(response.json()["response"].strip())

# Extra newlines for readability in terminal output.
print("\n\n")
