"""A small check of the "supermask" claim of Zhou et al. (2019) on the same LeNet-300-100 + MNIST setup.

Train a dense network from W0 (same recipe as experiment.py), build a one-shot mask from (W0, W_final) with
three criteria, and measure the test accuracy of the UNTRAINED network mask * W0.
  random                  : random mask, same number of survivors per layer
  large_final             : keep the weights with the largest |W_final|
  large_final_same_sign   : keep the largest max(0, W_final * sign(W0)), i.e. large and not sign-flipped
Also with the survivors set to a signed constant (alpha * sign(W0), alpha = std of the layer's init).
Same fraction kept in every layer. 5 seeds.

Run: python3 _figures/lottery-ticket-hypothesis/supermask.py     -> supermask_results.json
"""
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import experiment as ex

HERE = Path(__file__).resolve().parent
KEEP = [0.8, 0.6, 0.4, 0.2, 0.1, 0.05]
SEEDS = 5


def keep_top(score, frac):
    flat = score.ravel()
    k = int(round(frac * flat.size))
    idx = np.argsort(-flat, kind="stable")[:k]
    m = np.zeros(flat.size, np.float32)
    m[idx] = 1
    return m.reshape(score.shape)


def one_seed(seed):
    data = ex.load_mnist()
    xt, yt = data[4], data[5]
    rng = np.random.default_rng(1000 + seed)
    ws0, bs0 = ex.glorot(rng)
    ones = [np.ones_like(w) for w in ws0]
    wsT, _, res = ex.train(ws0, bs0, ones, data, seed * 100)
    rows = []
    mrng = np.random.default_rng(777 + seed)
    for frac in KEEP:
        crit = {
            "random": [keep_top(mrng.random(w.shape), frac) for w in ws0],
            "large_final": [keep_top(np.abs(wT), frac) for wT in wsT],
            "large_final_same_sign": [keep_top(np.maximum(0, wT * np.sign(w0)), frac) for w0, wT in zip(ws0, wsT)],
        }
        for name, masks in crit.items():
            acc_init = ex.loss_acc([w * m for w, m in zip(ws0, masks)], bs0, xt, yt)[1]
            alpha = [w.std() for w in ws0]
            acc_const = ex.loss_acc([a * np.sign(w) * m for a, w, m in zip(alpha, ws0, masks)], bs0, xt, yt)[1]
            rows.append(dict(seed=seed, keep=frac, criterion=name, acc_original_init=acc_init,
                             acc_signed_constant=acc_const, dense_trained_acc=res["final_test_acc"]))
    return rows


if __name__ == "__main__":
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(SEEDS, os.cpu_count() or 1)) as pool:
        rows = [r for rs in pool.map(one_seed, range(SEEDS)) for r in rs]
    (HERE / "supermask_results.json").write_text(json.dumps(dict(
        meta=dict(seeds=SEEDS, keep=KEEP, wall_seconds=round(time.time() - t0)), rows=rows), indent=1))
    print(f"{'keep':>5} {'criterion':<22} {'orig init':>10} {'signed const':>13}")
    for frac in KEEP:
        for name in ("random", "large_final", "large_final_same_sign"):
            sel = [r for r in rows if r["keep"] == frac and r["criterion"] == name]
            a = np.mean([r["acc_original_init"] for r in sel]) * 100
            b = np.mean([r["acc_signed_constant"] for r in sel]) * 100
            print(f"{frac*100:4.0f}% {name:<22} {a:9.1f}% {b:12.1f}%")
    print(f"done in {time.time()-t0:.0f}s")
