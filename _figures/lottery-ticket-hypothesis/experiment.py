"""Iterative magnitude pruning on LeNet-300-100 + MNIST, in plain NumPy.

For each seed it trains a dense 784-300-100-10 MLP, then repeats:
  1. prune the smallest-magnitude weights of every layer (20% of the survivors in the
     two hidden layers, 10% in the output layer, as in Frankle & Carbin 2019, p. 3),
  2. reset the survivors to their ORIGINAL initial values  -> "winning ticket",
  3. retrain.
At every sparsity level it also trains two controls on the same sparsity:
  * "reinit": the winning-ticket mask with a fresh random initialization (the paper's control),
  * "random": a random mask with the same per-layer sparsity, original initial values.

Run:   python3 _figures/lottery-ticket-hypothesis/experiment.py            (full run)
       python3 _figures/lottery-ticket-hypothesis/experiment.py --quick    (1 seed, 4 rounds)
Output: results.json and results.csv next to this script (raw numbers, one row per run).
MNIST is downloaded once into .sources/lottery-ticket-hypothesis/ (gitignored).
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import csv
import gzip
import json
import time
import urllib.request
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / ".sources" / "lottery-ticket-hypothesis"
URL = "https://storage.googleapis.com/cvdf-datasets/mnist/"
FILES = ["train-images-idx3-ubyte", "train-labels-idx1-ubyte",
         "t10k-images-idx3-ubyte", "t10k-labels-idx1-ubyte"]

SIZES = [784, 300, 100, 10]
PRUNE_RATE = [0.20, 0.20, 0.10]   # per round, per layer (output layer at half the rate)
LR = 1.2e-3                        # Adam, as in the paper's Lenet setup (p. 3)
BATCH = 256
ITERS = 1500                       # about 7 epochs of the 55,000 training images
EVAL_EVERY = 50
ROUNDS = 16                        # 0.8^16 = 2.8% of the hidden weights left


# ---------------------------------------------------------------- data

def load_mnist():
    DATA.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        p = DATA / (f + ".gz")
        if not p.exists():
            urllib.request.urlretrieve(URL + f + ".gz", p)

    def images(f):
        return np.frombuffer(gzip.open(DATA / (f + ".gz")).read(), np.uint8, offset=16).reshape(-1, 784)

    def labels(f):
        return np.frombuffer(gzip.open(DATA / (f + ".gz")).read(), np.uint8, offset=8)

    x = images(FILES[0]).astype(np.float32) / 255.0
    y = labels(FILES[1]).astype(np.int64)
    xt = images(FILES[2]).astype(np.float32) / 255.0
    yt = labels(FILES[3]).astype(np.int64)
    # fixed split: 55,000 train, 5,000 validation (for the early-stopping iteration)
    rng = np.random.default_rng(12345)
    idx = rng.permutation(len(x))
    tr, va = idx[:55000], idx[55000:]
    return x[tr], y[tr], x[va], y[va], xt, yt


# ---------------------------------------------------------------- model

def glorot(rng):
    """Gaussian Glorot initialization; biases start at zero."""
    ws = [(rng.standard_normal((a, b)) * np.sqrt(2.0 / (a + b))).astype(np.float32)
          for a, b in zip(SIZES[:-1], SIZES[1:])]
    bs = [np.zeros(b, np.float32) for b in SIZES[1:]]
    return ws, bs


def forward(ws, bs, x):
    acts = [x]
    h = x
    for i, (w, b) in enumerate(zip(ws, bs)):
        h = h @ w + b
        if i < len(ws) - 1:
            h = np.maximum(h, 0)
        acts.append(h)
    return acts


def loss_acc(ws, bs, x, y):
    logits = forward(ws, bs, x)[-1]
    z = logits - logits.max(1, keepdims=True)
    logp = z - np.log(np.exp(z).sum(1, keepdims=True))
    return float(-logp[np.arange(len(y)), y].mean()), float((logits.argmax(1) == y).mean())


def train(ws0, bs0, masks, data, seed):
    """Train from (ws0, bs0) with fixed masks. Returns final weights and the early-stop record."""
    x, y, xv, yv, xt, yt = data
    rng = np.random.default_rng(seed)
    ws = [w * m for w, m in zip(ws0, masks)]
    bs = [b.copy() for b in bs0]
    params = ws + bs
    m1 = [np.zeros_like(p) for p in params]
    m2 = [np.zeros_like(p) for p in params]
    b1, b2, eps = 0.9, 0.999, 1e-8
    n = len(x)
    order, pos = rng.permutation(n), 0
    best = dict(val_loss=1e9, it=0, test_acc=0.0)
    for it in range(1, ITERS + 1):
        if pos + BATCH > n:
            order, pos = rng.permutation(n), 0
        idx = order[pos:pos + BATCH]
        pos += BATCH
        acts = forward(ws, bs, x[idx])
        logits = acts[-1]
        z = np.exp(logits - logits.max(1, keepdims=True))
        g = z / z.sum(1, keepdims=True)
        g[np.arange(BATCH), y[idx]] -= 1
        g /= BATCH
        grads_w, grads_b = [None] * 3, [None] * 3
        for i in (2, 1, 0):
            grads_w[i] = acts[i].T @ g
            grads_b[i] = g.sum(0)
            if i > 0:
                g = (g @ ws[i].T) * (acts[i] > 0)
        grads = [gw * m for gw, m in zip(grads_w, masks)] + grads_b
        for k, (p, gr) in enumerate(zip(params, grads)):
            m1[k] = b1 * m1[k] + (1 - b1) * gr
            m2[k] = b2 * m2[k] + (1 - b2) * gr * gr
            p -= LR * (m1[k] / (1 - b1 ** it)) / (np.sqrt(m2[k] / (1 - b2 ** it)) + eps)
        for w, m in zip(ws, masks):
            w *= m   # pruned weights stay exactly zero
        if it % EVAL_EVERY == 0:
            vl, _ = loss_acc(ws, bs, xv, yv)
            if vl < best["val_loss"]:
                best = dict(val_loss=vl, it=it, test_acc=loss_acc(ws, bs, xt, yt)[1])
    final_test = loss_acc(ws, bs, xt, yt)[1]
    train_acc = loss_acc(ws, bs, x[:10000], y[:10000])[1]
    return ws, bs, dict(early_stop_iter=best["it"], early_stop_test_acc=best["test_acc"],
                        final_test_acc=final_test, final_train_acc=train_acc)


def prune(ws, masks):
    """Remove the smallest-magnitude fraction of the surviving weights, layer by layer."""
    new = []
    for w, m, rate in zip(ws, masks, PRUNE_RATE):
        alive = np.abs(w[m > 0])
        k = int(round(rate * alive.size))
        thresh = np.partition(alive, k)[k - 1] if k > 0 else -1
        keep = (np.abs(w) > thresh) & (m > 0)
        new.append(keep.astype(np.float32))
    return new


def random_like(masks, rng):
    """Random masks with exactly the same number of survivors in each layer."""
    out = []
    for m in masks:
        flat = np.zeros(m.size, np.float32)
        flat[rng.choice(m.size, int(m.sum()), replace=False)] = 1
        out.append(flat.reshape(m.shape))
    return out


def remaining(masks):
    return float(sum(m.sum() for m in masks) / sum(m.size for m in masks))


# ---------------------------------------------------------------- one seed

def run_seed(args):
    seed, rounds = args
    data = load_mnist()
    rng = np.random.default_rng(1000 + seed)
    ws0, bs0 = glorot(rng)
    masks = [np.ones_like(w) for w in ws0]
    rows = []
    t0 = time.time()
    for r in range(rounds + 1):
        pm = remaining(masks)
        # the winning ticket: original init, current mask
        ws_t, bs_t, res = train(ws0, bs0, masks, data, seed * 100 + r)
        rows.append(dict(seed=seed, round=r, condition="ticket", remaining=pm, **res))
        if r > 0:
            ws_r, bs_r = glorot(np.random.default_rng(5000 + seed * 100 + r))
            _, _, res = train(ws_r, bs_r, masks, data, seed * 100 + r)
            rows.append(dict(seed=seed, round=r, condition="reinit", remaining=pm, **res))
            rm = random_like(masks, np.random.default_rng(9000 + seed * 100 + r))
            _, _, res = train(ws0, bs0, rm, data, seed * 100 + r)
            rows.append(dict(seed=seed, round=r, condition="random", remaining=pm, **res))
        else:
            dense = {k: res[k] for k in res}   # round 0 is the dense network, shared by all conditions
            for c in ("reinit", "random"):
                rows.append(dict(seed=seed, round=0, condition=c, remaining=pm, **dense))
        print(f"seed {seed} round {r:2d} remaining {pm*100:5.1f}%  ticket final {[x for x in rows if x['round']==r and x['condition']=='ticket'][0]['final_test_acc']:.4f}"
              f"  elapsed {time.time()-t0:.0f}s", flush=True)
        masks = prune(ws_t, masks)   # next round's mask comes from the trained ticket
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="1 seed, 4 rounds, to check it runs")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--rounds", type=int, default=ROUNDS)
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args()
    seeds, rounds = (1, 4) if a.quick else (a.seeds, a.rounds)
    load_mnist()  # download once before forking
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(seeds, os.cpu_count() or 1)) as ex:
        results = list(ex.map(run_seed, [(s, rounds) for s in range(seeds)]))
    rows = [r for rs in results for r in rs]
    wall = time.time() - t0
    out = Path(a.out)
    meta = dict(model="LeNet-300-100 (784-300-100-10 ReLU MLP)", data="MNIST, 55k train / 5k val / 10k test",
                optimizer=f"Adam lr {LR}", batch=BATCH, iters=ITERS, prune_rate_per_round=PRUNE_RATE,
                seeds=seeds, rounds=rounds, wall_seconds=round(wall), cpu_threads_per_run=1)
    suffix = "_quick" if a.quick else ""
    (out / f"results{suffix}.json").write_text(json.dumps(dict(meta=meta, rows=rows), indent=1))
    with open(out / f"results{suffix}.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"done in {wall:.0f}s; wrote results{suffix}.json and .csv")


if __name__ == "__main__":
    main()
