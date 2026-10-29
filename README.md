# EvE v2: Compact Dual Tesla P4 GPU Server

A small-footprint AI / GPU compute box built from an **HP ProDesk 600 G5 Mini** and **two NVIDIA Tesla P4 (8 GB) data-center GPUs**, each connected externally over **M.2 → OCuLink (PCIe x4)** and cooled with a custom **3x 60 mm fan** shroud.

Low power, quiet-ish, cheap, and surprisingly capable for local inference, training experiments, and video transcoding.

![EvE v2 on the rack](hardware/photos/13-rack-overview-angle.jpg)

> **Status:** work in progress. Hardware is assembled. Software and measured results are being filled in. See [TODO.md](TODO.md).

## What it is

| Part | Details |
|------|---------|
| Host | HP ProDesk 600 G5 Mini (USFF) |
| GPUs | 2x NVIDIA Tesla P4, 8 GB GDDR5, 2560 CUDA cores, compute capability 6.1, ~75 W each |
| GPU link | M.2 (PCIe x4) → OCuLink adapter → PCIe x16 riser, one per GPU |
| GPU power | Pico-PSU-style ATX 24-pin power module per GPU, fed from a 12 V 10 A brick |
| Cooling | Stock P4 heatsink replaced with a copper-fin heatsink and 3x 60 mm fans in a cut-out shroud, with a fan-speed controller and digital readout |

Items marked *to be verified* in the docs are filled in from the live machine, not from memory.

## Why this build

- The Tesla P4 is a 75 W, passively cooled, half-height card that is very cheap used.
- A USFF mini PC has no PCIe slot, but it does have two M.2 slots. OCuLink turns each into an external x4 PCIe link.
- Pascal (compute 6.1) still runs current CUDA toolkits and drivers, and its NVENC engines have no artificial concurrent-session cap.

## Repository layout

```
docs/                 Build documentation (BOM, power, cooling, PCIe/OCuLink, software, benchmarks)
hardware/photos/      Build photos with captions (hardware/photos/README.md)
scripts/              Helper scripts (system info collection, etc.)
```

## Documentation

- [Bill of materials](docs/bom.md)
- [PCIe / OCuLink link](docs/pcie-oculink.md)
- [Power](docs/power.md)
- [Cooling](docs/cooling.md)
- [Software setup](docs/software-setup.md)
- [Benchmarks](docs/benchmarks.md)
- [Build log](docs/build-log.md)

## Safety notes

This build uses an external 12 V supply feeding ATX-style power modules and bare GPU cards on a rack shelf. Cards are open to the air, so keep fingers, metal and liquids away. Do not run the GPUs without the fans, and use a supply rated for the load. You build and run this at your own risk.

## License

Code and scripts: MIT (see [LICENSE](LICENSE)). Documentation and photos: please attribute Spiritual Creations. *(License choice to be confirmed before publishing.)*

Built by [Spiritual Creations](https://spiritualcreations2024.org).
