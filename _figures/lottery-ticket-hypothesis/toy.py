"""The by-hand example for the lottery ticket post: one prune-and-rewind round on a tiny network.

Network: inputs (x1, x2, 1)  ->  8 ReLU units  ->  one logit.   24 + 8 = 32 weights, no other parameters.
Task:    XOR. Four corners (-1,-1) and (1,1) are class 0, (-1,1) and (1,-1) are class 1,
         four noisy points per corner (noise 0.25, made up for the example).
Train:   full-batch gradient descent, learning rate 0.5, 600 steps, logistic loss.
"Success" = loss below 0.1 and every point classified correctly.

Run:  python3 _figures/lottery-ticket-hypothesis/toy.py > _figures/lottery-ticket-hypothesis/toy.out.md
"""
import numpy as np

H, STEPS, LR = 8, 600, 0.5
PRUNE = 0.5

rng = np.random.default_rng(0)
X, Y = [], []
for cx, cy, label in [(-1, -1, 0), (1, 1, 0), (-1, 1, 1), (1, -1, 1)]:
    for _ in range(4):
        X.append([cx + 0.25 * rng.standard_normal(), cy + 0.25 * rng.standard_normal(), 1.0])
        Y.append(label)
X, Y = np.array(X), np.array(Y, float)


def logit(W1, w2, x):
    return np.maximum(x @ W1.T, 0) @ w2


def loss_acc(W1, w2):
    p = 1 / (1 + np.exp(-logit(W1, w2, X)))
    loss = -np.mean(Y * np.log(p + 1e-12) + (1 - Y) * np.log(1 - p + 1e-12))
    return loss, np.mean((p > 0.5) == Y)


def train(W1, w2, m1, m2):
    """Gradient descent with fixed masks. Returns final weights and (loss, accuracy) after every step."""
    W1, w2 = W1 * m1, w2 * m2
    hist = [loss_acc(W1, w2)]
    for _ in range(STEPS):
        h = np.maximum(X @ W1.T, 0)
        p = 1 / (1 + np.exp(-(h @ w2)))
        dz = (p - Y) / len(Y)
        g2 = h.T @ dz * m2
        g1 = (np.outer(dz, w2) * (h > 0)).T @ X * m1
        W1, w2 = W1 - LR * g1, w2 - LR * g2
        hist.append(loss_acc(W1, w2))
    return W1, w2, hist


def init(seed):
    """Gaussian init, rounded to 2 decimals so the example can be followed on paper."""
    r = np.random.default_rng(seed)
    return np.round(r.standard_normal((H, 3)) * 0.7, 2), np.round(r.standard_normal(H) * 0.7, 2)


def prune(W1, w2):
    """Magnitude pruning, layer by layer: drop the smallest 50% of each layer."""
    m1, m2 = np.ones((H, 3)), np.ones(H)
    m1.ravel()[np.argsort(np.abs(W1).ravel(), kind="stable")[: int(PRUNE * H * 3)]] = 0
    m2[np.argsort(np.abs(w2), kind="stable")[: int(PRUNE * H)]] = 0
    return m1, m2


def first_success(hist):
    for i, (l, a) in enumerate(hist):
        if l < 0.1 and a == 1:
            return i
    return None


ones1, ones2 = np.ones((H, 3)), np.ones(H)


def one_seed(seed, n_reinit=5):
    W1, w2 = init(seed)
    Wt, wt, h_dense = train(W1, w2, ones1, ones2)
    m1, m2 = prune(Wt, wt)
    W1s, w2s, h_ticket = train(W1, w2, m1, m2)
    reinit = []
    for k in range(n_reinit):
        Wr, wr = init(10000 + seed * n_reinit + k)
        _, _, h = train(Wr, wr, m1, m2)
        reinit.append(first_success(h))
    return dict(seed=seed, dense=first_success(h_dense), ticket=first_success(h_ticket), reinit=reinit)


# ---- statistics over many initializations -------------------------------------------------
N_SEEDS = 60
stats = [one_seed(s) for s in range(N_SEEDS)]
dense_ok = sum(s["dense"] is not None for s in stats)
ticket_ok = sum(s["ticket"] is not None for s in stats)
reinit_ok = sum(r is not None for s in stats for r in s["reinit"])
reinit_n = sum(len(s["reinit"]) for s in stats)
both = [s for s in stats if s["dense"] is not None]
ticket_given_dense = sum(s["ticket"] is not None for s in both)
reinit_given_dense = sum(r is not None for s in both for r in s["reinit"])
reinit_given_dense_n = sum(len(s["reinit"]) for s in both)

