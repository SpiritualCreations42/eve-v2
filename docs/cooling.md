# Cooling

The Tesla P4 is a passively cooled card designed for server airflow. Here its stock heatsink is replaced with a copper-fin heatsink ([photo 01](../hardware/photos/01-p4-bare-heatsink-removed.jpg)) and three 60 mm fans in a cut-out shroud ([photo 04](../hardware/photos/04-p4-three-fan-topdown.jpg)).

## Case cooling

The HP ProDesk 600 G5 Mini case is modded to carry three more 60 mm fans, on the same fan hub.

## Fan control

The fans are driven automatically from GPU temperature. How the XIAO does it is left as an exercise for the reader.


```
EvE (nvidia-smi GPU temps) ──► XIAO microcontroller ──PWM──► Thermalright 12-port fan hub ──► 9x 60 mm fans
```

- A **XIAO** board polls `nvidia-smi` for the GPU temperatures and sets the fan speed.
- The XIAO's PWM output goes to a **Thermalright 12-port fan hub** (the unit with the blue light bar, visible in [photo 13](../hardware/photos/13-rack-overview-angle.jpg)), which splits it out to nine fans: three Thermalright 60 mm fans on each GPU, plus three more on the modded ProDesk case.
- The small digital readout seen in the photos shows the fan speed as a percentage.

*To be filled in:*

- [ ] Hub model and how it is powered

The GPU driver reports fan speed as N/A because the fans are external and not wired to the card. Fan speed is set on the controller.

Idle GPU temperatures on 2026-10-30: GPU 0 32 °C, GPU 1 38 °C.

Under sustained LLM inference on both cards (about 2.5 minutes at 98–99% utilisation), peak temperatures were 61 °C (GPU 0) and 59 °C (GPU 1). See [benchmarks](benchmarks.md).

*To be filled in:*

- [ ] Exact Thermalright 60 mm fan model, CFM, noise
- [ ] Controller model and wiring (manual vs automatic)
- [ ] Shroud construction and dimensions
- [ ] Idle and load GPU temperatures at each fan speed
