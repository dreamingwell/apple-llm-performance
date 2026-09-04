#!/usr/bin/env python3
"""Validate everything under data/. Run by CI on every push and pull request.

    python3 tracker/validate.py

Reports every problem it finds, not the first, and exits non-zero if any is
fatal. Warnings do not fail the build but are printed, because a record that is
merely thin is worth seeing without blocking a contribution.

This is the contract an agent has to satisfy. If a rule here feels wrong, change
the rule in a separate commit from the data, so a reviewer can see which of the
two moved.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import registry as R  # noqa: E402

ERRORS = []
WARNINGS = []

ALIAS_OWNER = {}
SEVERITIES = {"critical", "high", "medium", "low"}
KINDS = {"quant", "pruned", "native"}
ID_RE = re.compile(r"^[a-z][a-z0-9]*$")
ISSUE_RE = re.compile(r"^[\w.-]+/[\w.-]+#\d+$")


def err(where, msg):
    ERRORS.append(f"{where}: {msg}")


def warn(where, msg):
    WARNINGS.append(f"{where}: {msg}")


# ------------------------------------------------------------------- engines
def check_engines():
    seen_order = {}
    for m in R.ENGINE_MODULES:
        w = m.__source_file__
        if not ID_RE.match(m.ID):
            err(w, f"ID {m.ID!r} must be lowercase alphanumeric")
        if os.path.basename(w) != f"{m.ID}.py":
            err(w, f"filename must match ID ({m.ID}.py)")
        for mod in m.MODALITIES:
            if mod not in R.MODALITIES:
                err(w, f"unknown modality {mod!r}; expected one of {R.MODALITIES}")
        if m.QUANT_FAMILY not in {"gguf", "mlx", "ds4"}:
            err(w, f"unknown QUANT_FAMILY {m.QUANT_FAMILY!r}")
        order = getattr(m, "DISPLAY_ORDER", None)
        if order is None:
            err(w, "missing DISPLAY_ORDER")
        elif order in seen_order:
            err(w, f"DISPLAY_ORDER {order} already used by {seen_order[order]}")
        else:
            seen_order[order] = m.ID
        for field in ("NAME", "FORMAT", "INTERFACE", "API", "LICENSE", "WHAT", "SITE"):
            if not getattr(m, field, None):
                err(w, f"missing or empty {field}")
        if getattr(m, "SITE", "") and not str(m.SITE).startswith("http"):
            err(w, f"SITE {m.SITE!r} must be a URL; it is linked from the prose")
        aliases = getattr(m, "PROSE_ALIASES", None)
        if not aliases:
            err(w, "PROSE_ALIASES must list the names this engine goes by in the notes")
        for alias in aliases or []:
            if not alias or not alias.strip():
                err(w, "PROSE_ALIASES contains an empty name")
            elif alias in ALIAS_OWNER and ALIAS_OWNER[alias] != m.ID:
                err(w, f"alias {alias!r} is also claimed by {ALIAS_OWNER[alias]!r}; "
                       "an ambiguous name would link to the wrong engine")
            else:
                ALIAS_OWNER[alias] = m.ID
        if len(getattr(m, "WHAT", "")) < 80:
            warn(w, "WHAT is very short; it is the reader's only description of this engine")
        feed = getattr(m, "RELEASE_FEED", None)
        if feed is not None:
            if feed.get("scheme") not in {"release", "semver", "none"}:
                err(w, f"RELEASE_FEED scheme {feed.get('scheme')!r} must be release/semver/none")
            if feed.get("scheme") != "none" and not feed.get("repo"):
                err(w, "RELEASE_FEED needs a repo unless scheme is 'none'")
        for key in getattr(m, "CROSS_ISSUES", []):
            if not ISSUE_RE.match(key):
                err(w, f"malformed issue key {key!r}; expected owner/repo#123")
            elif key not in R.EMETA:
                err(w, f"CROSS_ISSUES cites {key} which has no entry in data/issues/")


# -------------------------------------------------------------------- models
def check_models():
    for m in R.MODEL_MODULES:
        w = m.__source_file__
        if not ID_RE.match(m.ID):
            err(w, f"ID {m.ID!r} must be lowercase alphanumeric")
        if os.path.basename(w) != f"{m.ID}.py":
            err(w, f"filename must match ID ({m.ID}.py)")
        if m.MODALITY not in R.MODALITIES:
            err(w, f"unknown MODALITY {m.MODALITY!r}")
        for field in ("NAME", "ARCH", "LICENSE", "CONTEXT", "HF", "NOTE"):
            if not getattr(m, field, None):
                err(w, f"missing or empty {field}")
        if getattr(m, "PARAMS_B", None) in (None, 0):
            err(w, "PARAMS_B must be the total parameter count in billions")
        if not getattr(m, "SOURCES", None):
            err(w, "SOURCES must cite at least one link; every figure needs a provenance")
        for src in getattr(m, "SOURCES", []):
            if len(src) != 2 or not str(src[1]).startswith("http"):
                err(w, f"malformed SOURCES entry {src!r}; expected (label, url)")
        if len(getattr(m, "NOTE", "")) < 80:
            warn(w, "NOTE is very short; it is the reason to read the page over a spec sheet")

        # engine cells
        cells = getattr(m, "ENGINES", {})
        if not cells:
            err(w, "ENGINES is empty; a model with no engine cell renders no tabs")
        for eid, c in cells.items():
            at = f"{w} [{eid}]"
            if eid not in R.ENGINE_BY_ID:
                err(at, f"unknown engine {eid!r}")
                continue
            eng = R.ENGINE_BY_ID[eid]
            if m.MODALITY not in eng["mods"]:
                err(at, f"engine handles {eng['mods']} but this model is {m.MODALITY!r}")
            if c.get("status") not in R.STATUSES:
                err(at, f"status {c.get('status')!r} must be one of {R.STATUSES}")
            if not c.get("label"):
                err(at, "missing label")
            if not c.get("note"):
                err(at, "missing note; a status with no explanation is not reviewable")
            for key in c.get("issues", []):
                if not ISSUE_RE.match(key):
                    err(at, f"malformed issue key {key!r}")
                elif key not in R.EMETA:
                    err(at, f"cites {key} which has no entry in data/issues/")
        if m.BEST_ENGINE not in cells:
            err(w, f"BEST_ENGINE {m.BEST_ENGINE!r} has no cell in ENGINES")
        elif cells[m.BEST_ENGINE].get("status") == "none":
            err(w, f"BEST_ENGINE {m.BEST_ENGINE!r} is marked out of scope")

        # quant ladder
        lad = getattr(m, "LADDER", {}) or {}
        # only families an in-scope engine would actually load
        fams = {R.FAM[eid] for eid, c in cells.items()
                if eid in R.FAM and c.get("status") != "none"}
        for fam in fams:
            if fam not in lad or not lad[fam]:
                warn(w, f"no measured ladder for the {fam!r} family, which its engines load")
        for fam, rungs in lad.items():
            last = None
            for r in rungs:
                at = f"{w} [{fam} {r.get('label','?')}]"
                if r.get("kind") not in KINDS:
                    err(at, f"kind {r.get('kind')!r} must be one of {sorted(KINDS)}")
                if not isinstance(r.get("gb"), (int, float)) or r["gb"] <= 0:
                    err(at, "gb must be a positive size in gigabytes")
                if r.get("kind") == "quant":
                    if r.get("bpw") is None:
                        err(at, "a quant rung needs bpw")
                    elif not 0.5 <= r["bpw"] <= 20:
                        err(at, f"bpw {r['bpw']} is outside a believable range; check PARAMS_B")
                elif r.get("bpw") is not None:
                    err(at, f"kind {r['kind']!r} must not carry a bpw")
                if not r.get("repo"):
                    err(at, "missing repo")
                if last is not None and r["gb"] > last:
                    err(at, "ladder must be ordered largest first")
                last = r["gb"]

        # KV geometry
        kv = getattr(m, "KV", None)
        if kv is None or set(kv) != {"bytes_per_token", "max_context", "derivation"}:
            err(w, "KV must be {bytes_per_token, max_context, derivation}")
        elif kv["bytes_per_token"] is not None:
            if m.MODALITY != "text":
                err(w, "only text models should declare a per-token KV cost")
            if not kv["derivation"]:
                err(w, "a KV figure needs a derivation saying which layers were counted")
            if not kv["max_context"]:
                err(w, "a KV figure needs max_context to size a stream against")


# ----------------------------------------------------------------- use cases
def check_use_cases():
    seen_order = {}
    for m in R.USE_CASE_MODULES:
        w = m.__source_file__
        if os.path.basename(w) != f"{m.ID}.py":
            err(w, f"filename must match ID ({m.ID}.py)")
        if m.MODALITY not in R.MODALITIES:
            err(w, f"unknown MODALITY {m.MODALITY!r}")
        if m.FIDELITY_GATE not in {b[1] for b in R.__dict__.get("BANDS", [])} | {"full", "mild", "low", "unusable"}:
            err(w, f"FIDELITY_GATE {m.FIDELITY_GATE!r} is not a band name")
        order = getattr(m, "DISPLAY_ORDER", None)
        if order is None:
            err(w, "missing DISPLAY_ORDER")
        elif order in seen_order:
            err(w, f"DISPLAY_ORDER {order} already used by {seen_order[order]}")
        else:
            seen_order[order] = m.ID
        if not m.AXIS:
            err(w, "AXIS must explain how the ranking was decided")
        if not m.RANK:
            err(w, "RANK is empty")
        seen = set()
        for entry in m.RANK:
            if len(entry) != 3:
                err(w, f"RANK entry {entry!r} must be (model_id, metric, value)")
                continue
            mid, metric, value = entry
            if mid not in R.MODEL_BY_ID:
                err(w, f"RANK cites unknown model {mid!r}")
                continue
            if mid in seen:
                err(w, f"RANK lists {mid!r} twice")
            seen.add(mid)
            if R.MODEL_BY_ID[mid]["mod"] != m.MODALITY:
                err(w, f"RANK cites {mid!r} ({R.MODEL_BY_ID[mid]['mod']}) in a "
                       f"{m.MODALITY} category")
            if not metric or not str(value):
                err(w, f"RANK entry for {mid!r} needs both a metric name and a value")


# -------------------------------------------------------------------- issues
def check_issues():
    for m in R.ISSUE_MODULES:
        w = m.__source_file__
        slug = m.REPO.replace("/", "__").replace(".", "_")
        if os.path.basename(w) != f"{slug}.py":
            err(w, f"filename must match REPO ({slug}.py)")
        for num, meta in m.ISSUES.items():
            at = f"{w} [#{num}]"
            if not isinstance(num, int) or num <= 0:
                err(at, "issue number must be a positive integer")
            if meta.get("severity") not in SEVERITIES:
                err(at, f"severity {meta.get('severity')!r} must be one of {sorted(SEVERITIES)}")
            if not meta.get("headline"):
                err(at, "missing headline")
            if not meta.get("why"):
                err(at, "missing 'why'; an issue with no consequence stated is noise")


# ------------------------------------------------------------------- global
def check_global():
    cited = set()
    for mid, cells in R.MATRIX.items():
        for c in cells.values():
            cited.update(c["items"])
    for keys in R.CROSS_BY_ENGINE.values():
        cited.update(keys)
    orphans = sorted(set(R.EMETA) - cited)
    if orphans:
        warn("data/issues", f"{len(orphans)} issues are tracked but cited nowhere: "
                            + ", ".join(orphans[:6]) + ("..." if len(orphans) > 6 else ""))
    prose_blocks = [m.NOTE for m in R.MODEL_MODULES]
    prose_blocks += [c["note"] for m in R.MODEL_MODULES for c in m.ENGINES.values()]
    prose_blocks += [m.WHAT for m in R.ENGINE_MODULES]
    haystack = "\n".join(prose_blocks)
    for alias, eid, _site in R.ENGINE_PROSE_LINKS:
        # An alias drawn from the engine's own name is legitimate even when no
        # note happens to use it yet. Anything else that matches nothing is a
        # typo, and will silently never link.
        if alias in R.ENGINE_BY_ID[eid]["name"]:
            continue
        if not re.search(rf"(?<![\w.-]){re.escape(alias)}(?![\w-])", haystack):
            warn(f"data/engines/{eid}.py",
                 f"PROSE_ALIASES lists {alias!r}, which is neither this engine's name "
                 "nor used in any note; nothing will ever link")

    for key in sorted(R.PR_KEYS):
        if key not in R.EMETA:
            err("data/pr_keys.py", f"{key} is listed as a PR but has no issue entry")
    ids = [m.ID for m in R.MODEL_MODULES]
    if len(ids) != len(set(ids)):
        err("data/models", "duplicate model IDs")
    for mod in R.MODALITIES:
        if not any(m["mod"] == mod for m in R.MODELS):
            warn("data/models", f"no models with modality {mod!r}")
        if not any(u["mod"] == mod for u in R.USE_CASES):
            warn("data/use_cases", f"no use case with modality {mod!r}")


# --------------------------------------------------------------- code shape
# The renderer imports its data from the registry. If it also defines one of
# those names at module level, the local definition silently wins and the data/
# files stop mattering - which is exactly how a hand-maintained PR_KEYS set and
# a 30-entry issue table survived the split and shadowed the real ones.
def check_no_shadowing():
    import ast
    path = os.path.join(HERE, "render_status.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    imported = set()
    assigned = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "registry":
            imported.update(a.asname or a.name for a in node.names)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    assigned[t.id] = node.lineno
    for name in sorted(imported & set(assigned)):
        err(f"tracker/render_status.py:{assigned[name]}",
            f"{name} is imported from the registry and then reassigned here; "
            "the local value would shadow data/ and render stale facts")


def check_watch_state():
    """The polled issue states the page renders its open/closed pills from.

    This is the one input that is written by redirecting a command's stdout over
    it, which is how it once got truncated to nothing. The page still rendered -
    build.py reads whatever is there - so neither the build nor the output check
    noticed. Verify it covers what is tracked.
    """
    path = os.path.join(HERE, "watch-state.txt")
    if not os.path.exists(path):
        err("tracker/watch-state.txt", "missing; run tracker/probe.py")
        return
    keys = set()
    for line in open(path, encoding="utf-8"):
        k = line.split("|", 1)[0].strip()
        if k:
            keys.add(k)
    if not keys:
        err("tracker/watch-state.txt", "is empty; the page would show no issue states at all")
        return
    tracked = set(R.EMETA)
    missing = tracked - {k for k in keys if "@" not in k}
    if len(missing) > len(tracked) // 4:
        err("tracker/watch-state.txt",
            f"has no state for {len(missing)} of {len(tracked)} tracked issues; "
            "it looks truncated - re-run tracker/probe.py")
    elif missing:
        warn("tracker/watch-state.txt",
             f"{len(missing)} tracked issues have no polled state yet: "
             + ", ".join(sorted(missing)[:4]))


def main():
    check_engines()
    check_models()
    check_use_cases()
    check_issues()
    check_global()
    check_no_shadowing()
    check_watch_state()

    for wmsg in WARNINGS:
        print(f"warning: {wmsg}")
    for e in ERRORS:
        print(f"error:   {e}")
    print(f"\n{len(R.MODEL_MODULES)} models, {len(R.ENGINE_MODULES)} engines, "
          f"{len(R.USE_CASE_MODULES)} use cases, {len(R.EMETA)} tracked issues")
    print(f"{len(ERRORS)} errors, {len(WARNINGS)} warnings")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    raise SystemExit(main())
