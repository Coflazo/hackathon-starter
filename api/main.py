"""FastAPI starter: one demo endpoint with an LLM call behind record-and-replay.

    uv venv && uv pip install -r requirements.txt
    DEMO_MODE=1 uvicorn main:app --reload
"""
from __future__ import annotations

import logging
import os
import time
from collections import defaultdict

import httpx2
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from replay import ReplayError, with_replay

app = FastAPI(title="Hackathon starter API")
log = logging.getLogger("demo")
# ponytail: in-memory per-IP limit, per process; use a shared store if the demo stays public.
MAX_PER_MINUTE = int(os.environ.get("DEMO_RATE_LIMIT", "20"))
_hits: dict[str, list[float]] = defaultdict(list)


def _limited(ip: str) -> bool:
    now = time.monotonic()
    _hits[ip] = [t for t in _hits[ip] if now - t < 60] + [now]
    return len(_hits[ip]) > MAX_PER_MINUTE


class DemoIn(BaseModel):
    input: str = Field(min_length=1, max_length=2000)


def _providers() -> list[tuple[str, str, str]]:
    out = []
    for prefix in ("LLM", "FALLBACK"):
        base, model = os.environ.get(f"{prefix}_BASE_URL"), os.environ.get(f"{prefix}_MODEL")
        if base and model:
            out.append((base.rstrip("/"), os.environ.get(f"{prefix}_API_KEY", ""), model))
    return out


def chat(prompt: str) -> str:
    last: Exception = RuntimeError("no LLM provider configured")
    for base, key, model in _providers():
        try:
            r = httpx2.post(f"{base}/chat/completions", timeout=8,
                           headers={"Authorization": f"Bearer {key}"},
                           json={"model": model, "messages": [{"role": "user", "content": prompt}]})
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"] or ""
        except Exception as exc:  # try the next provider
            last = exc
    raise last


@app.get("/health")
def health() -> dict:
    return {"ok": True, "demo_mode": os.environ.get("DEMO_MODE") == "1"}


@app.post("/demo")
def demo(body: DemoIn, request: Request) -> dict:
    if _limited(request.client.host if request.client else "local"):
        raise HTTPException(status_code=429, detail="Too many requests. Try again in a minute.")
    try:
        output, source = with_replay("demo", lambda: chat(f"Answer in two sentences: {body.input}"))
    except ReplayError as exc:
        log.error("demo endpoint: %s", exc)  # details stay in the server log
        raise HTTPException(status_code=502, detail="The demo service is unavailable right now.") from exc
    return {"output": output, "source": source}
