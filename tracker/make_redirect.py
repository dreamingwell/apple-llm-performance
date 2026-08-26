#!/usr/bin/env python3
"""Emit a forwarding stub for a route that used to serve the tracker.

    python3 tracker/make_redirect.py --from research/mlx-models [--card card-x.jpg]

The canonical home is the GitHub Pages site. Two older addresses on
dreamingwell.com still receive traffic and always will - `/research/mlx-models/`
is the URL the original Reddit post used - so each serves a stub instead of a
copy of the page.

GitHub Pages cannot issue a 301, so the stub does the job four ways: a meta
refresh for scrapers and no-JS clients, `rel=canonical` so search engines
consolidate, Open Graph tags so a link preview still resolves, and a script that
carries the query string across. That last part matters: the tracker encodes the
selected chip, memory, machine count and use case in the query string, so
dropping it would break every deep link anyone has shared.

Every old route forwards straight to the Pages site rather than chaining through
the other old route - one hop, not two.
"""
import argparse

TARGET = "https://dreamingwell.github.io/apple-llm-performance/"
TITLE = "Apple LLM Performance Tracker"
DESC = "Open weight AI models and their Apple M-series compatibility."

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="DreamingWell">
<meta property="og:url" content="{target}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{target}{card}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{target}{card}">
<style>
  :root {{ color-scheme: light dark; }}
  body {{ margin: 0; min-height: 100vh; display: grid; place-items: center;
    font: 400 1rem/1.6 "IBM Plex Sans", system-ui, -apple-system, sans-serif;
    background: #eef1f5; color: #141a20; padding: 2rem; text-align: center; }}
  .eyebrow {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .7rem;
    letter-spacing: .14em; text-transform: uppercase; color: #a85a26; }}
  h1 {{ font-size: 1.4rem; margin: .6rem 0 .4rem; letter-spacing: -.02em; }}
  p {{ margin: .3rem 0; }}
  .muted {{ color: #5f6b78; font-size: .88rem; max-width: 34rem; }}
  a {{ color: #a85a26; }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #0e1216; color: #e3e8ee; }}
    .eyebrow, a {{ color: #de8a4c; }}
    .muted {{ color: #8894a2; }}
  }}
</style>
</head>
<body>
<main>
  <span class="eyebrow">This page has moved</span>
  <h1>{title}</h1>
  <p><a id="go" href="{target}">{target}</a></p>
  <p class="muted">It is open source now, so it lives with its repository. The old
  <code>/{route}/</code> address still works and always will.</p>
</main>
<script>
  (function () {{
    var to = "{target}" + (location.search || "") + (location.hash || "");
    var a = document.getElementById("go");
    if (a) a.setAttribute("href", to);
    location.replace(to);
  }})();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="route", required=True,
                    help="the old route, e.g. research/mlx-models")
    ap.add_argument("--card", default="card.jpg",
                    help="card filename on the target site")
    a = ap.parse_args()
    print(HTML.format(target=TARGET, title=TITLE, desc=DESC,
                      route=a.route.strip("/"), card=a.card), end="")


if __name__ == "__main__":
    main()
