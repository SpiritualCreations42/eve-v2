# MJX PPO workload

Reinforcement-learning workload used to load both Tesla P4s for hours at a time.

- `ppo_aurora.py`: custom JAX PPO trainer on MuJoCo MJX (GAE, 3x128 MLPs, 4096 parallel environments). Configured with environment variables (`XML`, `TAG`, `ASCALE`, `SEED`, `NENV`, `UPDATES`, ...).
- `queue.sh`: runs a list of training configs back to back on one GPU (`CUDA_VISIBLE_DEVICES`) and evaluates each result on CPU. `touch STOP` ends the queue after the current run.
- `eval_cpu.py`: evaluates a saved policy in the CPU MuJoCo solver.

The robot model (`aurora.xml`) and reference gait table (`gait_a.npy`) belong to a separate project and are not included; any MJCF quadruped works as a stand-in. Needs JAX with CUDA 12, `mujoco`, `mujoco-mjx` and `optax`.

Example, one queue per GPU:

    ./queue.sh 0 runA:0.15:10:1:2 runB:0.25:11:1:4
    ./queue.sh 1 runC:0.20:20:1:2 runD:0.30:21:1:4

Each config is `TAG:ACTION_SCALE:SEED:YAW_PENALTY:LATERAL_PENALTY`.
