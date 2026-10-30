# Bill of Materials

Part numbers, prices and links are *to be filled in*. Items below are what is visible in the build photos.

| # | Item | Qty | Notes |
|---|------|-----|-------|
| 1 | HP ProDesk 600 G5 Mini | 1 | Host. Two M.2 2230/2280 slots used for the GPU links |
| 2 | NVIDIA Tesla P4 8 GB | 2 | Used data-center pulls |
| 3 | M.2 → OCuLink adapter | 2 | One per GPU |
| 4 | OCuLink (PCIe x4) → PCIe x16 riser board | 2 | Board marked "OCULINK X4 / PCIe 4.0 X4 / TO GPU", with DIP switches for power-on and reset delay |
| 5 | Pico-PSU-style 24-pin ATX power module | 2 | Mounts on the riser's 24-pin header; powers the riser and GPU |
| 6 | 12 V 10 A DC power supply | per label | See [power](power.md) |
| 7 | 60 mm PWM fans | 6 | Three per GPU |
| 8 | Copper-fin heatsink | 2 | Replaces the stock P4 heatsink |
| 9 | XIAO microcontroller | 1 | Polls GPU temperature and sets fan speed (model to be filled in) |
| 9b | Thermalright 12-port fan hub | 1 | Distributes the PWM signal to all fans |
| 9c | Digital fan-speed readout | 1 | Shows speed as a percentage |
| 10 | Shroud material, tape, adhesive, wire, connectors | n/a | See [cooling](cooling.md) |
