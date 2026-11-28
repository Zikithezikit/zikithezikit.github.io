"""Control for experiment.py: does the dense network keep improving if it trains 4 times longer?

experiment.py trains every network for 1,500 iterations (about 7 epochs). If the dense network is still
improving at that point, a ticket that "beats" it may only be learning faster. This trains the dense
network from the same initializations for 6,000 iterations and records test accuracy at the early-stop
iteration and at the end.

Run: python3 _figures/lottery-ticket-hypothesis/dense_long.py    -> dense_long_results.json
"""
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

import experiment as ex

HERE = Path(__file__).resolve().parent
LONG = 6000


def one(seed):
    ex.ITERS = LONG
    data = ex.load_mnist()
    ws0, bs0 = ex.glorot(np.random.default_rng(1000 + seed))
    _, _, res = ex.train(ws0, bs0, [np.ones_like(w) for w in ws0], data, seed * 100)
    return dict(seed=seed, iters=LONG, **res)


if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=min(5, os.cpu_count() or 1)) as pool:
        rows = list(pool.map(one, range(5)))
    (HERE / "dense_long_results.json").write_text(json.dumps(rows, indent=1))
    for k in ("early_stop_test_acc", "final_test_acc", "early_stop_iter"):
        v = np.array([r[k] for r in rows], float)
        scale = 1 if k == "early_stop_iter" else 100
        print(f"{k}: mean {v.mean()*scale:.2f}  min {v.min()*scale:.2f}  max {v.max()*scale:.2f}")
