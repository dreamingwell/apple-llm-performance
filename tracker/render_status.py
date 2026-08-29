#!/usr/bin/env python3
"""Render the vllm-mlx watchlist state file into a model-first status page."""
import os, re, html, datetime, hashlib, json
# One record per file under data/, assembled by tracker/registry.py. MODELS and
# the per-engine matrix used to live in this file and in engines.py; they were
# split so two agents editing two different models never touch the same file.
from registry import (ENGINES, ENGINE_BY_ID, EMETA, MATRIX, BEST, engine_order,
                      repo_label, CROSS_BY_ENGINE, RELEASE_FEEDS, FAM,
                      LADDERS, KV, PARAMS, ACTIVE, SPEEDS, USE_CASES, MODELS,
                      MACHINES, GENS, modality, SCLASS, ENGINE_PROSE_LINKS, PR_KEYS)
from bands import BANDS, FAM_OVERRIDE, FIDELITY_NOTES
import throughput


def card_name():
    """Content-hashed social card filename; CDN caches images for 4h."""
    p = os.path.join(ASSETS, "og-card.jpg")
    if not os.path.exists(p):
        return "card.jpg"
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:10]
    return f"card-{h}.jpg"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
SITE = os.path.join(ROOT, "docs")
STATE = os.path.join(HERE, "watch-state.txt")

# key -> (severity, headline, why it matters)
META = dict(EMETA)


# works/degraded/blocked/none -> the CSS verdict classes the page already uses

CROSS = ["waybarrios/vllm-mlx#619", "waybarrios/vllm-mlx#584", "waybarrios/vllm-mlx#672",
         "waybarrios/vllm-mlx#546", "waybarrios/vllm-mlx#627", "waybarrios/vllm-mlx#682",
         "waybarrios/vllm-mlx#732", "waybarrios/vllm-mlx#570"]

SEV_LABEL = {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low"}
SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def read_state():
    rows, releases = {}, {}
    if not os.path.exists(STATE):
        return rows, releases
    for line in open(STATE):
        line = line.strip()
        if not line or "|" not in line:
            continue
        key, state, _label = (line.split("|", 2) + ["", ""])[:3]
        if key.endswith("@release"):
            releases[key[:-len("@release")]] = state
        else:
            rows[key] = state
    return rows, releases


def pill(state):
    s = (state or "open").lower()
    if s == "merged":
        return "merged", "Merged"
    if s == "closed":
        return "closed", "Closed"
    return "open", "Open"


def issue_url(key):
    repo, num = key.split("#")
    kind = "pull" if key in PR_KEYS else "issues"
    return f"https://github.com/{repo}/{kind}/{num}"


def slug(name):
    return "m-" + "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")


def best_cell(m):
    """The engine a model card opens on."""
    eid = BEST[m["id"]]
    return eid, MATRIX[m["id"]][eid]


def fam_for(eid, mid):
    return FAM_OVERRIDE.get((eid, mid), FAM[eid])


def ladder_for(eid, mid):
    """Measured rungs this engine can load for this model, largest first."""
    if MATRIX[mid][eid]["s"] == "none":
        return []
    return LADDERS.get(mid, {}).get(fam_for(eid, mid), [])


def engine_payload(m):
    """Every engine that can run this model, with its own quant ladder.

    Ordered by architecture support first, then by whether it is the
    recommended engine - the browser walks this and takes the first entry with a
    rung that fits, so preference only breaks ties between equally-supported
    engines.
    """
    mid = m["id"]
    best = BEST[mid]
    rank = {"ready": 0, "degraded": 1, "blocked": 2, "unknown": 3}
    out = []
    for eid in engine_order(mid):
        c = MATRIX[mid][eid]
        lad = ladder_for(eid, mid)
        if not lad:
            continue
        out.append({"id": eid, "name": ENGINE_BY_ID[eid]["name"], "s": SCLASS[c["s"]],
                    "label": c["label"], "fam": fam_for(eid, mid),
                    "note": FIDELITY_NOTES.get((mid, fam_for(eid, mid)), ""),
                    "ladder": lad})
    out.sort(key=lambda d: (rank[d["s"]], 0 if d["id"] == best else 1,
                            -(d["ladder"][-1]["gb"] if d["ladder"] else 0)))
    return out


def model_payload(m):
    bpt, maxctx, why = KV.get(m["id"], (None, None, ""))
    return {"engines": engine_payload(m),
            "kv": {"bpt": bpt, "maxctx": maxctx, "why": why},
            "params": PARAMS.get(m["id"]),
            # Parameters read per decoded token. The browser divides the chip's
            # bandwidth by these bytes to get the decode ceiling; null here means
            # no published count, and the page says so instead of guessing.
            "active": ACTIVE.get(m["id"])}


def index_rows(rows):
    """One line per model. The size, engine and headroom cells are all filled in
    by the browser once a cluster is selected - the server-rendered values are
    just the default-cluster answer so the page is not blank without JS."""
    out = []
    for m in sorted(MODELS, key=lambda m: m["name"].casefold()):
        eid, c = best_cell(m)
        lad = ladder_for(eid, m["id"])
        gb = lad[-1]["gb"] if lad else m["w"]
        payload = html.escape(json.dumps(model_payload(m)), quote=True)
        out.append(f"""
        <a class="ix-row v-{SCLASS[c['s']]}" href="#{m['id']}" data-model="{m['id']}"
           data-sw="{SCLASS[c['s']]}" data-swlabel="{html.escape(c['label'])}"
           data-mod="{modality(m)}" data-payload="{payload}">
          <span class="ix-name"><i class="ix-bar" aria-hidden="true"></i><em>{html.escape(m['name'])}</em></span>
          <span class="ix-status v-{SCLASS[c['s']]}">{html.escape(c['label'])}</span>
          <span class="ix-eng">{html.escape(ENGINE_BY_ID[eid]['name'])}</span>
          <span class="ix-size">{gb:.0f} GB</span>
          <span class="ix-tps"></span>
          <span class="ix-meta fit"></span>
        </a>""")
    return "".join(out)


def src_links(m):
    out = [f"""<a class="src" href="https://huggingface.co/{m['hf']}" target="_blank" rel="noopener">{html.escape(m['hf'])}</a>"""]
    out += [f"""<a class="src" href="{u}" target="_blank" rel="noopener">{html.escape(lbl)}</a>""" for lbl, u in m["srcs"]]
    return "".join(out)


def scores(pairs):
    return "".join(
        f"""<div class="score"><span class="score-k">{html.escape(k)}</span>"""
        f"""<span class="score-v">{html.escape(v)}</span></div>"""
        for k, v in pairs)


# Text that must not be linkified: an existing anchor, a code span, or any tag.
_SKIP = re.compile(r"(<a\b[^>]*>.*?</a>|<code>.*?</code>|<[^>]+>)", re.S)

# An engine name is only a mention if it stands alone. The lookarounds keep
# "ds4-server" and "mlx-lm.server" from being clipped mid-token.
_ENGINE_MENTIONS = [
    (re.compile(rf"(?<![\w.-]){re.escape(alias)}(?![\w-])"), eid, site)
    for alias, eid, site in ENGINE_PROSE_LINKS]


def link_engines(out):
    """Link the first mention of each engine to its own website.

    First mention only: the notes name an engine repeatedly, and linking every
    occurrence turns a paragraph into a wall of blue. Existing links, code spans
    and tag interiors are left alone, so a hand-written [text](url) always wins.
    """
    seen = set()
    parts = _SKIP.split(out)
    for i, part in enumerate(parts):
        if i % 2:                     # the captured skip-group; leave verbatim
            continue
        for pat, eid, site in _ENGINE_MENTIONS:
            if eid in seen:
                continue
            new_part, n = pat.subn(
                lambda m: f'<a href="{site}" target="_blank" rel="noopener">{m.group(0)}</a>',
                part, count=1)
            if n:
                seen.add(eid)
                part = new_part
        parts[i] = part
    return "".join(parts)


def prose(text, engines=True):
    """HTML-escape, then render inline `code` spans, [text](url) links, and
    link the first mention of each inference engine to its own website."""
    out = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", html.escape(text))
    out = re.sub(r"\*\*([^*]+)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", out)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                 lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>',
                 out)
    return link_engines(out) if engines else out


API_ROWS = [("endpoints", "Endpoints"), ("streaming", "Streaming"), ("tools", "Tool calling"),
            ("structured", "Structured output"), ("concurrency", "Concurrency"), ("gotcha", "Watch for")]


def api_block(e):
    api = e.get("api_detail")
    if not api:
        return ""
    rows = "".join(
        f"""<div class="api-row"><dt>{html.escape(label)}</dt><dd>{prose(api[k])}</dd></div>"""
        for k, label in API_ROWS if api.get(k))
    return f"""<dl class="api">{rows}</dl>"""


def engine_build(mid, eid):
    """The chosen rung is filled in by the browser; this is the static fallback."""
    lad = ladder_for(eid, mid)
    if not lad:
        c = MATRIX[mid][eid]
        label = c["q"][0] if c.get("q") else "no build published for this engine"
        return f"""<div class="eng-build none"><span class="eng-build-k">Build</span><span>{html.escape(label)}</span></div>"""
    return (f"""<div class="eng-build"><span class="eng-build-k">Build</span>"""
            f"""<a class="build-link" href="#" target="_blank" rel="noopener"></a>"""
            f"""<span class="build-bpw"></span></div>""")


def engine_meta_line(e):
    bits = [("Interface", e["surface"]), ("Format", e["fmt"]), ("API", e["api"]), ("License", e["lic"])]
    return "".join(f"""<div><dt>{html.escape(k)}</dt><dd>{html.escape(v)}</dd></div>""" for k, v in bits)


def engine_tabs(m, rows):
    mid, order = m["id"], engine_order(m["id"])
    tabs, panes = [], []
    for i, eid in enumerate(order):
        c, e = MATRIX[mid][eid], ENGINE_BY_ID[eid]
        sc = SCLASS[c["s"]]
        sel = "true" if i == 0 else "false"
        n_open = sum(1 for k in c["items"] if rows.get(k, "open").lower() == "open")
        tabs.append(f"""
          <button type="button" role="tab" class="eng-tab s-{sc}" data-eng="{eid}"
                  aria-selected="{sel}" aria-controls="{mid}-{eid}" id="{mid}-{eid}-tab">
            <span class="eng-tab-n">{html.escape(e['name'])}</span>
            <span class="eng-tab-s s-{sc}">{html.escape(c['label'])}</span>
          </button>""")
        lad = ladder_for(eid, mid)
        w_attr = ' data-has-ladder="1"' if lad else ""
        items = render_items(c["items"], rows)
        body = (f"""<ul class="rows">{items}\n          </ul>"""
                if items else
                """<p class="eng-clear">Nothing open tracked against this engine for this model.</p>""")
        # A blocked engine cannot load the model at all, so quoting a build, a
        # resident size, a fidelity band or a context table for it is noise at
        # best and misleading at worst. Leave the reason and the issues.
        sizing = "" if c["s"] in ("blocked", "none") else f"""
          {engine_build(mid, eid)}
          <div class="eng-fit s-{sc}"{w_attr}></div>
          <p class="fidelity" hidden></p>
          <div class="tput" hidden></div>
          <div class="ctx-wrap" hidden><span class="ctx-k">Concurrent contexts in the KV headroom</span>
            <table class="ctx"><thead><tr><th>Context each</th><th>KV per stream</th><th>Decode ceiling</th><th>Streams</th></tr></thead>
            <tbody></tbody></table>
            <p class="ctx-why"></p></div>"""
        panes.append(f"""
        <div class="eng-pane" id="{mid}-{eid}" role="tabpanel" aria-labelledby="{mid}-{eid}-tab"
             data-eng="{eid}"{'' if i == 0 else ' hidden'}>
          <dl class="eng-meta">{engine_meta_line(e)}</dl>{sizing}
          <p class="eng-note">{prose(c['note'])}</p>
          <p class="blockers-label">{n_open} open of {len(c['items'])} tracked on this engine</p>
          {body}
        </div>""")
    return f"""
      <div class="eng" data-model="{mid}">
        <div class="eng-tabs" role="tablist" aria-label="Engines for {html.escape(m['name'])}">{''.join(tabs)}
        </div>
        <div class="eng-panes">{''.join(panes)}
        </div>
      </div>"""


