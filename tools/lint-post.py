#!/usr/bin/env python3
"""Check a post for structure problems and AI-sounding prose.

Usage:
  python3 tools/lint-post.py <post.md> [...]     # check these files
  python3 tools/lint-post.py --changed           # posts/drafts changed vs origin/main
  python3 tools/lint-post.py --strict ...        # warnings also fail

Errors (exit 1): broken front matter, missing images, broken references, math flag wrong.
Warnings: prose tells, style drift. Fix them or keep them on purpose.
"""
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

STOCK_WORDS = [
    "delve", "leverage", "leveraging", "seamless", "seamlessly", "robust", "tapestry",
    "landscape", "realm", "pivotal", "crucial", "paramount", "game-changer", "game changer",
    "revolutionize", "revolutionizing", "revolutionary", "cutting-edge", "unleash",
    "harness", "empower", "elevate", "showcase", "showcasing", "intricate", "meticulous",
    "testament", "embark", "navigate the", "ever-evolving", "in today's", "underscore",
    "vibrant", "bustling", "boast", "furthermore", "moreover", "additionally",
]
FILLER = [
    "it's worth noting", "it is worth noting", "it's important to note", "it is important to note",
    "let's dive", "dive into", "dive deep", "let's explore", "let's take a look", "in this section",
    "in this post, we", "in conclusion", "to sum up", "in summary", "at the end of the day",
    "simply put", "needless to say", "as we've seen", "as we saw", "imagine ", "the beauty of",
    "here's the thing", "the key takeaway", "plays a crucial role", "a wide range of",
]
NOT_BUT = re.compile(r"\b(?:isn't|is not|not)\s+(?:just|only|merely)\b[^.]{0,80}?\bbut\b", re.I)
EM_DASH = re.compile(r"\s?[—–]\s?")
DASH = re.compile(r"\s?[—–]\s?|\w \- \w")  # English: also " - " used as a dash
TAG_OK = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IMG = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)[^)]*\)(\{:[^}]*\})?")
CITE = re.compile(r"\]\(#ref-(\d+)\)")
ANCHOR = re.compile(r'id="ref-(\d+)"')
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})? [+-]\d{4}$")


class Report:
    def __init__(self, path):
        self.path, self.errors, self.warnings = path, [], []

    def err(self, line, msg):
        self.errors.append((line, msg))

    def warn(self, line, msg):
        self.warnings.append((line, msg))


def split_front_matter(text):
    if not text.startswith("---\n"):
        return None, text, 0
    end = text.find("\n---", 4)
    if end < 0:
        return None, text, 0
    fm = text[4:end]
    return fm, text[end + 4:], fm.count("\n") + 2


def prose_lines(body, offset):
    """Yield (line_no, text) for prose: skip code fences, display math, HTML, tables keep."""
    in_code = in_math = False
    for i, line in enumerate(body.split("\n"), start=offset + 1):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if s == "$$" or (s.startswith("$$") and s.count("$$") == 1):
            in_math = not in_math
            continue
        if in_math:
            continue
        # drop inline code and inline math before prose checks
        clean = re.sub(r"`[^`]*`", "", line)
        clean = re.sub(r"\$\$.*?\$\$", "", clean)
        # single-$ math does not render on this site (see assets/js/data/mathjax.js)
        for m in re.finditer(r"(?<![\\$])\$([^$\n]+?)\$", clean):
            if re.search(r"[\\^_{}]", m.group(1)):
                yield i, None, f"single-$ math '${m.group(1)}$' will not render: use $${m.group(1)}$$"
        clean = re.sub(r"\]\([^)]*\)", "]", clean)  # urls
        yield i, line, clean


