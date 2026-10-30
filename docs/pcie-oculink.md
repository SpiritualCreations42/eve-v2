# PCIe / OCuLink Link

Each Tesla P4 connects to the mini PC through its own M.2 → OCuLink → PCIe x16 chain.

```
ProDesk M.2 slot ──► M.2→OCuLink adapter ──► OCuLink cable ──► OCuLink→PCIe x16 riser ──► Tesla P4
                                                               (+ ATX power module)
```

## Measured link (read from the running system, 2026-10-30)

| GPU | PCI address | Root port | Link capability | Negotiated |
|-----|-------------|-----------|-----------------|------------|
| GPU 0 | 01:00.0 | 00:1b.0 | PCIe 3.0 x16 (card) | **x4** (Gen 1 speed while idle in P8, Gen 3 under load) |
| GPU 1 | 02:00.0 | 00:1b.4 | PCIe 3.0 x16 (card) | **x4**, Gen 3 (8 GT/s) |

Both cards link at x4, which is the most the M.2 slots can offer. `lspci` reports "downgraded" because the P4 is an x16 card. At idle the link drops to a lower speed to save power, so check it under load for the real figure (`nvidia-smi --query-gpu=pcie.link.gen.current,pcie.link.width.current --format=csv`).

The PCI tree shows the two cards behind separate PCH root ports (00:1b.0 and 00:1b.4), so each has its own link.

## Riser settings

The riser boards have DIP switches / jumpers for CLKRUN# delay, PERST# delay and power mode (AUTO / ON). See [photo 08](../hardware/photos/08-pico-psu-closeup-oculink-switches.jpg).

*To be filled in:*

- [ ] Switch and jumper positions used
- [ ] Which physical M.2 slot feeds which GPU
- [ ] Power-on order: risers and GPUs before or with the host
