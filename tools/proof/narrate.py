"""Narration for the demo video with local Kokoro TTS (offline, free; voice bm_lewis, en-gb).

    ~/.local/share/liminal-tts/.venv/bin/python tools/proof/narrate.py prepare [demo-path.json]
        speaks each step's line to proof/clips/NN.wav and writes proof/durations.json,
        so record.mjs holds every step exactly as long as its line
    ~/.local/share/liminal-tts/.venv/bin/python tools/proof/narrate.py build
        places the clips at the recorded step times: proof/narration.wav and proof/captions.srt
    python3 tools/proof/narrate.py prepare --silent [demo-path.json]
        no TTS (CI, or a machine without Kokoro): silent clips timed at 150 words a minute
"""

import json
import os
import sys
import wave
from pathlib import Path

import numpy as np

TTS = Path.home() / ".local/share/liminal-tts"
OUT = Path(os.environ.get("PROOF_DIR", "proof"))
RATE = 24000


def ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def write_wav(path: Path, audio: np.ndarray) -> None:
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())


def read_wav(path: Path) -> np.ndarray:
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32767


def spoken_seconds(text: str) -> float:
    return max(len(text.split()) / 150 * 60, 1.0)  # 150 words a minute, the pitch pace


def prepare(spec_path: str, silent: bool = False) -> None:
    steps = json.loads(Path(spec_path).read_text())["steps"]
    (OUT / "clips").mkdir(parents=True, exist_ok=True)
    if not silent:
        from kokoro_onnx import Kokoro  # only in the Kokoro venv

        kokoro = Kokoro(str(TTS / "kokoro-v1.0.onnx"), str(TTS / "voices-v1.0.bin"))
    durations = []
    for i, s in enumerate(steps, 1):
        if silent:
            audio, rate = np.zeros(int(spoken_seconds(s["say"]) * RATE), dtype=np.float32), RATE
        else:
            audio, rate = kokoro.create(s["say"], voice="bm_lewis", speed=1.0, lang="en-gb")
        assert rate == RATE, rate
        write_wav(OUT / "clips" / f"{i:02}.wav", audio)
        durations.append(round(len(audio) / RATE, 3))
    (OUT / "durations.json").write_text(json.dumps(durations))
    print(f"{len(durations)} lines, {sum(durations):.1f}s of narration -> {OUT}/clips/")


def build() -> None:
    steps = json.loads((OUT / "timeline.json").read_text())["steps"]
    clips = [read_wav(OUT / "clips" / f"{s['step']:02}.wav") for s in steps]
    total = max(s["start"] + len(c) / RATE for s, c in zip(steps, clips, strict=True)) + 0.5
    track = np.zeros(int(total * RATE), dtype=np.float32)
    srt = []
    for i, (s, c) in enumerate(zip(steps, clips, strict=True), 1):
        at = int(s["start"] * RATE)
        track[at : at + len(c)] += c
        srt.append(f"{i}\n{ts(s['start'])} --> {ts(s['start'] + len(c) / RATE)}\n{s['caption'] or s['say']}\n")
    write_wav(OUT / "narration.wav", track)
    (OUT / "captions.srt").write_text("\n".join(srt))
    print(f"narration {total:.1f}s -> {OUT}/narration.wav, {OUT}/captions.srt")


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if x != "--silent"]
    if args and args[0] == "prepare":
        prepare(args[1] if len(args) > 1 else "tools/proof/demo-path.json", silent="--silent" in sys.argv)
    else:
        build()
