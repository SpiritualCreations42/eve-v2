import os, time, pickle, functools
import numpy as np, jax, jax.numpy as jnp, optax, mujoco
from mujoco import mjx

E = os.environ.get
XML = E('XML', 'aurora.xml'); MASS = float(E('MASS', 1.16)); TAG = E('TAG', 'run'); KP = float(E('KP', 2.9))
NENV = int(E('NENV', 2048)); T = int(E('T', 20)); UPDATES = int(E('UPDATES', 1500)); SEED = int(E('SEED', 0))
ASCALE = float(E('ASCALE', 0.1)); FWD_W = float(E('FWD_W', 2.0)); YW = float(E("YAW_W", 1.0)); YPW = float(E("Y_W", 2.0)); EPLEN = 400; GAMMA = 0.97; LAM = 0.95
STANCE = {'fl': (16.8, 27.2, -30.5), 'fr': (-19.4, -0.7, -48.8), 'rl': (-7.6, -0.7, -61.6), 'rr': (12.5, 17.0, -31.1)}

mm = mujoco.MjModel.from_xml_path(XML)
sc = MASS / mm.body_mass.sum(); mm.body_mass[:] *= sc; mm.body_inertia[:] *= sc
mm.opt.timestep = 0.005; mm.actuator_gainprm[:, 0] = KP; mm.actuator_biasprm[:, 1] = -KP
mm.opt.solver = mujoco.mjtSolver.mjSOL_NEWTON; mm.opt.iterations = 2; mm.opt.ls_iterations = 5
NU = mm.nu; names = [mujoco.mj_id2name(mm, mujoco.mjtObj.mjOBJ_ACTUATOR, i) for i in range(NU)]
TABN = np.load(E('GAIT', 'gait_a.npy')); q0 = TABN[0].copy(); P = TABN.shape[0]; TAB = jnp.array(TABN)
d_ = mujoco.MjData(mm); d_.qpos[:7] = [0, 0, 0, 1, 0, 0, 0]; d_.qpos[7:] = q0; mujoco.mj_forward(mm, d_)
feet = [mujoco.mj_name2id(mm, mujoco.mjtObj.mjOBJ_GEOM, f'{l}_foot') for l in STANCE]
Z0 = float(-(min(d_.geom_xpos[g, 2] for g in feet) - 0.006) + 0.002)
Q0 = jnp.array(q0); LO = jnp.array(mm.jnt_range[1:, 0]); HI = jnp.array(mm.jnt_range[1:, 1])
mx = mjx.put_model(mm); D0 = mjx.make_data(mm)
OBS = 3 + 3 + NU + NU + NU + 2

def quat_rot_inv(q, v):  # rotate world vector v into body frame (inverse rotation)
    w = q[0]; qv = -q[1:4]; t = 2 * jnp.cross(qv, v)
    return v + w * t + jnp.cross(qv, t)

def obs_fn(d, last, t):
    g = quat_rot_inv(d.qpos[3:7], jnp.array([0., 0., -1.]))
    ph = 2 * jnp.pi * (t % P) / P
    return jnp.concatenate([g, d.qvel[3:6], d.qpos[7:] - TAB[t % P], d.qvel[6:], last, jnp.array([jnp.sin(ph), jnp.cos(ph)])])

def reset_one(rng):
    n = jax.random.uniform(rng, (NU,), minval=-0.05, maxval=0.05)
    d = D0.replace(qpos=jnp.concatenate([jnp.array([0., 0., Z0, 1., 0., 0., 0.]), Q0 + n]), qvel=jnp.zeros(6 + NU), ctrl=Q0)
    return d

def physics(d, tgt):
    d = d.replace(ctrl=tgt)
    return jax.lax.fori_loop(0, 10, lambda i, dd: mjx.step(mx, dd), d)

