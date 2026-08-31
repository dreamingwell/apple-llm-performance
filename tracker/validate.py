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
import datetime
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
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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


# ------------------------------------------------------------------ hardware
# The picker's chip table lives in the page's JavaScript, which is the only
# place that knows which memory sizes a chip is actually offered in. A price
# record for a chip or a memory size the picker does not offer would never
# render, so it is read back out here rather than duplicated into data/.
MACHINES_RE = re.compile(
    r"""(\w+):\s*\{\{[^\n]*?label:\s*"([^"]+)"[^\n]*?mem:\s*\[([^\]]*)\]""")


def picker_machines():
    """chip id -> (label, {memory sizes}) as the page's picker offers them."""
    src = open(os.path.join(HERE, "render_status.py"), encoding="utf-8").read()
    start = src.find("var MACHINES = {{")
    end = src.find("}};", start)
    if start == -1 or end == -1:
        return None
    out = {}
    for cid, label, mems in MACHINES_RE.findall(src[start:end]):
        out[cid] = (label, {int(g) for g in mems.replace(" ", "").split(",") if g})
    return out or None


def check_hardware():
    machines = picker_machines()
    if machines is None:
        err("tracker/validate.py", "could not read the MACHINES table out of "
                                   "render_status.py; the picker's chip table moved and "
                                   "picker_machines() needs updating")
        return

    priced = set()
    for m in R.HARDWARE_MODULES:
        w = m.__source_file__
        if not ID_RE.match(m.ID):
            err(w, f"ID {m.ID!r} must be lowercase alphanumeric")
        if os.path.basename(w) != f"{m.ID}.py":
            err(w, f"filename must match ID ({m.ID}.py)")
        if m.ID not in machines:
            err(w, f"{m.ID!r} is not a chip the picker offers; a price for a machine "
                   "nobody can select would never render")
            continue
        label, mems = machines[m.ID]
        if m.LABEL != label:
            err(w, f"LABEL {m.LABEL!r} does not match the picker's {label!r}")

        prices = getattr(m, "PRICES", {})
        unpriced = getattr(m, "UNPRICED", {})
        if not prices and not unpriced:
            err(w, "neither PRICES nor UNPRICED; an empty record says nothing")
        for gb in sorted(set(prices) & set(unpriced)):
            err(w, f"{gb} GB is both priced and listed as unpriced")
        for gb, why in unpriced.items():
            if gb not in mems:
                err(w, f"UNPRICED lists {gb} GB, which the picker does not offer for "
                       f"{m.ID}")
            elif not why:
                err(w, f"UNPRICED[{gb}] must say why there is no figure")

        for gb, e in prices.items():
            at = f"{w} [{gb} GB]"
            if gb not in mems:
                err(at, f"the picker does not offer {gb} GB on {m.ID}; "
                        f"it offers {sorted(mems)}")
            usd = e.get("usd")
            if not isinstance(usd, int) or isinstance(usd, bool) or usd <= 0:
                err(at, "usd must be a positive whole number of dollars")
            elif usd > 100000:
                err(at, f"usd {usd} is beyond anything Apple sells; check the figure")
            if e.get("basis") not in R.PRICE_BASES:
                err(at, f"basis {e.get('basis')!r} must be one of "
                        f"{sorted(R.PRICE_BASES)}")
            if e.get("chassis") not in R.CHASSIS:
                err(at, f"chassis {e.get('chassis')!r} must be one of "
                        f"{sorted(R.CHASSIS)} - a price has to say what kind of "
                        "machine it buys, because the same chip does not sustain "
                        "the same throughput in a fanless laptop as in a Studio")
            if not e.get("config"):
                err(at, "missing config; a price with no machine attached is not "
                        "checkable")
            as_of = e.get("as_of", "")
            if not DATE_RE.match(str(as_of)):
                err(at, f"as_of {as_of!r} must be YYYY-MM-DD; a price with no date is a "
                        "liability")
            else:
                try:
                    when = datetime.date.fromisoformat(as_of)
                except ValueError:
                    err(at, f"as_of {as_of!r} is not a real date")
                else:
                    if when > datetime.date.today():
                        err(at, f"as_of {as_of} is in the future")
            src = e.get("source")
            if not src or len(src) != 2 or not str(src[1]).startswith("http"):
                err(at, f"malformed source {src!r}; expected (label, url)")
            if gb in mems:
                priced.add((m.ID, gb))

    for cid, (label, mems) in machines.items():
        if not any(c == cid for c, _ in priced):
            warn("data/hardware", f"no price on record for any {label} configuration")
            continue
        missing = sorted(g for g in mems if (cid, g) not in priced)
        for gb in missing:
            mod = next((m for m in R.HARDWARE_MODULES if m.ID == cid), None)
            if mod is not None and gb in getattr(mod, "UNPRICED", {}):
                continue
            warn(f"data/hardware/{cid}.py", f"no price for the {gb} GB {label}")


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


def main():
    check_engines()
    check_models()
    check_use_cases()
    check_hardware()
    check_issues()
    check_global()
    check_no_shadowing()

    for wmsg in WARNINGS:
        print(f"warning: {wmsg}")
    for e in ERRORS:
        print(f"error:   {e}")
    priced = sum(len(h["prices"]) for h in R.HARDWARE.values())
    print(f"\n{len(R.MODEL_MODULES)} models, {len(R.ENGINE_MODULES)} engines, "
          f"{len(R.USE_CASE_MODULES)} use cases, {len(R.EMETA)} tracked issues, "
          f"{priced} priced configurations")
    print(f"{len(ERRORS)} errors, {len(WARNINGS)} warnings")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    raise SystemExit(main())
