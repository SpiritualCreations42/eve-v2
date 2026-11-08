# Troubleshooting

Problems met on this build, what was tried, and what is still open. Newest findings first within each section. Times are UTC, with local time (CST, UTC−6) in brackets where it helps.

## GPU 0 falls off the PCIe bus under load (open)

**Status, 2026-11-08: not fixed.** GPU 0 has dropped seven times on the current Ubuntu 26.04 install (the last one with no USB devices attached). GPU 1 has never dropped.

### Symptom

Always the same sequence in `dmesg`:

```
pcieport 0000:00:1b.0: AER: Correctable error message received from 0000:00:1b.0
NVRM: Xid (PCI:0000:01:00): 79, GPU has fallen off the bus.
NVRM: Xid (PCI:0000:01:00): 154, GPU recovery action changed from 0x0 (None) to 0x1 (GPU Reset Required)
```

- The first line is a **physical-layer receive error (`RxErr`)** on root port `00:1b.0`, the port GPU 0 sits behind. It is a *correctable* error, so the link did not report a hard fault before the card vanished.
- `nvidia-smi` then prints `Unable to determine the device handle for GPU0`, and only GPU 1 is listed.
- The root port retrains at 2.5 GT/s afterwards (it should be 8 GT/s) and `lspci` shows the card's config space as dead.
- The machine itself keeps running. Containers using GPU 0 hang, and a normal reboot or shutdown can stall waiting on the stuck process (in one case the machine eventually shut itself down). A **full power cycle** is needed to bring GPU 0 back. Reloading the driver does not help.

### Timeline

| # | When (UTC) | Workload | What GPU 0 was doing just before |
|---|-----------|----------|----------------------------------|
| 1 | 2026-11-04, about 4.5 h after boot | ComfyUI loading Flux GGUF (DisTorch2) onto GPU 0 | Model load |
| 2 | 2026-11-04 15:48:41 (09:48) | ComfyUI stress run, after finishing the first Flux image | Jumped from 49 W to 76.8 W, fault about 5 s later |
| 3 | 2026-11-07 03:36:30 (11-06 21:36) | ComfyUI stress run, about 24 min in (2 Flux + 3 SDXL jobs queued) | Steady 48 W, 54 °C, at a job change (26 W, 1 % util, memory dropping) |
| 4 | 2026-11-07 05:35:47 (23:35) | One Flux GGUF job, GPU 1 as weight donor, about 4.5 min in | Steady 48 W, 100 % util, 52 °C |
| 5 | 2026-11-07 06:12:49 (00:12) | One Flux GGUF job, **system RAM** as weight donor, about 6 min in | Steady 48 W, 100 % util, 53 °C |
| 6 | 2026-11-07, about 42 min into the same stress run (2 Flux + 3 SDXL), USB drives attached | ComfyUI stress run | Not recorded in detail |
| 7 | 2026-11-08 04:15:55 (11-07 22:15 CST) | One SDXL + IPAdapter + Canny ControlNet job through the ComfyUI API, about 1 min after queueing, **no USB devices attached** | Cold model load, then sampling; AER `RxErr` on `00:1b.0` at 04:15:55, Xid 79 one second later |

Per-second logs for drops 4 and 5 (75 s before the fault to 3 s after) are in [`data/`](data/). In both runs GPU 0 sat at about 48 W with irregular one-second jumps to 70–81 W (the software power cap throttle bit, `0x4`): 10 of them before drop 4 and 14 before drop 5. The fault came 12 s after the last spike in drop 4 and 3 s after the last one in drop 5, but the earlier spikes caused nothing, so the spikes are not a reliable trigger.

### What has been ruled out

| Suspect | Evidence |
|---------|----------|
| Power ceiling on GPU 0 | GPU 0 reached 70–81 W many times without a fault, and drops 3, 4 and 5 happened at a steady 48 W. |
| Fan hub sharing a Pico PSU | The fan hub originally drew from a Pico PSU, which shut itself off under combined load. It now runs from its own 12 V / 5 V supply (a buck-converter board with INA228 metering), and the Pico PSU no longer shuts off. GPU 0 still dropped three times afterwards (drops 3 to 5). |
| GPU 1 to GPU 0 weight streaming (DisTorch2 donor) | Drop 5 used system RAM as the donor and GPU 1 stayed idle. It still dropped. |
| Compute, PCIe copies, GPU to GPU, or load steps in general | A standalone PyTorch test (below) passed every phase on both GPUs. |
| **Cables, docks, redrivers** | **Not the cables.** New docks, new cables and new OCuLink with redrivers are fitted, and they have already been swapped between ports. Do not suggest swapping them again. |
| Temperature | 52–54 °C at every drop. |
| ASPM power saving | `lspci -vv` shows ASPM disabled on both root ports and on GPU 1 (GPU 0 was down when checked). |
| BAR / resource allocation at boot | No "can't assign" or "failed to assign" messages in `dmesg`. BAR1 is 256 MB and BAR3 32 MB on GPU 1 (GPU 0 was down when checked), and the root-port windows cover them. Kernel command line includes `pci=realloc`. |
| Boot drive / storage | SMART clean, filesystem clean. Not related. |
| VRAM exhaustion and fp16 / precision | About 2.5 GB of 8 GB in use at the drops. ComfyUI already loads bf16 weights with a manual cast to fp32 and an fp32 VAE on this card, so the "Pascal fp16" explanation does not match the logs. The Windows-only shared-memory fallback and TDR concepts do not apply on Linux. |
| BIOS PCI resources (Above-4G, Resizable BAR) | Above-4G decoding is already active (GPU BAR1 256 MB and BAR3 32 MB in the 64-bit window at `0x4000000000`, almost empty). The Tesla P4 has no Resizable BAR capability. The HP BIOS exposes no Above-4G / ReBAR option through `hp-bioscfg`. No assignment failures in `dmesg`. |
| All USB ports loaded ("too much for the mini PC to power") | **Refuted.** A 65-minute stress run with every USB device removed passed with no errors, but drop 7 happened a few hours later with no USB devices attached. |
| Idle link errors | A single correctable `RxErr` on `00:1b.0` and on GPU 0 was logged at idle (0 % util) on 2026-11-07 18:54:58 UTC, and the card stayed up. The link throws errors without load. |

