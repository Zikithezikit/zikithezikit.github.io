#!/usr/bin/env python3
"""Every number in the AI data compression post is printed by this script.

Run:  python3 _figures/2026-02-17-ai-data-compression/toy.py
Standard library only.
"""
import heapq
import math
import random


def phi(x):
    """Standard normal CDF."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def h(title):
    print(f"\n## {title}\n")


# ---------------------------------------------------------------- 1. entropy
h("1. Entropy, code lengths, Huffman")
P = {"A": 0.5, "B": 0.25, "C": 0.125, "D": 0.125}
H = -sum(p * math.log2(p) for p in P.values())
print("| symbol | p | -log2 p | p * (-log2 p) |")
print("|---|---:|---:|---:|")
for s, p in P.items():
    print(f"| {s} | {p} | {-math.log2(p):.0f} | {-p * math.log2(p):.3f} |")
print(f"\nH = {H:.3f} bits per symbol")
print(f"2**H = {2 ** H:.2f}")
print(f"uniform over 4 symbols: H = {math.log2(4):.0f} bits per symbol")
assert H == 1.75


def huffman(probs):
    heap = [(p, i, {s: ""}) for i, (s, p) in enumerate(probs.items())]
    heapq.heapify(heap)
    n = len(heap)
    while len(heap) > 1:
        p1, _, c1 = heapq.heappop(heap)
        p2, _, c2 = heapq.heappop(heap)
        merged = {s: "0" + c for s, c in c1.items()}
        merged.update({s: "1" + c for s, c in c2.items()})
        heapq.heappush(heap, (p1 + p2, n, merged))
        n += 1
    return heap[0][2]


code = huffman(P)
avg = sum(P[s] * len(c) for s, c in code.items())
print("\n| symbol | Huffman code | length |")
print("|---|---|---:|")
for s in P:
    print(f"| {s} | {code[s]} | {len(code[s])} |")
print(f"\naverage length = {avg:.3f} bits per symbol")
assert avg == H

# the code Shannon prints for this source: A 0, B 10, C 110, D 111
shannon = {"A": "0", "B": "10", "C": "110", "D": "111"}
assert sorted(len(c) for c in shannon.values()) == sorted(len(c) for c in code.values())

# a message of 8 symbols, with the probabilities of P
msg = "AABACABD"
bits = "".join(shannon[s] for s in msg)
print(f"\nmessage {msg} -> {bits} ({len(bits)} bits; fixed 2-bit code: {2 * len(msg)} bits)")
dec, cur = [], ""
inv = {c: s for s, c in shannon.items()}
for b in bits:
    cur += b
    if cur in inv:
        dec.append(inv[cur])
        cur = ""
assert "".join(dec) == msg

# ------------------------------------------------- 2. wrong model, more bits
h("2. Coding with the wrong probabilities (cross-entropy)")
models = {
    "true p": [0.5, 0.25, 0.125, 0.125],
    "uniform": [0.25] * 4,
    "mild guess": [0.4, 0.3, 0.2, 0.1],
    "reversed": [0.125, 0.125, 0.25, 0.5],
}
print("| model q | cross-entropy (bits per symbol) | excess over H |")
print("|---|---:|---:|")
pv = list(P.values())
for name, q in models.items():
    ce = -sum(p * math.log2(qq) for p, qq in zip(pv, q))
    print(f"| {name} | {ce:.3f} | {ce - H:.3f} |")

# ------------------------------------------------------------- 3. Gaussian R(D)
h("3. Gaussian rate-distortion")
s2 = 4.0
print("| D | R(D) = 0.5 log2(4/D) |")
print("|---:|---:|")
for D in [4, 2, 1, 0.5, 0.25]:
    R = 0 if D >= s2 else 0.5 * math.log2(s2 / D)
    print(f"| {D} | {R:.2f} |")
print(f"\nD at R = 1 bit: sigma2 * 2**(-2R) = {s2 * 2 ** -2:.1f}; at R = 2: {s2 * 2 ** -4:.2f}; at R = 3: {s2 * 2 ** -6:.3f}")

# test channel: X = Xhat + N, Xhat ~ N(0, s2 - D), N ~ N(0, D) independent.
D = 1.0
var_xhat = s2 - D
rho2 = var_xhat / s2  # squared correlation between X and Xhat
mi = -0.5 * math.log2(1 - rho2)  # mutual information of jointly Gaussian pair
print(f"\ntest channel for D = {D}: var(Xhat) = {var_xhat}, rho^2 = {rho2}, I(X; Xhat) = {mi:.3f} bits")
rng = random.Random(1)
n = 200_000
err = 0.0
xs = []
for _ in range(n):
    xh = rng.gauss(0, math.sqrt(var_xhat))
    x = xh + rng.gauss(0, math.sqrt(D))
    err += (x - xh) ** 2
    xs.append(x)
print(f"simulated: var(X) = {sum(v * v for v in xs) / n:.2f}, E[(X - Xhat)^2] = {err / n:.2f} ({n:,} samples, seed 1)")

# reverse water-filling for three independent Gaussian components
h("3b. Reverse water-filling")
var = [4.0, 1.0, 0.25]
budget = 1.25  # total distortion allowed (sum over components)


def rate(ds):
    return sum(0.5 * math.log2(v / d) for v, d in zip(var, ds))


theta = 0.5
wf = [min(theta, v) for v in var]
print(f"sigma2 = {var}, total distortion {budget}")
print(f"water level theta = {theta}: D_i = {wf}, sum = {sum(wf)}, R = {rate(wf):.2f} bits")
c = budget / sum(var)
prop = [c * v for v in var]
print(f"same relative distortion for all: D_i = {[round(d, 4) for d in prop]}, sum = {sum(prop):.2f}, R = {rate(prop):.2f} bits")
# brute-force check over a grid of allocations
best = (1e9, None)
step = 0.0025
d1 = step
while d1 <= var[0]:
    d2 = step
    while d2 <= var[1]:
        d3 = budget - d1 - d2
        if step <= d3 <= var[2]:
            r = rate([d1, d2, d3])
            if r < best[0]:
                best = (r, (d1, d2, d3))
        d2 += step
    d1 += step
print(f"grid search minimum: R = {best[0]:.2f} bits at D = {tuple(round(x, 3) for x in best[1])}")
assert abs(best[0] - rate(wf)) < 0.01

# ------------------------------------------------ 4. a 2x2 patch, transform+quantize
h("4. A 2x2 patch through transform, quantizer, inverse transform")
patch = [121, 125, 80, 85]  # a b / c d  (made up)
a, b, c_, d = patch


def fwd(p):
    a, b, c, d = p
    return [(a + b + c + d) / 2, (a - b + c - d) / 2, (a + b - c - d) / 2, (a - b - c + d) / 2]


def inv(y):
    s, hz, vt, dg = y
    return [(s + hz + vt + dg) / 2, (s - hz + vt - dg) / 2, (s + hz - vt - dg) / 2, (s - hz - vt + dg) / 2]


y = fwd(patch)
print(f"pixels {patch}")
print(f"coefficients y = {y} (orthonormal 2x2 transform)")
assert inv(y) == [float(v) for v in patch]
print(f"sum of squares: pixels {sum(v * v for v in patch)}, coefficients {sum(v * v for v in y):.0f}")
print(f"share of the squares in the first coefficient: {100 * y[0] ** 2 / sum(v * v for v in y):.1f}%")
STEP = 8
q = [round(v / STEP) for v in y]
yhat = [k * STEP for k in q]
rec = inv(yhat)
print(f"step {STEP}: indices {q}, dequantized {yhat}")
print(f"reconstruction {rec}")
err = [r - p for r, p in zip(rec, patch)]
print(f"pixel errors {err}, total squared error {sum(e * e for e in err):.0f}, coefficient-domain error {sum((u - v) ** 2 for u, v in zip(y, yhat)):.0f}")

# --------------------------------------------- 5. rate + lambda * distortion
h("5. Loss = rate + lambda * distortion on that patch")
sigma = [200.0, 5.0, 30.0, 3.0]  # made-up scale of each coefficient


def bits(k, step, s):
    """-log2 of the probability that N(0, s^2) puts in the bin of index k (bin width = step)."""
    k = abs(k)  # the Gaussian is symmetric
    lo, hi = (k - 0.5) * step, (k + 0.5) * step
    if k == 0:
        pm = 2 * phi(hi / s) - 1
    else:  # use tails, which stay accurate far from zero
        pm = 0.5 * (math.erfc(lo / (s * math.sqrt(2))) - math.erfc(hi / (s * math.sqrt(2))))
    return -math.log2(pm)


rows = []
for step in [2, 4, 8, 16, 32]:
    q = [round(v / step) for v in y]
    R = sum(bits(k, step, s) for k, s in zip(q, sigma))
    Dtot = sum((k * step - v) ** 2 for k, v in zip(q, y))
    rows.append((step, R, Dtot))
print("| step | rate R (bits) | distortion D (squared error) |")
print("|---:|---:|---:|")
for step, R, Dt in rows:
    print(f"| {step} | {R:.1f} | {Dt:.0f} |")
print()
for lam in [1.0, 0.1, 0.01]:
    ls = [(R + lam * Dt, step) for step, R, Dt in rows]
    print(f"lambda = {lam}: " + ", ".join(f"step {s}: L = {l:.1f}" for l, s in ls) + f" -> best step {min(ls)[1]}")

# ------------------------------------ 6. noise instead of rounding
h("6. Rounding versus additive uniform noise")
rng = random.Random(7)
n = 200_000
ys = [rng.gauss(0, 5) for _ in range(n)]
e_round = sum((round(v) - v) ** 2 for v in ys) / n
e_noise = sum(rng.uniform(-0.5, 0.5) ** 2 for _ in range(n)) / n
print(f"mean squared error of rounding: {e_round:.4f}; of uniform(-0.5, 0.5) noise: {e_noise:.4f}; 1/12 = {1 / 12:.4f} ({n:,} samples)")

# ------------------------------------------ 7. the scale matters
h("7. Cost of the same quantized value under different scales")
print("| scale sigma | bits to code index 5 | bits to code index 0 |")
print("|---:|---:|---:|")
for s in [1, 2, 5, 10]:
    print(f"| {s} | {bits(5, 1, s):.2f} | {bits(0, 1, s):.2f} |")
# a flat patch (all indices 0) vs an edge patch (indices of size ~5), right and wrong scale
flat = [0] * 8
edge = [5, -4, 6, 5, -5, 4, 6, -5]
for name, idx in [("flat", flat), ("edge", edge)]:
    for s in [0.5, 5]:
        print(f"{name} patch, scale {s}: {sum(bits(k, 1, s) for k in idx):.1f} bits for {len(idx)} values")

# --------------------------------------------- 8. next-token prediction
h("8. Next-token probabilities as code lengths (made-up probabilities)")
lm = {"mat": 0.4, "floor": 0.2, "bed": 0.1, "other (30 words, 1% each)": 0.3}
for w, p in lm.items():
    print(f"- {w}: p = {p}, -log2 p = {-math.log2(p):.2f} bits")
print(f"- one word out of the 30 others at p = 0.01: {-math.log2(0.01):.2f} bits")
good = [0.4, 0.9, 0.7]
poor = [0.05, 0.1, 0.1]
print(f"three tokens, probabilities {good}: {-sum(math.log2(p) for p in good):.2f} bits; {poor}: {-sum(math.log2(p) for p in poor):.2f} bits")

# ------------------------------------------------ 9. Delétang table arithmetic
h("9. Numbers from Table 1 of Deletang et al.")
size_gb = 1.0
params = 70e9
param_bytes = 2 * params
print(f"70B parameters at 2 bytes = {param_bytes / 1e9:.0f} GB; against 1 GB of data: {100 * param_bytes / 1e9:.0f}% of the raw size")
print(f"Chinchilla 70B on enwik9: raw 8.3% + parameters {100 * param_bytes / 1e9:.0f}% = {8.3 + 100 * param_bytes / 1e9:.1f}% (table: 14008.3)")
