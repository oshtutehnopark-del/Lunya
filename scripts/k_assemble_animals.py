import subprocess, wave, math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

S = "/tmp/claude-0/-home-user/96502a5f-267a-5e70-abdd-8e11d247afa6/scratchpad"
SC = "/home/user/sovushka/ep01/scenes"
U = "/root/.claude/uploads/96502a5f-267a-5e70-abdd-8e11d247afa6/"
OUT = "/home/user/sovushka/lunya_zhivotnye.mp4"
W, H, FPS, SR = 1920, 1080, 24, 44100
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"; BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F = lambda p, s: ImageFont.truetype(p, s)
DARK = (74, 52, 46)
DUR = {int(k): v for k, v in json.load(open(f"{S}/vo_animals_k/dur.json")).items()}

# ---------------- segments: (path, start-in-source, duration, interpolate 16fps) ----------------
SEGS = [(U + "b62a5833-2026-11-18_203513.mp4", 0, 10.0, False),   # 0 intro
        (SC + "/a1_cow.mp4", 0, 5.0, True),                       # 1 cow
        (SC + "/a2_dog.mp4", 0, 5.0, True),                       # 2 dog
        (SC + "/a3_cat.mp4", 0, 5.0, True),                       # 3 cat
        (SC + "/a4_duck.mp4", 0, 5.0, True),                      # 4 duck
        (SC + "/w3.mp4", 0, 5.0, True),                           # 5 quiz 1 thinking
        (SC + "/a3_cat.mp4", 2.0, 3.0, True),                     # 6 answer: cat
        (SC + "/w1.mp4", 0, 4.5, True),                           # 7 quiz 2
        (SC + "/a1_cow.mp4", 2.0, 3.0, True),                     # 8 answer: cow
        (SC + "/n3_basket.mp4", 0, 5.5, False),                   # 9 celebration
        (SC + "/n4_sunset.mp4", 0, 4.0, True)]                    # 10 goodbye
BOUND = [0]
for sg in SEGS: BOUND.append(BOUND[-1] + sg[2])
TOTAL = BOUND[-1]; NF = int(TOTAL * FPS)
B = BOUND
VO = []
def say(i, t): VO.append((i, t)); return t + DUR[i]
say(1, 0.8); say(2, 5.0)
for j in range(4): say(3 + j, B[1 + j] + 0.2)
say(7, B[5] + 0.3); say(8, B[6] + 0.2); say(9, B[7] + 0.3); say(10, B[8] + 0.2)
CELEB = B[9]; say(11, CELEB + 0.4)
ANI = [("КОРОВА", (121, 85, 72), "МУ-У!", 1), ("СОБАЧКА", (141, 110, 99), "ГАВ-ГАВ!", 2),
       ("КОТИК", (251, 140, 0), "МЯУ!", 3), ("УТОЧКА", (251, 192, 45), "КРЯ-КРЯ!", 4)]
SOUND_T = [B[1 + j] + 0.2 + DUR[3 + j] - 1.0 for j in range(4)]
QUIZ = [(B[5] + 0.4, B[6], "МЯУ!", 2), (B[7] + 0.4, B[8], "МУ-У!", 0)]
print("total", round(TOTAL, 1), [round(x, 1) for x in BOUND])

# ---------------- audio ----------------
def load(i):
    with wave.open(f"{S}/vo_animals_k/l{i}.wav") as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
def tone(f, dur, decay=4.0, harm=(1, .5, .25, .12)):
    t = np.arange(int(dur * SR)) / SR
    return sum(a * np.sin(2 * np.pi * f * (i + 1) * t) * np.exp(-t * decay * (1 + i * .8)) for i, a in enumerate(harm))
def mid(m): return 440 * 2 ** ((m - 69) / 12)
def add(buf, x, t0, g=1.0):
    i = int(t0 * SR); e_ = min(len(buf), i + len(x))
    if e_ > i: buf[i:e_] += x[:e_ - i] * g
