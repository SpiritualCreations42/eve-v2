# Software Setup

Read from the running system on 2026-10-30. The machine was running from bench-test drives at the time, not its final boot and data drives, so OS-level details (versions, installed services) may differ once the final drives are back in.

| Item | Value |
|------|-------|
| OS | Ubuntu 26.04.1 LTS |
| Kernel | 7.0.0-42-generic |
| BIOS | HP R22 Ver. 02.26.00 (2026-05-05) |
| NVIDIA driver | 580.178.04 (proprietary, installed from the Ubuntu repos) |
| CUDA (driver) | 13.0 |
| Tesla P4 VBIOS | 86.04.8C.00.10 |
| Docker | 29.9.2, Compose v5.6.1 |
| NVIDIA Container Toolkit | 1.20.1 (`nvidia` runtime registered) |

## Verify both GPUs

```bash
nvidia-smi -L
docker run --rm --gpus all nvidia/cuda:12.6.3-base-ubuntu24.04 nvidia-smi -L
```

Both cards show up as `Tesla P4`, 7680 MiB each, power limit 75 W.

## Services running in Docker

| Service | Purpose |
|---------|---------|
| Ollama | Local LLM inference |
| Open WebUI | Chat front end for Ollama |
| Meshroom | GPU photogrammetry |
| nvidia_gpu_exporter, node_exporter | Prometheus metrics for GPU and host |

Everything is managed with Docker Compose.

## Notes

- The Tesla P4 has no artificial NVENC concurrent-session cap, unlike GeForce cards, so no encoder patch is needed for transcoding.
- Pascal (compute capability 6.1) is supported by the current 580-series driver branch.

*To be filled in:* compose files for the services above, and which GPU each service uses.
