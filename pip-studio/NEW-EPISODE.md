# How to make the next Pip episode

Instructions for the scheduled session that makes a new episode every 2 days.

## Rules

- Pip is our own character: a round grey chick with yellow eyes, dark wingtips and an orange beak. Keep him exactly as drawn in `pages/pip-en.html`.
- Everything must be original: no characters, songs, melodies, names or looks from existing cartoons or brands. Use only `music.py`'s own tune and effects.
- Toddler pace: short sentences, one idea per scene, big simple shapes, no scary content.
- Two languages, same pictures: `pages/<ep>-en.html` and `pages/<ep>-ru.html`.
- Two voices: `"who": "narrator"` explains, `"who": "pip"` says the short word in the bubble and the goodbye.

## Steps

1. `./setup.sh` (first run in a fresh container downloads ~400 MB of voice models).
2. Pick the first `[ ]` topic in `EPISODES.md`.
3. Copy `pages/pip-en.html` to `pages/<ep>-en.html`. Change only:
   - the `SCENES` list (captions, bubble words, items, durations; the speech text there is only for the live page),
   - `drawItem` (add drawings for the new objects; keep them simple, flat and colourful),
   - the title string used on the title scene and the page `<title>`.
   Make `pages/<ep>-ru.html` the same way with Russian text (the Russian page uses the Nunito font).
4. Write `episodes/<ep>.json` like `episodes/ep01-colors.json`:
   - scene start = sum of earlier scene durations; total `duration` = sum + ~1.5 s;
   - narrator line at scene start + 0.15, Pip's bubble word at scene start + 3.4 (when the bubble pops),
   - effects: `whoosh` at each scene start, `boing` at start + 0.63 and `boing_small` at + 0.97 for a dropped item, `ding` with each bubble, `sparkle`+`pop` on the title, `byebye` on the goodbye.
5. Build both languages:
   ```bash
   PIP_PY=$PWD/.venv/bin/python ./build.sh episodes/<ep>.json ru
   PIP_PY=$PWD/.venv/bin/python ./build.sh episodes/<ep>.json en
   ```
   Every narration line must report as fitting. Fix `STILL TOO LONG` lines by moving times or shortening text, then rebuild.
6. Look at 3 frames per language (title, a middle scene, the goodbye) with `ffmpeg -ss <t> -i <mp4> -frames:v 1`. Fix anything clipped or overlapping.
7. Copy the two MP4s to `../videos/` as `<ep>-ru.mp4` and `<ep>-en.mp4`, mark the topic `[x]` with the date in `EPISODES.md`, commit and push.
8. Send both MP4s to the user, with a YouTube title and description in each language, and remind them to mark the video "Made for kids".
