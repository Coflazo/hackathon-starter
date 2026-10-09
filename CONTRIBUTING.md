# Contributing

The starter stays small on purpose: generic plumbing that keeps a demo alive, and no product. A change
belongs here if almost every hackathon project would want it.

## Before you open a pull request

```bash
cd web && npm install && DEMO_MODE=1 npx playwright test
cd api && uv venv && uv pip install -r requirements.txt && .venv/bin/python -m pytest -q
```

Both smoke suites must pass. They walk the demo path; a change that breaks them is not merged.

## Workflow

- One branch per change: `feat/`, `fix/`, `docs/`, `chore/`, `test/`, `ci/`.
- [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): subject`, imperative,
  72 characters at most, the body says why.
- Open a pull request from the template, link the issue with `Closes #N`, and wait for green CI.
- Add a line to `CHANGELOG.md` under `[Unreleased]`.
- Never commit keys. `.env.local` stays local; CI runs gitleaks.
