#!/usr/bin/env python3
"""ComfyUI GPU stress test for EvE (2x Tesla P4). Queues Flux GGUF (DisTorch2 across both GPUs)
then SDXL batches, while logging nvidia-smi + dmesg. Output: /tmp/stress/{gpu.csv,summary.txt,dmesg_*.txt}"""
import json, os, subprocess, time, urllib.request, random, threading

API = os.environ.get("COMFY_API", "http://127.0.0.1:8188")
OUT = os.path.expanduser(os.environ.get("OUT_DIR", "~/gputest-logs/flux-job"))
os.makedirs(OUT, exist_ok=True)

def post(path, data):
    req = urllib.request.Request(API + path, json.dumps(data).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def get(path):
    return json.load(urllib.request.urlopen(API + path, timeout=30))

def flux(seed, prefix):
    return {
        "1": {"class_type": "UnetLoaderGGUFDisTorch2MultiGPU", "inputs": {"unet_name": "flux1-dev-Q4_K_S.gguf", "compute_device": "cuda:0", "virtual_vram_gb": 5.5, "donor_device": os.environ.get("DONOR", "cpu"), "expert_mode_allocations": "", "eject_models": True}},
        "2": {"class_type": "DualCLIPLoaderGGUFMultiGPU", "inputs": {"clip_name1": "clip_l.safetensors", "clip_name2": "t5-v1_1-xxl-encoder-Q4_K_M.gguf", "type": "flux", "device": "cuda:0"}},
        "3": {"class_type": "VAELoaderMultiGPU", "inputs": {"vae_name": "ae.safetensors", "device": "cuda:0"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": "isometric pixel art quadruped robot, tactics RPG sprite, detailed, clean outlines", "clip": ["2", 0]}},
        "5": {"class_type": "FluxGuidance", "inputs": {"conditioning": ["4", 0], "guidance": 3.5}},
        "6": {"class_type": "BasicGuider", "inputs": {"model": ["1", 0], "conditioning": ["5", 0]}},
        "7": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "8": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "9": {"class_type": "BasicScheduler", "inputs": {"model": ["1", 0], "scheduler": "simple", "steps": 20, "denoise": 1.0}},
        "10": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "11": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["7", 0], "guider": ["6", 0], "sampler": ["8", 0], "sigmas": ["9", 0], "latent_image": ["10", 0]}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["3", 0]}},
        "13": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": prefix}},
    }

def sdxl(seed, prefix):
    return {
        "1": {"class_type": "CheckpointLoaderSimpleMultiGPU", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors", "device": "cuda:1"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "isometric pixel art robot sprite, game asset", "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "blurry, photo, text", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 2}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "seed": seed, "steps": 30, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0], "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": prefix}},
    }

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True).stdout

def dmesg(tag):
    open(f"{OUT}/dmesg_{tag}.txt", "w").write(sh("sudo -n dmesg 2>&1 | grep -iE 'xid|nvrm|pcie.*(error|aer)|fallen off|nvidia.*(timeout|reset)' | tail -50"))

stop = False
def logger():
    q = "timestamp,index,temperature.gpu,power.draw,utilization.gpu,memory.used,clocks.sm,pcie.link.gen.current,pcie.link.width.current,clocks_throttle_reasons.active"
    with open(f"{OUT}/gpu.csv", "w") as f:
        while not stop:
            f.write(sh(f"nvidia-smi --query-gpu={q} --format=csv,noheader 2>&1"))
            f.flush()
            time.sleep(1)

dmesg("before")
t = threading.Thread(target=logger, daemon=True); t.start()
jobs = []
for i in range(1): jobs.append(("flux", post("/prompt", {"prompt": flux(random.randint(1, 2**31), f"stress/flux_{i}")})["prompt_id"]))
for i in range(0): jobs.append(("sdxl", post("/prompt", {"prompt": sdxl(random.randint(1, 2**31), f"stress/sdxl_{i}")})["prompt_id"]))
start = time.time()
res = {}
deadline = start + 60 * 60
while len(res) < len(jobs) and time.time() < deadline:
    for kind, pid in jobs:
        if pid in res: continue
        h = get(f"/history/{pid}")
        if pid in h:
            s = h[pid]["status"]
            res[pid] = (kind, s.get("status_str"), round(time.time() - start))
    time.sleep(10)
stop = True; time.sleep(6)
dmesg("after")

rows = [l.split(", ") for l in open(f"{OUT}/gpu.csv") if l.count(",") >= 9]
summ = []
for idx in ("0", "1"):
    r = [x for x in rows if x[1] == idx]
    if not r: summ.append(f"GPU{idx}: NO SAMPLES (GPU missing from nvidia-smi?)"); continue
    num = lambda k: [float(x[k].split()[0]) for x in r if x[k].split()[0].replace('.', '').isdigit()]
    summ.append(f"GPU{idx}: samples={len(r)} maxTemp={max(num(2))}C maxPower={max(num(3))}W maxUtil={max(num(4))}% maxMem={max(num(5))}MiB minSMclk={min(num(6))} minPCIe=gen{min(num(7)):.0f} x{min(num(8)):.0f}")
last = sh("nvidia-smi --query-gpu=index,name,temperature.gpu --format=csv,noheader")
with open(f"{OUT}/summary.txt", "w") as f:
    f.write(f"elapsed_s={round(time.time()-start)} jobs_done={len(res)}/{len(jobs)}\n")
    for pid, v in res.items(): f.write(f"{v[0]} {v[1]} finished_at={v[2]}s\n")
    f.write("\n".join(summ) + "\nGPUs at end:\n" + last)
    f.write("\ndmesg_before:\n" + open(f"{OUT}/dmesg_before.txt").read() + "\ndmesg_after:\n" + open(f"{OUT}/dmesg_after.txt").read() + "\nDONE\n")
