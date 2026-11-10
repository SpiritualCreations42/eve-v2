import sys, pickle, numpy as np, mujoco
tag, ascale, xml = sys.argv[1], float(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else 'aurora.xml'
mass = 1.16; kp = 2.9; P_ = pickle.load(open(f'ppo_{tag}.pkl', 'rb')); pr, nm = P_['params'], P_['norm']
mm = mujoco.MjModel.from_xml_path(xml); sc = mass / mm.body_mass.sum(); mm.body_mass[:] *= sc; mm.body_inertia[:] *= sc
mm.opt.timestep = 0.005; mm.actuator_gainprm[:, 0] = kp; mm.actuator_biasprm[:, 1] = -kp   # default (accurate) solver
TAB = np.load('gait_a.npy'); P = len(TAB); NU = mm.nu
lo, hi = mm.jnt_range[1:, 0], mm.jnt_range[1:, 1]
d0 = mujoco.MjData(mm); d0.qpos[:7] = [0, 0, 0, 1, 0, 0, 0]; d0.qpos[7:] = TAB[0]; mujoco.mj_forward(mm, d0)
feet = [mujoco.mj_name2id(mm, mujoco.mjtObj.mjOBJ_GEOM, f'{l}_foot') for l in ('fl', 'fr', 'rl', 'rr')]
Z0 = -(min(d0.geom_xpos[g, 2] for g in feet) - 0.006) + 0.002
def mlp(ps, x):
    for w, b in ps[:-1]: x = np.tanh(x @ w + b)
    return x @ ps[-1][0] + ps[-1][1]
def run(seed, det=True, use_policy=True):
    rng = np.random.default_rng(seed); d = mujoco.MjData(mm)
    d.qpos[:7] = [0, 0, Z0, 1, 0, 0, 0]; d.qpos[7:] = TAB[0] + rng.uniform(-.05, .05, NU); d.ctrl[:] = TAB[0]
    last = np.zeros(NU); fell = False
    for t in range(400):
        q = d.qpos[3:7]; w = q[0]; qv = -q[1:4]; v = np.array([0, 0, -1.]); tt = 2 * np.cross(qv, v); g = v + w * tt + np.cross(qv, tt)
        ob = np.concatenate([g, d.qvel[3:6], d.qpos[7:] - TAB[t % P], d.qvel[6:], last, [np.sin(2 * np.pi * (t % P) / P), np.cos(2 * np.pi * (t % P) / P)]])
        a = np.clip(mlp(pr['pi'], (ob - nm['mean']) / np.sqrt(nm['var'] + 1e-6)), -1, 1) if use_policy else np.zeros(NU)
        d.ctrl[:] = np.clip(TAB[t % P] + ascale * a, lo, hi); last = a
        for _ in range(10): mujoco.mj_step(mm, d)
        up = 1 - 2 * (d.qpos[4] ** 2 + d.qpos[5] ** 2)
        if up < 0.5: fell = True; break
    return -d.qpos[0], d.qpos[1], up, fell, t
for use in (False, True):
    res = [run(s, use_policy=use) for s in range(6)]
    print('policy' if use else 'open-loop gait', 'fwd m', [round(r[0], 2) for r in res], 'fell', [int(r[3]) for r in res], 'dy', [round(r[1], 2) for r in res])
