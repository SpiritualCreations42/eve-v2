#!/usr/bin/env python3
"""Standalone GPU load test (no ComfyUI). Phases: soak, steps, ramp, pcie, p2p, mixed."""
import argparse
import sys
import time

import torch


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def burn(a, b, secs):
    end = time.monotonic() + secs
    while time.monotonic() < end:
        torch.mm(a, b)
        torch.cuda.synchronize(a.device)


def phase_soak(dev, a, b, secs):
    end = time.monotonic() + secs
    while time.monotonic() < end:
        burn(a, b, min(30, max(0.0, end - time.monotonic())))
        log("soak running, %.0f s left" % max(0.0, end - time.monotonic()))


def phase_steps(dev, a, b, secs):
    for period in (10, 2, 0.5, 0.1):
        log("square wave period %.1f s for %d s" % (period, secs))
        end = time.monotonic() + secs
        while time.monotonic() < end:
            burn(a, b, period / 2)
            time.sleep(period / 2)


def phase_ramp(dev, a, b, secs):
    for pct in range(10, 101, 10):
        log("duty cycle %d%% for %d s" % (pct, secs))
        end = time.monotonic() + secs
        while time.monotonic() < end:
            on = 0.2 * pct / 100
            burn(a, b, on)
            time.sleep(0.2 - on)


def phase_pcie(dev, a, b, secs):
    n = 64 * 1024 * 1024  # 256 MB of float32
    h = torch.empty(n, dtype=torch.float32, pin_memory=True)
    d = torch.empty(n, dtype=torch.float32, device=dev)
    t0 = time.monotonic()
    moved = 0
    last = t0
    while time.monotonic() - t0 < secs:
        d.copy_(h, non_blocking=True)
        h.copy_(d, non_blocking=True)
        torch.cuda.synchronize(dev)
        moved += 2 * n * 4
        if time.monotonic() - last >= 10:
            log("pcie host<->device %.2f GB/s" % (moved / (time.monotonic() - last) / 1e9))
            moved, last = 0, time.monotonic()


def phase_p2p(dev, a, b, secs, peer):
    n = 64 * 1024 * 1024
    x = torch.empty(n, dtype=torch.float32, device=dev)
    y = torch.empty(n, dtype=torch.float32, device="cuda:%d" % peer)
    t0 = time.monotonic()
    moved = 0
    last = t0
    while time.monotonic() - t0 < secs:
        y.copy_(x)
        x.copy_(y)
        torch.cuda.synchronize(dev)
        torch.cuda.synchronize(y.device)
        moved += 2 * n * 4
        if time.monotonic() - last >= 10:
            log("gpu%d<->gpu%d %.2f GB/s" % (dev.index, peer, moved / (time.monotonic() - last) / 1e9))
            moved, last = 0, time.monotonic()


def phase_mixed(dev, a, b, secs):
    # compute on the default stream while a second stream streams data over PCIe,
    # similar to the offload pattern of the Flux GGUF workflow
    n = 64 * 1024 * 1024
    h = torch.empty(n, dtype=torch.float32, pin_memory=True)
    d = torch.empty(n, dtype=torch.float32, device=dev)
    s = torch.cuda.Stream(device=dev)
    t0 = time.monotonic()
    last = t0
    while time.monotonic() - t0 < secs:
        with torch.cuda.stream(s):
            d.copy_(h, non_blocking=True)
            h.copy_(d, non_blocking=True)
        for _ in range(4):
            torch.mm(a, b)
        torch.cuda.synchronize(dev)
        if time.monotonic() - last >= 30:
            log("mixed running, %.0f s left" % (secs - (time.monotonic() - t0)))
            last = time.monotonic()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gpu", type=int, required=True)
    p.add_argument("--phase", required=True, choices=["soak", "steps", "ramp", "pcie", "p2p", "mixed"])
    p.add_argument("--secs", type=int, default=60)
    p.add_argument("--peer", type=int, default=1)
    args = p.parse_args()
    dev = torch.device("cuda:%d" % args.gpu)
    torch.cuda.set_device(dev)
    log("gpu%d %s phase=%s secs=%d torch=%s" % (args.gpu, torch.cuda.get_device_name(dev), args.phase, args.secs, torch.__version__))
    a = torch.randn(4096, 4096, device=dev)
    b = torch.randn(4096, 4096, device=dev)
    try:
        if args.phase == "p2p":
            phase_p2p(dev, a, b, args.secs, args.peer)
        else:
            globals()["phase_" + args.phase](dev, a, b, args.secs)
    except RuntimeError as e:
        log("CUDA ERROR:", e)
        return 2
    log("phase finished OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
