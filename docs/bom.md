# Bill of Materials

Total build cost: about **$600**. Part numbers, prices and links are *to be filled in*.

| # | Item | Qty | Notes |
|---|------|-----|-------|
| 1 | HP ProDesk 600 G5 Mini, barebones | 1 | Host, bought on eBay. Both M.2 2230/2280 slots used for the GPU links. Case modded to carry three fans |
| 2 | NVIDIA Tesla P4 8 GB | 2 | Used data-center pulls, bought on eBay |
| 3 | M.2 → OCuLink adapter | 2 | One per M.2 slot, one per GPU |
| 4 | JHH OCuLink PCIe 4.0 x4 dock (OCuLink → PCIe x16) | 2 | One per GPU. Board marked "OCULINK X4 / PCIe 4.0 X4 / TO GPU", with DIP switches for power-on and reset delay |
| 5 | 120 W Pico PSU (24-pin ATX) | 2 | One per dock. Mounts on the dock's 24-pin header and powers the dock and GPU |
| 6 | 12 V 300 W power supply | 1 | Feeds both Pico PSUs. See [power](power.md) |
| 6b | 90 W universal laptop power brick | 1 | Powers the ProDesk |
| 6c | PNY 2 TB 2.5" SATA SSD | 1 | Boot drive |
| 6d | KingSpec NX 512 GB NVMe SSD | 1 | External data drive |
| 6e | ORICO 40 Gbps NVMe enclosure, with fan | 1 | Connects over USB-C. The link negotiated at 10 Gbps on the ProDesk when checked |
| 7 | Thermalright 60 x 60 x 25 mm fans, black | 9 | Three per GPU, plus three on the modded ProDesk case. No RGB |
| 8 | Copper-fin heatsink | 2 | Replaces the stock P4 heatsink |
| 9 | XIAO microcontroller | 1 | Polls GPU temperature and sets fan speed |
| 9b | Thermalright 12-port fan hub | 1 | Distributes the PWM signal to all fans. Has an IR remote and RGB header support, neither used here since the fans have no RGB |
| 9c | Digital fan-speed readout | 1 | Shows speed as a percentage |
| 10 | Shroud material, tape, adhesive, wire, connectors | n/a | See [cooling](cooling.md) |
