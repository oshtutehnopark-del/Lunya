"""Music bed + sound effects for a Pip episode (all synthesized here, original tune).

usage: python music.py episodes/ep01-colors.json out/bed.wav
"""
import json, sys
import numpy as np
import soundfile as sf

SR = 44100
rng = np.random.default_rng(7)


def hz(m): return 440 * 2 ** ((m - 69) / 12)


def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def pluck(m, dur=0.5, vol=0.3, bright=0.5):
    n = int(SR * dur); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2*np.pi*f*t) + bright*0.5*np.sin(4*np.pi*f*t) + bright*0.25*np.sin(6*np.pi*f*t)
    return vol * s * env(n, 0.004, dur * 0.35)


def bell(m, dur=1.0, vol=0.25):
    n = int(SR * dur); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2*np.pi*f*t) + 0.5*np.sin(2*np.pi*f*2.76*t)*np.exp(-t/0.15) + 0.3*np.sin(2*np.pi*f*5.4*t)*np.exp(-t/0.08)
    return vol * s * env(n, 0.002, dur * 0.4)


def pop(vol=0.35):
    n = int(SR * 0.09); t = np.arange(n) / SR
    f = 500 + 1400 * t / t[-1]
    return vol * np.sin(2*np.pi*np.cumsum(f)/SR) * env(n, 0.002, 0.03)


def boing(vol=0.35, base=180):
    n = int(SR * 0.4); t = np.arange(n) / SR
    f = base * (1 + 0.9*np.exp(-t/0.05)) * (1 + 0.08*np.sin(2*np.pi*14*t))
    return vol * np.sin(2*np.pi*np.cumsum(f)/SR) * env(n, 0.002, 0.12)


def whoosh(vol=0.12):
    n = int(SR * 0.35); t = np.arange(n) / SR
    k = np.convolve(rng.standard_normal(n), np.ones(30)/30, mode='same')
    return vol * k / np.abs(k).max() * np.sin(np.pi * t / t[-1]) ** 2


def seq(notes, step, vol, dur=1.0):
    out = np.zeros(int(SR * (step * len(notes) + dur)))
    for i, m in enumerate(notes):
        b = bell(m, dur, vol); s = int(i * step * SR); out[s:s+len(b)] += b
    return out


SFX = {
    "sparkle": lambda: seq([72, 76, 79, 84, 88], 0.07, 0.12, 0.8),
    "pop": lambda: pop(0.3),
    "whoosh": whoosh,
    "boing": lambda: boing(0.32),
    "boing_small": lambda: boing(0.14, 260),
    "ding": lambda: np.concatenate([pop(0.3), np.zeros(1)]) if False else _ding(),
    "count1": lambda: _count(84, 200),
    "count2": lambda: _count(88, 230),
    "count3": lambda: _count(91, 260),
    "fanfare": lambda: _mix(pop(0.3), seq([72, 76, 79, 84], 0.09, 0.16)),
    "byebye": lambda: _mix(seq([84, 79, 76, 72], 0.12, 0.15), _hops()),
}


def _mix(*parts):
    out = np.zeros(max(len(p) for p in parts))
    for p in parts: out[:len(p)] += p
    return out


def _ding():
    a = pop(0.3); b = bell(84, 1.0, 0.2); c = bell(88, 1.0, 0.16)
    out = np.zeros(int(SR * 1.2)); out[:len(a)] += a
    s = int(0.05 * SR); out[s:s+len(b)] += b[:len(out)-s]
    s = int(0.15 * SR); out[s:s+len(c)] += c[:len(out)-s]
    return out


def _count(m, base):
    b = bell(m, 0.7, 0.22); o = boing(0.25, base)
    out = np.zeros(int(SR * 0.8)); out[:len(b)] += b
    s = int(0.03 * SR); out[s:s+len(o)] += o
    return out


def _hops():
    out = np.zeros(int(SR * 1.8))
    for k in range(4):
        b = boing(0.1, 300); s = int((0.1 + k * 0.33) * SR); out[s:s+len(b)] += b
    return out


def music_bed(dur):
    N = int(SR * dur); music = np.zeros(N)
    def add(t, sig):
        i = int(t * SR); j = min(N, i + len(sig))
        if i < N: music[i:j] += sig[: j - i]
    b = 60 / 112
    chords = [[48, 52, 55], [45, 48, 52], [41, 45, 48], [43, 47, 50]]  # C Am F G
    mel = [(0,76,1),(1,79,1),(2,81,1),(3,79,1),(4,76,1.5),(5.5,74,0.5),(6,72,2),
           (8,72,1),(9,74,1),(10,76,1),(11,79,1),(12,81,1),(13,79,1),(14,74,2),
           (16,76,1),(17,79,1),(18,84,1.5),(19.5,81,0.5),(20,79,1),(21,76,1),(22,72,2),
           (24,74,1),(25,76,1),(26,79,1),(27,76,1),(28,74,1),(29,74,1),(30,72,2)]
    t0 = 0.0
    while t0 < dur:
        for bar in range(8):
            ch = chords[bar % 4]; bt = t0 + bar * 4 * b
            add(bt, pluck(ch[0] - 12, 4*b, 0.22, 0.2))
            add(bt + 2*b, pluck(ch[0] - 5, 2*b, 0.12, 0.2))
            for k in range(4):
                for nn, m in enumerate(ch):
                    add(bt + k*b + 0.5*b + nn*0.012, pluck(m + 12, 0.35, 0.05, 0.6))
            for k in range(8):
                n = int(SR*0.05); add(bt + k*b/2, 0.025*rng.standard_normal(n)*env(n, 0.001, 0.015))
        for off, m, ln in mel:
            add(t0 + off*b, pluck(m, max(0.3, ln*b*1.1), 0.13, 0.8))
        t0 += 32 * b
    fade = np.ones(N); fi = int(0.5*SR); fo = int(2.5*SR)
    fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
    return music * fade


def main(ep_path, out_path):
    ep = json.load(open(ep_path, encoding="utf-8"))
    N = int(SR * ep["duration"])
    music = music_bed(ep["duration"]); sfx = np.zeros(N)
    for ev in ep.get("sfx", []):
        sig = SFX[ev["type"]]()
        i = int(ev["t"] * SR); j = min(N, i + len(sig))
        if i < N: sfx[i:j] += sig[: j - i]
    # music and effects kept as two channels' worth of info: write a 2-column file (music, sfx)
    sf.write(out_path, np.stack([music, sfx], 1).astype(np.float32), SR)
    print("bed:", out_path)


if __name__ == "__main__":
    main(*sys.argv[1:3])
