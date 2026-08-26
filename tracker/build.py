#!/usr/bin/env python3
"""Build the site into docs/, which GitHub Pages serves.

    python3 tracker/build.py

Renders the page from tracker/engines.py (the hand-maintained facts),
tracker/quants.py (measured quant ladders) and tracker/watch-state.txt (the last
polled issue states), wraps it in a complete HTML document, and copies the
social card in under a content-hashed name so CDNs pick up changes.

Everything is standard library. No install step, no network access - the build
is reproducible offline from what is committed.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
SITE = os.path.join(ROOT, "docs")
sys.path.insert(0, HERE)

import render_status  # noqa: E402

# The renderer emits a bare fragment because the same output is also published
# as a Claude artifact, where the host supplies the document shell. Served from
# a plain web server it needs a real <head>, or Open Graph parsers find nothing.
SPLIT = '<div class="wrap">'
DOC = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
{head}
</head>
<body>
{body}
</body>
</html>
"""


def wrap(page):
    i = page.find(SPLIT)
    if i == -1:
        raise SystemExit("build: split marker not found in rendered page")
    return DOC.format(head=page[:i].strip(), body=page[i:].strip())


def check(page):
    """Refuse to ship a page with control characters in it.

    This is not hypothetical: a CSS rule once carried `content: "\\2212"` through
    a non-raw Python string, where `\\221` is an octal escape. The page shipped
    with U+0091 in it and rendered a tofu box followed by a stray "2".
    """
    bad = sorted({ord(c) for c in page
                  if ord(c) < 9 or 13 < ord(c) < 32 or 0x7f <= ord(c) <= 0x9f})
    if bad:
        raise SystemExit("build: control characters in output: "
                         + ", ".join(f"U+{c:04X}" for c in bad))


def main():
    os.makedirs(SITE, exist_ok=True)
    page = wrap(render_status.render())
    check(page)

    out = os.path.join(SITE, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)

    card = os.path.join(ASSETS, "og-card.jpg")
    if os.path.exists(card):
        digest = hashlib.sha256(open(card, "rb").read()).hexdigest()[:10]
        shutil.copy(card, os.path.join(SITE, f"card-{digest}.jpg"))
        shutil.copy(card, os.path.join(SITE, "card.jpg"))

    # Pages would otherwise hand the tree to Jekyll, which mangles raw HTML.
    open(os.path.join(SITE, ".nojekyll"), "w").close()

    print(f"build: wrote {os.path.relpath(out, ROOT)} ({len(page):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
