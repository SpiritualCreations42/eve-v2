# Roadmap

Planned additions to this repo.

## Measurements
- Full-power burn test with throttle reasons logged
- Per-model tokens/s with both GPUs loaded at once
- Wall power draw, idle and loaded
- Whisper speech-to-text speed
- NVENC transcoding throughput
- A small training run

## Stability
- Swap the two OCuLink cables and docks to see whether the GPU 0 dropouts follow the path or the card
- Log each dock's 12 V rail during a ComfyUI run
- Rerun the Flux job with the BIOS Above-4G / Resizable BAR options changed, and with the link pinned to Gen 2

## Documentation
- Part numbers, prices and links in the bill of materials
- Shroud construction and dimensions
- How the fan hub is powered
- Dock DIP-switch settings and power-on sequence
- Compose files for the services in [software-setup](docs/software-setup.md)
- Re-check software versions once the final boot and data drives are installed
