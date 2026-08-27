#!/usr/bin/env python3
"""Load data/ and present it in the shape the renderer expects.

The data lives as one file per record - one model, one engine, one use case, one
issue tracker - so two agents adding two models never touch the same file. This
module is the only place that knows how those files assemble into the structures
the page renders from, which means a schema change happens here and in
tracker/validate.py rather than scattered through the renderer.

Nothing here validates. Loading is deliberately permissive so validate.py can
report every problem at once with a useful message, rather than the first one as
a traceback.
"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

MODALITIES = ["text", "image", "video", "audio"]
STATUSES = ["works", "degraded", "blocked", "none"]

# works/degraded/blocked/none -> the CSS verdict classes the page uses
SCLASS = {"works": "ready", "degraded": "degraded", "blocked": "blocked", "none": "unknown"}


def _load_dir(sub):
    """Import every .py in data/<sub>/ as a module, sorted by filename."""
    d = os.path.join(DATA, sub)
    out = []
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        if not name.endswith(".py") or name.startswith("_"):
            continue
        path = os.path.join(d, name)
        spec = importlib.util.spec_from_file_location(f"data_{sub}_{name[:-3]}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.__source_file__ = os.path.relpath(path, ROOT)
        out.append(mod)
    return out


MODEL_MODULES = _load_dir("models")
ENGINE_MODULES = _load_dir("engines")
USE_CASE_MODULES = _load_dir("use_cases")
ISSUE_MODULES = _load_dir("issues")


# --------------------------------------------------------------------- engines
def _engine(m):
    e = {"id": m.ID, "name": m.NAME, "mods": list(m.MODALITIES), "fmt": m.FORMAT,
         "surface": m.INTERFACE, "api": m.API, "lic": m.LICENSE, "repo": m.REPO,
         "what": m.WHAT, "api_kind": "api"}
    if getattr(m, "API_DETAIL", None):
        e["api_detail"] = m.API_DETAIL
    return e


# Tab order comes from each engine's DISPLAY_ORDER, not from the filename, so
# adding an engine cannot silently reshuffle every card.
ENGINE_MODULES.sort(key=lambda m: (getattr(m, "DISPLAY_ORDER", 9999), m.ID))
ENGINES = [_engine(m) for m in ENGINE_MODULES]
ENGINE_BY_ID = {e["id"]: e for e in ENGINES}

ENGINE_SITES = {m.ID: m.SITE for m in ENGINE_MODULES}

# Longest alias first, so "vLLM Metal" is matched before a shorter alias could
# claim part of it, and "MLX-Audio" before anything that is a prefix of it.
ENGINE_PROSE_LINKS = sorted(
    ((alias, m.ID, m.SITE) for m in ENGINE_MODULES for alias in m.PROSE_ALIASES),
    key=lambda t: -len(t[0]))

FAM = {m.ID: m.QUANT_FAMILY for m in ENGINE_MODULES}
CROSS_BY_ENGINE = {m.ID: list(m.CROSS_ISSUES) for m in ENGINE_MODULES}
RELEASE_FEEDS = [dict(m.RELEASE_FEED, engine=m.ID)
                 for m in ENGINE_MODULES if getattr(m, "RELEASE_FEED", None)]


# ---------------------------------------------------------------------- models
def _model(m):
    d = {"id": m.ID, "mod": m.MODALITY, "name": m.NAME, "arch": m.ARCH,
         "lic": m.LICENSE, "ctx": m.CONTEXT, "hf": m.HF, "note": m.NOTE,
         "srcs": [tuple(x) for x in m.SOURCES],
         "agentic": [tuple(x) for x in m.SCORES.get("agentic", [])],
         "coding": [tuple(x) for x in m.SCORES.get("coding", [])],
         "w": 0.0, "est": False}
    if getattr(m, "CONTEXT_LABEL", None):
        d["ctx_label"] = m.CONTEXT_LABEL
    lad = getattr(m, "LADDER", {}) or {}
    smallest = min((r["gb"] for rungs in lad.values() for r in rungs), default=0.0)
    d["w"] = smallest
    return d


MODELS = [_model(m) for m in MODEL_MODULES]
MODEL_BY_ID = {m["id"]: m for m in MODELS}
PARAMS = {m.ID: m.PARAMS_B for m in MODEL_MODULES}
LADDERS = {m.ID: (getattr(m, "LADDER", {}) or {}) for m in MODEL_MODULES}
QUANT_SOURCES = {m.ID: (getattr(m, "QUANT_SOURCES", {}) or {}) for m in MODEL_MODULES}
KV = {m.ID: (m.KV["bytes_per_token"], m.KV["max_context"], m.KV["derivation"])
      for m in MODEL_MODULES}
BEST = {m.ID: m.BEST_ENGINE for m in MODEL_MODULES}

MATRIX = {
    m.ID: {eid: {"s": c["status"], "label": c["label"], "w": None, "q": None,
                 "note": c["note"], "items": list(c["issues"])}
           for eid, c in m.ENGINES.items()}
    for m in MODEL_MODULES
}


# ------------------------------------------------------------------ use cases
USE_CASE_MODULES.sort(key=lambda m: (getattr(m, "DISPLAY_ORDER", 9999), m.ID))
USE_CASES = [{"id": m.ID, "label": m.LABEL, "mod": m.MODALITY, "gate": m.FIDELITY_GATE,
              "axis": m.AXIS, "rank": [tuple(r) for r in m.RANK]}
             for m in USE_CASE_MODULES]


# ---------------------------------------------------------------------- issues
EMETA = {}
for _m in ISSUE_MODULES:
    for _num, _meta in _m.ISSUES.items():
        EMETA[f"{_m.REPO}#{_num}"] = (_meta["severity"], _meta["headline"], _meta["why"])

_pr = importlib.util.spec_from_file_location("data_pr_keys", os.path.join(DATA, "pr_keys.py"))
_prm = importlib.util.module_from_spec(_pr)
_pr.loader.exec_module(_prm)
PR_KEYS = set(_prm.PR_KEYS)


# ------------------------------------------------------------------- derived
def modality(m):
    return m.get("mod", "text")


def engine_order(mid):
    """Engines that could plausibly load this model, best first.

    Filtered by modality: an image model never shows a chat server, and an LLM
    never shows mflux. Without this every media card would carry a column of
    "out of scope" for every engine it has nothing to do with.
    """
    best = BEST[mid]
    rest = [e["id"] for e in ENGINES
            if e["id"] != best and e["id"] in MATRIX[mid]
            and MATRIX[mid][e["id"]].get("s") != "none"]
    return [best] + rest


REPO_LABELS = {
    "waybarrios/vllm-mlx": "vllm-mlx",
    "ml-explore/mlx-lm": "mlx-lm",
    "ggml-org/llama.cpp": "llama.cpp",
    "jundot/omlx": "oMLX",
    "antirez/ds4": "ds4",
    "ollama/ollama": "ollama",
    "lmstudio-ai/lmstudio-bug-tracker": "LM Studio",
    "vllm-project/vllm-metal": "vLLM Metal",
}


def repo_label(key):
    return REPO_LABELS.get(key.split("#")[0], key.split("#")[0])
