"""Figures for the lottery-ticket-hypothesis post.

Run: python3 _figures/lottery-ticket-hypothesis/make_figures.py
Needs results.json from experiment.py (and supermask_results.json from supermask.py for the last chart).
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools" / "figures"))
import blogstyle as bs  # noqa: E402

OUT = ROOT / "assets" / "images" / "lottery-ticket-hypothesis"
C = bs.COLORS


def load():
    data = json.loads((HERE / "results.json").read_text())
    rows = data["rows"]
    rounds = sorted({r["round"] for r in rows})
    out = {}
    for cond in ("ticket", "reinit", "random"):
        out[cond] = {}
        for key in ("early_stop_test_acc", "final_test_acc", "early_stop_iter"):
            mean, lo, hi = [], [], []
            for rd in rounds:
                v = np.array([r[key] for r in rows if r["round"] == rd and r["condition"] == cond], float)
                mean.append(v.mean())
                lo.append(v.min())
                hi.append(v.max())
            out[cond][key] = (np.array(mean), np.array(lo), np.array(hi))
    remaining = np.array([np.mean([r["remaining"] for r in rows if r["round"] == rd]) * 100 for rd in rounds])
    return data["meta"], rounds, remaining, out


def curves(ax, remaining, res, key, scale, conds):
    style = {"ticket": (C["blue"], "winning ticket"), "reinit": (C["red"], "same mask, new init"),
             "random": (C["gray"], "random mask")}
    for cond in conds:
        color, label = style[cond]
        mean, lo, hi = (a * scale for a in res[cond][key])
        ax.errorbar(remaining, mean, yerr=[mean - lo, hi - mean], color=color, marker="o", ms=4.5, lw=2,
                    capsize=3, elinewidth=1.2, label=label)
    ax.set_xscale("log")
    ax.invert_xaxis()
    ticks = [100, 51.3, 21.1, 7.0, 3.6]
    ticks = [t for t in ticks if t >= remaining.min() * 0.9]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:g}%" for t in ticks])
    ax.minorticks_off()
    ax.set_xlabel("weights remaining (log scale)")


def accuracy_chart():
    import matplotlib.pyplot as plt

    meta, rounds, remaining, res = load()
    bs.apply()
    fig, ax = plt.subplots(figsize=(8, 4.9))
    curves(ax, remaining, res, "early_stop_test_acc", 100, ("ticket", "reinit", "random"))
    ax.set_ylabel("test accuracy at early stop (%)")
    ax.legend(loc="lower left")
    bs.titles(fig, "Winning tickets keep their accuracy as weights are pruned",
              f"LeNet-300-100 on MNIST, {meta['seeds']} seeds; dots are means, bars are min and max (measured)")
    return bs.save_png(
        fig, OUT / "accuracy-vs-sparsity.png",
        alt=ALT["accuracy"], caption=CAPTION["accuracy"])


def early_stop_chart():
    import matplotlib.pyplot as plt

    meta, rounds, remaining, res = load()
    bs.apply()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    curves(ax, remaining, res, "early_stop_iter", 1, ("ticket", "reinit"))
    ax.set_ylabel("iteration of minimum validation loss")
    ax.axhline(1500, color=C["faint"], lw=1.2, ls="--")
    ax.text(remaining.max(), 1510, "end of training (1,500)", color=C["muted"], fontsize=9.5, ha="left", va="bottom")
    lows = [res[c]["early_stop_iter"][1].min() for c in ("ticket", "reinit")]
    ax.set_ylim(float(np.floor(min(lows) / 100) * 100 - 100), 1600)
    ax.legend(loc="lower right")
    bs.titles(fig, "How fast each network learns",
              f"Iteration at which early stopping would end training, {meta['seeds']} seeds, mean with min and max (measured)")
    return bs.save_png(fig, OUT / "early-stop-iteration.png", alt=ALT["early"], caption=CAPTION["early"])


def loop_diagram():
    s = bs.Svg(900, 470, "One round of the lottery ticket procedure",
               "Repeat until the mask is as sparse as you want. The original weights are kept the whole time.")
    th0 = s.box(40, 100, 160, 76, "θ0", fill="light_blue", stroke="blue", sub="random initialization")
    train = s.box(290, 100, 170, 76, "train", fill="light_gray", stroke="gray", sub="to completion, giving θT")
    prune = s.box(560, 100, 170, 76, "prune", fill="light_gold", stroke="gold", sub="drop smallest 20% of |w|")
    rewind = s.box(560, 250, 170, 76, "rewind", fill="light_green", stroke="green", sub="survivors back to θ0")
    s.arrow(th0, train)
    s.arrow(train, prune)
    s.arrow(prune, rewind)
    s.text(660, 218, "mask m", size=12.5, color="muted", anchor="start")
    # loop back: retrain the rewound network, then prune again
    s.parts.append(
        f'<defs><marker id="loop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{C["green"]}"/></marker></defs>'
        f'<path d="M560,288 H375 V176" fill="none" stroke="{C["green"]}" stroke-width="1.8" marker-end="url(#loop)"/>')
    s.text(467, 280, "retrain m ⊙ θ0,", size=12.5, color="muted")
    s.text(467, 306, "then prune again", size=12.5, color="muted")
    # control
    ctrl = s.box(290, 380, 440, 62, "control: same mask m, fresh random weights θ′", fill="light_gold", stroke="red")
    s.parts.append(
        f'<defs><marker id="ctl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{C["red"]}"/></marker></defs>'
        f'<path d="M730,138 H800 V411 H730" fill="none" stroke="{C["red"]}" stroke-width="1.8" '
        f'stroke-dasharray="6 5" marker-end="url(#ctl)"/>')
    s.text(808, 260, "same", size=12.5, color="muted", anchor="start")
    s.text(808, 278, "mask,", size=12.5, color="muted", anchor="start")
    s.text(808, 296, "new", size=12.5, color="muted", anchor="start")
    s.text(808, 314, "weights", size=12.5, color="muted", anchor="start")
    del ctrl
    return s.save(OUT / "ticket-loop.svg", alt=ALT["loop"], caption=CAPTION["loop"])


def supermask_chart():
    import matplotlib.pyplot as plt

    path = HERE / "supermask_results.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    rows, keep = data["rows"], data["meta"]["keep"]
    bs.apply()
    fig, ax = plt.subplots(figsize=(8, 5.3))
    style = {"random": (C["gray"], "random mask"), "large_final": (C["gold"], "keep large final weights"),
             "large_final_same_sign": (C["blue"], "large final weights that kept their sign")}
    for name, (color, label) in style.items():
        mean = [np.mean([r["acc_original_init"] for r in rows if r["keep"] == k and r["criterion"] == name]) * 100
                for k in keep]
        ax.plot([k * 100 for k in keep], mean, color=color, marker="o", ms=5, lw=2, label=label)
    const = [np.mean([r["acc_signed_constant"] for r in rows if r["keep"] == k
                      and r["criterion"] == "large_final_same_sign"]) * 100 for k in keep]
    ax.plot([k * 100 for k in keep], const, color=C["blue_dark"], marker="s", ms=4.5, lw=1.8, ls="--",
            label="same, survivors set to signed constants")
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xticks([k * 100 for k in keep])
    ax.set_xticklabels([f"{k*100:g}%" for k in keep])
    ax.minorticks_off()
    ax.set_xlabel("weights kept (log scale)")
    ax.set_ylabel("test accuracy, no training (%)")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=10)
    bs.titles(fig, "A mask alone can classify digits",
              f"Untrained LeNet-300-100 with a one-shot mask, mean of {data['meta']['seeds']} seeds (measured)")
    return bs.save_png(fig, OUT / "supermask.png", alt=ALT["supermask"], caption=CAPTION["supermask"])


def cover():
    import matplotlib.patches as mp

    def draw(ax):
        # 100 weights, 7 kept: the "7%" of the kicker
        keep = {13, 24, 38, 51, 66, 72, 89}
        for k in range(100):
            i, j = divmod(k, 10)
            ax.add_patch(mp.FancyBboxPatch(
                (0.03 + j * 0.097, 0.9 - i * 0.097), 0.08, 0.08, boxstyle="round,pad=0,rounding_size=0.015",
                fc=C["blue"] if k in keep else C["light_gray"], ec="none"))

    bs.cover(OUT / "cover.png", title="Lottery Ticket\nHypothesis", kicker=COVER_KICKER, draw=draw)


# text that depends on the measured numbers (checked against results.json)
ALT = {
    "accuracy": "Test accuracy against the share of weights remaining, five seeds each. The winning ticket stays between 97.6% and 98.2% from 100% down to 2.9% of the weights. The same masks with new random weights fall to 95.2%, and random masks to 92.6%",
    "early": "Iteration of minimum validation loss against the share of weights remaining. The winning ticket falls from 1,390 for the dense network to 930 at 26.3% remaining, then climbs back to 1,490 at 2.9%. The same masks with new random weights stay between 1,330 and 1,500, the end of training",
    "loop": "Diagram of one round: random weights theta 0 are trained, the smallest 20% of weights are pruned to make a mask, the survivors are rewound to theta 0, and the rewound network is retrained and pruned again; a control keeps the mask but draws fresh random weights",
    "supermask": "Test accuracy of an untrained network with a mask against the share of weights kept. Random masks stay near 10%. Keeping the largest final weights peaks at 74.5% with 40% kept. Keeping large weights that kept their sign reaches 81.2% with 40% kept, and 86.7% when the survivors are set to signed constants",
}
CAPTION = {
    "accuracy": "Measured. LeNet-300-100 on MNIST, 5 seeds, 17 training runs per ticket. Pruning schedule of Frankle and Carbin [\\[2, p. 3\\]](#ref-2). Test accuracy at the iteration of minimum validation loss.",
    "early": "Measured, same runs as the chart above. Every network trains for 1,500 iterations, so a value near 1,500 means the validation loss was still falling when training stopped.",
    "loop": "The procedure of Frankle and Carbin [\\[2, p. 2\\]](#ref-2), with the random-reinitialization control they use [\\[2, p. 4\\]](#ref-2).",
    "supermask": "Measured, 5 seeds. One-shot masks built from the weights before and after training one dense network, then applied to the untrained initial weights. Criteria from Zhou et al. [\\[7, p. 7\\]](#ref-7).",
}
COVER_KICKER = "7% of the weights,\nsame accuracy"

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("all", "loop"):
        loop_diagram()
    if mode in ("all", "data"):
        accuracy_chart()
        early_stop_chart()
        supermask_chart()
        cover()
