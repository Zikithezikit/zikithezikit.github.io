"""Figures for the {{SLUG}} post. Run: python3 _figures/{{SLUG}}/make_figures.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "figures"))
import blogstyle as bs  # noqa: E402

OUT = ROOT / "assets" / "images" / "{{SLUG}}"


def cover():
    bs.cover(OUT / "cover.png", title="Two to six words", kicker="the key number")


def example_chart():
    import matplotlib.pyplot as plt

    bs.apply()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    labels, values = ["A", "B", "C"], [3.2, 5.1, 4.4]
    bars = ax.bar(labels, values, color=bs.COLORS["blue"])
    ax.bar_label(bars, fmt="%.1f")
    bs.titles(fig, "What the chart answers", "Units, and where the numbers come from")
    bs.save_png(fig, OUT / "example.png", alt="Bars for A, B and C: B is highest at 5.1",
                caption="Made-up numbers. Replace with the real source.")


def example_diagram():
    s = bs.Svg(900, 300, "What the diagram shows", "One line on how to read it")
    a = s.box(60, 130, 200, 70, "input", fill="light_blue")
    b = s.box(350, 130, 200, 70, "step", fill="light_green")
    c = s.box(640, 130, 200, 70, "output", fill="light_gold")
    s.arrow(a, b)
    s.arrow(b, c, label="maybe")
    s.save(OUT / "example.svg", alt="Input goes to a step, which produces the output")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    cover()
    # example_chart()
    # example_diagram()