# ---- the example we walk through: the first seed where dense and ticket succeed, no reinit does
chosen = next(s["seed"] for s in stats
              if s["dense"] is not None and s["ticket"] is not None and all(r is None for r in s["reinit"]))
seed = chosen
W1_0, w2_0 = init(seed)
W1_t, w2_t, h_dense = train(W1_0, w2_0, ones1, ones2)
m1, m2 = prune(W1_t, w2_t)
W1_s, w2_s, h_ticket = train(W1_0, w2_0, m1, m2)
rW1, rw2 = init(10000 + seed * 5)           # first of the five fresh initializations
_, _, h_reinit = train(rW1, rw2, m1, m2)


def md_matrix(M, name, fmt="{:+.2f}", zero="0"):
    out = [f"| {name} | x1 | x2 | 1 |", "|---|---:|---:|---:|"]
    for i, row in enumerate(M):
        cells = [zero if v == 0 else fmt.format(v) for v in row]
        out.append(f"| unit {i + 1} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def md_vector(v, name, fmt="{:+.2f}", zero="0"):
    head = "| " + name + " | " + " | ".join(f"unit {i + 1}" for i in range(len(v))) + " |"
    sep = "|---|" + "---:|" * len(v)
    row = "| value | " + " | ".join(zero if x == 0 else fmt.format(x) for x in v) + " |"
    return "\n".join([head, sep, row])


print(f"<!-- init seed {seed}; first seed where dense and ticket succeed and none of 5 reinits does -->\n")
print("### Initial weights (theta_0)\n")
print(md_matrix(W1_0, "W1 at init"))
print()
print(md_vector(w2_0, "w2 at init"))
print()
print("### Trained dense weights (rounded to 2 decimals for display)\n")
print(md_matrix(W1_t, "W1 trained"))
print()
print(md_vector(w2_t, "w2 trained"))
print(f"\ndense: first success at step {first_success(h_dense)}, "
      f"loss {h_dense[-1][0]:.3f}, accuracy {h_dense[-1][1]*100:.0f}% after {STEPS} steps\n")

print("### Ranking by magnitude\n")
mag1 = np.sort(np.abs(W1_t).ravel())
mag2 = np.sort(np.abs(w2_t))
k1, k2 = int(PRUNE * H * 3), int(PRUNE * H)
print("hidden layer, 24 magnitudes sorted, smallest first:\n")
print("pruned (12): " + ", ".join(f"{v:.3f}" for v in mag1[:k1]))
print("kept (12):   " + ", ".join(f"{v:.3f}" for v in mag1[k1:]))
print(f"\ncut between {mag1[k1 - 1]:.3f} and {mag1[k1]:.3f}\n")
print("output layer, 8 magnitudes sorted, smallest first:\n")
print("pruned (4): " + ", ".join(f"{v:.3f}" for v in mag2[:k2]))
print("kept (4):   " + ", ".join(f"{v:.3f}" for v in mag2[k2:]))
print(f"\ncut between {mag2[k2 - 1]:.3f} and {mag2[k2]:.3f}\n")

print("### Mask\n")
print(md_matrix(m1, "mask W1", fmt="{:.0f}"))
print()
print(md_vector(m2, "mask w2", fmt="{:.0f}"))
print(f"\nweights kept: {int(m1.sum() + m2.sum())} of {m1.size + m2.size}\n")

print("### Rewound ticket (mask times theta_0)\n")
print(md_matrix(W1_0 * m1, "W1 rewound"))
print()
print(md_vector(w2_0 * m2, "w2 rewound"))
print()

print("### Retraining, same 600 steps\n")
print("| step | dense from theta_0 | ticket (rewound) | same mask, fresh init |")
print("|---:|---|---|---|")
for t in (0, 25, 50, 100, 200, 600):
    cells = [f"loss {h[t][0]:.3f}, acc {h[t][1]*100:.0f}%" for h in (h_dense, h_ticket, h_reinit)]
    print(f"| {t} | " + " | ".join(cells) + " |")
print(f"\nfirst step with loss < 0.1 and 100% accuracy: dense {first_success(h_dense)}, "
      f"ticket {first_success(h_ticket)}, fresh init {first_success(h_reinit)}\n")

print("### Retrained ticket weights (rounded to 2 decimals)\n")
print(md_matrix(W1_s, "W1 ticket"))
print()
print(md_vector(w2_s, "w2 ticket"))
print()

# forward passes by hand with the ROUNDED retrained weights
Wr2, wr2 = np.round(W1_s, 2), np.round(w2_s, 2)
print("### Forward passes, rounded ticket weights\n")
for x, cls in ((np.array([1.0, 1.0, 1.0]), 0), (np.array([1.0, -1.0, 1.0]), 1)):
    print(f"x = ({x[0]:+.0f}, {x[1]:+.0f}, 1), class {cls}:\n")
    tot = 0.0
    for i in range(H):
        if wr2[i] == 0:
            continue
        terms = [(Wr2[i, j], x[j]) for j in range(3) if Wr2[i, j] != 0]
        pre = sum(a * b for a, b in terms)
        act = max(pre, 0)
        expr = " + ".join(f"({a:+.2f})({b:+.0f})" for a, b in terms)
        print(f"- unit {i + 1}: pre = {expr} = {pre:+.2f}, relu = {act:.2f}, times w2 {wr2[i]:+.2f} = {act*wr2[i] + 0.0:+.2f}")
        tot += act * wr2[i]
    print(f"\nlogit = {tot:+.2f}, probability of class 1 = {1/(1+np.exp(-tot)):.3f}\n")
    assert (tot > 0) == (cls == 1)

alive_hidden = int((m1 * m2[:, None]).sum())
print("### What the mask kept\n")
print(f"- hidden weights kept: {int(m1.sum())}, of which {alive_hidden} sit on a unit whose output weight was also kept")
print(f"- weights that can still change the output: {alive_hidden + int(m2.sum())} of {m1.size + m2.size}")
same_kept = int(np.sum(np.sign(W1_0[m1 > 0]) == np.sign(W1_t[m1 > 0])) + np.sum(np.sign(w2_0[m2 > 0]) == np.sign(w2_t[m2 > 0])))
n_kept = int(m1.sum() + m2.sum())
same_pruned = int(np.sum(np.sign(W1_0[m1 == 0]) == np.sign(W1_t[m1 == 0])) + np.sum(np.sign(w2_0[m2 == 0]) == np.sign(w2_t[m2 == 0])))
n_pruned = int((m1 == 0).sum() + (m2 == 0).sum())
print(f"- kept weights whose trained value has the same sign as the initial value: {same_kept} of {n_kept}")
print(f"- pruned weights whose trained value has the same sign as the initial value: {same_pruned} of {n_pruned}\n")

print("### Over 60 initializations\n")
print(f"- dense network reaches the target: {dense_ok} of {N_SEEDS}")
print(f"- rewound ticket reaches the target: {ticket_ok} of {N_SEEDS}")
print(f"- among the {len(both)} initializations where dense succeeded: ticket {ticket_given_dense} of {len(both)}; "
      f"same mask with a fresh init {reinit_given_dense} of {reinit_given_dense_n}")
print(f"- same mask with a fresh init (5 fresh inits per seed, all seeds): {reinit_ok} of {reinit_n}")
assert h_ticket[-1][1] == 1 and h_dense[-1][1] == 1

# ---- compact tables, in the layout used in the post ----------------------------------------
def tri(v):
    return ", ".join("0" if x == 0 else f"{x:.2f}" for x in v)


print("\n### Compact tables\n")
print("| unit | θ0 (x1, x2, 1) | θT after training | mask | m ⊙ θ0 |")
print("|---|---|---|:---:|---|")
for i in range(H):
    print(f"| {i + 1} | {tri(W1_0[i])} | {tri(W1_t[i])} | {' '.join(f'{int(v)}' for v in m1[i])} | {tri(W1_0[i] * m1[i])} |")
print()
print("| output weight | " + " | ".join(f"u{i + 1}" for i in range(H)) + " |")
print("|---|" + "---:|" * H)
for name, v in (("θ0", w2_0), ("θT", w2_t), ("mask", m2), ("m ⊙ θ0", w2_0 * m2)):
    cells = [f"{int(x)}" if name == "mask" else ("0" if x == 0 else f"{x:.2f}") for x in v]
    print(f"| {name} | " + " | ".join(cells) + " |")
