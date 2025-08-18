#! /usr/bin/env python
# ↑ "Shebang" line: lets Unix-like systems run this file directly (e.g., `./script.py`)
#   using whichever `python` is first on your PATH. Harmless on Windows.

# ── Imports ────────────────────────────────────────────────────────────────────
# We bring in a few Python modules (some built-in, some third-party) that
# we’ll use below.

import sys  # Access to Python runtime bits like argv and the module search path.
import os  # Tools for working with file/folder paths (join, dirname, etc.).
import asyncio  # Python’s built-in framework for asynchronous, non-blocking I/O.
import httpx  # Third-party HTTP client that supports async requests.
import json  # Built-in JSON encoder/decoder (text ↔ Python dict).

# This modifies Python’s module search path so we can import from your project.
# - __file__ is the path to THIS script file.
# - os.path.abspath(__file__) gives the absolute path (no ".." parts).
# - os.path.dirname(...) gets the directory containing the file.
# - Wrapping dirname(...) again moves one level up (the parent folder).
# - sys.path.append(...) tells Python to ALSO look there when importing modules.
#   (We do this so `from lib.utils import ...` works when running this file directly.)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# We import two helper functions that YOU already have in your codebase:
# - ws_minify(text): collapses whitespace/newlines so prompts are compact.
# - get_random_ollama_model(): returns a random local Ollama model name (string).
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ─────────────────────────────────────────────────────
# Triple-quoted strings allow easy multi-line text. We immediately pass it
# through ws_minify to remove extra spaces/linebreaks (clean prompt = fewer tokens).
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")

# ── Concurrency parameters & endpoint ─────────────────────────────────────────
# N = how many requests you’ll run IN PARALLEL (true async concurrency).
# Start small on a slow VM; increase slowly as resources allow.
N = 3

# Ollama’s HTTP endpoint for text generation (default host/port).
url = "http://localhost:11434/api/generate"

# Build a list of model names (length N). Each concurrent task will pick one.
# Example names might be "llama3", "qwen2.5", etc., depending on what you’ve pulled.
models = [get_random_ollama_model() for _ in range(N)]


# ── One streaming task (runs once per model) ──────────────────────────────────
# This is an *async function* (declared with `async def`). It:
#   1) opens a streaming POST request to Ollama,
#   2) reads *lines* as they arrive (Ollama sends NDJSON: one JSON object per line),
#   3) prints the text chunks immediately as they arrive,
#   4) stops when the final "done": true line appears.
async def stream_one(client, model):
    # Print a section header so you can see which model’s output follows.
    # `flush=True` forces the text to appear immediately in the terminal.
    print(f"\n=== {model} ===", flush=True)

    # `client.stream(...)` starts an HTTP request in *streaming* mode.
    # Arguments:
    #   - "POST": HTTP method
    #   - url: endpoint string (see above)
    #   - json={...}: request body as a Python dict; httpx turns it into JSON.
    #     • "model": which local model to run
    #     • "prompt": your user text
    #     • "stream": True asks Ollama to send partial results as they’re generated
    #
    # The `async with` block ensures the connection is properly closed when done.
    async with client.stream(
        "POST", url, json={"model": model, "prompt": user_prompt, "stream": True}
    ) as response:
        # `response.aiter_lines()` is an *async iterator* that yields each line
        # of text as soon as it arrives from the server—no need to wait for the
        # whole response. Ollama’s lines are JSON objects, one per line:
        #   {"response":"Hello", "done":false, ...}
        #   {"response":" world!", "done":false, ...}
        #   {"done":true, ...}
        async for line in response.aiter_lines():
            # Some lines can be empty (keep-alive heartbeats, etc.). Skip them.
            if not line:
                continue

            # Turn the JSON text into a Python dict so we can read fields.
            data = json.loads(line)

            # If this line contains a "response" field, that’s the next text chunk.
            # We print it immediately WITHOUT adding a newline (`end=""`) so that
            # chunks appear stuck together as one flowing sentence/paragraph.
            # `flush=True` makes it appear right away.
            if "response" in data:
                print(data["response"], end="", flush=True)

            # When the server signals it's finished (done == true), print a blank
            # line so the next model’s header doesn’t clash with this output, then
            # break out of the loop to end this task.
            if data.get("done"):
                print("\n\n", flush=True)
                break


# ── Program entry point (spins up the client & runs tasks) ────────────────────
# Another async function that:
#   • Configures timeouts suitable for slow local inference,
#   • Creates ONE shared HTTP client (so connections are reused),
#   • Starts N streaming tasks concurrently and waits for all to finish.
async def main():
    # httpx.Timeout sets per-phase limits (not a single total time):
    #   connect=10.0  → up to 10s to connect (DNS/TCP/TLS). Localhost is fast,
    #                   but VMs/bridged networking can occasionally be sluggish.
    #   read=None     → NO read timeout. The task can wait indefinitely for
    #                   streamed chunks—useful for slow models.
    #   write=60.0    → up to 60s to upload the request (mostly a safety net).
    #   pool=15.0     → wait up to 15s to acquire a connection from the pool
    #                   when many tasks are active.
    timeout = httpx.Timeout(connect=10.0, read=None, write=60.0, pool=15.0)

    # Create ONE AsyncClient and share it across all tasks.
    # Why one? Connection pooling + keep-alive = fewer handshakes and better throughput.
    async with httpx.AsyncClient(timeout=timeout) as client:
        # asyncio.gather(...) starts multiple coroutines *at once* and waits
        # for all of them to finish. The starred generator expression
        # produces N separate `stream_one(...)` coroutines—one per model.
        #
        # Concurrency note: while one request is waiting on network I/O,
        # another can make progress, which is why this is faster/smoother
        # than doing them sequentially on a slow VM.
        await asyncio.gather(*(stream_one(client, model) for model in models))


# This is the standard “run the async program” line for a normal .py file.
# It creates an event loop, runs `main()` to completion, and then cleans up.
asyncio.run(main())

# ── Optional tips (not executed) ──────────────────────────────────────────────
# • If outputs interleave too much across tasks, add:
#       lock = asyncio.Lock()
#   and wrap prints in `async with lock:` to serialize printing.
#
# • To limit concurrency (e.g., keep only 2 requests in-flight at once),
#   use a semaphore:
#       sem = asyncio.Semaphore(2)
#       async def stream_one(...):
#           async with sem:
#               ...same body...
#
# • For ultra-slow VMs, you can also set `timeout=None` on the AsyncClient to
#   disable *all* timeouts. Keeping `connect` finite is usually nicer.
