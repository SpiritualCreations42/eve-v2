# Power

```
12 V 300 W supply ──┬──► 120 W Pico PSU ──► OCuLink dock ──► Tesla P4 (GPU 0)
                    └──► 120 W Pico PSU ──► OCuLink dock ──► Tesla P4 (GPU 1)

90 W universal laptop brick ──► HP ProDesk 600 G5 Mini
```

- Each dock has its own **120 W Pico PSU** on the dock's 24-pin header ([photo 05](../hardware/photos/05-p4-oculink-pico-psu-side.jpg), [photo 08](../hardware/photos/08-pico-psu-closeup-oculink-switches.jpg)).
- Both Pico PSUs run from a single **12 V 300 W power supply**.
- The ProDesk is powered separately by a **90 W universal laptop power brick**.
- The Tesla P4 has a 75 W power limit (confirmed with `nvidia-smi`) and is powered through the dock.

Idle readings on 2026-10-30: GPU 0 about 6.4 W (P8), GPU 1 about 23.7 W (P0, light load). Under sustained LLM inference on both cards, peak GPU power was 61.6 W (GPU 0) and 64.9 W (GPU 1), below the 75 W limit. See [benchmarks](benchmarks.md).

*To be filled in:*

- [ ] Measured power at the wall, idle and loaded
- [ ] Power-on sequencing (docks and GPUs before or with the host)
