# GPU isolation test

Scripts used to separate "the hardware link is bad" from "something in the software workload triggers it". See [Troubleshooting](../../docs/troubleshooting.md) for what the results meant.

| File | What it does |
|------|--------------|
| `run_gpu_test.sh` | Runs the whole sequence, logs `nvidia-smi` once a second (power, clocks, PCIe link, throttle reasons), and stops at the first Xid error or non-zero exit. Pass `long` to add a 40 minute mixed phase on both GPUs. Logs go to `~/gputest-logs/`. |
| `gpu_load.py` | The load generator (PyTorch). Phases: `soak`, `steps` (square-wave load at 10 / 2 / 0.5 / 0.1 s periods), `ramp`, `pcie` (pinned host-to-device and back copies), `p2p` (GPU to GPU), `mixed` (compute plus a second-stream copy). |
| `docker-compose.yml` | Runs `gpu_load.py` in the same container image as ComfyUI, reusing its PyTorch install read-only, so the CUDA stack matches the real workload. |
| `comfyui_flux_job.py` | Queues one Flux GGUF image through a running ComfyUI and logs both GPUs once a second. `DONOR=cuda:1` (default in the original run) or `DONOR=cpu` picks where the DisTorch2 offload streams weights from. `COMFY_API` sets the ComfyUI address. |

## Run it

```bash
mkdir -p ~/gputest && cp * ~/gputest/ && cd ~/gputest
./run_gpu_test.sh                     # stops the ComfyUI container first, ~40 min
cat ~/gputest-logs/latest/summary.txt
```

The compose file expects the ComfyUI install at `~/comfyui/mnt` (its virtual environment holds the PyTorch build). Run the Flux job with ComfyUI up:

```bash
COMFY_API=http://127.0.0.1:8188 DONOR=cpu python3 comfyui_flux_job.py
```