### The standalone test passed

`scripts/gpu-isolation-test/run_gpu_test.sh` ran 41 minutes (2026-11-07 04:36 to 05:18 UTC) with ComfyUI stopped, in the same container image and CUDA stack. All 15 phases exited cleanly with **0 Xid and 0 RxErr**:

| Phase | GPU 0 alone | GPU 1 alone | Both |
|-------|:-----------:|:-----------:|:----:|
| Sustained load, 180 s (300 s for both) | pass | pass | pass |
| Square-wave load steps, 45 s | pass | pass | pass |
| Power ramp, 10 s | pass | pass | – |
| Pinned host to GPU copies, 120 s | pass | pass | – |
| Compute plus second-stream copies, 180 s (300 s for both) | pass | pass | pass |
| GPU to GPU copies, 120 s | pass | – | – |

Peak power was 73.5 W (GPU 0) and 70.1 W (GPU 1) against the 75 W limit. About 1,300 samples per GPU were at 95 % utilisation or more, and both links held PCIe 3.0 x4 under load.

So the same hardware ran 41 minutes of synthetic load cleanly and then dropped within 4.5 to 6 minutes of a real Flux job, twice in a row. The difference is the ComfyUI workload, not the raw power or bandwidth.

A later full ComfyUI stress run (2 Flux Q4_K_S + 3 SDXL, both GPUs, 65 minutes, 2026-11-08 00:54 to 01:59 UTC) also passed with no Xid and no AER while every USB device was unplugged (GPU 0 peaked at 55 °C and 81.8 W). That run led to the USB-load theory, which drop 7 then contradicted. Steady load is not the trigger; both failures near a cold start (drop 7) and at job changes (drops 3 to 5) point at abrupt state changes.

### Open leads

1. **The workload itself.** DisTorch2 offload streams model weights between host (or the donor GPU) and GPU 0 on every sampling step, on top of continuous compute. The standalone `pcie` and `mixed` phases used pinned 256 MB copies instead. A closer reproduction of ComfyUI's copy sizes and cadence would show whether the traffic pattern, not the load level, is what matters.
2. **The rest of the GPU 0 path.** All seven drops are on one root port and always begin with a physical-layer error. The docks, OCuLink cables and redrivers are new and have already been swapped between ports, so they are ruled out. What remains on that path is the M.2 adapters, the M.2 slots and root port, and the BIOS settings below.
3. **Dock supply droop.** Log each dock's 12 V rail with an INA228 (under-voltage alert) across a run. Rules the dock supply in or out during the fast load swings.
4. **Different vBIOS versions.** The two cards report different vBIOS versions (GPU 0 `86.04.55.00.01`, GPU 1 `86.04.8C.00.10`) with the same InfoROM and PCI IDs, and the older-numbered one is the card that drops. Not a conclusion, only a difference worth keeping in mind. Do not cross-flash without checking the exact board part number first.
5. **BIOS settings.** Windows 11 reported a code 12 (insufficient resources) error on this machine on 2026-10-31. Above-4G decoding turned out to be active already and the P4 has no Resizable BAR, so resources are not the problem. PCI Express Power Management, Runtime Power Management and Extended Idle Power States were Enabled; they could not be written from Linux (`hp_bioscfg` returns `Invalid command type`) and were switched off in F10 setup by hand before the 2026-11-08 runs.
6. **Diagnostic only:** pin the root port's link speed to Gen 2 and see whether the fault disappears. If it does, signal margin at Gen 3 is the problem. This is a probe, not a fix.
7. **Driver and monitoring churn.** Persistence mode was off (`nvidia-persistenced` ran with `--no-persistence-mode`), so every `nvidia-smi` call cold-initialised the cards, and the Prometheus GPU exporter runs `nvidia-smi` on every scrape. Persistence mode was enabled on 2026-11-08 and a one-hour watch is running. Unproven as a cause; recorded as a lead only.

### Recovery

1. Stop anything using the GPUs. Containers holding GPU 0 will not exit cleanly, so expect a zombie process.
2. Full power cycle (hold the power button; a normal reboot may hang on the stuck process).
3. After boot: `nvidia-smi` lists both GPUs, `dmesg | grep -iE "xid|AER"` shows only the boot-time "AER: enabled" lines.

### Useful side observation

Whenever a process holds a CUDA context on a GPU (ComfyUI opens one on GPU 0 as soon as it starts and keeps it while it runs), that GPU sits at P0 and about 23 W at idle at Gen 3, while a GPU with no context idles in P8 at about 6.6 W. That is normal driver behaviour with an open context, not a fault. With ComfyUI stopped, both cards settle to P8 within about 20 seconds.

Reading idle state needs care. With persistence mode off, each one-shot `nvidia-smi` re-initialises the card and reports it in P0 at about 23 W; a continuous `nvidia-smi -l 5` shows the true idle state. ComfyUI is now set to `restart: "no"` so it no longer starts at boot: start it with `docker compose up -d` and stop it with `docker compose down`.

## Reproducing

Everything above can be rerun with the scripts in [`scripts/gpu-isolation-test/`](../scripts/gpu-isolation-test/). Run the standalone test first; if it passes, run the Flux job with each `DONOR` setting while watching GPU 0.
