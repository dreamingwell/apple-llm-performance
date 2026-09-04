#!/usr/bin/env python3
"""Refresh tracker/watch-state.txt: the current state of every tracked issue.

    GITHUB_TOKEN=... python3 tracker/probe.py > tracker/watch-state.txt

Prints one `key|state|headline` line per item, plus one per engine release feed.
The watchlist is not a separate list to maintain - it is derived from the issue
metadata already in engines.py and render_status.py, so adding an issue there is
enough and this picks it up on the next run.

Uses the REST API over urllib so the only requirement is Python. A token is
effectively required: unauthenticated GitHub allows 60 requests an hour and this
makes a little over a hundred. In GitHub Actions the automatic GITHUB_TOKEN is
enough - see .github/workflows/refresh.yml.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import registry as R         # noqa: E402
import render_status as rs   # noqa: E402

META = dict(rs.META)
API = "https://api.github.com/"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""


def get(path):
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "apple-llm-performance-tracker",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            print(f"probe: rate limited on {path} - set GITHUB_TOKEN", file=sys.stderr)
        return None
    except Exception:
        return None


def probe_issue(key):
    repo, num = key.split("#")
    d = get(f"repos/{repo}/issues/{num}")
    if not d:
        return None
    state = d.get("state", "open")
    if (d.get("pull_request") or {}).get("merged_at"):
        state = "MERGED"
    return f"{key}|{state}|{META.get(key, ('', key, ''))[1][:96]}"


def probe_release(feed):
    repo, scheme = feed["repo"], feed["scheme"]
    if not repo or scheme == "none":
        return None
    if scheme == "semver":
        # llama.cpp publishes hourly b##### build tags alongside semver releases;
        # only the semver ones mean "a release happened".
        tags = get(f"repos/{repo}/tags?per_page=40") or []
        tag = next((t["name"] for t in tags if t.get("name", "").startswith("v")), None)
    else:
        tag = (get(f"repos/{repo}/releases/latest") or {}).get("tag_name")
    return f"{repo}@release|{tag}|latest release" if tag else None


def main():
    if not TOKEN:
        print("probe: no GITHUB_TOKEN set; expect rate limiting", file=sys.stderr)
    lines = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        lines += [r for r in pool.map(probe_issue, sorted(META)) if r]
        lines += [r for r in pool.map(probe_release, R.RELEASE_FEEDS) if r]
    if not lines:
        print("probe: nothing fetched, refusing to emit an empty state", file=sys.stderr)
        return 1
    # A partial fetch is a failure, not a shorter watchlist. Rate limiting can
    # drop most of the results while every individual request still "succeeds",
    # and the caller usually redirects stdout straight over the state file.
    expected = len(META) + len(R.RELEASE_FEEDS)
    if len(lines) < expected // 2:
        print(f"probe: only {len(lines)} of {expected} items came back - refusing to "
              "emit a truncated watchlist", file=sys.stderr)
        return 1

    sys.stdout.write("\n".join(lines) + "\n")
    print(f"probe: {len(lines)} items", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
