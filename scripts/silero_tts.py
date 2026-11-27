import json, base64, urllib.request, subprocess, sys, os, time
BASE = "https://neurosenko-tts-silero.hf.space/run/predict"
def req(fn, data):
    r = urllib.request.Request(BASE, data=json.dumps({"fn_index": fn, "data": data}).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=180).read())
POLISH = "highpass=f=90,equalizer=f=3200:t=q:w=1.2:g=2,acompressor=threshold=-18dB:ratio=2.5:attack=5:release=80"
def make(lines, outdir):
    os.makedirs(outdir, exist_ok=True)
    req(0, ['ru']); req(1, ['ru', 'v5_6_ru'])
    dur = {}
    for i, t in lines.items():
        for attempt in range(3):
            try:
                out = req(2, [t, 'text', 'kseniya'])['data'][0]
                raw = f"{outdir}/raw{i}.wav"
                if isinstance(out, dict) and out.get('data'):
                    open(raw, "wb").write(base64.b64decode(out['data'].split(',', 1)[1]))
                else:
                    urllib.request.urlretrieve("https://neurosenko-tts-silero.hf.space/file=" + out['name'], raw)
                break
            except Exception as e:
                print("retry", i, str(e)[:80]); time.sleep(3)
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", raw, "-af",
                        "silenceremove=start_periods=1:start_threshold=-55dB,areverse,silenceremove=start_periods=1:start_threshold=-55dB,areverse," + POLISH + ",apad=pad_dur=0.08",
                        "-ar", "44100", "-ac", "1", f"{outdir}/l{i}.wav"], check=True)
        dur[i] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{outdir}/l{i}.wav"], capture_output=True, text=True).stdout)
        print(os.path.basename(outdir), i, round(dur[i], 2), t, flush=True)
    json.dump(dur, open(f"{outdir}/dur.json", "w"))
