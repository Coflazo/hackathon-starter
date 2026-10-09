"""Checks the demo video against the rules judges and events apply.

    python3 tools/proof/check_video.py [--limit 180] [--wow-by 10]
Exits 1 and lists every failure: too long, no audio or captions, the wow step after the first
--wow-by seconds, or a sponsor from demo-path.json never named in the narration.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

OUT = Path(os.environ.get("PROOF_DIR", "proof"))


def probe(path: Path) -> dict:
    res = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def check(limit: float, wow_by: float) -> list[str]:
    info = probe(OUT / "demo.mp4")
    timeline = json.loads((OUT / "timeline.json").read_text())
    kinds = {s["codec_type"] for s in info["streams"]}
    duration = float(info["format"]["duration"])
    problems = []
    if duration > limit:
        problems.append(f"video is {duration:.1f}s, limit {limit:.0f}s")
    for kind in ("video", "audio", "subtitle"):
        if kind not in kinds:
            problems.append(f"no {kind} stream")
    wow = [s for s in timeline["steps"] if s.get("wow")]
    if not wow:
        problems.append("no step is marked wow")
    elif wow[0]["start"] > wow_by:
        problems.append(f"the wow starts at {wow[0]['start']:.1f}s, after {wow_by:.0f}s")
    said = " ".join(s["say"].lower() for s in timeline["steps"])
    problems += [f"sponsor {sp} is never named" for sp in timeline.get("sponsors", []) if sp.lower() not in said]
    return problems


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=float, default=180)
    ap.add_argument("--wow-by", type=float, default=10)
    a = ap.parse_args()
    found = check(a.limit, a.wow_by)
    print("\n".join(found) or "video checks ok")
    sys.exit(1 if found else 0)
