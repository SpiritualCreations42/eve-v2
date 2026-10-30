# Benchmarks

First round measured on 2026-10-30. Everything here is LLM inference through Ollama, not a synthetic burn-in, so treat the power and temperature numbers as "realistic sustained inference load", not the worst case a P4 can produce.

## Single GPU, 8B model

`hermes3:8b` (4.7 GB, 4-bit) on one Tesla P4, about 90 seconds of back-to-back 400-token generations:

| Metric | Result |
|--------|--------|
| Generation speed | **about 27.7 tokens/s** (steady, 4 runs) |
| Prompt processing | about 600 tokens/s (warm) |
| GPU power | peak 60.6 W |
| GPU temperature | peak 54 °C |
| SM clock | 1113 MHz at 99% utilisation |

## Both GPUs loaded at once

`hermes3:8b` on one card and `qwen3:4b-instruct` on the other, generating continuously for about 2.5 minutes. Data: [load-test-2026-10-30-both-gpus.csv](data/load-test-2026-10-30-both-gpus.csv) (2 s samples).

| | GPU 0 | GPU 1 |
|---|---|---|
| Utilisation | up to 99% | up to 98% |
| Power (peak / mean under load) | 61.6 W / 59.0 W | 64.9 W / 62.4 W |
| Temperature (start → peak) | 46 → 61 °C | 39 → 59 °C |
| SM clock under load | 1113 MHz, steady | 1113 MHz, steady |
| PCIe link | Gen 3 x4 | Gen 3 x4 |

After the load stopped and the models were unloaded, temperatures fell back to about 50 °C within a minute.

Observations:

- Neither card hit its 75 W limit. LLM token generation is memory-bound, so the P4s sat at about 60 to 65 W.
- The 85 °C abort guard never triggered, and peak temperature stayed around 60 °C with the external fans.
- The SM clock sat at a constant 1113 MHz (card maximum 1531 MHz). It stayed flat through the whole run while temperature was well below the limit, so it points to a power-state clock for this kind of load and not heat. Throttle reasons were not captured during the run, so this is not confirmed.
- The fan controller's display reads 100 in the photos. The fan speed during the test was not recorded.

## Not measured yet

- [ ] Per-model tokens/s while both GPUs were loaded (the per-run output was lost to a truncated log)
- [ ] A true worst-case burn (full-power compute load) with throttle reasons logged
- [ ] Wall power draw
- [ ] Whisper speech-to-text speed
- [ ] NVENC transcoding throughput
- [ ] Small training run
