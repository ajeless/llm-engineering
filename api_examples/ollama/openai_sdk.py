#!/usr/bin/env python
# ↑ Shebang: lets Unix-like systems run this file directly with `./script.py`.
#   It tells the shell to use whichever Python interpreter is first on PATH.

# ── Imports ────────────────────────────────────────────────────────────────
import sys  # Access Python runtime features (argv, path, etc.).
import os  # Tools for working with filesystem paths (dirname, abspath, etc.).
from openai import OpenAI  # Official OpenAI Python client (usable with Ollama too).

# Extend Python’s import search path so we can load your local utils module.
# Step by step:
#   1. __file__ is THIS script’s filename.
#   2. os.path.abspath(__file__) → full absolute path to it.
#   3. os.path.dirname(...) → directory containing this file.
#   4. wrapping dirname(...) again → the parent directory.
#   5. sys.path.append(...) → tell Python to also look there for imports.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your two helper functions:
#   • ws_minify(text): collapses whitespace/newlines for compact prompts.
#   • get_random_ollama_model(): returns a random local Ollama model name.
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Triple-quoted string makes multi-line text easier.
# Immediately pass it to ws_minify → trims spaces/newlines to reduce token usage.
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")


# ── API configuration ──────────────────────────────────────────────────────
# Ollama can pretend to be an "OpenAI-compatible" API server.
# - base_url points to your local Ollama instance (default port 11434).
# - /v1 is the OpenAI-style REST API root.
url = "http://localhost:11434/v1"

# OpenAI client requires *some* API key value, but Ollama ignores it.
# We provide a dummy placeholder ("ollama").
api_key = "ollama"

# Pick a random local model to use (string like "llama3", "qwen2.5", etc.).
model = get_random_ollama_model()

# The OpenAI Chat API expects a *list of messages*, not just one prompt string.
# Each message is a dict:
#   • "role": either "system", "user", or "assistant"
#   • "content": the text content
# Here, we send one "user" message with our prompt.
messages = [{"role": "user", "content": user_prompt}]


# ── Create the API client ──────────────────────────────────────────────────
# Instantiate the OpenAI client, pointing it at our local Ollama server.
# - base_url: overrides the default (cloud.openai.com)
# - api_key: required argument, but ignored by Ollama
client = OpenAI(base_url=url, api_key=api_key)


# ── Send the request and print result ──────────────────────────────────────
# Ask for a chat completion:
#   • model = which Ollama model to run
#   • messages = the conversation so far (list of role/content dicts)
# Ollama returns an OpenAI-compatible response object.
response = client.chat.completions.create(model=model, messages=messages)

# The response contains a list of "choices". We grab the first one [0].
# Inside that, `.message.content` is the generated text.
print(response.choices[0].message.content)

# Print a couple extra newlines for spacing in terminal output.
print("\n\n")
