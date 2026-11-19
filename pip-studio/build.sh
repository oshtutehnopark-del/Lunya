#!/usr/bin/env bash
# Build one Pip episode in one language.
#   ./build.sh episodes/ep01-colors.json ru
# Steps: render frames (once) -> music + effects -> narration -> mix -> MP4 at -14 LUFS.
set -euo pipefail
cd "$(dirname "$0")"
EP_JSON="$1"; LANG_CODE="$2"
PY="${PIP_PY:-python3}"
EP_ID=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1]))['id'])" "$EP_JSON")
DUR=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1]))['duration'])" "$EP_JSON")
PAGE=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1]))['pages'][sys.argv[2]])" "$EP_JSON" "$LANG_CODE")
OUT="out/$EP_ID"; FRAMES="$OUT/frames-$LANG_CODE"
mkdir -p "$OUT" "$FRAMES"

if [ ! -f "$FRAMES/f00000.jpg" ]; then
  echo "== rendering frames ($PAGE)"
  node render.js "$PAGE" "$FRAMES" "$DUR"
fi

echo "== music + effects"
"$PY" music.py "$EP_JSON" "$OUT/bed.wav"
echo "== narration ($LANG_CODE)"
"$PY" voice.py "$EP_JSON" "$LANG_CODE" "$OUT/voice-$LANG_CODE.wav"
echo "== mix"
"$PY" mix.py "$OUT/bed.wav" "$OUT/voice-$LANG_CODE.wav" "$OUT/mix-$LANG_CODE.wav"

echo "== encode"
ffmpeg -y -v error -framerate 30 -i "$FRAMES/f%05d.jpg" -i "$OUT/mix-$LANG_CODE.wav" \
  -map 0:v -map 1:a -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k \
  -shortest -movflags +faststart "$OUT/$EP_ID-$LANG_CODE.mp4"
echo "done: $OUT/$EP_ID-$LANG_CODE.mp4"
