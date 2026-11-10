# Workloads: GPU physics simulation and reinforcement learning

Besides LLM inference ([Benchmarks](benchmarks.md)), EvE runs sustained reinforcement-learning jobs on both Tesla P4s. The P4 is a Pascal card with no tensor cores, so this is a test of plain CUDA throughput and of long-run stability.

## What runs

A custom PPO trainer written in JAX drives MuJoCo MJX (MuJoCo physics compiled to run on the GPU). The task is teaching a 12-joint quadruped robot to walk. Each GPU runs its own independent training job, 4096 simulated robots in parallel, with the physics and the neural network both on the GPU. Scripts: [scripts/mjx-ppo](../scripts/mjx-ppo).

## Measured results

| Metric | Value |
|--------|-------|
| Throughput per P4 | about 20,000 simulation steps per second (196.6M steps in 9,620 s) |
| One training run | 2,400 updates, 196.6M steps, about 2.7 hours per GPU |
| GPU memory in use | about 0.7 GB of 8 GB per job |
| Utilization | 99 to 100 % on both cards for the whole run |
| Temperature under load | 58 to 59 C |
| Power under load | about 47 to 50 W per card (75 W limit) |
| Core clock under load | 1113 MHz |
| PCIe link during these runs | Gen3 x4 on both cards |

Both GPUs ran back-to-back queues of three runs each (about 8 hours per GPU) more than once, with no job failures and no driver errors in the kernel log.

## Notes and caveats

- The per-job memory footprint is small, so a P4 could run several of these jobs at once; each GPU currently runs one.
- The MJX numbers use a cheap solver setting (2 Newton iterations) for training speed. Results are re-checked in the standard CPU MuJoCo solver, which is slower and more accurate.
- Stability data here does not settle the GPU 0 PCIe drops described in [Troubleshooting](troubleshooting.md); these runs are an additional data point, not a fix.
