#!/usr/bin/env python3
"""Re-measure one model's quant ladder from Hugging Face and rewrite its file.

    python3 tracker/measure.py --model qwen38
    python3 tracker/measure.py --model qwen38 --dry-run
    python3 tracker/measure.py --all            # rewrites 20+ files; see AGENTS.md

Scoped to one model on purpose. The LADDER block lives in data/models/<id>.py, so
measuring one model touches one file and cannot conflict with another agent's
model. --all exists for a deliberate sweep, not for routine work: it rewrites
every model file and will collide with every open pull request.

gb is summed repo bytes. bpw is gb*8/PARAMS_B, which is the *effective* bits per
weight rather than whatever the quant is named - the two diverge badly on MoE
models, where GLM-4.7's "UD-IQ1_S" is really 2.17 bpw because the non-expert
tensors are carried at higher precision.

Rungs whose loss is structural rather than numeric (REAP expert pruning) are
marked kind="pruned" and carry no bpw, because bits-per-surviving-weight says
nothing about the experts that were deleted. Media checkpoints are marked
kind="native" for the same reason: they bundle text encoders and a VAE, so repo
bytes over transformer parameters is not a precision figure at all.
"""
import argparse
import collections
import json
import os
import re
import sys
import urllib.request
from pprint import pformat

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import registry as R  # noqa: E402

# Draft heads, projectors and imatrix files are not weights anyone serves.
DRAFT = re.compile(r"(mmproj|^mtp-|-mtp|dflash|dspark|eagle3|imatrix|Qwen3\.5-\d|MTP)", re.I)
PRUNED = re.compile(r"(REAP|reap\d)", re.I)

MIN_GB_GGUF = 1.0     # below this a .gguf is a projector, not a model
MIN_GB_MLX = 0.05     # TTS checkpoints are hundreds of megabytes


def api(url):
    try:
        with urllib.request.urlopen(url) as r:
            return json.load(r)
    except Exception as e:
        print(f"  ERR {url}: {e}", file=sys.stderr)
        return []


def tree(repo):
    return api(f"https://huggingface.co/api/models/{repo}/tree/main?recursive=true")


def kind_of(mid, repo, label):
    if R.MODEL_BY_ID[mid]["mod"] != "text":
        return "native"
    return "pruned" if PRUNED.search(repo) or PRUNED.search(label) else "quant"


def rung(mid, repo, label, gb):
    kind = kind_of(mid, repo, label)
    bpw = round(gb * 8 / R.PARAMS[mid], 2) if kind == "quant" else None
    return {"label": label, "repo": repo, "gb": round(gb, 2), "kind": kind, "bpw": bpw}


def gguf_rungs(mid, repo, only):
    """One rung per quant name in the repo, summing its shards."""
    sizes = collections.defaultdict(int)
    for f in tree(repo):
        p = f.get("path", "")
        if not p.endswith(".gguf"):
            continue
        base = re.sub(r"\.gguf$", "", re.sub(r"-\d{5}-of-\d{5}", "", p.split("/")[-1]))
        if DRAFT.search(base):
            continue
        if only and not only.search(base):
            continue
        sizes[base] += f.get("size", 0)
    return [rung(mid, repo, k, v / 1e9) for k, v in sizes.items() if v / 1e9 >= MIN_GB_GGUF]


def mlx_rungs(mid, repo):
    """An MLX repo is one precision, so it is one rung: the sum of its tensors."""
    total = sum(f.get("size", 0) for f in tree(repo)
                if f.get("path", "").endswith(".safetensors"))
    gb = total / 1e9
    if gb < MIN_GB_MLX:
        return []
    return [rung(mid, repo, repo.split("/")[-1], gb)]


def thin(rungs, keep=9):
    """Drop rungs within 3% of a larger sibling - same fit, no extra information."""
    rungs = sorted(rungs, key=lambda r: -r["gb"])
    out = []
    for r in rungs:
        if (out and r["gb"] > out[-1]["gb"] * 0.97
                and r["kind"] == out[-1]["kind"] and r["gb"] > 1):
            continue
        out.append(r)
    if len(out) <= keep:
        return out
    idx = sorted({0, len(out) - 1}
                 | {round(i * (len(out) - 1) / (keep - 1)) for i in range(keep)})
    return [out[i] for i in idx]


def measure(mid):
    mod = MODULE[mid]
    srcs = getattr(mod, "QUANT_SOURCES", {}) or {}
    if not srcs:
        print(f"{mid}: no QUANT_SOURCES to measure", file=sys.stderr)
        return None
    # Some repos hold more than one checkpoint - antirez/deepseek-v4-gguf carries
    # both Flash and Pro - so without a filter each model absorbs the other's
    # files and the bits-per-weight figure comes out nonsense.
    filters = {fam: re.compile(pat, re.I)
               for fam, pat in (getattr(mod, "QUANT_FILTER", {}) or {}).items()}
    ladder = {}
    for fam, repos in srcs.items():
        rungs = []
        for repo in repos:
            rungs += (gguf_rungs(mid, repo, filters.get(fam))
                      if fam in ("gguf", "ds4") else mlx_rungs(mid, repo))
        ladder[fam] = thin(rungs)
    return ladder


def show(mid, ladder):
    print(f"== {mid}")
    for fam, rungs in ladder.items():
        if not rungs:
            print(f"  {fam}: (nothing found)")
            continue
        print(f"  {fam}:")
        for r in rungs:
            b = f"{r['bpw']:5.2f} bpw" if r["bpw"] else f"  {r['kind']:7s}"
            print(f"    {r['gb']:8.2f} GB  {b}  {r['label'][:64]}")


def splice(path, ladder):
    """Replace only the LADDER assignment, leaving every other byte alone."""
    with open(path, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"^LADDER = ", src, re.M)
    if not m:
        raise SystemExit(f"{path}: no LADDER assignment to replace")
    i = src.index("{", m.end())
    depth, j = 0, i
    while j < len(src):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                j += 1
                break
        j += 1
    new = src[:m.end()] + pformat(ladder, width=96, sort_dicts=False) + src[j:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--model", help="model id, matching data/models/<id>.py")
    g.add_argument("--all", action="store_true",
                   help="sweep every model; rewrites every file, conflicts with open PRs")
    ap.add_argument("--dry-run", action="store_true", help="print the ladder, write nothing")
    a = ap.parse_args()

    if a.model and a.model not in MODULE:
        raise SystemExit(f"unknown model {a.model!r}; have: {', '.join(sorted(MODULE))}")
    ids = sorted(MODULE) if a.all else [a.model]

    changed = []
    for mid in ids:
        ladder = measure(mid)
        if ladder is None:
            continue
        show(mid, ladder)
        if a.dry_run:
            continue
        path = os.path.join(ROOT, "data", "models", f"{mid}.py")
        before = open(path, encoding="utf-8").read()
        splice(path, ladder)
        if open(path, encoding="utf-8").read() != before:
            changed.append(mid)

    if a.dry_run:
        print("\ndry run: nothing written")
    elif changed:
        print(f"\nrewrote: {', '.join(changed)}")
        print("now run: python3 tracker/validate.py && python3 tracker/build.py")
    else:
        print("\nno change")


MODULE = {m.ID: m for m in R.MODEL_MODULES}

if __name__ == "__main__":
    main()
