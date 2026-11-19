"""Final mix: voice over music (ducked) + effects.

usage: python mix.py out/bed.wav out/voice-ru.wav out/final-ru.wav
bed.wav is the 2-column file from music.py (col 0 = music, col 1 = effects).
"""
import sys
import numpy as np
import soundfile as sf

bed, sr = sf.read(sys.argv[1]); voice, sr2 = sf.read(sys.argv[2])
assert sr == sr2
n = min(len(bed), len(voice))
music, sfx, voice = bed[:n, 0], bed[:n, 1], voice[:n]

# duck the music to ~40% while the narrator speaks (smooth 250 ms ramps)
act = (np.abs(voice) > 0.01).astype(float)
k = int(0.25 * sr)
act = np.convolve(act, np.ones(k) / k, mode="same")
duck = 1 - 0.6 * np.clip(act * 3, 0, 1)

mix = 0.55 * music * duck + 0.8 * sfx + 1.0 * voice
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix = mix / np.abs(mix).max() * 0.89
sf.write(sys.argv[3], np.stack([mix, mix], 1).astype(np.float32), sr)
print("mix:", sys.argv[3])