def step_one(d, last, t, a):
    tgt = jnp.clip(TAB[t % P] + ASCALE * a, LO, HI)
    d2 = physics(d, tgt)
    vx = -d2.qvel[0]; vy = d2.qvel[1]; wz = d2.qvel[5]; q = d2.qpos[3:7]; up = 1 - 2 * (q[1] ** 2 + q[2] ** 2)
    yaw = jnp.arctan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] ** 2 + q[3] ** 2))
    r = (- YW * jnp.abs(yaw) * 0.1 - YPW * jnp.abs(d2.qpos[1]) * 0.1 + FWD_W * jnp.clip(vx, -0.3, 0.6) + 0.5 * up - 0.5 * jnp.abs(vy) - 0.3 * jnp.abs(wz)
         - 0.02 * jnp.sum((a - last) ** 2) - 0.0005 * jnp.sum(d2.qfrc_actuator[6:] ** 2))
    done = (up < 0.5) | (t + 1 >= EPLEN)
    fell = up < 0.5
    return d2, r, done, fell, -d2.qpos[0], d2.qpos[1]

def mlp_init(key, sizes):
    ps = []
    for i, (a, b) in enumerate(zip(sizes[:-1], sizes[1:])):
        key, k = jax.random.split(key); ps.append((jax.random.normal(k, (a, b)) * jnp.sqrt(2.0 / a) * (0.01 if i == len(sizes) - 2 else 1.0), jnp.zeros(b)))
    return ps
def mlp(ps, x):
    for w, b in ps[:-1]: x = jnp.tanh(x @ w + b)
    return x @ ps[-1][0] + ps[-1][1]

key = jax.random.PRNGKey(SEED); key, k1, k2 = jax.random.split(key, 3)
params = {'pi': mlp_init(k1, [OBS, 128, 128, 128, NU]), 'v': mlp_init(k2, [OBS, 128, 128, 128, 1]), 'logstd': jnp.full((NU,), -1.0)}
norm = {'mean': jnp.zeros(OBS), 'var': jnp.ones(OBS), 'n': jnp.array(1e-4)}
opt = optax.chain(optax.clip_by_global_norm(1.0), optax.adam(3e-4)); ost = opt.init(params)

def logp_fn(p, o, a):
    mu = mlp(p['pi'], o); ls = p['logstd']
    return jnp.sum(-0.5 * ((a - mu) / jnp.exp(ls)) ** 2 - ls - 0.5 * jnp.log(2 * jnp.pi), -1)

vstep = jax.vmap(step_one); vobs = jax.vmap(obs_fn); vreset = jax.vmap(reset_one)

@jax.jit
def rollout(params, norm, carry, key):
    def body(c, k):
        d, last, t, ep_r, ep_stats = c
        o = vobs(d, last, t); on = (o - norm['mean']) / jnp.sqrt(norm['var'] + 1e-6)
        k1, k2 = jax.random.split(k)
        mu = mlp(params['pi'], on); a = jnp.clip(mu + jnp.exp(params['logstd']) * jax.random.normal(k1, mu.shape), -3, 3)
        lp = logp_fn(params, on, a); v = mlp(params['v'], on)[:, 0]
        d2, r, done, fell, x, up = vstep(d, last, t, jnp.clip(a, -1, 1))
        ep_r2 = ep_r + r
        stats = jnp.stack([jnp.where(done, ep_r2, 0.), jnp.where(done, x, 0.), jnp.where(done, 1., 0.), jnp.where(fell, 1., 0.), jnp.where(done, jnp.abs(up), 0.)], 1)
        rk = jax.random.split(k2, NENV); dn = vreset(rk)
        d3 = jax.tree_util.tree_map(lambda a_, b_: jnp.where(done.reshape((-1,) + (1,) * (a_.ndim - 1)), b_, a_), d2, dn)
        last3 = jnp.where(done[:, None], 0., jnp.clip(a, -1, 1)); t3 = jnp.where(done, 0, t + 1); ep_r3 = jnp.where(done, 0., ep_r2)
        return (d3, last3, t3, ep_r3, ep_stats), (o, a, lp, v, r, done.astype(jnp.float32), (done & ~fell).astype(jnp.float32), stats)
    keys = jax.random.split(key, T)
    carry, tr = jax.lax.scan(body, carry, keys)
    d, last, t, ep_r, es = carry
    ov = (vobs(d, last, t) - norm['mean']) / jnp.sqrt(norm['var'] + 1e-6)
    return carry, tr, mlp(params['v'], ov)[:, 0]

