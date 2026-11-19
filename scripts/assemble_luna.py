import subprocess, wave, math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = "/tmp/claude-0/-home-user/96502a5f-267a-5e70-abdd-8e11d247afa6/scratchpad"
SC = "/home/user/sovushka/ep01/scenes"
CLIP = "/root/.claude/uploads/96502a5f-267a-5e70-abdd-8e11d247afa6/b18f151f-2026-11-18_105405.mp4"
OUT = "/home/user/sovushka/lunya_schitaem_yabloki.mp4"
W, H, FPS, SR = 1920, 1080, 24, 44100
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"; BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F = lambda p, s: ImageFont.truetype(p, s)
COLS = [(239, 83, 80), (255, 167, 38), (102, 187, 106), (66, 165, 245), (171, 71, 188)]
DARK = (74, 52, 46); WORDS = ["ОДИН", "ДВА", "ТРИ", "ЧЕТЫРЕ", "ПЯТЬ"]
DUR = {int(k): v for k, v in json.load(open(f"{S}/vo_luna/dur.json")).items()}

# ---------------- timeline ----------------
U = "/root/.claude/uploads/96502a5f-267a-5e70-abdd-8e11d247afa6/"
VO = []
def say(i, t): VO.append((i, t)); return t + DUR[i]
SEGS = [(U+"b62a5833-2026-11-18_203513.mp4", 0, 10.0, False),
        (U+"09e865a2-2026-11-18_203524.mp4", 0, 10.0, False),
        (SC+"/w2.mp4", 0, 5.0, True),
        (SC+"/w3.mp4", 0, 5.0, True),
        (U+"21e9a24f-2026-11-18_203517.mp4", 4.5, 5.5, False),
        (SC+"/w1.mp4", 0, 5.0, True),
        (U+"ce3354b7-2026-11-18_203535.mp4", 0, 10.0, False),
        (SC+"/w6.mp4", 0, 3.5, True),
        (U+"21e9a24f-2026-11-18_203517.mp4", 0, 4.4, False)]
BOUND = [0]
for sg in SEGS: BOUND.append(BOUND[-1] + sg[2])
TOTAL = BOUND[-1]; NF = int(TOTAL * FPS)
say(1, 0.8); say(2, 5.2); say(4, 10.4)
APPLE_LAND = [14.0 + k * 2.2 for k in range(5)]
for k in range(5): say(5 + k, APPLE_LAND[k] + 0.05)
e = say(10, 23.8)
CLEAR_T = e + 0.2; Q1_POP = CLEAR_T + 0.4
e = say(11, Q1_POP + 0.6); Q1_ANS = e + 3.0
e = say(12, Q1_ANS); Q2_SWAP = e + 0.4
e = say(13, Q2_SWAP + 0.6); Q2_ANS = e + 3.0
e = say(14, Q2_ANS); F0 = e + 0.4
say(15, F0 + 0.2)
G0 = BOUND[7]; say(16, G0 + 0.5)
TOG = [1e9] * 5; D0 = 23.8; C0 = 10.0
print("total", round(TOTAL, 1), "F0", round(F0, 1), "G0", round(G0, 1))

# ---------------- clips ----------------
def seg_reader(path, ss, dur, interp):
    vf = (f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1," if interp else f"fps={FPS},") + f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}"
    return subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-ss", str(ss), "-i", path, "-t", str(dur + 0.3), "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)

# ---------------- audio ----------------
def load(i):
    with wave.open(f"{S}/vo_luna/l{i}.wav") as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
def tone(f, dur, decay=4.0, harm=(1, .5, .25, .12)):
    t = np.arange(int(dur * SR)) / SR
    return sum(a * np.sin(2 * np.pi * f * (i + 1) * t) * np.exp(-t * decay * (1 + i * .8)) for i, a in enumerate(harm))
def mid(m): return 440 * 2 ** ((m - 69) / 12)
def add(buf, x, t0, g=1.0):
    i = int(t0 * SR); e_ = min(len(buf), i + len(x))
    if e_ > i: buf[i:e_] += x[:e_ - i] * g
def sweep(f0, f1, dur, g=1):
    t = np.arange(int(dur * SR)) / SR; f = f0 + (f1 - f0) * t / dur
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * g
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
for k in range(5):
    add(fx, sweep(1400, 500, .5, .10), APPLE_LAND[k] - .55); add(fx, sweep(260, 120, .25, .45), APPLE_LAND[k])
    for j, m in enumerate([76, 79, 84]): add(fx, tone(mid(m + k), .5, 6), APPLE_LAND[k] + .05 + j * .05, .10)
