import os, shutil, time, sys, json
from gradio_client import Client, handle_file
S="/tmp/claude-0/-home-user/96502a5f-267a-5e70-abdd-8e11d247afa6/scratchpad"
OUT="/home/user/sovushka/ep01/scenes"
tok=open(f"{S}/.hf_token").read().strip()
JOBS=[
 ("w1","f_9.5","The cute fluffy owl with a red knitted scarf smiles and talks happily to the camera, opening and closing its beak, blinking, then waves one wing hello. Pixar 3D animation, smooth natural motion."),
 ("w2","f_0.5","The cute owl with a red scarf in the tree hollow excitedly bounces and claps its wings, looking around happily, raindrops dripping from the leaves. Pixar 3D animation, smooth motion."),
 ("w3","f_8","The cute owl with a red scarf tilts its head curiously, looks up thoughtfully as if counting, nods several times, then smiles widely. Pixar 3D animation, smooth motion."),
 ("w4","f_2.5","The cute owl with a red scarf does a happy little dance in the tree hollow, wiggling its body and flapping its wings joyfully. Pixar 3D animation, smooth motion."),
 ("w5","f_9.5","The cute owl with a red scarf claps its wings and cheers excitedly, big happy smile, eyes sparkling, bouncing a little. Pixar 3D animation, smooth motion."),
 ("w6","f_4.5","The cute owl with a red scarf waves goodbye with its wing, then yawns sleepily, closes its eyes and snuggles into its scarf. Pixar 3D animation, smooth motion."),
]
cl=Client('zerogpu-aoti/wan2-2-fp8da-aoti-faster', token=tok, verbose=False)
for name, fr, prompt in JOBS:
    dst=f"{OUT}/{name}.mp4"
    if os.path.exists(dst): print(name,"exists",flush=True); continue
    for attempt in range(2):
        t=time.time()
        try:
            r=cl.predict(handle_file(f"{S}/frames/{fr}.png"), prompt, 6, api_name='/generate_video', duration_seconds=5.0)
            v=r[0]['video'] if isinstance(r[0],dict) else r[0]
            shutil.copy(v,dst); print(name,"OK",round(time.time()-t),flush=True); break
        except Exception as e:
            msg=getattr(e,'message',None) or repr(e)[:300]
            print(name,"ERR",round(time.time()-t),msg,flush=True)
            if "quota" in msg.lower() or "limit" in msg.lower(): sys.exit(3)
print("ALLDONE",flush=True)
