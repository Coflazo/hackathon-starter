# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Proof kit, from build drills 10 and 11: `tools/proof/run.sh` runs the whole kit in one command
  and stops the server on any failure; the recorder outlines what each beat narrates, shows a dot
  where a click lands, adds a `select` action, `focus_testid`, a `setup` page load and
  `PROOF_CHROME_ARGS`, and runs in the `en-US` locale; `check_video.py` fails on two step
  screenshots that look the same (SSIM 0.995 or more, calibrated on drill 11's video panels).

### Changed

- Next.js 16.4.0 to 16.4.3 (security advisory on 16.4.0).
- The template's demo path merges the "sample data" beat into the wow step: its frame repeated
  the previous one (SSIM 0.996), which the new check catches.

- Proof kit `scroll` action: brings an element (by `data-testid`) into view, so a long report
  page can be walked beat by beat instead of holding one static frame.

### Fixed

- Proof kit captions now show the spoken narration, not the short step label: deaf and muted
  viewers, and a video panel reading the transcript, saw only a few words per step.

### Added

- Proof kit (`tools/proof/`): records the demo path through a DevTools screencast, narrates it with
  local Kokoro TTS or silent timing, muxes a captioned MP4 and a GIF, checks the video (length, wow
  by 10 s, captions, sponsors named) and builds the "what is proven" table from test results. CI runs
  it and uploads the `proof` artifact.

### Changed

- TypeScript 5.9.3 to 7.0.2 in `web/` (the native compiler); `next build` and the smoke test pass.

## [1.0.0] - 2026-10-09

### Added

- `web/`: Next.js 16 app with one demo page, an API route, `lib/replay.ts` (record and replay with
  a fixture fallback) and `lib/llm.ts` (a primary and a fallback OpenAI-compatible provider).
- `api/`: FastAPI twin with `replay.py` and the same demo endpoint.
- `DEMO_MODE` and `RECORD` switches; sample answers are labelled "Sample data" on screen.
- Per-IP rate limit on `/demo`, `RECORD` ignored in production, generic client errors, strict
  fixture keys.
- Smoke tests: a Playwright demo-path test and five API tests.
- CI with build, smoke tests and gitleaks; `WRITEUP.md` submission template with a "what is proven"
  table.
- Theme-aware README banner designed in Figma, community files, issue forms, a pull request
  template, Dependabot and CodeQL.

### Security

- API dependencies updated: fastapi 0.143.0 and starlette 1.7.0 (starlette 0.38.6 had
  CVE-2024-47874, CVE-2025-54121 and five 2026 advisories), uvicorn 0.54.0 (h11 0.16.0 fixes
  CVE-2025-43859), pytest 9.1.1 (CVE-2025-71176). The API's outgoing call and the test client use
  httpx2, which Starlette 1.x expects.

[Unreleased]: https://github.com/Coflazo/hackathon-starter/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Coflazo/hackathon-starter/releases/tag/v1.0.0
