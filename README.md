# hackathon-starter

Generic plumbing for a hackathon demo that cannot break on stage: a demo-mode switch,
record-and-replay fallbacks for every external call, and one smoke test that walks the demo path.
It holds no product. Use it only where the event's rules allow pre-existing generic boilerplate,
and say so in your submission.

## What is in it

| Part | What it does |
|---|---|
| `web/` | Next.js 16 app with one demo page, an API route, and `lib/replay.ts` + `lib/llm.ts` |
| `api/` | FastAPI twin with `replay.py` and the same demo endpoint |
| `fixtures/` (both) | Recorded answers the demo falls back to; the sample answer is labelled "Sample data" on screen |
| `e2e/demo-path.spec.ts`, `api/test_smoke.py` | The smoke tests: cut features, never these |
| `.github/workflows/ci.yml` | Build, smoke tests and gitleaks on every push and pull request |
| `WRITEUP.md` | Submission template with a "what is proven" table |

## How the fallback works

| Setting | Behaviour |
|---|---|
| `DEMO_MODE=1` | Every call answers from `fixtures/<key>.json`; the demo is identical each run |
| `RECORD=1` | Calls go live and the answers are saved as fixtures |
| neither | Live call with a timeout; on failure, the fixture; with no fixture, a clear error state |

The LLM client tries `LLM_*` first (the sponsor's model, if a prize needs it), then `FALLBACK_*`.
Both are any OpenAI-compatible endpoint. Copy `web/.env.example` to `web/.env.local`.

A public deploy is an open door to your LLM quota, so `/demo` is rate-limited per IP
(`DEMO_RATE_LIMIT`, default 20 a minute; in memory, per instance). `RECORD` is ignored in
production, so visitors can never overwrite the demo fixture. Errors reach the client as a
generic message; details stay in the server log.

## Run it

```bash
cd web && npm install && npm run dev            # http://localhost:3000
DEMO_MODE=1 npx playwright test                  # smoke test (PLAYWRIGHT_CHANNEL=chrome reuses installed Chrome)

cd api && uv venv && uv pip install -r requirements.txt
DEMO_MODE=1 .venv/bin/uvicorn main:app --reload  # http://localhost:8000/docs
.venv/bin/python -m pytest -q
```

Need components? `npx shadcn@latest init` inside `web/` adds Tailwind and shadcn/ui.

## What is proven

| Claim | Verdict | Evidence |
|---|---|---|
| The web demo path works offline in demo mode | Proven | `e2e/demo-path.spec.ts`, 2 tests pass |
| The API demo path works offline, fails clearly without a fixture, rate-limits, refuses path-like fixture keys | Proven | `api/test_smoke.py`, 5 tests pass |
| Live LLM calls fall back to the second provider | Not yet tested | Covered by code review only |

## License

MIT
