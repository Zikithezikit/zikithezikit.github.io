"""Shared look for the blog's charts, diagrams and covers.

Charts:   bs.apply(); fig, ax = plt.subplots(); ...; bs.titles(fig, ...); bs.save_png(fig, path, alt=..)
Diagrams: s = bs.Svg(900, 400, "Title", "subtitle"); a = s.box(...); s.arrow(a, b); s.save(path, alt=..)
Cover:    bs.cover(path, title="Ribbon filters", kicker="9 bits per key")

save_png / save / cover print the Markdown image line with the real w and h.
"""
from html import escape
from pathlib import Path

COLORS = {
    "ink": "#1f2937",
    "muted": "#6b7280",
    "faint": "#9ca3af",
    "grid": "#e5e7eb",
    "line": "#d1d5db",
    "blue": "#2F6BFF",
    "blue_dark": "#1d4fd0",
    "green": "#13805c",
    "gold": "#c4972f",
    "gold_dark": "#8a6a14",
    "red": "#b8473d",
    "gray": "#6b6b6b",
    "light_blue": "#e6eeff",
    "light_green": "#e8fbf3",
    "light_gold": "#fff7dc",
    "light_gray": "#f2f2f2",
    "white": "#ffffff",
}
SERIES = [COLORS[k] for k in ("blue", "green", "gold", "red", "gray")]
SANS = "Arial, Helvetica, sans-serif"
MONO = "Menlo, Consolas, monospace"


def _c(name):
    return COLORS.get(name, name)


def _print_md(path, w, h, alt, caption):
    print(f'![{alt or "ALT TEXT: say what it shows"}]({Path(path).name}){{: w="{w}" h="{h}" .shadow }}')
    print(f"_{caption or 'Caption: what is measured or where it is from.'}_\n")


# ---------- charts (matplotlib) ----------

def apply():
    import matplotlib as mpl
    from cycler import cycler

    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
        "font.size": 11,
        "text.color": COLORS["ink"],
        "axes.labelcolor": COLORS["muted"],
        "axes.edgecolor": COLORS["line"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "axes.prop_cycle": cycler(color=SERIES),
        "grid.color": COLORS["grid"],
        "grid.linewidth": 0.8,
        "xtick.color": COLORS["muted"],
        "ytick.color": COLORS["muted"],
        "ytick.left": False,
        "legend.frameon": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    })


def titles(fig, title, subtitle=None):
    fig.suptitle(title, x=0.02, ha="left", fontsize=15, fontweight="bold", color=COLORS["ink"])
    if subtitle:
        fig.text(0.02, 0.905, subtitle, ha="left", fontsize=10.5, color=COLORS["muted"])
    fig.tight_layout(rect=(0, 0, 1, 0.9 if subtitle else 0.94))


def save_png(fig, path, alt=None, caption=None, dpi=150):
    import matplotlib.pyplot as plt

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi)
    w, h = (round(v) for v in fig.get_size_inches() * dpi)
    plt.close(fig)
    _print_md(path, w, h, alt, caption)
    return w, h


# ---------- diagrams (hand-written SVG) ----------

class Box:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2


class Svg:
    def __init__(self, width, height, title=None, subtitle=None):
        self.w, self.h, self.title = width, height, title or ""
        self.parts = [f'<rect width="{width}" height="{height}" rx="10" fill="#ffffff"/>']
        if title:
            self.text(width / 2, 30, title, size=19, bold=True)
        if subtitle:
            self.text(width / 2, 53, subtitle, size=12.5, color="muted")

    def text(self, x, y, s, size=14, color="ink", anchor="middle", bold=False, mono=False):
        weight = ' font-weight="bold"' if bold else ""
        family = f' font-family="{MONO}"' if mono else ""
        self.parts.append(
            f'<text x="{x:g}" y="{y:g}" font-size="{size}" fill="{_c(color)}" '
            f'text-anchor="{anchor}"{weight}{family}>{escape(str(s))}</text>')

    def box(self, x, y, w, h, label=None, fill="light_gray", stroke="gray", sub=None, mono=False):
        self.parts.append(
            f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="6" '
            f'fill="{_c(fill)}" stroke="{_c(stroke)}" stroke-width="1.4"/>')
        if label:
            ty = y + h / 2 + (0 if sub else 5)
            self.text(x + w / 2, ty, label, size=15, bold=True, mono=mono)
        if sub:
            self.text(x + w / 2, y + h / 2 + 20, sub, size=12, color="muted")
        return Box(x, y, w, h)

    def arrow(self, a, b, label=None, color="gray", elbow=False):
        """Arrow from box a to box b, right/left or down/up edges; elbow=True for a 90-degree path."""
        if abs(b.cx - a.cx) >= abs(b.cy - a.cy):
            x1, y1 = (a.x + a.w, a.cy) if b.cx > a.cx else (a.x, a.cy)
            x2, y2 = (b.x, b.cy) if b.cx > a.cx else (b.x + b.w, b.cy)
        else:
            x1, y1 = (a.cx, a.y + a.h) if b.cy > a.cy else (a.cx, a.y)
            x2, y2 = (b.cx, b.y) if b.cy > a.cy else (b.cx, b.y + b.h)
        if elbow and x1 != x2 and y1 != y2:
            d = f"M{x1:g},{y1:g} H{(x1 + x2) / 2:g} V{y2:g} H{x2:g}"
        else:
            d = f"M{x1:g},{y1:g} L{x2:g},{y2:g}"
        mid = f"m{len(self.parts)}"
        self.parts.append(
            f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" '
            f'markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            f'fill="{_c(color)}"/></marker></defs>'
            f'<path d="{d}" fill="none" stroke="{_c(color)}" stroke-width="1.8" marker-end="url(#{mid})"/>')
        if label:
            self.text((x1 + x2) / 2, (y1 + y2) / 2 - 8, label, size=12.5, color="muted")

    def save(self, path, alt=None, caption=None):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'width="{self.w}" height="{self.h}" font-family="{SANS}" role="img" '
               f'aria-label="{escape(alt or self.title)}">' + "".join(self.parts) + "</svg>")
        path.write_text(svg, encoding="utf-8")
        _print_md(path, self.w, self.h, alt, caption)
        return self.w, self.h


# ---------- cover ----------

def cover(path, title, kicker=None, draw=None):
    """1200x630 cover. draw(ax) may add one visual on the right half (axes in 0..1 units)."""
    import matplotlib.pyplot as plt

    apply()
    fig = plt.figure(figsize=(8, 4.2), dpi=150)  # 1200 x 630
    fig.text(0.06, 0.58, title, fontsize=34, fontweight="bold", color=COLORS["ink"], va="bottom", wrap=True)
    if kicker:
        fig.text(0.06, 0.44, kicker, fontsize=22, color=COLORS["blue"], va="top")
    if draw:
        ax = fig.add_axes((0.55, 0.1, 0.4, 0.8))
        ax.set_axis_off()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        draw(ax)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"cover: {path} (1200 x 630)")
