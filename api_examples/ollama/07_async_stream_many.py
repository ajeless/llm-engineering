#!/usr/bin/env python
# ↑ Shebang: lets Unix-like systems run this file directly with `./07_async_stream_many.py`.
#   Harmless on Windows (ignored there).

# ── Imports ─────────────────────────────────────────────────────────────────
import asyncio  # Event loop + async/await primitives.
import sys  # Modify Python's import search path at runtime.
import os  # Filesystem helpers (dirname, abspath, etc.).
import json  # Parse NDJSON lines (JSON per line).
import httpx  # Async HTTP client with streaming support.

# Ensure we can import from your project root (e.g., lib/utils.py) when run directly.
# Steps:
#   1) __file__ → path to THIS script
#   2) abspath(__file__) → absolute path (no "..")
#   3) dirname(...) → containing folder
#   4) dirname(...) again → parent folder (project root)
#   5) sys.path.append(...) → tell Python to ALSO search here for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Your helpers:
#   • ws_minify(text): collapse whitespace/newlines (compact prompts).
#   • get_random_ollama_model(): return a local Ollama model name (string).
from lib.utils import ws_minify, get_random_ollama_model


# ── Build the user prompt ───────────────────────────────────────────────────
# Multiline for readability in code; ws_minify() compacts it for the API.
user_prompt = ws_minify("""
    Identify your model and creator.
    Explain your purpose, key strengths and limitations.
    When would you be the optimal choice over competing models?
""")

# ── API endpoint & models ───────────────────────────────────────────────────
# Same endpoint as non-streaming; we enable streaming with "stream": True.
url = "http://localhost:11434/api/generate"

# Spin up a few concurrent streams. Adjust the count to taste.
N = 3
models = [get_random_ollama_model() for _ in range(N)]


# ── One streaming task (per model) ──────────────────────────────────────────
# Streams NDJSON lines and prints text chunks as they arrive.
# Optional `lock` prevents interleaved printing from multiple tasks.
async def stream_one(client, model, lock=None):
    # Start a streaming POST request to Ollama.
    async with client.stream(
        "POST",
        url,
        json={"model": model, "prompt": user_prompt, "stream": True},
    ) as response:
        # Header per model, optionally serialized so headers don’t overlap.
        if lock:
            async with lock:
                print(f"\n=== {model} (streaming) ===\n", flush=True)
        else:
            print(f"\n=== {model} (streaming) ===\n", flush=True)

        # Read one line at a time as they arrive.
        async for line in response.aiter_lines():
            if not line:
                continue  # skip keep-alives/empty lines
            data = json.loads(line)

            # Print text chunks *immediately*; serialize if a lock was provided.
            if "response" in data:
                if lock:
                    async with lock:
                        print(data["response"], end="", flush=True)
                else:
                    print(data["response"], end="", flush=True)

            # When done, add a couple of newlines and return.
            if data.get("done"):
                if lock:
                    async with lock:
                        print("\n\n", flush=True)
                else:
                    print("\n\n", flush=True)
                break


# ── Main program: run multiple streaming tasks concurrently ─────────────────
async def main():
    # Timeouts tuned for local inference:
    #   connect=10s, read=None (no read timeout for long generations), write=60s, pool=15s.
    timeout = httpx.Timeout(connect=10.0, read=None, write=60.0, pool=15.0)

    # Optional: lock to keep print output tidy across concurrent tasks.
    lock = asyncio.Lock()

    # Optional: throttle concurrency (e.g., if CPU/VRAM is limited).
    # Remove the semaphore if you want to let all N streams run at once.
    sem = asyncio.Semaphore(3)  # at most 3 in-flight streams

    async with httpx.AsyncClient(timeout=timeout) as client:

        async def wrapped(model):
            async with sem:
                await stream_one(client, model, lock=lock)

        # Kick off all streaming tasks concurrently and wait for completion.
        await asyncio.gather(*(wrapped(m) for m in models))


# ── Launch the event loop ───────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
