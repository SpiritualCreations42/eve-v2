# TODO (delete before publishing)

## Pull from the live machine once it is powered back up
- [x] CPU, RAM, storage, BIOS version (`lscpu`, `free -h`, `lsblk`, `dmidecode`)
- [x] OS and kernel, NVIDIA driver and CUDA versions
- [x] `nvidia-smi` full output, per-GPU PCIe link width and speed (`lspci -vv`)
- [x] Negotiated link widths (done)
- [x] Idle temperatures and power (done)
- [x] Load temperatures and GPU power under LLM load (done)
- [ ] Fan speeds and power at the wall
- [ ] Worst-case burn test (needs a tool approved for EvE)
- [x] Docker / compose services running, GPU passthrough test
- [ ] Benchmarks: LLM tokens/s, Whisper, transcoding

## Hardware docs to finish
- [ ] Part numbers, prices and links for the BOM (total is about $600)
- [ ] Wiring diagram for power-on sequence
- [ ] Re-check OS, driver and service versions once the final boot and data drives are back in
- [ ] Shroud: dimensions, material, print/cut files if any
- [ ] Photo captions reviewed

## Before going public
- [ ] Remove TODO.md
- [ ] Confirm license
- [ ] Scrub hostnames, IPs, serial numbers, MAC addresses
- [ ] Check photos for anything private
