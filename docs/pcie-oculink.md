# PCIe / OCuLink Link

Both M.2 slots in the ProDesk are used. Each carries an M.2 → OCuLink adapter that feeds a JHH PCIe 4.0 x4 dock, and each dock holds one Tesla P4.

```
ProDesk M.2 slot ──► M.2→OCuLink adapter ──► OCuLink cable ──► JHH OCuLink PCIe 4.0 x4 dock ──► Tesla P4
                                                                (+ 120 W Pico PSU)
```

## Measured link (read from the running system, 2026-10-30)

| GPU | PCI address | Root port | Link capability | Negotiated |
|-----|-------------|-----------|-----------------|------------|
| GPU 0 | 01:00.0 | 00:1b.0 | PCIe 3.0 x16 (card) | **x4** (Gen 1 speed while idle in P8, Gen 3 under load) |
| GPU 1 | 02:00.0 | 00:1b.4 | PCIe 3.0 x16 (card) | **x4**, Gen 3 (8 GT/s) |

Both cards link at x4, which is the most the M.2 slots can offer. The docks are PCIe 4.0 capable, but the P4 is a PCIe 3.0 card, so the link runs at Gen 3. `lspci` reports "downgraded" because the P4 is an x16 card. At idle the link drops to a lower speed to save power, so check it under load for the real figure (`nvidia-smi --query-gpu=pcie.link.gen.current,pcie.link.width.current --format=csv`).

The PCI tree shows the two cards behind separate PCH root ports (00:1b.0 and 00:1b.4), so each has its own link.

## Dock settings

The JHH docks have DIP switches / jumpers for CLKRUN# delay, PERST# delay and power mode (AUTO / ON). See [photo 08](../hardware/photos/08-pico-psu-closeup-oculink-switches.jpg).
