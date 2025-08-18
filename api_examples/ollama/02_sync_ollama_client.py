#!/usr/bin/env python
# ↑ Shebang: lets Unix-like systems run this file directly with `./02_sync_ollama_client.py`.
#   Harmless on Windows (ignored there).

# ── Imports ─────────────────────────────────────────────────────────────────
import sys  # Interact with Python runtime (e.g., tweak sys.path).
import os  # Filesystem path helpers (dirname, abspath, etc.).
import ollama  # Official Python client for Ollama (wraps its REST API for you).

# Add the project’s parent directory to Python’s module search path so we can
# import from lib/utils when running this file directly (not as a package).
# Steps:
#   1) __file__ → path to this script
#   2) abspath(__file__) → absolute path (no "..")
#   3) dirname(...) → folder containing this script
#   4) dirname(...) again → go one level up (the project root)
#   5) sys.path.append(...) → tell Python to ALSO search there for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Your helpers:
#   • ws_minify(text): collapse whitespace/newlines (cheaper prompts).
#   • get_random_ollama_model(): pick a random local model name (string).
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Triple-quoted string = easy multi-line prompt in code.
# ws_minify(...) trims extra spaces/linebreaks → fewer tokens for the LLM.
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")


# ── Choose a model ──────────────────────────────────────────────────────────
# Example local models: "llama3", "qwen2.5", "mistral", etc. (depends on what you pulled).
model = get_random_ollama_model()


# ── Make a synchronous generation call ──────────────────────────────────────
# ollama.generate(...) calls the local Ollama instance (default http://localhost:11434)
# and returns a Python dict with fields like: {"response":"...", "done":True, ...}
# stream=False → wait for the FULL reply (no partial/streamed chunks).
result = ollama.generate(
    model=model,
    prompt=user_prompt,
    stream=False,
)

# ── Print the model’s text ──────────────────────────────────────────────────
print(result["response"].strip())
print("\n\n")  # extra spacing in the terminal
