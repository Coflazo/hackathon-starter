#!/bin/sh
# Joins the recording, the narration and soft captions into demo.mp4, and makes demo.gif.
#   sh tools/proof/mux.sh [proof]
set -eu
D="${1:-${PROOF_DIR:-proof}}"
ffmpeg -loglevel error -y -f concat -safe 0 -i "$D/frames/frames.txt" -vsync vfr \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:white" \
  -pix_fmt yuv420p -c:v libx264 "$D/raw.mp4"
ffmpeg -loglevel error -y -i "$D/raw.mp4" -i "$D/narration.wav" -i "$D/captions.srt" \
  -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=3[v]" -map "[v]" -map 1:a -map 2:s -c:v libx264 -pix_fmt yuv420p -c:a aac -c:s mov_text \
  -metadata:s:s:0 language=eng -shortest "$D/demo.mp4"
ffmpeg -loglevel error -y -i "$D/raw.mp4" -vf "fps=8,scale=800:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" "$D/demo.gif"
echo "muxed -> $D/demo.mp4, $D/demo.gif"
