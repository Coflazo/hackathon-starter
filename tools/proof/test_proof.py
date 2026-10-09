"""Tests for the proof kit: the claims table and the video checklist."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import check_video  # noqa: E402
import proof_table  # noqa: E402


def test_table_marks_proven_failing_and_untested():
    passed = {"test_a ok": True, "test_b bad": False}
    out = proof_table.table([{"claim": "A", "tests": ["test_a"]}, {"claim": "B", "tests": ["test_b"]},
                             {"claim": "C", "tests": ["nothing"]}], passed)
    assert "| A | Proven |" in out and "| B | Failing |" in out and "| C | Not yet tested | no test |" in out


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="needs ffmpeg")
def test_video_checklist(tmp_path, monkeypatch):
    srt = tmp_path / "c.srt"
    srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nhello\n")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=white:s=64x64:d=3", "-f", "lavfi",
                    "-i", "anullsrc=r=24000:cl=mono", "-i", str(srt), "-map", "0:v", "-map", "1:a", "-map", "2:s",
                    "-c:s", "mov_text", "-t", "3", str(tmp_path / "demo.mp4")], check=True)
    steps = [{"step": 1, "start": 0.0, "say": "Powered by Acme", "caption": "x", "wow": False},
             {"step": 2, "start": 12.0, "say": "the wow", "caption": "y", "wow": True}]
    (tmp_path / "timeline.json").write_text(json.dumps({"sponsors": ["Acme", "Globex"], "steps": steps}))
    monkeypatch.setattr(check_video, "OUT", tmp_path)
    problems = check_video.check(limit=2, wow_by=10)
    assert any("limit 2s" in p for p in problems)
    assert any("wow starts at 12.0s" in p for p in problems)
    assert problems[-1] == "sponsor Globex is never named"
    assert not any("stream" in p for p in problems)
