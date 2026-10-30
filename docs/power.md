# Power

Per GPU: a Pico-PSU-style 24-pin ATX power module sits on the riser's 24-pin header ([photo 05](../hardware/photos/05-p4-oculink-pico-psu-side.jpg), [photo 08](../hardware/photos/08-pico-psu-closeup-oculink-switches.jpg)). The module is fed with 12 V DC.

The Tesla P4 has a 75 W power limit (confirmed with `nvidia-smi`), powered through the slot connector on the riser.

Idle readings on 2026-10-30: GPU 0 about 6.4 W (P8), GPU 1 about 23.7 W (P0, light load).

*To be filled in:*

- [ ] PSU model and rating, how many GPUs per brick
- [ ] Measured idle and load power at the wall
- [ ] Power-on sequencing
- [ ] Fuse / protection
