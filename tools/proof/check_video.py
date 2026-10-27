"""Checks the demo video against the rules judges and events apply.

    python3 tools/proof/check_video.py [--limit 180] [--wow-by 10]
Exits 1 and lists every failure: too long, no audio or captions, the wow step after the first
--wow-by seconds, a sponsor from demo-path.json never named in the narration, or two step
screenshots that look the same (a beat that does not change the picture reads as a reused frame).
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

OUT = Path(os.environ.get("PROOF_DIR", "proof"))


def probe(path: Path) -> dict:
    res = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def ssim(a: Path, b: Path) -> float:
    """Structural similarity of two screenshots, 1.0 for identical, both scaled to the same size."""
    res = subprocess.run(["ffmpeg", "-nostats", "-i", str(a), "-i", str(b), "-lavfi",
                          "[0:v]scale=640:360[a];[1:v]scale=640:360[b];[a][b]ssim", "-f", "null", "-"],
                         capture_output=True, text=True, check=True)
    return float(re.search(r"All:([\d.]+)", res.stderr).group(1))


def repeated_frames(shots: list[Path], limit: float = 0.995) -> list[str]:
    """Pairs of step screenshots at or above `limit` SSIM. Calibrated on drill 11: frames a video panel
    called reused scored 1.000; distinct beats that differ only by an outline scored at most 0.983."""
    return [f"steps {a.stem} and {b.stem} look the same (SSIM {v:.3f}): change the picture or merge the beats"
            for i, a in enumerate(shots) for b in shots[i + 1:] if (v := ssim(a, b)) >= limit]


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
    problems += repeated_frames(sorted((OUT / "shots").glob("*.png")))
    return problems


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=float, default=180)
    ap.add_argument("--wow-by", type=float, default=10)
    a = ap.parse_args()
    found = check(a.limit, a.wow_by)
    print("\n".join(found) or "video checks ok")
    sys.exit(1 if found else 0)