def check(path: Path) -> Report:
    r = Report(path)
    text = path.read_text(encoding="utf-8")
    fm_text, body, offset = split_front_matter(text)
    if fm_text is None:
        r.err(1, "no YAML front matter")
        return r
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        r.err(1, f"front matter is not valid YAML: {e}")
        return r

    is_draft = "_drafts" in path.parts
    required = ["title", "author", "categories", "tags", "image"] + ([] if is_draft else ["date"])
    for key in required:
        if not fm.get(key):
            r.err(1, f"front matter: missing '{key}'")
    if not fm.get("description"):
        r.warn(1, "front matter: no 'description' (used in search results and the home page)")
    if fm.get("lang") not in ("en", "he"):
        r.warn(1, "front matter: set lang to 'en' or 'he'")
    if "date" in fm and not DATE_RE.match(str(fm["date"])):
        r.err(1, f"front matter: date '{fm['date']}' should look like 2026-11-15 08:00:00 +0200")
    if not is_draft and not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$", path.name):
        r.err(1, "file name should be YYYY-MM-DD-kebab-slug.md")
    for t in fm.get("tags") or []:
        if not TAG_OK.match(str(t)) and fm.get("lang") != "he":
            r.warn(1, f"tag '{t}' should be lowercase-hyphenated")
    img = fm.get("image") or {}
    if isinstance(img, dict) and not img.get("alt"):
        r.err(1, "front matter: image.alt is empty")

    # blank out HTML comments, keeping line numbers
    body = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), body, flags=re.S)

    media = (fm.get("media_subpath") or "").strip("/")

    def resolve(src):
        if re.match(r"^[a-z]+://", src):
            return None
        p = src.lstrip("/") if src.startswith("/") else (f"{media}/{src}" if media else src)
        return ROOT / p

    if isinstance(img, dict) and img.get("path"):
        f = resolve(img["path"])
        if f and not f.exists():
            r.err(1, f"cover image not found: {f.relative_to(ROOT)}")

    # math / mermaid flags
    has_math = "$$" in body
    if has_math and not fm.get("math"):
        r.err(1, "post uses $$ but front matter does not have math: true")
    if fm.get("math") and not has_math:
        r.warn(1, "math: true but no $$ in the post")
    has_mermaid = "```mermaid" in body
    if has_mermaid and not fm.get("mermaid"):
        r.err(1, "post has a mermaid block but mermaid is not true")

    # references
    cited = {int(n) for n in CITE.findall(body)}
    for m in re.finditer(r"\[\\\[(\d+)(?:,[^\]]*)?\\\]\]\(#ref-(\d+)\)", body):
        if m.group(1) != m.group(2):
            r.err(0, f"citation [{m.group(1)}] links to #ref-{m.group(2)}")
    anchors = {int(n) for n in ANCHOR.findall(body)}
    for n in sorted(cited - anchors):
        r.err(0, f"cited [{n}] but there is no <span id=\"ref-{n}\">")
    for n in sorted(anchors - cited):
        r.warn(0, f"reference [{n}] is listed but never cited")

    # line-based checks
    h2 = []
    for i, raw, clean in prose_lines(body, offset):
        if raw is None:
            r.err(i, clean)
            continue
        low = clean.lower()
        for m in IMG.finditer(raw):
            alt, src, attrs = m.group(1), m.group(2), m.group(3) or ""
            if len(alt.strip()) < 15:
                r.err(i, f"image '{src}': alt text missing or too short to describe it")
            if 'w="' not in attrs or 'h="' not in attrs:
                r.warn(i, f"image '{src}': add {{: w=\"..\" h=\"..\" }} with the real size")
            f = resolve(src)
            if f and not f.exists():
                r.err(i, f"image not found: {f.relative_to(ROOT)}")
        if raw.startswith("## "):
            h2.append((i, raw[3:].strip()))
        if raw.lstrip().startswith(("<", "|", "{:")) and not raw.lstrip().startswith("|"):
            continue
        dash = EM_DASH if fm.get("lang") == "he" else DASH
        # a dash alone in a table cell means "none", which is fine
        if dash.search(re.sub(r"\|\s*[—–-]\s*(?=\|)", "|", clean)):
            r.warn(i, "em/en dash as punctuation: use a period, comma, colon or parentheses")
        for w in STOCK_WORDS:
            if re.search(rf"\b{re.escape(w)}\b", low):
                r.warn(i, f"stock word '{w}'")
        for p in FILLER:
            if p in low:
                r.warn(i, f"filler '{p.strip()}'")
        if NOT_BUT.search(clean):
            r.warn(i, "'not just X but Y': say Y")
        if re.search(r"[A-Za-z)]!(\s|$)", clean) and not raw.lstrip().startswith("!"):
            r.warn(i, "exclamation mark")
        if "|" in raw and "$$" in raw and raw.lstrip().startswith("|"):
            for seg in re.findall(r"\$\$(.*?)\$\$", raw):
                if "|" in seg:
                    r.err(i, "a '|' inside math in a table row breaks the table: use \\vert or \\mid")
        if "{{" in raw or "{%" in raw:
            if "{% raw %}" not in body:
                r.warn(i, "'{{' or '{%' is read by Liquid: add a space or wrap in {% raw %}")

    numbered = [t for _, t in h2 if re.match(r"^\d{2}\. ", t)]
    others = [t for _, t in h2 if not re.match(r"^\d{2}\. ", t) and t not in ("Sources", "References")]
    if numbered and others:
        r.warn(0, "some H2 headings are numbered ('## 01. ...') and some are not")
    for k, t in enumerate(numbered, start=1):
        if not t.startswith(f"{k:02d}. "):
            r.warn(0, f"heading '{t}' breaks the 01, 02, 03 sequence")
            break
    return r


def changed_posts():
    base = subprocess.run(["git", "merge-base", "HEAD", "origin/main"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip() or "HEAD"
    out = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AM", base], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    out += subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "_posts", "_drafts"],
                          cwd=ROOT, capture_output=True, text=True).stdout.split()
    return sorted({ROOT / p for p in out if re.match(r"^_(posts|drafts)/[^/]+\.md$", p)})


def main(argv):
    strict = "--strict" in argv
    args = [a for a in argv if not a.startswith("--")]
    files = changed_posts() if "--changed" in argv else [Path(a).resolve() for a in args]
    if not files:
        print("no posts to check" if "--changed" in argv else __doc__)
        return 0
    failed = False
    for f in files:
        rep = check(f)
        name = f.relative_to(ROOT) if f.is_relative_to(ROOT) else f
        for kind, items in (("error", rep.errors), ("warn", rep.warnings)):
            for line, msg in items:
                print(f"{name}:{line}: {kind}: {msg}")
        print(f"{name}: {len(rep.errors)} errors, {len(rep.warnings)} warnings")
        failed |= bool(rep.errors) or (strict and bool(rep.warnings))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
