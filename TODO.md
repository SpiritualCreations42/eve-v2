# TODO (delete before publishing)

## Pull from the live machine once it is powered back up
- [ ] CPU, RAM, storage, BIOS version (`lscpu`, `free -h`, `lsblk`, `dmidecode`)
- [ ] OS and kernel, NVIDIA driver and CUDA versions
- [ ] `nvidia-smi` full output, per-GPU PCIe link width and speed (`lspci -vv`)
- [ ] Which M.2 slot feeds which GPU, and negotiated link widths
- [ ] Idle and load temperatures, fan speeds, power draw
- [ ] Docker / compose services running, GPU passthrough test
- [ ] Benchmarks: LLM tokens/s, Whisper, transcoding

## Hardware docs to finish
- [ ] Exact adapter, power module and fan part numbers (BOM prices and links)
- [ ] Fan controller wiring and what it controls
- [ ] Wiring diagram for power-on sequence
- [ ] Shroud: dimensions, material, print/cut files if any
- [ ] Photo captions reviewed

## Before going public
- [ ] Remove TODO.md
- [ ] Confirm license
- [ ] Scrub hostnames, IPs, serial numbers, MAC addresses
- [ ] Check photos for anything private
