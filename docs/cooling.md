# Cooling

The Tesla P4 is a passively cooled card designed for server airflow. Here its stock heatsink is replaced with a copper-fin heatsink ([photo 01](../hardware/photos/01-p4-bare-heatsink-removed.jpg)) and three 60 mm fans in a cut-out shroud ([photo 04](../hardware/photos/04-p4-three-fan-topdown.jpg)).

A fan-speed controller with a digital readout shows speed as a percentage ([photo 11](../hardware/photos/11-single-p4-on-rack.jpg)).

The GPU driver reports fan speed as N/A because the fans are external and not wired to the card. Fan speed is set on the controller.

Idle GPU temperatures on 2026-10-30: GPU 0 32 °C, GPU 1 38 °C.

Under sustained LLM inference on both cards (about 2.5 minutes at 98–99% utilisation), peak temperatures were 61 °C (GPU 0) and 59 °C (GPU 1). See [benchmarks](benchmarks.md).

*To be filled in:*

- [ ] Fan model, CFM, noise
- [ ] Controller model and wiring (manual vs automatic)
- [ ] Shroud construction and dimensions
- [ ] Idle and load GPU temperatures at each fan speed
