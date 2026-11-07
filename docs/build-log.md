# Build Log

Newest entries at the bottom. Photos live in [hardware/photos](../hardware/photos/).

## Assembly
- Tesla P4 cards stripped of stock heatsink and fitted with copper-fin heatsink, fan shroud and 3x 60 mm fans
- OCuLink risers with Pico-PSU-style power modules assembled and wired
- ProDesk Mini opened up for the two M.2 → OCuLink adapters
- Whole stack mounted on a wire shelf

*Dates, details and lessons learned to be added.*

## 2026-11: bring-up and GPU stability testing
- Ubuntu 26.04 installed, Docker stack and ComfyUI running on both GPUs
- Fan hub moved off the Pico PSUs onto its own 12 V / 5 V supply (300 W adjustable buck, 5 V buck, INA228 metering with small OLED readouts), after the Pico PSU shut itself off under the combined load
- GPU 0 fell off the PCIe bus five times between 2026-11-04 and 2026-11-07 under ComfyUI Flux GGUF load; GPU 1 never did
- A standalone PyTorch load test ran 41 minutes on both GPUs with no faults, so the trigger is specific to the ComfyUI workload on GPU 0's path
- Full write-up, timeline and next steps: [Troubleshooting](troubleshooting.md); test scripts in [scripts/gpu-isolation-test](../scripts/gpu-isolation-test/)