def cross_tabs(rows, releases):
    feeds = {f["engine"]: f for f in RELEASE_FEEDS}
    tabs, panes = [], []
    for i, e in enumerate(ENGINES):
        eid = e["id"]
        keys = CROSS_BY_ENGINE.get(eid, [])
        n_open = sum(1 for k in keys if rows.get(k, "open").lower() == "open")
        sel = "true" if i == 0 else "false"
        tabs.append(f"""
          <button type="button" role="tab" class="eng-tab" data-eng="{eid}"
                  aria-selected="{sel}" aria-controls="cross-{eid}" id="cross-{eid}-tab">
            <span class="eng-tab-n">{html.escape(e['name'])}</span>
            <span class="eng-tab-s">{n_open} open</span>
          </button>""")
        items = render_items(keys, rows)
        body = (f"""<ul class="cross-list">{items}\n          </ul>""" if items else
                """<p class="eng-clear">Nothing server-wide tracked against this engine.</p>""")
        panes.append(f"""
        <div class="eng-pane" id="cross-{eid}" role="tabpanel" aria-labelledby="cross-{eid}-tab"
             data-eng="{eid}"{'' if i == 0 else ' hidden'}>
          <dl class="eng-meta">{engine_meta_line(e)}{release_cell(feeds.get(eid), releases)}</dl>
          <p class="eng-note">{prose(e['what'])}</p>
          {api_block(e)}
          {body}
        </div>""")
    return f"""
      <div class="eng" data-model="cross">
        <div class="eng-tabs" role="tablist" aria-label="Engines">{''.join(tabs)}
        </div>
        <div class="eng-panes">{''.join(panes)}
        </div>
      </div>"""


def release_cell(feed, releases):
    """The engine's latest release, shown alongside its other facts."""
    if not feed:
        return ""
    if feed["scheme"] == "none":
        tag = "no tag feed"
    else:
        tag = releases.get(feed["repo"], "not seen yet")
    note = f" &middot; {html.escape(feed['note'])}" if feed["note"] else ""
    return (f"""<div><dt>Latest release</dt><dd>{html.escape(tag)}"""
            f"""<span class="rel-note">{note}</span></dd></div>""")


def release_rows(releases):
    out = []
    for f in RELEASE_FEEDS:
        e = ENGINE_BY_ID[f["engine"]]
        repo = f["repo"]
        name = (f"""<a href="https://github.com/{repo}" target="_blank" rel="noopener">{html.escape(e['name'])}</a>"""
                if repo else html.escape(e["name"]))
        tag = "no tag feed" if f["scheme"] == "none" else releases.get(repo, "not seen yet")
        note = f"""<span class="rel-note">{html.escape(f['note'])}</span>""" if f["note"] else ""
        out.append(f"""<div class="rel"><span class="rel-repo">{name}{note}</span>"""
                   f"""<span class="rel-tag">{html.escape(tag)}</span></div>""")
    return "".join(out)


def tok_label(n):
    """A context length as the page writes it: 2k, 64k, 1M."""
    if n is None:
        return ""
    if n >= 1000000:
        return f"{n / 1000000:.2f}M".replace(".00M", "M")
    return f"{round(n / 1024)}k" if n >= 1024 else str(n)


def ladder_rung(mid, label):
    """The measured rung a SPEEDS record names, if it is one of ours."""
    for rungs in LADDERS.get(mid, {}).values():
        for r in rungs:
            if r.get("label") == label:
                return r
    return None


def speed_ceiling(mid, rec):
    """The bound this measurement can be checked against, or None with a reason.

    Deliberately conservative: a record that does not state its build and its
    context is not compared to anything, because the comparison would be
    arithmetic over an assumption rather than over the run.
    """
    rung = ladder_rung(mid, rec.get("build"))
    if rung is not None and throughput.rung_reason(rung):
        return None, throughput.rung_reason(rung)
    if rec.get("decode_tps") is None:
        return None, "prefill is compute-bound, so this page does not derive a bound for it"
    if not rec.get("gb") or not rec.get("context"):
        return None, "the report does not state the build and the context, so there is nothing to compare"
    if ACTIVE.get(mid) is None:
        return None, throughput.NO_ACTIVE
    bpt = KV.get(mid, (None, None, ""))[0]
    mc = MACHINES.get(rec.get("chip"))
    if not mc:
        return None, "unknown chip"
    cap = throughput.ceiling_tps(mc["bw"], rec["gb"], ACTIVE[mid], PARAMS.get(mid),
                                 bpt, rec["context"])
    return cap, ""


def speed_conditions(rec):
    """The run this figure came off, in the order that decides whether it is
    comparable: which engine, which machine, which build, how much context."""
    mc = MACHINES.get(rec.get("chip"), {})
    bits = [ENGINE_BY_ID[rec["engine"]]["name"]]
    machine = mc.get("label", rec.get("chip", "?"))
    if rec.get("mem_gb"):
        machine += f" {rec['mem_gb']} GB"
    bits.append(machine)
    if rec.get("build"):
        b = rec["build"]
        if len(b) > 46:
            b = b[:44] + "\u2026"
        bits.append(f"{b} ({rec['gb']:.0f} GB)" if rec.get("gb") else b)
    elif rec.get("gb"):
        bits.append(f"{rec['gb']:.0f} GB build")
    else:
        bits.append("build not stated")
    bits.append(f"{tok_label(rec['context'])} context" if rec.get("context")
                else "context not stated")
    return bits


def speeds_block(mid):
    """Published measurements for one model. Someone else's number, with whose.

    This is the page's highest confidence class and it is rendered as such -
    plainly, above the arithmetic, with the conditions of the run beside the
    figure rather than in a footnote. Without those conditions a
    tokens-per-second figure compares to nothing, which is why the block prints
    'build not stated' rather than quietly omitting it.
    """
    recs = SPEEDS.get(mid) or []
    if not recs:
        return ""
    rows = []
    for rec in recs:
        kind = "decode" if rec.get("decode_tps") is not None else "prefill"
        val = rec.get("decode_tps") if kind == "decode" else rec.get("prefill_tps")
        cap, _why = speed_ceiling(mid, rec)
        against = (f"""<span class="sp-vs">{val / cap * 100:.0f}% of the {cap:.0f} tok/s bound</span>"""
                   if cap else "")
        conds = " &middot; ".join(html.escape(b) for b in speed_conditions(rec))
        rows.append(f"""
          <li class="sp-row">
            <div class="sp-head">
              <span class="sp-n">{val:g}<span class="sp-u"> tok/s</span></span>
              <span class="sp-kind">{kind}</span>{against}
            </div>
            <p class="sp-cond">{conds}</p>
            <p class="sp-note">{prose(rec.get('note', ''))}</p>
            <a class="sp-src" href="{html.escape(rec['url'], quote=True)}" target="_blank"
               rel="noopener">{html.escape(rec['who'])}</a>
          </li>""")
    return f"""
        <div class="speeds">
          <span class="q-cat">Measured by others &mdash; not by us, and not derived</span>
          <ul class="sp-list">{''.join(rows)}
          </ul>
        </div>"""


def calibration():
    """Every decode measurement complete enough to check against the bound.

    The point of the table is that the page does not have to assert an
    efficiency constant: the gap between what the arithmetic allows and what
    somebody actually got is data, and it is shown rather than folded into a
    fudge factor.
    """
    rows, fracs = [], []
    for m in sorted(MODELS, key=lambda m: m["name"].casefold()):
        for rec in SPEEDS.get(m["id"]) or []:
            cap, _why = speed_ceiling(m["id"], rec)
            if not cap:
                continue
            frac = rec["decode_tps"] / cap
            fracs.append(frac)
            mc = MACHINES[rec["chip"]]
            rows.append(f"""
            <tr>
              <td>{html.escape(m['name'])}</td>
              <td>{html.escape(ENGINE_BY_ID[rec['engine']]['name'])}</td>
              <td>{html.escape(mc['label'])}, {rec['gb']:.0f} GB build, {tok_label(rec['context'])}</td>
              <td class="cal-n">{cap:.0f}</td>
              <td class="cal-n cal-meas">{rec['decode_tps']:g}</td>
              <td class="cal-n">{frac * 100:.0f}%</td>
            </tr>""")
    if not rows:
        return "", ""
    lo, hi = min(fracs), max(fracs)
    summary = (f"Across the {len(rows)} published decode measurement"
               f"{'' if len(rows) == 1 else 's'} on this page that state their build and "
               f"their context, real decode landed between {lo * 100:.0f}% and {hi * 100:.0f}% "
               "of the bound. That spread is the reason the page quotes the bound and shows "
               "you the measurements, rather than multiplying by an efficiency constant and "
               "calling the product an estimate.")
    table = f"""
        <table class="cal">
          <thead><tr><th>Model</th><th>Engine</th><th>Run</th><th>Ceiling</th>
            <th>Measured</th><th>Of bound</th></tr></thead>
          <tbody>{''.join(rows)}
          </tbody>
        </table>"""
    return table, summary


def render_items(keys, rows):
    present = [k for k in keys if k in META]
    present.sort(key=lambda k: (SEV_ORDER.get(META[k][0], 9), k))
    out = []
    for key in present:
        sev, headline, why = META[key]
        state = rows.get(key, "open")
        cls, txt = pill(state)
        repo, num = key.split("#")
        short = repo_label(key)
        out.append(f"""
        <li class="row sev-{sev}">
          <div class="row-head">
            <a class="ref" href="{issue_url(key)}" target="_blank" rel="noopener">{short}&thinsp;#{num}</a>
            <span class="pill {cls}">{txt}</span>
            <span class="sev-tag">{SEV_LABEL[sev]}</span>
          </div>
          <h4>{html.escape(headline)}</h4>
          <p>{prose(why)}</p>
        </li>""")
    return "".join(out)


def render():
    rows, releases = read_state()
    stamp = datetime.datetime.now().astimezone()
    now = stamp.strftime("%Y-%m-%d %H:%M")
    now_iso = stamp.isoformat(timespec="seconds")

    cards = []
    for m in MODELS:
        eid, c = best_cell(m)
        sc = SCLASS[c["s"]]
        payload = html.escape(json.dumps(model_payload(m)), quote=True)
        cards.append(f"""
    <section class="model v-{sc}" id="card-{m['id']}" data-model="{m['id']}" data-sw="{sc}"
             data-swlabel="{html.escape(c['label'])}" data-mod="{modality(m)}" data-payload="{payload}">
      <div class="model-head">
        <div class="model-id">
          <h2>{html.escape(m['name'])}</h2>
          <span class="verdict v-{sc}">{html.escape(c['label'])}</span>
        </div>
        <dl class="spec">
          <div><dt>Architecture</dt><dd>{html.escape(m['arch'])}</dd></div>
          <div><dt>License</dt><dd>{html.escape(m['lic'])}</dd></div>
          <div><dt>{html.escape(m.get('ctx_label', 'Context'))}</dt><dd>{html.escape(m['ctx'])}</dd></div>
        </dl>
        <p class="model-fit"></p>
        <p class="model-note">{prose(m['note'])}</p>
        <div class="srcs"><span class="q-cat">Sources</span>{src_links(m)}</div>{speeds_block(m['id'])}
        <details class="scores-wrap">
          <summary>Benchmark scores</summary>
          <div class="scores">
            <div class="score-col"><span class="score-cat">Agentic</span>{scores(m['agentic'])}</div>
            <div class="score-col"><span class="score-cat">Coding</span>{scores(m['coding'])}</div>
          </div>
        </details>
      </div>
      {engine_tabs(m, rows)}
    </section>""")

    # Serialised here rather than baked into TEMPLATE: a frozen literal silently
    # went stale once already when new models were added to USE_CASES.
    usecases = json.dumps([{"id": u["id"], "label": u["label"], "gate": u["gate"],
                            "axis": u["axis"], "mod": u.get("mod", "text"),
                            "rank": [[r[0], r[1], r[2]] for r in u["rank"]]}
                           for u in USE_CASES])
    bands = json.dumps([[b[0], b[1], b[2], b[3]] for b in BANDS])

    cal_table, cal_summary = calibration()
    doc = TEMPLATE.format(now=now, now_iso=now_iso, usecases=usecases, bands=bands,
                          machines=json.dumps(MACHINES, sort_keys=True),
                          gens=json.dumps(GENS),
                          calibration=f'<div class="cal-wrap">{cal_table}</div>',
                          tputsummary=cal_summary,
                          cards="".join(cards), index=index_rows(rows),
                          cross=cross_tabs(rows, releases))
    return doc.replace("/apple-llm-performance/card.jpg",
                       "/apple-llm-performance/" + card_name())


