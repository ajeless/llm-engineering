#!/usr/bin/env python
# ↑ Shebang: lets Unix-like systems run this file directly with `./03_sync_openai_client.py`.
#   Harmless on Windows (ignored there).

# ── Imports ─────────────────────────────────────────────────────────────────
import sys  # Adjust Python's import search path at runtime.
import os  # Filesystem path helpers (dirname, abspath, etc.).
from openai import (
    OpenAI,
)  # Official OpenAI client (can point to Ollama's OpenAI-compatible API).

# Add the project’s parent directory to Python’s module search path so we can
# import from lib/utils when running this file directly (not as a package).
# Steps:
#   1) __file__ → this script’s path
#   2) abspath(__file__) → absolute path (no "..")
#   3) dirname(...) → directory containing this script
#   4) dirname(...) again → parent directory (project root)
#   5) sys.path.append(...) → tell Python to ALSO search there for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Your helpers:
#   • ws_minify(text): collapse whitespace/newlines (cheaper prompts).
#   • get_random_ollama_model(): pick a random local model name (string).
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Triple-quoted string = easy multi-line text in code.
# ws_minify(...) trims extra spaces/linebreaks → fewer tokens for the LLM.
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")


# ── Point the OpenAI client at your local Ollama ────────────────────────────
# Ollama exposes an OpenAI-compatible REST API under /v1 (default port 11434).
# We provide *some* API key because the OpenAI client requires one, but Ollama ignores it.
base_url = "http://localhost:11434/v1"
api_key = "ollama"  # placeholder; not validated by Ollama

# Instantiate the client (normally talks to OpenAI Cloud, but we override base_url).
client = OpenAI(base_url=base_url, api_key=api_key)


# ── Choose a model & prepare messages ───────────────────────────────────────
# Example models depend on what you’ve pulled locally (e.g., "llama3", "mistral", "qwen2.5").
model = get_random_ollama_model()

# OpenAI-style "chat" input uses a list of messages:
#   role = "system" | "user" | "assistant"
#   content = text for that role
# Here, we send just a single user message.
messages = [{"role": "user", "content": user_prompt}]


# ── Send a synchronous chat completion request ──────────────────────────────
# This blocks until Ollama finishes the generation (no streaming here).
resp = client.chat.completions.create(
    model=model,
    messages=messages,
)

# The response has a list of "choices"; we take the first one and print its text.
print(resp.choices[0].message.content.strip())
print("\n\n")  # extra spacing in the terminal
