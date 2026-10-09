"""Record-and-replay for every external call (Python twin of web/lib/replay.ts).

DEMO_MODE=1 -> always answer from fixtures/<key>.json; RECORD=1 -> call live and save the answer;
otherwise call live and fall back to the fixture when the call fails.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Callable

FIXTURES = Path(__file__).parent / "fixtures"


class ReplayError(RuntimeError):
    pass


def _fixture(key: str) -> Any | None:
    path = FIXTURES / f"{key}.json"
    return json.loads(path.read_text()) if path.exists() else None


def with_replay(key: str, live: Callable[[], Any]) -> tuple[Any, str]:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", key):  # keys are code constants, never paths
        raise ReplayError(f"invalid fixture key: {key}")
    if os.environ.get("DEMO_MODE") == "1":
        data = _fixture(key)
        if data is None:
            raise ReplayError(f"DEMO_MODE is on but fixtures/{key}.json is missing")
        return data, "fixture"
    try:
        data = live()
    except Exception as exc:  # any live failure falls back to the recorded answer
        data = _fixture(key)
        if data is None:
            raise ReplayError(f"live call failed and no fixture for {key}: {exc}") from exc
        return data, "fixture"
    if os.environ.get("RECORD") == "1":
        FIXTURES.mkdir(exist_ok=True)
        (FIXTURES / f"{key}.json").write_text(json.dumps(data, indent=2))
    return data, "live"