TEMPLATE = """<title>Apple LLM Performance Tracker</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Open weight AI models and their Apple M-series compatibility.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="DreamingWell">
<meta property="og:url" content="https://dreamingwell.github.io/apple-llm-performance/">
<meta property="og:title" content="Apple LLM Performance Tracker">
<meta property="og:description" content="Open weight AI models and their Apple M-series compatibility.">
<meta property="og:image" content="https://dreamingwell.github.io/apple-llm-performance/card.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Dark card over a glowing Apple Silicon die reading Can Your Mac Run It? - find the best LLM for your Mac, updated daily. Open source on GitHub.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Apple LLM Performance Tracker">
<meta name="twitter:description" content="Open weight AI models and their Apple M-series compatibility.">
<meta name="twitter:image" content="https://dreamingwell.github.io/apple-llm-performance/card.jpg">
<meta name="twitter:image:alt" content="Dark card over a glowing Apple Silicon die reading Can Your Mac Run It? - find the best LLM for your Mac, updated daily. Open source on GitHub.">
<link rel="canonical" href="https://dreamingwell.github.io/apple-llm-performance/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
  :root {{
    --bg: #eef1f5; --surface: #ffffff; --surface-2: #f6f8fa;
    --ink: #141a20; --ink-2: #3d4854; --muted: #5f6b78;
    --line: #d9e0e8; --line-soft: #e8edf2;
    --accent: #a85a26;
    --critical: #a8352a; --high: #8a5410; --medium: #4a6070; --low: #78838f;
    --ok: #25704e; --ok-tint: #e8f5ee; --warn: #8a5410;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #0e1216; --surface: #161c22; --surface-2: #1b232a;
      --ink: #e3e8ee; --ink-2: #b9c3cd; --muted: #8894a2;
      --line: #29333d; --line-soft: #202932;
      --accent: #de8a4c;
      --critical: #ef7565; --high: #ddb24f; --medium: #7f97a8; --low: #6d7883;
      --ok: #59bc88; --ok-tint: #12251c; --warn: #ddb24f;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #0e1216; --surface: #161c22; --surface-2: #1b232a;
    --ink: #e3e8ee; --ink-2: #b9c3cd; --muted: #8894a2;
    --line: #29333d; --line-soft: #202932;
    --accent: #de8a4c;
    --critical: #ef7565; --high: #ddb24f; --medium: #7f97a8; --low: #6d7883;
    --ok: #59bc88; --ok-tint: #12251c; --warn: #ddb24f;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: "IBM Plex Sans", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    font-size: 16px; line-height: 1.55; -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 64rem; margin: 0 auto; padding: 3rem 1.5rem 5rem; }}
  header {{ display: flex; flex-direction: column; gap: .5rem; margin-bottom: 2rem; }}
  .eyebrow {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .72rem;
    letter-spacing: .13em; text-transform: uppercase; color: var(--accent); font-weight: 600; }}
  h1 {{ font-size: clamp(1.7rem, 4vw, 2.3rem); font-weight: 700; margin: 0;
    letter-spacing: -.02em; text-wrap: balance; }}
  .sub {{ color: var(--muted); margin: 0; max-width: 48rem; }}
  html {{ scroll-behavior: smooth; }}
  @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
  .rig {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: 1.1rem 1.3rem; margin: 0 0 1.25rem; }}
  .rig select optgroup {{ font-weight: 600; }}
  .rig-controls {{ display: flex; gap: 1.1rem; flex-wrap: wrap; align-items: flex-end; }}
  .rig-f {{ display: flex; flex-direction: column; gap: .28rem; min-width: 0; }}
  .rig-f > span {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .64rem;
    letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .rig select {{ font-family: inherit; font-size: .88rem; font-weight: 500; color: var(--ink);
    background: var(--surface-2); border: 1px solid var(--line); border-radius: 6px;
    padding: .4rem .6rem; min-width: 8.5rem; }}
  .rig select:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
  .rig-out {{ margin: .9rem 0 0; font-size: .87rem; color: var(--ink-2); font-variant-numeric: tabular-nums; }}
  .rig-out strong {{ color: var(--ink); font-weight: 600; }}
  .rig-warn {{ margin: .5rem 0 0; font-size: .8rem; color: var(--critical);
    border-left: 2px solid var(--critical); padding-left: .6rem; }}
  .ix-status.v-toolarge {{ color: var(--low); border-color: var(--line); }}
  .ix-row.v-toolarge {{ border-left-color: var(--low); opacity: .78; }}
  .verdict.v-toolarge {{ color: var(--low); border-color: var(--line); background: var(--surface-2); }}
  .model.v-toolarge .model-head {{ border-top-color: var(--low); }}
  .index {{ margin: 0 0 2.75rem; }}
  .ix-top {{ display: flex; flex-direction: column; align-items: flex-start; gap: .5rem;
    margin-bottom: .85rem; }}
  .uc-f {{ display: flex; align-items: baseline; gap: .5rem; }}
  .uc-f > span {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .64rem;
    letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .uc-f select {{ font-family: inherit; font-size: .84rem; font-weight: 500; color: var(--ink);
    background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: .3rem .5rem; }}
  .uc-f select:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
  .uc-out {{ margin: 0 0 .9rem; font-size: .87rem; color: var(--ink-2); }}
  .uc-out strong {{ color: var(--ink); font-weight: 600; }}
  .uc-out .uc-why {{ display: block; margin-top: .2rem; font-size: .78rem; color: var(--muted); }}
  .uc-fold {{ margin-top: .3rem; }}
  .uc-fold > summary {{ cursor: pointer; list-style: none; display: inline-flex; align-items: center;
    gap: .3rem; font-size: .78rem; color: var(--accent); border-bottom: 1px dotted currentColor;
    width: fit-content; }}
  .uc-fold > summary::-webkit-details-marker {{ display: none; }}
  .uc-fold > summary::after {{ content: "\\203A"; font-size: .9em; transition: transform .15s ease; }}
  .uc-fold[open] > summary::after {{ transform: rotate(90deg); }}
  .uc-fold > summary:hover {{ color: var(--ink-2); }}
  .uc-fold .uc-why {{ margin-top: .45rem; }}
  .ix-row.uc-best {{ background: var(--ok-tint); box-shadow: inset 3px 0 0 0 var(--ok); }}
  .ix-row.uc-best:hover, .ix-row.uc-best:focus-visible {{ background: var(--ok-tint); }}
  .ix-row.uc-best .ix-name::after {{ content: "best here"; margin-left: .5rem;
    font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .58rem; letter-spacing: .08em;
    text-transform: uppercase; color: var(--ok); border: 1px solid var(--ok);
    border-radius: 3px; padding: .1em .3em; vertical-align: .1em; }}
  .ix-row.uc-out-of-scope {{ opacity: .5; }}
  .ix-head {{ font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; color: var(--accent);
    margin: 0 0 .7rem; font-weight: 600; font-family: "IBM Plex Mono", ui-monospace, monospace; }}
  .ix-rows {{ display: flex; flex-direction: column; gap: 1px; background: var(--line);
    border: 1px solid var(--line); border-radius: 9px; overflow: hidden; }}
  .ix-row {{ display: grid; grid-template-columns: minmax(6rem, 1.4fr) 9.25rem minmax(4rem, .55fr) 4.75rem 5.5rem minmax(4.5rem, .8fr);
    align-items: center; gap: .9rem; padding: .62rem 1rem; background: var(--surface);
    text-decoration: none; color: inherit; border-left: 3px solid var(--medium);
    transition: background .12s ease; }}
  .ix-row:hover, .ix-row:focus-visible {{ background: var(--surface-2); }}
  .ix-row.v-ready {{ border-left-color: var(--ok); }}
  .ix-row.v-degraded {{ border-left-color: var(--warn); }}
  .ix-row.v-blocked {{ border-left-color: var(--critical); }}
  .ix-row.v-nofit, .ix-row.v-unknown {{ border-left-color: var(--low); }}
  .ix-name {{ font-weight: 600; font-size: .92rem; letter-spacing: -.01em;
    position: relative; display: flex; align-items: center; min-width: 0; }}
  .ix-name em {{ font-style: normal; position: relative; }}
  /* Scored against the leader for the selected job, so the top row is always
     full. Width is set from JS; models with no number for that job get none. */
  .ix-bar {{ position: absolute; left: -.35rem; top: 50%; transform: translateY(-50%);
    height: 1.45rem; width: 0; border-radius: 3px; background: var(--ok);
    opacity: .16; transition: width .18s ease; pointer-events: none; }}
  .ix-row.uc-best .ix-bar {{ opacity: .28; }}
  /* no comparable figure on the leader's scale */
  .ix-row.no-bar .ix-name em::after {{ content: "\\2020"; margin-left: .3rem;
    font-size: .8em; color: var(--muted); vertical-align: super; line-height: 0; }}
  @media (prefers-reduced-motion: reduce) {{ .ix-bar {{ transition: none; }} }}
  .ix-status {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .66rem;
    font-weight: 600; letter-spacing: .05em; text-transform: uppercase; white-space: nowrap;
    padding: .14rem .5rem; border-radius: 4px; border: 1px solid; justify-self: start; }}
  .ix-status.v-ready {{ color: var(--ok); border-color: var(--ok); }}
  .ix-status.v-degraded {{ color: var(--warn); border-color: var(--warn); }}
  .ix-status.v-blocked {{ color: var(--critical); border-color: var(--critical); }}
  .ix-status.v-nofit, .ix-status.v-unknown {{ color: var(--low); border-color: var(--line); }}
  .ix-size {{ text-align: right; font-variant-numeric: tabular-nums; font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .78rem;
    color: var(--ink-2); font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }}
  .ix-meta {{ font-size: .76rem; color: var(--muted); text-align: right; white-space: nowrap; }}
  /* A ceiling, not a measurement, and the row has no space for that sentence -
     so the number never appears without the "<=" that says which it is. */
  .ix-tps {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .74rem;
    color: var(--ink-2); text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; }}
  .ix-legend {{ margin: .8rem 0 0; font-size: .78rem; color: var(--muted); max-width: 52rem; }}
  .ix-legend code {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .95em; }}
  .ix-legend strong {{ color: var(--ink-2); font-weight: 600; }}
  /* Six columns need about 40.5rem before the gaps; below that the row
     stacks rather than overflowing the page horizontally. */
  @media (max-width: 41rem) {{
    .ix-row {{ grid-template-columns: 1fr auto; row-gap: .3rem; }}
    .ix-size, .ix-meta, .ix-tps {{ text-align: left; }}
    .ix-eng {{ order: 5; }}
  }}
  .model {{ margin-bottom: 2.5rem; scroll-margin-top: 1rem; }}
  .nofit-row {{ scroll-margin-top: 1rem; }}
  .model-head {{ background: var(--surface); border: 1px solid var(--line);
    border-top: 3px solid var(--medium); border-radius: 10px 10px 0 0; padding: 1.35rem 1.5rem 1.15rem; }}
  .model.v-degraded .model-head {{ border-top-color: var(--warn); }}
  .model.v-blocked .model-head {{ border-top-color: var(--critical); }}
  .model.v-unknown .model-head {{ border-top-color: var(--low); }}
  .model.v-ready .model-head {{ border-top-color: var(--ok); }}
  .model-id {{ display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; margin-bottom: .9rem; }}
  .model-id h2 {{ font-size: 1.35rem; font-weight: 700; margin: 0; letter-spacing: -.02em; }}
  .verdict {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .7rem; font-weight: 600;
    letter-spacing: .06em; text-transform: uppercase; padding: .22rem .6rem; border-radius: 4px; border: 1px solid; }}
  .verdict.v-degraded {{ color: var(--warn); border-color: var(--warn); background: var(--surface-2); }}
  .verdict.v-blocked {{ color: var(--critical); border-color: var(--critical); background: var(--surface-2); }}
  .verdict.v-unknown {{ color: var(--low); border-color: var(--line); background: var(--surface-2); }}
  .verdict.v-ready {{ color: var(--ok); border-color: var(--ok); background: var(--surface-2); }}
  .vram {{ display: flex; align-items: baseline; gap: .7rem; flex-wrap: wrap;
    padding: .6rem .9rem; margin: 0 0 .7rem; border-radius: 6px;
    background: var(--surface-2); border: 1px solid var(--line-soft); border-left: 3px solid var(--accent); }}
  .vram.tight {{ border-left-color: var(--critical); }}
  .vram-k {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .66rem;
    letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .vram-v {{ font-size: .87rem; font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }}
  .quants {{ display: flex; flex-direction: column; gap: .3rem; margin: 0 0 .9rem; }}
  .q-cat {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .64rem;
    letter-spacing: .1em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .q {{ display: flex; align-items: baseline; gap: .6rem; flex-wrap: wrap; font-size: .82rem; }}
  .q.alt {{ opacity: .72; }}
  .q-repo {{ font-family: "IBM Plex Mono", ui-monospace, monospace; color: var(--accent);
    text-decoration: none; border-bottom: 1px solid transparent; word-break: break-all; }}
  .q-repo:hover, .q-repo:focus-visible {{ border-bottom-color: var(--accent); }}
  .q-repo.none {{ color: var(--muted); font-style: italic; border: none; }}
  .q-size {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-weight: 600;
    color: var(--ink); font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .q-note {{ font-size: .76rem; color: var(--muted); }}
  .srcs {{ display: flex; align-items: baseline; gap: .55rem; flex-wrap: wrap; margin: 0 0 .8rem; }}
  .src {{ font-size: .76rem; color: var(--accent); text-decoration: none;
    border: 1px solid var(--line); border-radius: 4px; padding: .1rem .45rem; background: var(--surface-2); }}
  .src:hover, .src:focus-visible {{ border-color: var(--accent); }}
  .nofit-row .srcs {{ margin-top: .4rem; margin-bottom: 0; }}
  .scores {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: .9rem 1.6rem;
    margin: 0 0 1rem; padding: .85rem 1rem; background: var(--surface-2);
    border: 1px solid var(--line-soft); border-radius: 7px; }}
  .score-col {{ display: flex; flex-direction: column; gap: .32rem; min-width: 0; }}
  .score-cat {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .66rem;
    letter-spacing: .1em; text-transform: uppercase; color: var(--accent); font-weight: 600; margin-bottom: .1rem; }}
  .score {{ display: flex; justify-content: space-between; align-items: baseline; gap: .8rem;
    border-bottom: 1px dotted var(--line); padding-bottom: .2rem; }}
  .score-k {{ font-size: .8rem; color: var(--ink-2); }}
  .score-v {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .82rem;
    font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .spec {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
    gap: .8rem 1.4rem; margin: 0 0 .95rem; }}
  .spec div {{ display: flex; flex-direction: column; gap: .1rem; min-width: 0; }}
  .spec dt {{ font-size: .68rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .spec dd {{ margin: 0; font-size: .85rem; color: var(--ink); font-weight: 500; }}
  .model-note {{ margin: 0 0 .8rem; font-size: .91rem; color: var(--ink-2); max-width: 52rem; }}
  .blockers-label {{ margin: 0; font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: .72rem; letter-spacing: .05em; text-transform: uppercase; color: var(--muted); }}
  .rows {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 1px;
    background: var(--line); border: 1px solid var(--line); border-top: none; border-radius: 0 0 10px 10px; overflow: hidden; }}
  .row {{ background: var(--surface); border-left: 3px solid var(--medium); padding: .9rem 1.15rem; }}
  .row.sev-critical {{ border-left-color: var(--critical); }}
  .row.sev-high {{ border-left-color: var(--high); }}
  .row.sev-medium {{ border-left-color: var(--medium); }}
  .row.sev-low {{ border-left-color: var(--low); }}
  .row-head {{ display: flex; align-items: center; gap: .6rem; flex-wrap: wrap; margin-bottom: .3rem; }}
  .ref {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .8rem; font-weight: 500;
    color: var(--accent); text-decoration: none; border-bottom: 1px solid transparent; }}
  .ref:hover, .ref:focus-visible {{ border-bottom-color: var(--accent); }}
  .pill {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .66rem; font-weight: 600;
    letter-spacing: .05em; text-transform: uppercase; padding: .14rem .45rem; border-radius: 4px; border: 1px solid var(--line); }}
  .pill.open {{ color: var(--ink-2); background: var(--surface-2); }}
  .pill.merged {{ color: var(--ok); background: var(--surface-2); border-color: var(--ok); }}
  .pill.closed {{ color: var(--muted); background: var(--surface-2); }}
  .sev-tag {{ font-size: .71rem; color: var(--muted); margin-left: auto; letter-spacing: .04em; }}
  .row h4 {{ font-size: .93rem; font-weight: 600; margin: 0 0 .22rem; letter-spacing: -.005em; }}
  .row p {{ margin: 0; font-size: .86rem; color: var(--ink-2); max-width: 52rem; }}

  .model-fit {{ margin: 0; font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: .8rem; color: var(--ink-2); }}
  .model-fit.toolarge {{ color: var(--critical); }}
  header {{ position: relative; }}
  .gh {{ position: absolute; top: 0; right: 0; display: inline-flex; align-items: center;
    gap: .4rem; text-decoration: none; color: var(--ink-2);
    border: 1px solid var(--line); border-radius: 999px; padding: .3rem .7rem .3rem .6rem;
    background: var(--surface); font-size: .78rem; font-weight: 500; }}
  .gh:hover {{ color: var(--ink); border-color: var(--accent); }}
  .gh svg {{ flex: none; }}
  @media (max-width: 620px) {{ header {{ padding-top: 2.2rem; }} }}
  .back {{ appearance: none; cursor: pointer; font: inherit; font-size: .82rem; font-weight: 500;
    color: var(--ink-2); background: var(--surface); border: 1px solid var(--line);
    border-radius: 999px; padding: .35rem .9rem .35rem .75rem; margin: 0 0 1.1rem;
    display: inline-flex; align-items: center; gap: .4rem; }}
  .back:hover {{ color: var(--ink); border-color: var(--accent); }}
  .detail .model {{ margin-bottom: 0; }}
  .back-bottom {{ margin: 1.25rem 0 0; }}
  .detail {{ margin-bottom: 2.75rem; }}
  html, body, .wrap {{ overflow-anchor: none; }}
  .sub-stamp {{ color: var(--muted); white-space: nowrap; }}
  .ix-eng {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .72rem;
    color: var(--muted); white-space: nowrap; }}
  .panel-lead {{ margin: 0 0 1.15rem; font-size: .89rem; color: var(--ink-2); max-width: 54rem; }}
  .panel.wide {{ padding-bottom: 1.35rem; }}

  /* A vertical rail rather than a tab strip. Eight engines wrapped into two
     ragged rows horizontally; as a list they stay scannable and there is room
     for the status text beside each name. */
  .eng {{ margin-top: 1px; display: grid; grid-template-columns: 13.5rem 1fr;
    gap: 1px; background: var(--line); border: 1px solid var(--line); }}
  .eng-tabs {{ display: flex; flex-direction: column; background: var(--surface-2);
    align-content: start; }}
  .eng-panes {{ background: var(--surface); min-width: 0; }}
  .eng-tab {{ appearance: none; border: 0; cursor: pointer; text-align: left;
    background: var(--surface-2); color: var(--muted);
    padding: .55rem .8rem; display: flex; flex-direction: column; gap: .1rem;
    font: inherit; border-left: 2px solid transparent;
    border-bottom: 1px solid var(--line-soft); }}
  .eng-tab:hover {{ background: var(--surface); color: var(--ink-2); }}
  .eng-tab[aria-selected="true"] {{ background: var(--surface); color: var(--ink);
    border-left-color: var(--accent); }}
  .eng-tab-n {{ font-size: .82rem; font-weight: 600; letter-spacing: -.005em; }}
  .eng-tab-s {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .6rem;
    letter-spacing: .04em; text-transform: uppercase; color: var(--muted); }}
  .eng-tab[aria-selected="true"] .eng-tab-s.s-ready {{ color: var(--ok); }}
  .eng-tab[aria-selected="true"] .eng-tab-s.s-degraded {{ color: var(--warn); }}
  .eng-tab[aria-selected="true"] .eng-tab-s.s-blocked {{ color: var(--critical); }}
  .eng-tab .eng-tab-s.s-ready::before,
  .eng-tab .eng-tab-s.s-degraded::before,
  .eng-tab .eng-tab-s.s-blocked::before,
  .eng-tab .eng-tab-s.s-unknown::before {{
    content: ""; display: inline-block; width: .4rem; height: .4rem; border-radius: 50%;
    margin-right: .32rem; vertical-align: baseline; }}
  .eng-tab .eng-tab-s.s-ready::before {{ background: var(--ok); }}
  .eng-tab .eng-tab-s.s-degraded::before {{ background: var(--warn); }}
  .eng-tab .eng-tab-s.s-blocked::before {{ background: var(--critical); }}
  .eng-tab .eng-tab-s.s-unknown::before {{ background: var(--low); }}
  @media (max-width: 820px) {{
    .eng {{ grid-template-columns: 1fr; }}
    .eng-tabs {{ flex-direction: row; flex-wrap: wrap; gap: 1px; background: var(--line); }}
    .eng-tab {{ flex: 1 1 9rem; border-left: 0; border-bottom: 0;
      border-top: 2px solid transparent; }}
    .eng-tab[aria-selected="true"] {{ border-top-color: var(--accent); }}
  }}
  .eng-pane {{ background: var(--surface); padding: 1.15rem 1.2rem 1.2rem;
    display: flex; flex-direction: column; gap: .8rem; min-width: 0; }}
  .model-fit {{ margin: 0 0 .35rem; }}
  .panel-fold > summary {{ cursor: pointer; list-style: none; display: flex; align-items: center;
    gap: .45rem; }}
  .panel-fold > summary::-webkit-details-marker {{ display: none; }}
  .panel-fold > summary::before {{ content: "+"; font-size: .95rem; line-height: 1;
    color: var(--accent); width: .7rem; }}
  .panel-fold[open] > summary::before {{ content: "\\2212"; }}
  .panel-fold > summary h2 {{ margin: 0; }}
  .panel-fold > summary:hover h2 {{ color: var(--ink-2); }}
  .panel-fold > ul {{ margin-top: 1.1rem; }}
  .panel-fold > .panel-lead {{ margin-top: 1.1rem; }}
  .scores-wrap {{ margin-top: .9rem; border-top: 1px solid var(--line-soft); padding-top: .7rem; }}
  .scores-wrap > summary {{ cursor: pointer; font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: .66rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted);
    font-weight: 600; list-style: none; display: flex; align-items: center; gap: .4rem; }}
  .scores-wrap > summary::-webkit-details-marker {{ display: none; }}
  .scores-wrap > summary::before {{ content: "+"; font-size: .85rem; line-height: 1;
    color: var(--accent); width: .7rem; }}
  .scores-wrap[open] > summary::before {{ content: "\\2212"; }}
  .scores-wrap > summary:hover {{ color: var(--ink-2); }}
  .scores-wrap .scores {{ margin-top: .6rem; }}
  .build-bpw {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .72rem;
    letter-spacing: .03em; padding: .1em .45em; border-radius: 4px; border: 1px solid var(--line); }}
  .build-bpw.b-full {{ color: var(--ok); border-color: var(--ok); }}
  .build-bpw.b-mild, .build-bpw.b-low, .build-bpw.b-pruned {{ color: var(--warn); border-color: var(--warn); }}
  .build-bpw.b-unusable {{ color: var(--critical); border-color: var(--critical); }}
  .fidelity {{ margin: 0; font-size: .85rem; color: var(--ink-2); padding: .65rem .8rem;
    border-left: 3px solid var(--warn); background: var(--surface-2); }}
  .fidelity.b-unusable {{ border-left-color: var(--critical); }}
  .fidelity strong {{ color: var(--ink); font-weight: 600; }}
  .fidelity.b-unusable strong {{ color: var(--critical); }}
  .ctx-wrap {{ display: flex; flex-direction: column; gap: .45rem; }}
  .ctx-k {{ font-size: .66rem; letter-spacing: .07em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; }}
  .ctx {{ border-collapse: collapse; font-size: .82rem; width: 100%; max-width: 34rem; }}
  .ctx th {{ text-align: left; font-size: .64rem; letter-spacing: .06em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; padding: .25rem .7rem .25rem 0;
    border-bottom: 1px solid var(--line); }}
  .ctx td {{ padding: .3rem .7rem .3rem 0; border-bottom: 1px solid var(--line-soft);
    font-variant-numeric: tabular-nums; color: var(--ink-2); }}
  .ctx th:last-child, .ctx td:last-child {{ text-align: right; padding-right: 0; }}
  .ctx-n {{ font-family: "IBM Plex Mono", ui-monospace, monospace; color: var(--ink); font-weight: 600; }}
  .ctx-n.none {{ color: var(--critical); font-weight: 400; }}
  .ctx-cap td {{ border-top: 1px solid var(--line); font-weight: 500; color: var(--ink); }}
  .ctx-cap .ctx-n {{ color: var(--ok); }}
  .ctx-why {{ margin: 0; font-size: .76rem; color: var(--muted); max-width: 46rem; }}
  .ctx-t {{ font-family: "IBM Plex Mono", ui-monospace, monospace; color: var(--ink-2);
    white-space: nowrap; }}

  /* Derived, so it is styled as arithmetic rather than as a fact: no verdict
     colour, the bound spelled with a "<=", and the sentence that says what it
     is sitting under it rather than in a tooltip. */
  .tput {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: .3rem .55rem;
    background: var(--surface-2); border: 1px dashed var(--line);
    border-radius: 6px; padding: .55rem .8rem; }}
  .tput-k {{ font-size: .66rem; letter-spacing: .07em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; }}
  .tput-v {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .95rem;
    font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }}
  .tput.none .tput-v {{ font-size: .82rem; font-weight: 400; color: var(--muted); }}
  .tput-at {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .76rem;
    color: var(--ink-2); }}
  .tput-why {{ flex-basis: 100%; font-size: .76rem; color: var(--muted); max-width: 46rem; }}

  /* Measurements. The highest confidence class on the page, so it is the one
     block that states its provenance inline instead of in a footnote. */
  .speeds {{ display: flex; flex-direction: column; gap: .4rem; }}
  .sp-list {{ list-style: none; margin: 0; padding: 0; display: flex;
    flex-direction: column; gap: 1px; background: var(--line);
    border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
  .sp-row {{ background: var(--surface-2); padding: .6rem .8rem; }}
  .sp-head {{ display: flex; align-items: baseline; flex-wrap: wrap; gap: .45rem; }}
  .sp-n {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 1.05rem;
    font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }}
  .sp-u {{ font-size: .72rem; font-weight: 500; color: var(--ink-2); }}
  .sp-kind {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .62rem;
    letter-spacing: .06em; text-transform: uppercase; color: var(--ok);
    border: 1px solid var(--ok); border-radius: 4px; padding: .1rem .4rem; }}
  .sp-vs {{ font-size: .72rem; color: var(--muted); margin-left: auto; white-space: nowrap; }}
  .sp-cond {{ margin: .25rem 0 0; font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: .72rem; color: var(--ink-2); }}
  .sp-note {{ margin: .3rem 0 0; font-size: .82rem; color: var(--ink-2); max-width: 52rem; }}
  .sp-src {{ display: inline-block; margin-top: .3rem; font-size: .74rem; }}

  .tp-h {{ font-size: .84rem; font-weight: 600; margin: 1.3rem 0 .35rem; letter-spacing: -.005em; }}
  .tp-p {{ margin: 0 0 .6rem; font-size: .87rem; color: var(--ink-2); max-width: 54rem; }}
  .tp-foot {{ color: var(--muted); font-size: .82rem; margin-top: 1rem; }}
  .tp-f {{ margin: 0 0 .7rem; padding: .6rem .8rem; background: var(--surface-2);
    border-left: 3px solid var(--accent); font-size: .84rem; overflow-x: auto; }}
  .tp-f code {{ font-family: "IBM Plex Mono", ui-monospace, monospace; white-space: nowrap; }}
  .tp-list {{ margin: 0; padding-left: 1.1rem; font-size: .86rem; color: var(--ink-2);
    max-width: 54rem; }}
  .tp-list li {{ margin-bottom: .4rem; }}
  .tp-list strong {{ color: var(--ink); font-weight: 600; }}
  .cal {{ border-collapse: collapse; font-size: .82rem; width: 100%; margin-bottom: .7rem; }}
  .cal th {{ text-align: left; font-size: .64rem; letter-spacing: .06em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; padding: .25rem .7rem .25rem 0;
    border-bottom: 1px solid var(--line); }}
  .cal td {{ padding: .32rem .7rem .32rem 0; border-bottom: 1px solid var(--line-soft);
    color: var(--ink-2); vertical-align: top; }}
  .cal-n {{ font-family: "IBM Plex Mono", ui-monospace, monospace; text-align: right;
    font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .cal-meas {{ color: var(--ink); font-weight: 600; }}
  .cal th:nth-child(n+4) {{ text-align: right; }}
  .cal-wrap {{ overflow-x: auto; }}

  .api {{ margin: 0; display: flex; flex-direction: column; gap: 1px;
    background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
  .api-row {{ background: var(--surface-2); padding: .7rem .85rem; display: grid;
    grid-template-columns: 9.5rem 1fr; gap: .2rem 1rem; align-items: baseline; }}
  .api-row dt {{ font-size: .68rem; letter-spacing: .07em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; }}
  .api-row dd {{ margin: 0; font-size: .85rem; color: var(--ink-2); }}
  .api-row:last-child dd {{ color: var(--ink-2); }}
  .api-row:last-child dt {{ color: var(--warn); }}
  .api-row code {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .8em;
    background: var(--surface); border: 1px solid var(--line-soft); border-radius: 4px;
    padding: .05em .3em; }}
  .api-row strong {{ color: var(--ink); font-weight: 600; }}
  @media (max-width: 640px) {{
    .api-row {{ grid-template-columns: 1fr; }}
  }}

  .eng-note code, .row p code, .model-note code {{ font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: .82em; background: var(--surface-2); border: 1px solid var(--line-soft);
    border-radius: 4px; padding: .05em .3em; }}
  .eng-meta {{ margin: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr));
    gap: .55rem 1.2rem; }}
  .eng-meta div {{ display: flex; flex-direction: column; gap: .1rem; }}
  .eng-meta dt {{ font-size: .66rem; letter-spacing: .07em; text-transform: uppercase;
    color: var(--muted); font-weight: 500; }}
  .eng-meta dd {{ margin: 0; font-size: .82rem; color: var(--ink-2); }}
  .eng-fit {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .8rem;
    color: var(--ink-2); background: var(--surface-2); border-left: 3px solid var(--line);
    padding: .6rem .8rem; }}
  .eng-fit.s-ready {{ border-left-color: var(--ok); }}
  .eng-fit.s-degraded {{ border-left-color: var(--warn); }}
  .eng-fit.s-blocked {{ border-left-color: var(--critical); }}
  .eng-fit.toolarge {{ border-left-color: var(--critical); color: var(--critical); }}
  .eng-build {{ font-size: .8rem; display: flex; flex-wrap: wrap; gap: .5rem; align-items: baseline; }}
  .eng-build-k {{ font-size: .66rem; letter-spacing: .07em; text-transform: uppercase;
    color: var(--muted); font-weight: 500; }}
  .eng-build a, .eng-build span:not(.eng-build-k) {{
    font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .78rem; }}
  .eng-build.none span:not(.eng-build-k) {{ color: var(--muted); }}
  .eng-note {{ margin: 0; font-size: .89rem; color: var(--ink-2); max-width: 54rem; }}
  .eng-clear {{ margin: 0; font-size: .85rem; color: var(--muted); }}
  .eng-pane .rows, .eng-pane .cross-list {{ margin-top: .15rem; }}
  @media (max-width: 640px) {{
    .eng-tab {{ flex: 1 1 100%; }}
  }}
  .panel {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: 1.4rem 1.5rem; margin-bottom: 1rem; }}
  .panel h2 {{ font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; color: var(--accent);
    margin: 0 0 1rem; font-weight: 600; font-family: "IBM Plex Mono", ui-monospace, monospace; }}
  .panel > ul {{ margin: 0; padding-left: 1.1rem; display: flex; flex-direction: column; gap: .55rem; }}
  .panel > ul > li {{ font-size: .89rem; color: var(--ink-2); }}
  .panel strong {{ color: var(--ink); font-weight: 600; }}
  .nofit {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: .9rem; }}
  .nofit-row {{ border-left: 2px solid var(--line); padding-left: .9rem; }}
  .nofit-head {{ display: flex; align-items: baseline; gap: .7rem; flex-wrap: wrap; }}
  .nofit-head h4 {{ font-size: .95rem; font-weight: 600; margin: 0; }}
  .nofit-mem {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .8rem;
    color: var(--muted); font-variant-numeric: tabular-nums; }}
  .nofit-arch {{ margin: .12rem 0 .3rem; font-size: .78rem; color: var(--muted);
    font-family: "IBM Plex Mono", ui-monospace, monospace; }}
  .nofit-row > p:last-child {{ margin: 0; font-size: .86rem; color: var(--ink-2); }}
  .cross-list {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 1px;
    background: var(--line); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
  .rel {{ display: flex; justify-content: space-between; align-items: baseline; gap: 1rem;
    padding: .5rem 0; border-bottom: 1px solid var(--line-soft); }}
  .rel:last-child {{ border-bottom: none; }}
  .rel-repo {{ font-size: .87rem; color: var(--ink-2); display: flex; flex-direction: column; gap: .12rem; }}
  .rel-note {{ font-size: .74rem; color: var(--muted); }}
  .rel-tag {{ font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: .87rem;
    font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }}
  .disclaimer {{ margin: 2rem 0 0; padding: .95rem 1.15rem; border-radius: 8px;
    background: var(--surface-2); border: 1px solid var(--line);
    border-left: 3px solid var(--warn); font-size: .82rem; color: var(--ink-2); max-width: 54rem; }}
  .disclaimer strong {{ color: var(--ink); font-weight: 600; }}
  footer {{ margin-top: 1.25rem; padding-top: 1.2rem; border-top: 1px solid var(--line);
    font-size: .82rem; color: var(--muted); }}
  [hidden] {{ display: none !important; }}
  a {{ color: var(--accent); }}
  :focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
</style>

<div class="wrap">
  <header>
    <a class="gh" href="https://github.com/dreamingwell/apple-llm-performance"
       target="_blank" rel="noopener" aria-label="Open source on GitHub">
      <svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" focusable="false"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-2.98-.88-2.98-2.9 0-.83.3-1.51.79-2.04-.08-.2-.35-1 .08-2.07 0 0 .65-.2 2.13.79a7.2 7.2 0 0 1 1.94-.26c.66 0 1.32.09 1.94.26 1.48-1 2.13-.79 2.13-.79.43 1.07.16 1.87.08 2.07.49.53.79 1.21.79 2.04 0 2.03-1.21 2.7-2.99 2.9.31.27.58.79.58 1.6 0 1.15-.01 2.09-.01 2.38 0 .21.15.46.55.38A7.99 7.99 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>
      <span>Open source</span>
    </a>
    <span class="eyebrow">Top Tier Open Weight Models on Apple Silicon</span>
    <h1>Apple LLM Performance Tracker</h1>
    <p class="sub">Select your Mac CPU model, RAM, and machine count below. Then view what AI models
    should run well on it &mdash; and those that won&rsquo;t.
    <span class="sub-stamp">Updated <time class="ago" datetime="{now_iso}">{now}</time>.</span></p>
  </header>

  <form class="rig" id="rig" aria-label="Cluster configuration">
    <div class="rig-controls">
      <label class="rig-f"><span>CPU Model</span>
        <select id="rig-chip"></select>
      </label>
      <label class="rig-f"><span>Memory each</span>
        <select id="rig-mem"></select>
      </label>
      <label class="rig-f"><span>Units</span>
        <select id="rig-n"></select>
      </label>
    </div>
    <p class="rig-out" id="rig-out"></p>
    <p class="rig-warn" id="rig-warn" hidden></p>
  </form>

  <nav class="index" id="list" aria-label="Model index">
    <div class="ix-top">
      <h2 class="ix-head">Models at a glance</h2>
      <label class="uc-f"><span>What for?</span>
        <select id="uc-sel"></select>
      </label>
    </div>
    <p class="uc-out" id="uc-out"></p>
    <div class="ix-rows">{index}
    </div>
    <p class="ix-legend">The <code>&le;</code> figure is a <strong>decode ceiling</strong> at 8k
    context, not a measurement: the chip&rsquo;s memory bandwidth divided by the bytes the engine has
    to read to emit one token. Real decode lands below it, and how far below depends on the engine.
    <a href="#throughput">Where that comes from, where it is wrong, and what has actually been
    measured</a>.</p>
  </nav>

  <div class="detail" id="detail" hidden>
    <button type="button" class="back" id="back">
      <span aria-hidden="true">&larr;</span> All models
    </button>
{cards}
    <button type="button" class="back back-bottom" id="back-bottom">
      <span aria-hidden="true">&larr;</span> All models
    </button>
  </div>

  <div class="panel wide">
    <details class="panel-fold">
      <summary><h2>General engine information</h2></summary>
    <p class="panel-lead">What each engine is, what its API actually implements, and the defects that follow
    you whichever model you load on it. All seven speak OpenAI on <code>/v1/chat/completions</code> with SSE
    streaming, and none is desktop-only &mdash; but &ldquo;OpenAI-compatible&rdquo; covers a wide range, and the
    differences land on exactly the features an agent leans on: whether tool-call arguments stream as deltas or
    arrive only after the turn, whether constrained decoding exists at all, and whether <code>tool_choice</code>
    is implemented. Five of the seven also serve Anthropic <code>/v1/messages</code>, so Claude Code can point
    at them directly.</p>
    {cross}
    </details>
  </div>

  <div class="panel" id="throughput">
    <details class="panel-fold">
      <summary><h2>Tokens per second</h2></summary>
    <p class="panel-lead">Two kinds of number appear on this page, and they are never mixed. A
    <strong>measurement</strong> is somebody else&rsquo;s run, shown with the machine, the build and the
    context it came off and a link to whoever took it. A <strong>ceiling</strong> is arithmetic over
    published specifications &mdash; the same class as the memory-fit figures &mdash; and it is an upper
    bound, not a prediction. Nothing here is self-reported to us, because a tokens-per-second figure
    with no build and no context compares to nothing; the two Qwen3.8 records on this page are kept
    precisely to show that.</p>
    <h3 class="tp-h">The ceiling, and where it comes from</h3>
    <p class="tp-p">Decoding one token at batch 1 reads the whole active weight set plus whatever the
    model attends over in its KV cache, and reuses almost none of it on the next step. So decode waits
    on memory, and peak memory bandwidth is a hard bound on it:</p>
    <p class="tp-f"><code>tok/s &le; bandwidth &divide; (build size &times; active&nbsp;&divide;&nbsp;total + KV per token &times; context)</code></p>
    <p class="tp-p">Every term is already on this page: the chip&rsquo;s bandwidth from its
    specification, the measured size of the build the picker chose, the model&rsquo;s published active
    parameter count, and the per-token KV cost derived from its <code>config.json</code>. Nothing is
    fitted and nothing is guessed, which is why a ceiling can be shown for a model nobody has ever
    benchmarked. A model whose ceiling on your machine is already too slow will not be rescued by a
    better engine.</p>
    <h3 class="tp-h">Where the ceiling is wrong</h3>
    <ul class="tp-list">
      <li><strong>It is a bound, not an estimate.</strong> {tputsummary}</li>
      <li><strong>Sparse MoE does badly against it.</strong> Each expert&rsquo;s weight read is small and
      scattered, so a batch-1 MoE never approaches peak bandwidth. Dense models get much closer.</li>
      <li><strong>It assumes uniform bits per weight.</strong> ds4&rsquo;s builds quantise routed experts
      to 2 bits while leaving attention projections, shared experts and output at Q8 &mdash; the build
      names say so &mdash; so the slice read per token is denser than the file average and the real
      ceiling is lower. Qwen3.8-Flash-Next is dragged the other way by a 51B n-gram table that is
      looked up, not streamed.</li>
      <li><strong>It assumes the whole cache is read.</strong> DeepSeek&rsquo;s DSA, MiniMax Sparse
      Attention and Qwen Sparse Attention all attend over a selected subset, so the ceiling falls with
      context faster than these models do.</li>
      <li><strong>Expert-pruned builds get no ceiling at all.</strong> Pruning deletes experts the
      router was not going to pick, so it buys memory and not speed: Kimi K3&rsquo;s 350 GB and 451 GB
      REAP builds decode at the same rate. Scaling by file size would claim otherwise.</li>
      <li><strong>Speculative decoding can beat it.</strong> An MTP or draft head emits several tokens
      per weight read. A measurement above the bound is not necessarily wrong &mdash; but the record has
      to say so, and the validator rejects one that does not.</li>
      <li><strong>Pooling does not raise it.</strong> Pipeline parallelism splits the layers; every
      token still traverses all of them in sequence, and pays a Thunderbolt hop on the way. The ceiling
      uses one machine&rsquo;s bandwidth however many machines are pooled, and is optimistic there.</li>
      <li><strong>Prefill is not covered.</strong> It is a batched matmul over the whole prompt, so it
      is compute-bound and this argument does not apply. Published prefill figures are shown; none is
      derived.</li>
    </ul>
    <h3 class="tp-h">The ceiling against the measurements</h3>
    <p class="tp-p">Every decode measurement on this page that states its build and its context,
    beside the bound for that exact run. This is the check on the arithmetic, and it is the honest
    place to look before trusting a ceiling anywhere else on the page.</p>
    {calibration}
    <p class="tp-p tp-foot">If you have measured one of these models on a Mac, that is the most
    valuable thing you can contribute &mdash; see CONTRIBUTING.md for the fields a record needs. A
    figure without the chip, the build and the context cannot be used.</p>
    </details>
  </div>

  <div class="panel">
    <details class="panel-fold">
      <summary><h2>Reading the scores</h2></summary>
    <ul>
      <li><strong>Terminal-Bench 2.0 and 2.1 are different benchmarks.</strong> Qwen3-Coder-Next's 36.2 is on v2.0; Qwen3.8-27B's 73.0 and GLM-5.2's 81.0 are on v2.1. Do not rank across the two &mdash; they are shown labelled, not normalised.</li>
      <li>Scores are vendor-reported or aggregator-reported, not reproduced here. Treat them as a shortlist filter, then verify the shortlist on your own context-rot harness.</li>
      <li>Nothing on this page has been measured on M5 Ultra hardware. Everything else is published numbers.</li>
      <li><strong>Tokens per second is never self-reported here.</strong> A figure is either somebody
      else's measurement, shown with the machine, build and context it came off, or a ceiling derived
      from memory bandwidth and marked <code>&le;</code>. The two are never mixed &mdash; see
      <a href="#throughput">Tokens per second</a>.</li>
      <li>Weights are the summed file sizes of the linked repository &mdash; safetensors for MLX builds, GGUF for the rest &mdash; measured, not estimated. A <strong>*</strong> marks the exception: a figure derived from parameter count because no build has been published anywhere.</li>
      <li><strong>The same model weighs different amounts on different engines.</strong> GGUF has quant tiers MLX does not, so llama.cpp can often fit a model MLX cannot &mdash; Qwen3-Coder-Next's GGUF ladder reaches down to 18.9 GB while its MLX ladder stops at 42.4 GB. Each engine tab states its own build and its own fit.</li>
      <li>Issue lists are scoped to the engine tab you are on, and are filtered for what actually applies on a Mac. A CUDA-only or ROCm-only report is not listed here even when it dominates the upstream thread.</li>
      <li>Fit assumes a 90% wired-memory limit plus framework overhead &mdash; ~10 GB for an LLM server, which has a paged KV pool and Metal buffers to hold, and ~1.5 GB for an image or audio runtime, which does not &mdash; and that pooling shards weights evenly. It answers "does this load", not "does this run well" &mdash; a model spread across machines still pays the Thunderbolt hop on every token.</li>
    </ul>
    </details>
  </div>

  <p class="disclaimer">
    <strong>Disclaimer.</strong> All of this is best effort and provided for entertainment purposes only.
    No warranty is given as to its accuracy. Benchmark scores are vendor- or aggregator-reported and are not
    reproduced here; issue states are a twice-daily snapshot; hardware figures are arithmetic, not measurements.
    Verify anything you intend to spend money on.
  </p>

  <footer>
    Polled twice daily against the GitHub API across llama.cpp, Ollama, LM Studio, oMLX, vllm-mlx, mlx-lm and ds4;
    state changes only &mdash; open&rarr;closed, merged, new release tag. The clock in the intro counts from the
    last <em>content</em> change, not the last check &mdash; the page is only republished when something actually
    moves, so a large number there means the watchlist has been quiet.
  </footer>
</div>

<script data-newblock="1">
(function () {{
  // The chip table lives in data/machines.py so that Python can read it too -
  // the decode ceiling divides by `bw`, and two copies of a bandwidth table
  // would go stale silently. Serialised here, not duplicated.
  var MACHINES = {machines};
  var GENS = {gens};
  var USE_CASES = {usecases};
  var BAND_RANK = {{ full: 0, mild: 1, low: 2, pruned: 2, unusable: 3 }};
  var ORDER = Object.keys(MACHINES);
  var MAX_UNITS = 6, PRACTICAL_UNITS = 4, WIRED = 0.90;
  // Framework overhead. The larger figure covers an LLM server's KV pool and
  // Metal buffers; a diffusion or TTS runtime carries far less, and charging it
  // 10 GB made a 310 MB model report "10 GB resident".
  var OVERHEAD_TEXT = 10, OVERHEAD_MEDIA = 1.5, OVERHEAD = OVERHEAD_TEXT;
  var BANDS = {bands};
  // The context the one-line ceilings are quoted at. A realistic agent turn:
  // long enough that the KV term is not free, short enough not to flatter a
  // model whose only advantage is a cheap cache. Stated wherever it is used.
  var REF_CTX = 8192;


  var chipSel = document.getElementById("rig-chip"),
      memSel  = document.getElementById("rig-mem"),
      nSel    = document.getElementById("rig-n"),
      out     = document.getElementById("rig-out"),
      warn    = document.getElementById("rig-warn");
  if (!chipSel) return;

  var DEF_CHIP = "m5ultra", DEF_MEM = 256, DEF_N = 1;

  var q = new URLSearchParams(location.search);
  var chip = MACHINES[q.get("chip")] ? q.get("chip") : DEF_CHIP;
  var mem  = parseInt(q.get("mem"), 10);
  if (!mem || MACHINES[chip].mem.indexOf(mem) === -1) {{
    mem = MACHINES[chip].mem.indexOf(DEF_MEM) !== -1 ? DEF_MEM : MACHINES[chip].mem[0];
  }}
  var n = parseInt(q.get("n"), 10);
  if (!n || n < 1 || n > MAX_UNITS) n = DEF_N;

  GENS.forEach(function (g) {{
    var grp = document.createElement("optgroup");
    grp.label = g;
    ORDER.filter(function (k) {{ return MACHINES[k].gen === g; }}).forEach(function (k) {{
      var o = document.createElement("option");
      o.value = k; o.textContent = MACHINES[k].label;
      grp.appendChild(o);
    }});
    chipSel.appendChild(grp);
  }});
  for (var i = 1; i <= MAX_UNITS; i++) {{
    var o = document.createElement("option");
    o.value = i; o.textContent = i + (i === 1 ? " machine" : " machines");
    nSel.appendChild(o);
  }}

  function fillMem(keepIfPossible) {{
    var opts = MACHINES[chip].mem;
    memSel.innerHTML = "";
    opts.forEach(function (g) {{
      var o = document.createElement("option");
      o.value = g; o.textContent = g + " GB";
      memSel.appendChild(o);
    }});
    if (opts.indexOf(keepIfPossible) === -1) {{
      keepIfPossible = opts.indexOf(DEF_MEM) !== -1 ? DEF_MEM : opts[opts.length - 1];
    }}
    memSel.value = keepIfPossible;
  }}

  function fmt(gb) {{
    if (gb >= 1000) return (gb / 1000).toFixed(2) + " TB";
    if (gb < 1) return Math.round(gb * 1000) + " MB";   // TTS models are sub-gigabyte
    return Math.round(gb) + " GB";
  }}

  function apply() {{
    chip = chipSel.value;
    var g = parseInt(memSel.value, 10);
    n = parseInt(nSel.value, 10);
    var perNode = g * WIRED, cluster = perNode * n, M = MACHINES[chip];

    // The interconnect only matters once there is something to interconnect.
    out.innerHTML = "<strong>" + n + " \u00d7 " + M.label + " " + g + " GB</strong> = " +
      fmt(g * n) + " pooled, about " + fmt(cluster) + " usable after the wired-memory limit. " +
      "Per-machine bandwidth " + (M.bw >= 1000 ? (M.bw / 1000).toFixed(1) + " TB/s" : M.bw + " GB/s") + "." +
      (n > 1 ? " Uses " + M.tb + " with " + M.link + " Gb/s connection speed." : "");

    if (n > 1 && !M.tb5) {{
      warn.hidden = false;
      warn.textContent = "Clustering multiple " + M.label + " machines will be very slow: " + M.tb +
        " has no RDMA path, so pooling falls back to ring pipeline parallelism.";
    }} else if (n > PRACTICAL_UNITS) {{
      warn.hidden = false;
      warn.textContent = "Past " + PRACTICAL_UNITS + " machines a full Thunderbolt mesh runs out of ports. " +
        "Treat these rows as arithmetic, not a supported setup.";
    }} else {{ warn.hidden = true; }}

    function fitDetail(w, over, kvWord) {{
      var OVERHEAD = over === undefined ? OVERHEAD_TEXT : over;
      var kv = kvWord === undefined ? " for KV" : kvWord;
      var resident = w + OVERHEAD;
      var nodes = Math.ceil(resident / perNode);
      if (resident > cluster) {{
        return {{ tooBig: true, nodes: nodes, resident: resident, free: 0,
                 short: "needs " + nodes + " machine" + (nodes === 1 ? "" : "s"),
                 text: "needs " + nodes + " machine" + (nodes === 1 ? "" : "s") }};
      }}
      if (nodes > 1) {{
        var freeP = cluster - resident;
        return {{ tooBig: false, nodes: nodes, resident: resident, free: freeP, copies: 1,
                 short: fmt(freeP) + " free",
                 text: "pooled across " + nodes + " of your " + n + ", " + fmt(freeP) + " left" + kv }};
      }}
      // It fits on one machine, so every machine runs its own copy. Nothing is
      // pooled and nothing is shared - the capacity simply multiplies.
      var free = perNode - resident;
      return {{ tooBig: false, nodes: 1, resident: resident, free: free, copies: n,
               short: fmt(free) + " free",
               text: n > 1
                 ? fmt(free) + " free" + kv + " per machine \u2014 run as individual compute, not as a cluster"
                 : fmt(free) + " free" + kv }};
    }}

    // Pick the target build for this cluster - not simply the biggest thing that
    // fits. Measured KL divergence flattens above 4 bits per weight (0.41 at
    // Q4_K_XL against 0.24 at Q5 and 0.10 at Q8), so paying an extra 200 GB for
    // Q8 buys almost nothing and costs the KV headroom that decides how much
    // context and how many concurrent streams you get. So: the CHEAPEST rung
    // that still clears 4 bits, and only if none does, the best of what is left.
    function pickIn(ladder, over) {{
      var fits = ladder.filter(function (r) {{ return r.gb + over <= cluster; }});
      if (!fits.length) return null;
      var full = fits.filter(function (r) {{
        return r.kind === "native" || (r.kind !== "pruned" && r.bpw >= 4);
      }});
      if (full.length) return full[full.length - 1];   // ladder is largest-first
      return fits[0];                                  // best available below 4 bpw
    }}
    function pick(ladder) {{ return pickIn(ladder, OVERHEAD_TEXT); }}

    function band(rung) {{
      if (rung.kind === "native") {{
        // Media checkpoints ship at a stated precision and bundle encoders and a
        // VAE with the transformer, so a bits-per-weight band would be invented.
        return {{ k: "full", label: "As published", why: "" }};
      }}
      if (rung.kind === "pruned") {{
        return {{ k: "pruned", label: "Expert-pruned",
                 why: "This build was not quantised down, it was pruned: whole experts were scored and " +
                      "deleted. The surviving weights are near lossless, and the capacity they came from " +
                      "is gone. Bits per weight does not describe this loss." }};
      }}
      for (var i = 0; i < BANDS.length; i++) {{
        if (rung.bpw >= BANDS[i][0]) {{
          return {{ k: BANDS[i][1], label: BANDS[i][2], why: BANDS[i][3] }};
        }}
      }}
      return {{ k: "unusable", label: "Below agentic-usable", why: "" }};
    }}

    // freeGB is per machine when the model fits on one, so multiply the stream
    // count by the number of copies to get the total the whole group serves.
    function ctxRows(bpt, maxctx, freeGB, copies) {{
      if (!bpt || !maxctx || freeGB <= 0) return [];
      copies = copies || 1;
      var out = [];
      [[1, "full"], [0.75, "three quarters"], [0.5, "half"], [0.25, "a quarter"]].forEach(function (f) {{
        var tok = Math.round(maxctx * f[0]);
        var per = bpt * tok;                       // bytes
        out.push({{ tok: tok, frac: f[1], perGB: per / 1e9,
                   streams: Math.floor((freeGB * 1e9) / per) * copies }});
      }});
      // A model can load and still have no room for a quarter of its advertised
      // window - MiniMax M3 on one 256 GB machine is exactly that. Saying "runs"
      // above four rows of "does not fit" is useless, so state what does fit.
      if (out[out.length - 1].streams < 1) {{
        var maxTok = Math.floor((freeGB * 1e9) / bpt);
        out.push({{ tok: maxTok, frac: "largest that fits", cap: true,
                   perGB: (bpt * maxTok) / 1e9, streams: maxTok >= 2048 ? copies : 0 }});
      }}
      return out;
    }}

    // Decode ceiling: bandwidth over the bytes read to emit one token. This is
    // a mirror of tracker/throughput.py, which carries the full statement of
    // what it assumes and where it is wrong. Keep the two identical.
    //
    // M.bw is one machine's bandwidth on purpose. Pipeline parallelism splits
    // the layers, but every token still traverses all of them in sequence, so
    // pooling does not raise the bound - it only adds a Thunderbolt hop that
    // this does not model.
    function ceiling(rung, pl, ctx) {{
      if (!rung || rung.kind === 'pruned' || rung.kind === 'native') return null;
      if (!pl.active || !pl.params) return null;
      var kv = pl.kv && pl.kv.bpt ? (pl.kv.bpt * (ctx || 0)) / 1e9 : 0;
      var per = rung.gb * (pl.active / pl.params) + kv;
      return per > 0 ? M.bw / per : null;
    }}

    function ceilingWhy(rung, pl) {{
      if (rung && rung.kind === 'pruned')
        return 'expert-pruned build, so per-token traffic does not scale with file size';
      if (rung && rung.kind === 'native') return 'not an autoregressive decoder';
      if (!pl.active) return 'no published active-parameter count for this model';
      return 'inputs missing';
    }}

    function tpsFmt(t) {{
      return t >= 10 ? String(Math.round(t)) : t.toFixed(1);
    }}

    function tokFmt(t) {{
      return t >= 1000000 ? (t / 1000000).toFixed(t % 1000000 ? 2 : 0) + "M"
                          : Math.round(t / 1000) + "k";
    }}

    document.querySelectorAll("[data-payload]").forEach(function (el) {{
      var pl;
      try {{ pl = JSON.parse(el.getAttribute("data-payload")); }} catch (e) {{ return; }}
      var engs = pl.engines || [];
      var isText = (el.getAttribute("data-mod") || "text") === "text";
      var over = isText ? OVERHEAD_TEXT : OVERHEAD_MEDIA;
      var kvWord = pl.kv && pl.kv.bpt ? " for KV" : "";

      var chosen = null, rung = null;
      for (var i = 0; i < engs.length; i++) {{
        var r = pickIn(engs[i].ladder, over);
        if (r) {{ chosen = engs[i]; rung = r; break; }}
      }}
      if (!chosen && engs.length) {{
        // nothing fits anywhere: report whichever engine has the smallest build
        chosen = engs.reduce(function (a, b) {{
          return b.ladder[b.ladder.length - 1].gb < a.ladder[a.ladder.length - 1].gb ? b : a;
        }});
        rung = chosen.ladder[chosen.ladder.length - 1];
      }}
      if (!chosen) {{
        var f0 = el.querySelector(".fit");
        if (f0) f0.textContent = "no build published";
        return;
      }}

      var f = fitDetail(rung.gb, over, kvWord);
      var bd = band(rung);
      var cls, label;
      if (chosen.s === "blocked" || chosen.s === "unknown") {{
        cls = chosen.s; label = chosen.label;
      }} else if (f.tooBig) {{
        cls = "toolarge"; label = "Too large";
      }} else if (bd.k === "unusable") {{
        cls = "blocked"; label = "Too degraded";
      }} else if (bd.k === "mild" || bd.k === "low" || bd.k === "pruned") {{
        cls = "degraded"; label = chosen.s === "ready" ? "Runs, " + bd.label.toLowerCase() : chosen.label;
      }} else {{
        cls = chosen.s; label = chosen.label;
      }}

      if (el.classList.contains("ix-row")) {{
        el.__pick = {{ model: el.querySelector(".ix-name").textContent.trim(), engine: chosen.name,
                      engineId: chosen.id, gb: rung.gb, bpw: rung.bpw, band: bd.k,
                      tooBig: f.tooBig || bd.k === "unusable" || chosen.s === "blocked" }};
        el.className = "ix-row v-" + cls;
        var st = el.querySelector(".ix-status");
        st.className = "ix-status v-" + cls;
        st.textContent = label;
        el.querySelector(".ix-eng").textContent = chosen.name;
        el.querySelector(".ix-size").textContent = fmt(rung.gb);
        el.querySelector(".fit").textContent = f.short;
        var tpsEl = el.querySelector(".ix-tps");
        if (tpsEl) {{
          var cap = f.tooBig ? null : ceiling(rung, pl, REF_CTX);
          tpsEl.textContent = cap ? '\u2264 ' + tpsFmt(cap) + ' tok/s' : '';
          tpsEl.title = cap
            ? 'Decode ceiling at 8k context on one machine: ' + M.bw +
              ' GB/s of bandwidth over the bytes read per token. Arithmetic, not a measurement.'
            : '';
        }}
        return;
      }}

      el.className = "model v-" + cls;
      // Open the card on the engine the glance row names for this cluster, so the
      // two never disagree - unless the reader has already picked a tab by hand.
      var grp = el.querySelector(".eng");
      if (grp && !grp.hasAttribute("data-user-picked")) {{
        var want = grp.querySelector('.eng-tab[data-eng="' + chosen.id + '"]');
        if (want && want.getAttribute("aria-selected") !== "true") {{
          grp.querySelectorAll(".eng-tab").forEach(function (t) {{
            t.setAttribute("aria-selected", t === want ? "true" : "false");
          }});
          grp.querySelectorAll(".eng-pane").forEach(function (pa) {{
            pa.hidden = pa.getAttribute("data-eng") !== chosen.id;
          }});
        }}
      }}
      var vb = el.querySelector(".verdict");
      vb.className = "verdict v-" + cls;
      vb.textContent = label;
      var mf = el.querySelector(".model-fit");
      if (mf) {{
        mf.className = "model-fit" + (f.tooBig ? " toolarge" : "");
        mf.textContent = chosen.s === "blocked"
          ? "No engine here can load this yet \u2014 see the tabs below for why."
          : f.tooBig
            ? "Does not fit. Smallest build is " + chosen.name + " at " + fmt(rung.gb) + ", which " + f.text + "."
            : "Best fit here: " + chosen.name + ", " + fmt(rung.gb) + " of weights, " + f.text + ".";
      }}

      // Each engine tab reports its own rung on the same cluster.
      engs.forEach(function (eng) {{
        var pane = el.querySelector('.eng-pane[data-eng="' + eng.id + '"]');
        if (!pane) return;
        var fit = pane.querySelector(".eng-fit");
        if (!fit || !fit.hasAttribute("data-has-ladder")) return;
        var r = pickIn(eng.ladder, over) || eng.ladder[eng.ladder.length - 1];
        var pf = fitDetail(r.gb, over, kvWord), pb = band(r);

        fit.classList.toggle("toolarge", pf.tooBig);
        fit.textContent = pf.tooBig
          ? "Too large: " + fmt(pf.resident) + " resident, " + pf.text + "."
          : fmt(pf.resident) + " resident on this cluster, " + pf.text + ".";

        var link = pane.querySelector(".build-link"), bpw = pane.querySelector(".build-bpw");
        if (link) {{
          link.textContent = r.label;
          link.setAttribute("href", "https://huggingface.co/" + r.repo);
        }}
        if (bpw) {{
          bpw.textContent = r.kind === "pruned" ? "expert-pruned"
                          : r.kind === "native" ? "as published"
                          : r.bpw.toFixed(2) + " bits/weight";
          bpw.className = "build-bpw b-" + pb.k;
        }}

        var fid = pane.querySelector(".fidelity");
        if (fid) {{
          if (pb.k === "full") {{
            fid.hidden = true;
          }} else {{
            fid.hidden = false;
            fid.className = "fidelity b-" + pb.k;
            fid.innerHTML = "<strong>" + pb.label + ".</strong> " + pb.why +
              (eng.note ? " " + eng.note : "");
          }}
        }}

        var tp = pane.querySelector(".tput");
        if (tp) {{
          var capRef = pf.tooBig ? null : ceiling(r, pl, REF_CTX);
          if (pf.tooBig) {{
            tp.hidden = true;
          }} else if (!capRef) {{
            tp.hidden = false;
            tp.className = "tput none";
            tp.innerHTML = '<span class="tput-k">Decode ceiling</span>' +
              '<span class="tput-v">not derived</span>' +
              '<span class="tput-why">' + ceilingWhy(r, pl) + '.</span>';
          }} else {{
            var maxc = pl.kv && pl.kv.maxctx ? pl.kv.maxctx : 0;
            var capMax = maxc ? ceiling(r, pl, maxc) : null;
            var wGb = r.gb * (pl.active / pl.params);
            var perGb = wGb + (pl.kv && pl.kv.bpt ? (pl.kv.bpt * REF_CTX) / 1e9 : 0);
            tp.hidden = false;
            tp.className = "tput";
            tp.innerHTML = '<span class="tput-k">Decode ceiling</span>' +
              '<span class="tput-v">\u2264 ' + tpsFmt(capRef) + ' tok/s</span>' +
              '<span class="tput-at">at 8k context' +
              (capMax ? ', \u2264 ' + tpsFmt(capMax) + ' tok/s at ' + tokFmt(maxc) : '') + '</span>' +
              '<span class="tput-why">' + M.bw + ' GB/s over ' + perGb.toFixed(1) +
              ' GB read per token (' + wGb.toFixed(1) + ' GB of active weights' +
              (pl.kv && pl.kv.bpt ? ' plus KV' : '') +
              '). Upper bound from published specifications, not a measurement \u2014 real decode ' +
              'lands below it. <a href="#throughput">How this is derived, and where it is wrong</a>' +
              (n > 1 && pf.nodes > 1 ? '. Pooling does not raise it: every token still crosses ' +
                'every layer, plus a Thunderbolt hop this does not model' : '') + '.</span>';
          }}
        }}

        var wrap = pane.querySelector(".ctx-wrap");
        if (wrap) {{
          var rows = pf.tooBig ? [] : ctxRows(pl.kv.bpt, pl.kv.maxctx, pf.free, pf.copies);
          if (!rows.length) {{
            wrap.hidden = true;
          }} else {{
            wrap.hidden = false;
            wrap.querySelector("tbody").innerHTML = rows.map(function (c) {{
              var label = c.cap ? tokFmt(c.tok) + " &mdash; " + c.frac
                                : tokFmt(c.tok) + " (" + c.frac + ")";
              var rowCap = ceiling(r, pl, c.tok);
              return "<tr" + (c.cap ? ' class="ctx-cap"' : "") + "><td>" + label + "</td><td>" +
                     (c.perGB < 1 ? (c.perGB * 1000).toFixed(0) + " MB" : c.perGB.toFixed(1) + " GB") +
                     '</td><td class="ctx-t">' +
                     (rowCap ? '\u2264 ' + tpsFmt(rowCap) + ' tok/s' : '\u2014') +
                     '</td><td class="ctx-n' + (c.streams < 1 ? ' none' : '') + '">' +
                     (c.streams < 1 ? "does not fit" : c.streams) + "</td></tr>";
            }}).join("");
            wrap.querySelector(".ctx-why").textContent =
              "KV at fp16: " + (pl.kv.bpt / 1024).toFixed(1) + " KiB per token. " + pl.kv.why + ". " +
              (pf.copies > 1 ? "Stream counts are the total across all " + pf.copies +
                               " machines, each running its own copy. " : "") +
              "Quantising the KV cache to 8-bit doubles every count above. The ceiling " +
              "column is one stream's bound at that context, not the group's total.";
          }}
        }}
      }});
    }});

    // The winner for the selected job: walk the curated ranking and take the
    // first model that both fits and clears that job's fidelity gate. Ranking is
    // fixed at build time because the benchmarks are not mutually comparable;
    // what changes with the cluster is only which entries are reachable.
    var ucId = ucSel ? ucSel.value : "";
    var uc = null;
    for (var ui = 0; ui < USE_CASES.length; ui++) {{
      if (USE_CASES[ui].id === ucId) {{ uc = USE_CASES[ui]; break; }}
    }}
    // Models built for a different kind of output are not "unranked", they are
    // irrelevant - a text model has no place in an image-generation table. The
    // default view shows text models; the others appear with their category.
    var wantMod = uc ? uc.mod : "text";
    document.querySelectorAll(".ix-row").forEach(function (r) {{
      r.classList.remove("uc-best", "uc-out-of-scope");
      r.hidden = (r.getAttribute("data-mod") || "text") !== wantMod;
    }});
    if (!uc) {{
      if (ucOut) ucOut.innerHTML = "";
      document.querySelectorAll(".ix-row").forEach(function (r) {{
        r.style.order = "";
        r.classList.remove("no-bar");
        var bar = r.querySelector(".ix-bar");
        if (bar) bar.style.width = "0";
      }});
    }} else {{
      var inScope = {{}};
      uc.rank.forEach(function (r) {{ inScope[r[0]] = true; }});
      var winner = null;
      for (var ri = 0; ri < uc.rank.length; ri++) {{
        var row = document.querySelector('.ix-row[data-model="' + uc.rank[ri][0] + '"]');
        if (!row || !row.__pick || row.__pick.tooBig) continue;
        if (BAND_RANK[row.__pick.band] > BAND_RANK[uc.gate]) continue;
        winner = {{ row: row, entry: uc.rank[ri] }};
        break;
      }}
      // Rank order for the chosen job, then everything that does not fit or does
      // not publish a number for it. The container is a flex column, so `order`
      // re-sequences without touching the DOM.
      var pos = {{}};
      uc.rank.forEach(function (r, i) {{ pos[r[0]] = i; }});

      // Bar widths are a ratio against the leader, but only where that ratio
      // means something: the two rows have to be quoting the SAME benchmark.
      // Scoring 87.4 on one suite against 1554 on another is not a comparison,
      // and this page's whole argument is that you cannot rank across suites.
      var num = function (v) {{
        var m = String(v).match(/-?[0-9]+([.][0-9]+)?/);
        return m ? parseFloat(m[0]) : null;
      }};
      var leadMetric = null, leadVal = null;
      for (var li = 0; li < uc.rank.length; li++) {{
        var lrow = document.querySelector('.ix-row[data-model="' + uc.rank[li][0] + '"]');
        if (lrow && lrow.__pick && !lrow.__pick.tooBig &&
            BAND_RANK[lrow.__pick.band] <= BAND_RANK[uc.gate]) {{
          leadMetric = uc.rank[li][1];
          leadVal = num(uc.rank[li][2]);
          break;
        }}
      }}
      // Compare anything on the leader's scale, not only its exact suite. SWE-bench
      // Pro against SWE-bench Verified is imprecise; an Elo of 1554 against a
      // percentage is meaningless. So: both values have to sit in the same band.
      var sameScale = function (a, b) {{
        return (a <= 100) === (b <= 100);
      }};
      var barFor = function (mid) {{
        if (!leadVal || pos[mid] === undefined) return null;
        var v = num(uc.rank[pos[mid]][2]);
        if (v === null || !sameScale(v, leadVal)) return null;
        return Math.max(0, Math.min(100, (v / leadVal) * 100));
      }};
      document.querySelectorAll(".ix-row").forEach(function (r) {{
        var mid = r.getAttribute("data-model");
        var ranked = pos[mid] !== undefined;
        if (!ranked) r.classList.add("uc-out-of-scope");
        var usable = ranked && r.__pick && !r.__pick.tooBig &&
                     BAND_RANK[r.__pick.band] <= BAND_RANK[uc.gate];
        // three tiers: usable in rank order, then ranked-but-unusable, then unranked
        var w0 = usable ? barFor(mid) : null;
        // Sort the usable tier by bar length so the chart reads monotonically;
        // rows with no comparable figure keep their curated place behind them.
        r.style.order = usable
          ? (w0 === null ? 1050 + pos[mid] : Math.round((100 - w0) * 10))
          : (ranked ? 2000 + pos[mid] : 4000);
        var bar = r.querySelector(".ix-bar");
        if (bar) {{
          var w = usable ? barFor(mid) : null;
          bar.style.width = w === null ? "0" : w.toFixed(1) + "%";
          // Only meaningful when the category has a numeric leader to compare
          // against; with no benchmark at all, nothing is "off scale".
          r.classList.toggle("no-bar", usable && w === null && leadVal !== null);
        }}
      }});
      if (winner) {{
        winner.row.classList.add("uc-best");
        var pk = winner.row.__pick;
        ucOut.innerHTML = "Best for <strong>" + uc.label.toLowerCase() + "</strong> on this cluster: " +
          "<strong>" + pk.model + "</strong> via " + pk.engine + ", " + fmt(pk.gb) +
          (pk.bpw === null ? ", as published" : " at " + pk.bpw.toFixed(2) + " bits/weight") +
          " &mdash; " + winner.entry[1] + " " + winner.entry[2] + "." +
          "<details class='uc-fold'><summary>How are these ranked?</summary>" +
          "<span class='uc-why'>" + uc.axis +
          (leadVal === null ? " No comparable numeric benchmark is published for these, so there are no bars."
                            : " Dimmed rows publish no number for this job. Ordered by bar where a " +
                              "comparable figure exists; bars are each model's score as a share of the " +
                              "leader's <em>" + leadMetric + "</em>. Rows quoting a different suite on the " +
                              "same scale are included and are approximate; a row marked \u2020 quotes a " +
                              "figure that is not on that scale at all, so it gets no bar rather than a " +
                              "fabricated one.") + "</span></details>";
      }} else {{
        ucOut.innerHTML = "<strong>Nothing suitable fits this cluster.</strong>" +
          "<span class='uc-why'>Every model ranked for " + uc.label.toLowerCase() +
          " is either too large here, or only fits at a precision below what this job tolerates. " +
          "Add memory, add a machine, or pick a different job.</span>";
      }}
    }}

    var p = new URLSearchParams();
    p.set("chip", chip); p.set("mem", g); p.set("n", n);
    if (ucId) p.set("uc", ucId);
    history.replaceState(null, "", location.pathname + "?" + p.toString() + (location.hash || ""));
  }}

  var ucSel = document.getElementById("uc-sel"), ucOut = document.getElementById("uc-out");
  if (ucSel) {{
    var o0 = document.createElement("option");
    o0.value = ""; o0.textContent = "Anything - just show me the list";
    ucSel.appendChild(o0);
    USE_CASES.forEach(function (u) {{
      var o = document.createElement("option");
      o.value = u.id; o.textContent = u.label;
      ucSel.appendChild(o);
    }});
    var uc0 = q.get("uc");
    if (uc0 && USE_CASES.some(function (u) {{ return u.id === uc0; }})) ucSel.value = uc0;
    ucSel.addEventListener("change", apply);
  }}

  // The hash is the view: no hash shows the list, #model-id shows that card.
  // Keeping the state in the URL means deep links, the browser Back button and
  // the on-page Back control are all the same mechanism.
  var listEl = document.getElementById("list"),
      detailEl = document.getElementById("detail"),
      backEl = document.getElementById("back"),
      cards = [].slice.call(document.querySelectorAll(".model"));

  function route(pin) {{
    // Swapping views changes the document height, and Chrome's scroll anchoring
    // reacts by moving the viewport to keep its anchor element stable - which is
    // what made this jump even with the anchor click prevented. Pin the scroll
    // position across the swap.
    var y = window.scrollY;
    var want = (location.hash || "").replace(/^#/, "");
    var found = null;
    cards.forEach(function (c) {{
      var mine = c.id === "card-" + want;
      c.hidden = !mine;
      if (mine) found = c;
    }});
    if (listEl) listEl.hidden = !!found;
    if (detailEl) detailEl.hidden = !found;
    // A fragment that is not a card is an in-page anchor - the throughput
    // explainer, say. Open the fold it lives in and let it scroll; pinning the
    // scroll position here would swallow the jump entirely.
    if (!found && want) {{
      var target = document.getElementById(want);
      if (target) {{
        var fold = target.querySelector ? target.querySelector("details") : null;
        if (fold) fold.open = true;
        window.scrollTo(0, Math.max(0, target.getBoundingClientRect().top + window.scrollY - 14));
        return null;
      }}
    }}
    // Restore now and again after layout: the adjustment does not always land in
    // the same tick as the attribute change.
    if (pin !== false) {{
      var hold = function () {{ if (window.scrollY !== y) window.scrollTo(0, y); }};
      hold();
      requestAnimationFrame(hold);
    }}
    return found;
  }}

  if (listEl) {{
    listEl.addEventListener("click", function (ev) {{
      var row = ev.target.closest ? ev.target.closest(".ix-row") : null;
      if (!row || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button !== 0) return;
      ev.preventDefault();
      history.pushState(null, "", location.pathname + location.search +
                        "#" + row.getAttribute("data-model"));
      route();
    }});
  }}
  var backBottomEl = document.getElementById("back-bottom");
  if (backBottomEl) {{
    backBottomEl.addEventListener("click", function () {{
      history.pushState(null, "", location.pathname + location.search);
      // Skip the scroll pin here: from the bottom of a long card, holding
      // position would leave the reader staring at the reference panels.
      route(false);
      var rig = document.getElementById("rig");
      if (rig) {{
        window.scrollTo(0, Math.max(0, rig.getBoundingClientRect().top + window.scrollY - 14));
      }}
    }});
  }}
  if (backEl) {{
    backEl.addEventListener("click", function () {{
      // Keep the cluster and use-case selections, drop the card.
      history.pushState(null, "", location.pathname + location.search);
      route();
    }});
  }}
  window.addEventListener("hashchange", function () {{ route(); }});
  window.addEventListener("popstate", function () {{ route(); }});

  chipSel.value = chip;
  fillMem(mem);
  nSel.value = n;
  chipSel.addEventListener("change", function () {{ chip = chipSel.value; fillMem(parseInt(memSel.value, 10)); apply(); }});
  memSel.addEventListener("change", apply);
  nSel.addEventListener("change", apply);
  apply();
  route();
}})();
</script>

<script>
  (function () {{
    document.querySelectorAll(".eng").forEach(function (grp) {{
      var tabs = [].slice.call(grp.querySelectorAll(".eng-tab"));
      var panes = [].slice.call(grp.querySelectorAll(".eng-pane"));
      function show(t) {{
        tabs.forEach(function (x) {{ x.setAttribute("aria-selected", x === t ? "true" : "false"); }});
        var id = t.getAttribute("data-eng");
        panes.forEach(function (p) {{ p.hidden = p.getAttribute("data-eng") !== id; }});
      }}
      tabs.forEach(function (t, i) {{
        t.addEventListener("click", function () {{ grp.setAttribute("data-user-picked", "1"); show(t); }});
        t.addEventListener("keydown", function (ev) {{
          var d = ev.key === "ArrowRight" ? 1 : ev.key === "ArrowLeft" ? -1 : 0;
          if (!d) return;
          ev.preventDefault();
          var next = tabs[(i + d + tabs.length) % tabs.length];
          show(next);
          next.focus();
        }});
      }});
    }});
  }})();
</script>

<script>
  (function () {{
    var el = document.querySelector("time.ago");

    if (!el) return;
    var t = Date.parse(el.getAttribute("datetime"));
    if (isNaN(t)) return;
    var abs = el.textContent;
    function render() {{
      var mins = Math.floor((Date.now() - t) / 60000);
      if (mins < 0) mins = 0;
      var out;
      if (mins < 1) out = "just now";
      else if (mins < 60) out = mins + "m ago";
      else if (mins < 1440) out = Math.floor(mins / 60) + "h " + (mins % 60) + "m ago";
      else out = Math.floor(mins / 1440) + "d " + Math.floor((mins % 1440) / 60) + "h ago";
      el.textContent = out;
      el.title = abs;
    }}
    render();
    setInterval(render, 60000);
  }})();
</script>
"""

if __name__ == "__main__":  # pragma: no cover - use tracker/build.py instead
    raise SystemExit("run: python3 tracker/build.py")