def gae(r, v, done, vlast, trunc):
    def body(c, x):
        adv, vn = c; r_, v_, d_, tr_ = x
        nonterm = 1.0 - d_ + tr_  # truncation: bootstrap
        delta = r_ + GAMMA * vn * nonterm - v_
        adv = delta + GAMMA * LAM * nonterm * adv
        return (adv, v_), adv
    _, advs = jax.lax.scan(body, (jnp.zeros_like(vlast), vlast), (r, v, done, trunc), reverse=True)
    return advs

@jax.jit
def update(params, ost, obs, act, lp0, adv, ret, key):
    B = obs.shape[0]; mb = B // 32
    def loss(p, o, a, l0, ad, rt):
        l = logp_fn(p, o, a); ratio = jnp.exp(l - l0)
        pg = -jnp.mean(jnp.minimum(ratio * ad, jnp.clip(ratio, 0.8, 1.2) * ad))
        vl = jnp.mean((mlp(p['v'], o)[:, 0] - rt) ** 2)
        ent = jnp.sum(p['logstd'] + 0.5 * jnp.log(2 * jnp.pi * jnp.e))
        return pg + 0.5 * vl - 1e-3 * ent
    def epoch(c, k):
        params, ost = c; perm = jax.random.permutation(k, B)
        def mbstep(c2, idx):
            params, ost = c2; g = jax.grad(loss)(params, obs[idx], act[idx], lp0[idx], adv[idx], ret[idx])
            up, ost = opt.update(g, ost, params); return (optax.apply_updates(params, up), ost), 0
        (params, ost), _ = jax.lax.scan(mbstep, (params, ost), perm[:32 * mb].reshape(32, mb))
        return (params, ost), 0
    (params, ost), _ = jax.lax.scan(epoch, (params, ost), jax.random.split(key, 4))
    return params, ost

key, k = jax.random.split(key); d = vreset(jax.random.split(k, NENV))
carry = (d, jnp.zeros((NENV, NU)), jnp.zeros(NENV, jnp.int32), jnp.zeros(NENV), None)
acc = np.zeros(5); log = open(f'ppo_{TAG}.log', 'a'); t0 = time.time(); best = -1e9
for u in range(UPDATES):
    key, k = jax.random.split(key)
    carry, tr, vlast = rollout(params, norm, (carry[0], carry[1], carry[2], carry[3], jnp.zeros(1)), k)
    o, a, lp, v, r, dn, tn, st = tr
    adv = gae(r, v, dn, vlast, tn); ret = adv + v
    of = o.reshape(-1, OBS); bm, bv = of.mean(0), of.var(0)
    n = norm['n'] + of.shape[0]; dl = bm - norm['mean']
    norm = {'mean': norm['mean'] + dl * of.shape[0] / n, 'var': (norm['var'] * norm['n'] + bv * of.shape[0] + dl ** 2 * norm['n'] * of.shape[0] / n) / n, 'n': n}
    on = (of - norm['mean']) / jnp.sqrt(norm['var'] + 1e-6)
    advf = adv.reshape(-1); advf = (advf - advf.mean()) / (advf.std() + 1e-6)
    key, k = jax.random.split(key)
    params, ost = update(params, ost, on, a.reshape(-1, NU), lp.reshape(-1), advf, ret.reshape(-1), k)
    acc += np.array(st.reshape(-1, 5).sum(0))
    if u % 20 == 19 or u == UPDATES - 1:
        s = acc; ne = float(s[2]); acc = np.zeros(5)
        line = f"{time.time()-t0:7.0f}s upd={u} steps={(u+1)*NENV*T} eps={int(ne)} rew/ep={float(s[0])/max(ne,1):.1f} x_end={float(s[1])/max(ne,1):.3f} y_end={float(s[4])/max(ne,1):.3f} fall%={100*float(s[3])/max(ne,1):.0f} std={float(jnp.exp(params['logstd']).mean()):.2f}"
        print(line, flush=True); log.write(line + '\n'); log.flush()
    if u % 25 == 0 or u == UPDATES - 1:
        pickle.dump({'params': jax.device_get(params), 'norm': jax.device_get(norm)}, open(f'ppo_{TAG}.pkl', 'wb'))
print('DONE'); log.write('DONE\n')
