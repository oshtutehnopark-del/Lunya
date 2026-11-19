# Pip Studio

Tools for making Pip cartoons in English and Russian.

## Make an episode

```bash
./build.sh episodes/ep01-colors.json ru
./build.sh episodes/ep01-colors.json en
```

The video lands in `out/<episode-id>/<episode-id>-<lang>.mp4` (1920×1080, 30 fps, −14 LUFS).

## Files

| File | What it does |
|---|---|
| `episodes/*.json` | Episode script: each line's start time and text in `en` and `ru`, plus sound effects |
| `voices.json` | Which voice reads each language |
| `pages/*.html` | The animation for each language (rendered to frames) |
| `render.js` | Renders a page to frames with Playwright |
| `music.py` | Original music bed and sound effects |
| `voice.py` | Narration: synthesizes, trims, checks every line fits before the next one |
| `mix.py` | Voice over ducked music + effects |

## Voices

- English: Kokoro (`af_heart`, `af_bella`, `af_nicole`, …), ONNX model in `models/`.
- Russian: Vosk TTS 0.9 multi (`speaker_id` 0–2 female, 3–4 male), ONNX model in `models/vosk/`.

Change the voice or speed in `voices.json`, then run `build.sh` again.

## When a line does not fit

`voice.py` prints each line as `start  length/slot`. A line longer than its slot is sped up by up to 15%.
If it still says `STILL TOO LONG`, move the next line's `t` later or shorten the text.
