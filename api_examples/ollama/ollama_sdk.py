#!/usr/bin/env python
# ↑ Shebang: lets Unix-like systems on PATH run this script directly with `./script.py`.
#   On Windows, this line is ignored.

# ── Imports ────────────────────────────────────────────────────────────────
import sys  # Lets us work with the Python runtime itself (argv, path, etc.).
import os  # File and folder utilities (dirname, abspath, etc.).
import ollama  # The official Python client for Ollama (simplifies calling its API).

# Add the parent directory of this script to Python’s import search path.
# Reason: so you can run this file directly AND still import from `lib.utils`.
# Steps:
#   1. __file__ → this file’s path.
#   2. abspath(__file__) → absolute path (no “..”).
#   3. dirname(...) → directory containing this file.
#   4. dirname(...) again → go up one folder.
#   5. append(...) → tell Python “check this folder when importing modules.”
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Bring in your own helper functions:
#   • ws_minify(text): collapse whitespace/newlines (cleaner prompts, fewer tokens).
#   • get_random_ollama_model(): pick a random local Ollama model string.
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Triple-quoted strings allow multi-line prompts for readability.
# ws_minify(...) shrinks it to a single neat line.
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")


# ── API endpoint & model ────────────────────────────────────────────────────
# Ollama’s “raw” REST API endpoint for text generation is /api/generate.
# (With the Python client we don’t actually use this URL directly—it’s implicit.)
url = "http://localhost:11434/api/generate"

# Choose a random local Ollama model (e.g., "llama3", "mistral", "qwen2.5").
model = get_random_ollama_model()


# ── Make a generation request ───────────────────────────────────────────────
# ollama.generate(...) is the high-level helper around the REST API.
# Arguments:
#   • model: which local model to use
#   • prompt: the user’s text
#   • stream: False means "wait for the full reply" (not partial/streamed chunks)
#
# The result is a Python dictionary that includes:
#   {"model":"...", "created_at":"...", "response":"...", "done":True, ...}
response = ollama.generate(model=model, prompt=user_prompt, stream=False)


# ── Print the result ────────────────────────────────────────────────────────
# The model’s reply is under the "response" key in the dictionary.
print(response["response"])

# Add a couple of blank lines for cleaner separation in terminal output.
print("\n\n")