n = int((TOTAL + .5) * SR); vo = np.zeros(n); mus = np.zeros(n); fx = np.zeros(n)
for i, t in VO: x = load(i); add(vo, x / max(1e-6, np.abs(x).max()) * 0.9, t)
beat = 60 / 108; prog = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
t, k = 0.3, 0
while t < TOTAL:
    ch = prog[(k // 8) % 4]
    add(mus, tone(mid(ch[k % 3] + (12 if k % 2 else 0)), .8, 5), t, .22)
    if k % 4 == 0: add(mus, tone(mid(ch[0] - 24), 1.6, 2.2, (1, .3)), t, .32)
    t += beat / 2; k += 1
tt = np.arange(n) / SR
mus *= np.clip((tt - 0.3) / 1.5, 0, 1) * np.clip((TOTAL - tt) / 2, 0, 1)
c_ = np.concatenate([[0], np.cumsum(np.abs(vo))]); ii = np.arange(n)
venv = (c_[np.minimum(ii + 2205, n)] - c_[np.maximum(ii - 2205, 0)]) / 4410
mus = mus / np.abs(mus).max() * 0.30 * (1 - 0.55 * np.clip(venv / 0.05, 0, 1))
for j, t0 in enumerate(SOUND_T):
    for q, m in enumerate([72, 76, 79]): add(fx, tone(mid(m + 2 * j), .6, 5), t0 + q * .06, .16)
for q0, qa, _, _ in QUIZ:
    for s_ in range(3): add(fx, tone(mid(93), .08, 40, (1,)), qa - 1.6 + s_ * .5, .22)
    for q, m in enumerate([72, 76, 79, 84]): add(fx, tone(mid(m), .8, 4), qa + q * .08, .16)
for q, m in enumerate([72, 76, 79, 84, 79, 84]): add(fx, tone(mid(m), 1.0, 3), CELEB + .1 + q * .12, .18)
mix = np.tanh((vo + mus + fx) * 1.05) * .9
with wave.open(f"{S}/animals.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())

# ---------------- graphics ----------------
def clamp(x): return max(0.0, min(1.0, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x): x = clamp(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def paste(fr, img, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if scale <= 0.02 or alpha <= 0.01: return
    if abs(scale - 1) > .005: img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if rot: img = img.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 1: a = img.split()[3].point(lambda v: int(v * alpha)); img = img.copy(); img.putalpha(a)
    fr.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))
def text_img(txt, font, fill, stroke=0, sfill=(255, 255, 255)):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); b = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 20, b[3] - b[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - b[0], 10 - b[1]), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill); return im
def blob(col, s=230, label=None):
    im = Image.new("RGBA", (s, s + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((4, 14, s - 4, s + 6), fill=tuple(int(c * .7) for c in col)); d.ellipse((4, 4, s - 4, s - 4), fill=col)
    d.ellipse((4, 4, s - 4, s - 4), outline=(255, 255, 255), width=8)
    d.ellipse((s * .22, s * .18, s * .42, s * .34), fill=(255, 255, 255, 110))
    if label:
        t = text_img(label, F(BLACK, 150), (255, 255, 255)); im.alpha_composite(t, ((s - t.width) // 2, (s - t.height) // 2))
    return im
def rainbow_blob(s=230):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cols = [(229, 57, 53), (251, 140, 0), (253, 216, 53), (67, 160, 71), (66, 165, 245), (57, 73, 171), (142, 36, 170)]
    for i, c in enumerate(cols): d.pieslice((4, 4, s - 4, s - 4), i * 360 / 7 - 90, (i + 1) * 360 / 7 - 90, fill=c)
    d.ellipse((4, 4, s - 4, s - 4), outline=(255, 255, 255), width=8); return im
QB = blob((255, 193, 7), label="?")
def label(txt, col):
    t = text_img(txt, F(BLACK, 78), (255, 255, 255)); w, h = t.width + 70, t.height + 40
    im = Image.new("RGBA", (w, h + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 10, w, h + 10), 40, fill=tuple(int(c * .7) for c in col)); d.rounded_rectangle((0, 0, w, h), 40, fill=col)
    d.rounded_rectangle((0, 0, w, h), 40, outline=(255, 255, 255), width=7); im.alpha_composite(t, (35, 20)); return im
def bubble(txt):
    t = text_img(txt, F(BLACK, 96), DARK); w, h = t.width + 90, t.height + 60
    im = Image.new("RGBA", (w, h + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, w, h), fill=(255, 255, 255, 240), outline=DARK, width=6)
    d.polygon([(w * .62, h - 14), (w * .8, h + 55), (w * .45, h - 6)], fill=(255, 255, 255, 240)); d.line([(w * .62, h - 8), (w * .8, h + 55), (w * .47, h - 2)], fill=DARK, width=6)
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2)); return im
LAB = [label(a[0], a[1]) for a in ANI]
BUB = {a[2]: bubble(a[2]) for a in ANI}
def banner(a, b, w=1100):
    im = Image.new("RGBA", (w, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 8, w, 230), 50, fill=(150, 90, 40, 120)); d.rounded_rectangle((0, 0, w, 220), 50, fill=(255, 248, 235, 245))
    ta = text_img(a, F(BLACK, 82), (229, 57, 53)); tb = text_img(b, F(BOLD, 50), DARK)
    im.alpha_composite(ta, ((w - ta.width) // 2, 22)); im.alpha_composite(tb, ((w - tb.width) // 2, 130)); return im
INTRO_B = banner("Уроки с Луней", "Животные и их голоса")
OUT_A = text_img("Ура! Молодцы!", F(BLACK, 120), (229, 57, 53), 8); OUT_B = text_img("До завтра!", F(BLACK, 90), (66, 165, 245), 8)
random.seed(9)
CONF = [(random.uniform(0, W), random.uniform(-700, 0), random.choice([(229,57,53),(251,140,0),(253,216,53),(67,160,71),(66,165,245)]), random.uniform(220, 420), random.uniform(0, 6.28)) for _ in range(140)]
BX, BY = W - 210, 200

def overlay(fr, t):
    for j, (name, col, snd, si) in enumerate(ANI):
        t0, t1 = B[si], B[si + 1]
        if t0 + 0.4 <= t < t1:
            a = ease((t1 - t) / .3); paste(fr, LAB[j], W - 60 - LAB[j].width / 2, 130, back((t - t0 - 0.4) / .4), a)
        if SOUND_T[j] <= t < t1:
            a = ease((t1 - t) / .3); paste(fr, BUB[snd], 330, 210, back((t - SOUND_T[j]) / .35) * (1 + .04 * math.sin(t * 9)), a, -5)
    for q0, qa, snd, ai in QUIZ:
        if q0 <= t < qa:
            paste(fr, QB, W - 210, 200, back((t - q0) / .4) * (1 + .06 * math.sin(t * 7)))
            paste(fr, BUB[snd], 330, 210, back((t - q0 - 0.8) / .35), 1, -5)
        elif qa <= t < qa + 3.0:
            a = ease((qa + 3.0 - t) / .3); L_ = LAB[ai]; paste(fr, L_, W - 60 - L_.width / 2, 130, back((t - qa) / .4), a)

def seg_reader(path, ss, dur, interp):
    vf = (f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1," if interp else f"fps={FPS},") + f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
    return subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-ss", str(ss), "-i", path, "-t", str(dur + 0.3), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)

def render():
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{S}/animals.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    cur = -1; rd = None; last = None
    for f in range(NF):
        t = f / FPS
        si = max(i for i in range(len(SEGS)) if BOUND[i] <= t + 1e-9)
        if si != cur:
            if rd: rd.stdout.close(); rd.kill()
            rd = seg_reader(*SEGS[si]); cur = si
        buf = rd.stdout.read(W * H * 3)
        if len(buf) == W * H * 3: last = Image.frombytes("RGB", (W, H), buf)
        fr = last.convert("RGBA")
        if t < 10:
            ba = ease((t - 5.0) / .6) * ease((9.6 - t) / .4); paste(fr, INTRO_B, W / 2, 900 + 60 * (1 - ba), 1, ba)
        overlay(fr, t)
        if t >= CELEB:
            lt = t - CELEB; d = ImageDraw.Draw(fr)
            if t < B[10] + 1.0:
                for x, y, c, sp, ph in CONF:
                    yy = y + sp * lt
                    if -20 < yy < H + 20:
                        xx = x + 40 * math.sin(lt * 3 + ph); w_ = 10 + 6 * math.sin(lt * 8 + ph)
                        d.rectangle((xx - w_, yy - 7, xx + w_, yy + 7), fill=c)
            if t < B[10]: paste(fr, OUT_A, W / 2, 150, back((lt - .2) / .5), 1, -4)
            else: paste(fr, OUT_B, W / 2, 150, back((t - B[10] - .2) / .5), 1, 4)
        for bnd in BOUND[1:-1]:
            d_ = abs(t - bnd)
            if d_ < .2: fr = Image.alpha_composite(fr, Image.new("RGBA", (W, H), (255, 255, 255, int(170 * (1 - d_ / .2)))))
        fa = ease((t - (TOTAL - .8)) / .8)
        if fa > 0: fr = Image.alpha_composite(fr, Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fa))))
        enc.stdin.write(fr.convert("RGB").tobytes())
    if rd: rd.stdout.close(); rd.kill()
    enc.stdin.close(); enc.wait()

render(); print("done", OUT)
