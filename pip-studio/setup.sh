#!/usr/bin/env bash
# One-time setup in a fresh container: Python venv with the TTS engines + voice models.
# Safe to run again: skips what is already there.
set -euo pipefail
cd "$(dirname "$0")"
VENV="${PIP_VENV:-$PWD/.venv}"

if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q numpy soundfile kokoro-onnx vosk-tts

mkdir -p models
get() { [ -s "$2" ] || curl -fsSL -o "$2" "$1"; }
get https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx models/kokoro-v1.0.onnx
get https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin   models/voices-v1.0.bin
if [ ! -f models/vosk/vosk-model-tts-ru-0.9-multi/model.onnx ]; then
  get https://alphacephei.com/vosk/models/vosk-model-tts-ru-0.9-multi.zip models/vosk-ru.zip
  mkdir -p models/vosk && (cd models/vosk && unzip -q -o ../vosk-ru.zip)
fi

which ffmpeg >/dev/null || { echo "ffmpeg is missing: apt-get install -y ffmpeg"; exit 1; }
node -e "require('playwright')" 2>/dev/null || { echo "playwright is missing for node"; exit 1; }
echo "setup ok. Build with: PIP_PY=$VENV/bin/python ./build.sh episodes/<episode>.json ru"
