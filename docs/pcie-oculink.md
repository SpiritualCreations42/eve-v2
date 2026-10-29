# PCIe / OCuLink Link

Each Tesla P4 connects to the mini PC through its own M.2 → OCuLink → PCIe x16 chain.

```
ProDesk M.2 slot ──► M.2→OCuLink adapter ──► OCuLink cable ──► OCuLink→PCIe x16 riser ──► Tesla P4
                                                               (+ ATX power module)
```

## Riser settings

The riser boards have DIP switches / jumpers for CLKRUN# delay, PERST# delay and power mode (AUTO / ON). See [photo 08](../hardware/photos/08-pico-psu-closeup-oculink-switches.jpg).

*To be verified / filled in from the live machine:*

- [ ] Switch and jumper positions used
- [ ] Which M.2 slot feeds which GPU
- [ ] Negotiated link width and speed per GPU (`lspci -vv`)
- [ ] Boot order: power the risers and GPUs before or with the host?
