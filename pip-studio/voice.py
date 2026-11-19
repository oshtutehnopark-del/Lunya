"""Narration track for a Pip episode.

usage: python voice.py episodes/ep01-colors.json ru out/voice-ru.wav

Each line is synthesized with the voice set in voices.json, trimmed of
leading/trailing silence, normalized, and placed at its start time.
A line that runs into the next one is sped up (up to 15%); if it still
does not fit, it is reported so the timing can be fixed in the script.
"""
import json, os, sys, warnings
import numpy as np

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
GAP = 0.12            # silence kept before the next line
MAX_SPEEDUP = 1.15


def resample(a, src, dst):
    if src == dst:
        return a
    n = int(len(a) * dst / src)
    return np.interp(np.arange(n) * src / dst, np.arange(len(a)), a)


def trim(a, thr=0.02, pad=0.03):
    idx = np.where(np.abs(a) > thr * np.abs(a).max())[0]
    if not len(idx):
        return a
    p = int(pad * SR)
    return a[max(0, idx[0] - p): idx[-1] + p]


def pitch_shift(a, p):
    """Raise pitch by factor p, keeping the length (resample, then stretch back)."""
    if abs(p - 1) < 1e-3:
        return a
    return speed_up(resample(a, SR * p, SR), 1 / p)


def speed_up(a, k):
    """Change tempo by k without changing pitch (simple overlap-add); k > 1 is faster."""
    if abs(k - 1) < 1e-4:
        return a
    win = int(0.04 * SR); hop_out = win // 2; hop_in = int(hop_out * k)
    w = np.hanning(win)
    n_frames = max(1, (len(a) - win) // hop_in)
    out = np.zeros(n_frames * hop_out + win); norm = np.zeros_like(out)
    for i in range(n_frames):
        seg = a[i * hop_in: i * hop_in + win]
        if len(seg) < win:
            break
        out[i * hop_out: i * hop_out + win] += seg * w
        norm[i * hop_out: i * hop_out + win] += w
    return out / np.maximum(norm, 1e-3)


_MODELS = {}


def _model(engine):
    """Load each TTS model once, shared by all roles that use it."""
    if engine not in _MODELS:
        if engine == "kokoro":
            from kokoro_onnx import Kokoro
            m = os.path.join(HERE, "models")
            _MODELS[engine] = Kokoro(os.path.join(m, "kokoro-v1.0.onnx"), os.path.join(m, "voices-v1.0.bin"))
        elif engine == "vosk":
            from vosk_tts import Model, Synth
            _MODELS[engine] = Synth(Model(model_path=os.path.join(HERE, "models/vosk/vosk-model-tts-ru-0.9-multi")))
        else:
            raise SystemExit("unknown engine " + engine)
    return _MODELS[engine]


class Engine:
    def __init__(self, cfg):
        self.cfg = cfg
        self.m = _model(cfg["engine"])

    def say(self, text):
        c = self.cfg
        if c["engine"] == "kokoro":
            a, sr = self.m.create(text, voice=c["voice"], speed=c.get("speed", 0.9), lang=c.get("lang", "en-us"))
            a = resample(np.asarray(a, float), sr, SR)
        else:
            import soundfile as sf, tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav") as f:
                self.m.synth(text, f.name, speaker_id=c.get("speaker_id", 0), speech_rate=c.get("speech_rate", 0.9))
                a, sr = sf.read(f.name)
            if a.ndim > 1:
                a = a.mean(1)
            a = resample(a, sr, SR)
        return pitch_shift(a, c.get("pitch", 1.0))


def main(ep_path, lang, out_path):
    import soundfile as sf
    ep = json.load(open(ep_path, encoding="utf-8"))
    roles = json.load(open(os.path.join(HERE, "voices.json")))[lang]
    engines = {role: Engine(cfg) for role, cfg in roles.items()}
    track = np.zeros(int(ep["duration"] * SR))
    lines = sorted(ep["lines"], key=lambda l: l["t"])
    problems = 0
    for i, ln in enumerate(lines):
        who = ln.get("who", "narrator")
        a = trim(engines[who].say(ln[lang]))
        a = a / (np.abs(a).max() + 1e-9) * 0.9
        end_limit = (lines[i + 1]["t"] - GAP) if i + 1 < len(lines) else ep["duration"] - 0.5
        slot = end_limit - ln["t"]
        dur = len(a) / SR
        note = ""
        if dur > slot:
            k = min(MAX_SPEEDUP, dur / slot)
            a = speed_up(a, k)
            dur = len(a) / SR
            note = f"  sped up x{k:.2f}"
            if dur > slot + 0.02:
                note += f"  STILL TOO LONG by {dur - slot:.2f}s: move the next line later or shorten the text"
                problems += 1
        s = int(ln["t"] * SR); e = min(len(track), s + len(a))
        track[s:e] += a[: e - s]
        print(f"{ln['t']:6.2f}s  {who:8s} {dur:4.2f}/{slot:4.2f}s  {ln[lang]}{note}")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    sf.write(out_path, track.astype(np.float32), SR)
    print(f"voice track: {out_path}" + (f"  ({problems} line(s) need fixing)" if problems else "  (all lines fit)"))


if __name__ == "__main__":
    main(*sys.argv[1:4])
