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
import throughput  # noqa: E402

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

        check_active_params(m, w)
        check_speeds(m, w)


# Parameters actually read per decoded token. It is what the decode ceiling
# divides bandwidth by, so a wrong figure here moves every throughput number on
# the card. None is a legitimate value - it means the lab has not published one,
# and the page says so instead of showing a ceiling derived from a guess.
def check_active_params(m, w):
    if m.MODALITY != "text":
        if getattr(m, "ACTIVE_PARAMS_B", None) is not None:
            err(w, "ACTIVE_PARAMS_B is a decode-time figure; only text models have one")
        return
    if not hasattr(m, "ACTIVE_PARAMS_B"):
        err(w, "text models must declare ACTIVE_PARAMS_B - the parameters read per "
               "decoded token, or None if the lab has not published a count")
        return
    a = m.ACTIVE_PARAMS_B
    if a is None:
        warn(w, "ACTIVE_PARAMS_B is None, so no decode ceiling can be shown for this model")
        return
    if not isinstance(a, (int, float)) or a <= 0:
        err(w, f"ACTIVE_PARAMS_B {a!r} must be a positive count in billions")
    elif m.PARAMS_B and a > m.PARAMS_B:
        err(w, f"ACTIVE_PARAMS_B {a} exceeds PARAMS_B {m.PARAMS_B}; active is a subset")


SPEED_KINDS = {"decode", "prefill"}


# Published throughput measurements. The bar is deliberately high, because the
# reason this page carried no tok/s figures for so long is that self-reported
# ones were unattributable and unreproducible: a number with no chip, no build
# and no context is not evidence of anything. Every record here names whose
# measurement it is and links to it.
def check_speeds(m, w):
    speeds = getattr(m, "SPEEDS", None)
    if speeds is None:
        return
    if not isinstance(speeds, (list, tuple)):
        err(w, "SPEEDS must be a list of measurement records")
        return
    kv_bpt = (getattr(m, "KV", None) or {}).get("bytes_per_token")
    for i, s in enumerate(speeds):
        at = f"{w} [SPEEDS {i}]"
        if not isinstance(s, dict):
            err(at, "each SPEEDS entry must be a dict")
            continue
        if m.MODALITY != "text":
            err(at, "SPEEDS records tokens per second; only text models have them")

        eid = s.get("engine")
        if eid not in R.ENGINE_BY_ID:
            err(at, f"unknown engine {eid!r}")
        elif eid not in getattr(m, "ENGINES", {}):
            err(at, f"engine {eid!r} has no cell in ENGINES for this model")

        chip = s.get("chip")
        if chip not in R.MACHINES:
            err(at, f"unknown chip {chip!r}; it must be a key in data/machines.py")
        elif s.get("mem_gb") is not None and s["mem_gb"] not in R.MACHINES[chip]["mem"]:
            err(at, f"{chip} was never sold with {s['mem_gb']} GB")

        if not s.get("who"):
            err(at, "missing 'who': a measurement with no measurer is a rumour")
        if not str(s.get("url", "")).startswith("http"):
            err(at, "missing or malformed 'url'; the measurement has to be followable")

        got = [k for k in SPEED_KINDS if s.get(k + "_tps") is not None]
        if not got:
            err(at, "a record needs decode_tps or prefill_tps, or it says nothing")
        for k in got:
            v = s[k + "_tps"]
            if not isinstance(v, (int, float)) or v <= 0:
                err(at, f"{k}_tps {v!r} must be a positive tokens/second figure")

        for k in ("context", "gb"):
            v = s.get(k)
            if v is not None and (not isinstance(v, (int, float)) or v <= 0):
                err(at, f"{k} {v!r} must be positive")

        for flag in ("speculative", "batched"):
            if flag in s and not isinstance(s[flag], bool):
                err(at, f"{flag} must be a bool")

        build = s.get("build")
        if build is not None and not (isinstance(build, str) and build.strip()):
            err(at, "build must name the exact checkpoint, or be left out")
        rung = next((r for rungs in (getattr(m, "LADDER", {}) or {}).values()
                     for r in rungs if r.get("label") == build), None)
        if rung is not None and throughput.rung_reason(rung):
            # An expert-pruned build reads the same bytes per token however much
            # of it was deleted, so there is no bound to check it against.
            continue

        # A decode figure is only checkable against the arithmetic when the
        # record says which build and which context it was taken at. Without
        # those it still belongs on the page as someone's measurement, but it
        # cannot be compared with anything - which is the whole complaint
        # against self-reported numbers, so say it out loud.
        if s.get("decode_tps") is not None and not (s.get("gb") and s.get("context")):
            warn(at, "decode figure without both 'gb' and 'context'; it cannot be checked "
                     "against the ceiling or compared with any other measurement")
            continue
        if s.get("decode_tps") is None or chip not in R.MACHINES:
            continue

        # Physical plausibility. Above the bandwidth bound the measurement is
        # either mistyped, taken with speculative decoding, or taken batched -
        # and the record has to say which.
        cap = throughput.ceiling_tps(R.MACHINES[chip]["bw"], s["gb"],
                                     getattr(m, "ACTIVE_PARAMS_B", None),
                                     getattr(m, "PARAMS_B", None),
                                     kv_bpt, s["context"])
        if cap is None:
            continue
        if s["decode_tps"] > cap and not (s.get("speculative") or s.get("batched")):
            err(at, f"{s['decode_tps']} tok/s exceeds the {cap:.1f} tok/s the "
                    f"{chip} memory bandwidth allows for a {s['gb']} GB build at "
                    f"{s['context']} context. Either a figure is wrong, or the run used "
                    "speculative decoding or batching - set speculative/batched and say so "
                    "in the note.")


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


# ---------------------------------------------------------------- machines
# The picker's chip table is also the divisor in every decode ceiling, so a
# typo in a bandwidth figure is not cosmetic.
def check_machines():
    w = "data/machines.py"
    for gen in R.GENS:
        if not any(mc["gen"] == gen for mc in R.MACHINES.values()):
            err(w, f"GENS lists {gen!r} but no chip belongs to it")
    for key, mc in sorted(R.MACHINES.items()):
        at = f"{w} [{key}]"
        if not ID_RE.match(key):
            err(at, "chip keys are lowercase alphanumeric; they appear in the ?chip= query")
        for field in ("label", "gen", "tb"):
            if not mc.get(field):
                err(at, f"missing {field}")
        if mc.get("gen") not in R.GENS:
            err(at, f"gen {mc.get('gen')!r} is not in GENS, so the chip would never be listed")
        if not isinstance(mc.get("bw"), (int, float)) or mc["bw"] <= 0:
            err(at, "bw must be peak memory bandwidth in GB/s; it divides every decode ceiling")
        mem = mc.get("mem")
        if not mem or sorted(mem) != list(mem) or len(set(mem)) != len(mem):
            err(at, "mem must be the ascending, deduplicated list of memory options")
        if not isinstance(mc.get("tb5"), bool):
            err(at, "tb5 must be a bool; it decides whether clustering is warned about")
        if not isinstance(mc.get("ports"), int) or mc["ports"] < 1:
            err(at, "ports must be the Thunderbolt port count")


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
    check_issues()
    check_machines()
    check_global()
    check_no_shadowing()

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