add(fx, sweep(400, 1600, .6, .15), CLEAR_T)
for q0, qa in [(Q1_POP, Q1_ANS), (Q2_SWAP, Q2_ANS)]:
    for j in range(4): add(fx, tone(mid(84), .12, 30, (1,)), q0 + j * .12, .15)
    for s in range(3): add(fx, tone(mid(93), .08, 40, (1,)), qa - 3 + s + .3, .25)
    for j, m in enumerate([72, 76, 79, 84]): add(fx, tone(mid(m), .8, 4), qa + j * .08, .16)
for j, m in enumerate([72, 76, 79, 84, 79, 84]): add(fx, tone(mid(m), 1.0, 3), F0 + .1 + j * .12, .18)
raw = b""
ca = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
ca = np.zeros(0)
mix = vo + mus + fx; mix[:len(ca)] += ca; mix = np.tanh(mix * 1.05) * .9
with wave.open(f"{S}/anim.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())

# ---------------- graphics ----------------
def clamp(x): return max(0.0, min(1.0, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x): x = clamp(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def paste(fr, img, cx, cy, scale=1.0, alpha=1.0, rot=0.0, anchor="c"):
    if scale <= 0.02 or alpha <= 0.01: return
    if abs(scale - 1) > .005: img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if rot: img = img.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 1: a = img.split()[3].point(lambda v: int(v * alpha)); img = img.copy(); img.putalpha(a)
    y = cy - img.height / 2 if anchor == "c" else cy - img.height
    fr.alpha_composite(img, (int(cx - img.width / 2), int(y)))
def text_img(txt, font, fill, stroke=0, sfill=(255, 255, 255)):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); b = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 20, b[3] - b[1] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - b[0], 10 - b[1]), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill); return im
def badge(txt, col, s=230):
    im = Image.new("RGBA", (s, s + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((4, 14, s - 4, s + 6), fill=tuple(int(c * .7) for c in col)); d.ellipse((4, 4, s - 4, s - 4), fill=col)
    d.ellipse((4, 4, s - 4, s - 4), outline=(255, 255, 255), width=8)
    t = text_img(txt, F(BLACK, 160), (255, 255, 255)); im.alpha_composite(t, ((s - t.width) // 2, (s - t.height) // 2)); return im
def make_apple(sz=150):
    k = 4; s = sz * k; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((s*.12, s*.28, s*.56, s*.95), fill=(200, 40, 42)); d.ellipse((s*.44, s*.28, s*.88, s*.95), fill=(200, 40, 42))
    d.ellipse((s*.2, s*.32, s*.8, s*.93), fill=(229, 57, 53)); d.ellipse((s*.25, s*.40, s*.39, s*.60), fill=(255, 255, 255, 160))
    d.rounded_rectangle((s*.47, s*.10, s*.53, s*.36), s*.03, fill=(109, 76, 65)); d.ellipse((s*.52, s*.12, s*.82, s*.28), fill=(76, 175, 80))
    return im.resize((sz, sz), Image.LANCZOS)
APPLE = make_apple()
PANEL = Image.new("RGBA", (1240, 230), (0, 0, 0, 0)); ImageDraw.Draw(PANEL).rounded_rectangle((0, 0, 1240, 230), 60, fill=(255, 248, 235, 215))
BADGES = [badge(str(i + 1), COLS[i]) for i in range(5)]; QBADGE = badge("?", (255, 193, 7))
WORD = [text_img(WORDS[i], F(BLACK, 72), COLS[i], 7) for i in range(5)]
NUMS = [text_img(str(i + 1), F(BLACK, 46), DARK, 5) for i in range(5)]
def banner(a, b, w=1100):
    im = Image.new("RGBA", (w, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 8, w, 230), 50, fill=(150, 90, 40, 120)); d.rounded_rectangle((0, 0, w, 220), 50, fill=(255, 248, 235, 245))
    ta = text_img(a, F(BLACK, 82), (229, 57, 53)); tb = text_img(b, F(BOLD, 50), DARK)
    im.alpha_composite(ta, ((w - ta.width) // 2, 22)); im.alpha_composite(tb, ((w - tb.width) // 2, 130)); return im
INTRO_B = banner("Уроки с Луней", "Считаем яблоки")
OUT_A = text_img("Ура! Молодцы!", F(BLACK, 120), (229, 57, 53), 8); OUT_B = text_img("До завтра!", F(BLACK, 90), (66, 165, 245), 8)
random.seed(9)
CONF = [(random.uniform(0, W), random.uniform(-700, 0), random.choice(COLS + [(255, 214, 0)]), random.uniform(220, 420), random.uniform(0, 6.28)) for _ in range(140)]
PX = W / 2; PY = 950; GROUND = PY + 60
ROW = [PX - 440 + k * 220 for k in range(5)]
Q1_X = ROW[1:4]; Q2_X = [r + 110 for r in ROW[:4]]
def fall_y(t, land):
    if t >= land:
        d = t - land
        if d < .28: return -abs(math.sin(d / .28 * math.pi)) * 50
        if d < .44: return -abs(math.sin((d - .28) / .16 * math.pi)) * 15
        return 0
    p = (t - (land - .6)) / .6; return -(1 - p * p) * 1000

def overlay(fr, t):
    show_panel = APPLE_LAND[0] - .9 <= t < F0 - .2
    if show_panel:
        pa = ease((t - (APPLE_LAND[0] - .9)) / .4) * ease((F0 - .2 - t) / .4)
        paste(fr, PANEL, PX, PY, 1, pa)
    apples = []
    if C0 <= t < CLEAR_T + .8:
        fly = clamp((t - CLEAR_T) / .7)
        for k in range(5):
            land = APPLE_LAND[k]
            if t < land - .6: continue
            y = fall_y(t, land) - fly * 1300; jump = 0; sc = 1
            d = t - TOG[k]
            if 0 <= d < .45: jump = math.sin(d / .45 * math.pi) * 60; sc = 1 + .15 * math.sin(d / .45 * math.pi)
            apples.append((ROW[k], y - jump, sc, k if t >= land and fly == 0 else None))
    elif CLEAR_T + .8 <= t < Q2_SWAP:
        for j, x in enumerate(Q1_X):
            p = t - (Q1_POP + j * .12)
            if p >= 0: apples.append((x, 0, back(p / .35), j if t >= Q1_ANS + j * .25 else None))
    elif Q2_SWAP <= t < F0:
        out = clamp((t - (F0 - .5)) / .3)
        for j, x in enumerate(Q2_X):
            p = t - (Q2_SWAP + j * .12)
            if p >= 0: apples.append((x, 0, back(p / .35) * (1 - out), j if t >= Q2_ANS + j * .25 else None))
    for x, y, sc, lab in apples:
        paste(fr, APPLE, x, GROUND - 25 + y, sc, 1, anchor="b")
        if lab is not None: paste(fr, NUMS[lab], x, GROUND - 5)
    cnt = None; q = False; lt = 0
    if APPLE_LAND[0] <= t < D0: cnt = max(k for k in range(5) if t >= APPLE_LAND[k]); lt = t - APPLE_LAND[cnt]
    elif TOG[0] <= t < CLEAR_T: cnt = max(j for j in range(5) if t >= TOG[j]); lt = t - TOG[cnt]
    elif Q1_POP + .5 <= t < Q1_ANS or Q2_SWAP + .5 <= t < Q2_ANS: q = True
    elif Q1_ANS <= t < Q2_SWAP: cnt = 2; lt = t - Q1_ANS
    elif Q2_ANS <= t < F0 - .2: cnt = 3; lt = t - Q2_ANS
    BX = 210 if BOUND[6] <= t < BOUND[7] else W - 210
    if cnt is not None:
        paste(fr, BADGES[cnt], BX, 190, back(lt / .4))
        paste(fr, WORD[cnt], BX, 370, 1, ease((lt - .2) / .3))
    if q: paste(fr, QBADGE, BX, 200, 1 + .08 * math.sin(t * 7))

def render():
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", f"{S}/anim.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
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
            ba = ease((t - 6.0) / .6) * ease((9.6 - t) / .4); paste(fr, INTRO_B, W / 2, 900 + 60 * (1 - ba), 1, ba)
        overlay(fr, t)
        if F0 <= t < G0 + 1.0:
            lt = t - F0; d = ImageDraw.Draw(fr)
            for x, y, c, sp, ph in CONF:
                yy = y + sp * lt
                if -20 < yy < H + 20:
                    xx = x + 40 * math.sin(lt * 3 + ph); w_ = 10 + 6 * math.sin(lt * 8 + ph)
                    d.rectangle((xx - w_, yy - 7, xx + w_, yy + 7), fill=c)
            if t < G0: paste(fr, OUT_A, W / 2, 150, back((lt - .2) / .5), 1, -4)
        if t >= G0: paste(fr, OUT_B, W / 2, 150, back((t - G0 - .4) / .5), 1, 4)
        for bnd in BOUND[1:-1]:
            d_ = abs(t - bnd)
            if d_ < .2: fr = Image.alpha_composite(fr, Image.new("RGBA", (W, H), (255, 255, 255, int(170 * (1 - d_ / .2)))))
        fa = ease((t - (TOTAL - .8)) / .8)
        if fa > 0: fr = Image.alpha_composite(fr, Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fa))))
        enc.stdin.write(fr.convert("RGB").tobytes())
        if f % 240 == 0: print("frame", f, "/", NF, flush=True)
    if rd: rd.stdout.close(); rd.kill()
    enc.stdin.close(); enc.wait()
render(); print("done", OUT)
