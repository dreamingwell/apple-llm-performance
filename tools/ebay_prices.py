#!/usr/bin/env python3
"""Harvest used-Mac prices from eBay for the chips Apple no longer sells.

    set -a; . ~/.config/ebay.env; set +a
    python3 tools/ebay_prices.py --chip m3ultra

STATUS: this tool works, and its output is NOT publishable. Read on before
using it, because the reason is the whole point.

eBay exposes sold prices through the Marketplace Insights API. That API is
access-restricted: a client-credentials token that works fine for Browse gets
`403 Access denied`, and requesting the `buy.marketplace.insights` scope fails
outright with "the requested scope is invalid, unknown, malformed, or exceeds
the scope granted". The legacy `findCompletedItems` operation that used to serve
this need was retired and now answers `418`. Without an approved Marketplace
Insights application there is no sold data at all.

What Browse gives instead is *active listings* - what sellers are currently
asking. That is real and current, but it is a different population from
completed sales, and the difference is not small. Measured on 2026-08-29 for a
Mac Studio M3 Ultra with 256 GB, filtered to that exact chip and memory and
bucketed by storage so the SSD is not doing the work:

    1 TB   n=11   median $10,900   range $7,900-$24,995
    2 TB   n=13   median $12,000
    4 TB   n=8    median $10,875

Apple sells a NEW M5 Ultra with 256 GB for $9,499. A used three-generation-old
machine cannot really cost more than a new better one; what the number actually
shows is that overpriced listings are the ones that fail to sell, so they
accumulate and drag the median of *active* stock upward. Publishing this would
tell a reader to buy the wrong thing, which is worse than telling them nothing -
so `data/hardware/` carries no eBay figures and the `ebay_sold` basis is
currently unused.

The tool is kept because the filtering, outlier rejection and sample floor are
the reusable part. If someone gets a Marketplace Insights application approved,
point `search()` at `item_sales/search`, change the basis to `ebay_sold`, and
the rest of this stands.

The filtering is deliberately strict, because a loose query is worse than no
data. A search for "Mac Studio M3 Ultra 256GB" returns M4 Max machines, 96 GB
machines, bare logic boards and empty boxes; every one of those would drag a
median somewhere untrue.
"""
import argparse
import json
import os
import re
import statistics
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tracker"))

MIN_SAMPLE = 5          # below this a median is an anecdote, not a price
OUTLIER_FACTOR = 3.0    # drop anything beyond this multiple of the median

# Titles that are not a whole working computer.
JUNK = re.compile(r"\b(logic\s*board|motherboard|for\s*parts|parts\s*only|as[- ]is|"
                  r"box\s*only|empty\s*box|screen|display\s*only|cracked|broken|"
                  r"no\s*power|read\s*description|bundle\s*of|lot\s*of|case|stand|"
                  r"adapter|cable|keyboard|mouse|riser|enclosure)\b", re.I)
# Sealed machines are priced against Apple's list, not the used market.
SEALED = re.compile(r"\b(bnib|brand\s*new|sealed|unopened|new\s*in\s*box|nib)\b", re.I)


def token():
    app, cert = os.environ.get("EBAY_APP_ID"), os.environ.get("EBAY_CERT_ID")
    if not app or not cert:
        raise SystemExit("set EBAY_APP_ID and EBAY_CERT_ID (source ~/.config/ebay.env)")
    import base64
    b = base64.b64encode(f"{app}:{cert}".encode()).decode()
    req = urllib.request.Request(
        "https://api.ebay.com/identity/v1/oauth2/token",
        data=urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope"}).encode(),
        headers={"Authorization": f"Basic {b}",
                 "Content-Type": "application/x-www-form-urlencoded"})
    return json.load(urllib.request.urlopen(req))["access_token"]


def search(tok, q, offset=0):
    u = ("https://api.ebay.com/buy/browse/v1/item_summary/search?q="
         + urllib.parse.quote(q) + f"&limit=200&offset={offset}"
         + "&filter=conditions:{USED|SELLER_REFURBISHED|CERTIFIED_REFURBISHED}")
    req = urllib.request.Request(u, headers={
        "Authorization": f"Bearer {tok}", "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"})
    return json.load(urllib.request.urlopen(req))


def wants(title, label, gb):
    """Does this title name this exact chip and this exact memory size?"""
    t = title.lower()
    if JUNK.search(t) or SEALED.search(t):
        return False
    # the chip, as a whole token: "m3 ultra" must not match "m3 max"
    chip = label.lower()
    if not re.search(rf"\bm{chip[1]}\b", t):
        return False
    tier = chip.split(" ", 1)[1] if " " in chip else ""
    for other in ("pro", "max", "ultra"):
        present = re.search(rf"\b{other}\b", t) is not None
        if present != (other == tier):
            return False
    # the memory, and not as part of the SSD size
    if not re.search(rf"\b{gb}\s*gb\b(?!\s*ssd)", t):
        return False
    return True


def price_for(tok, label, gb, verbose=False):
    seen, kept = {}, []
    for q in (f"Apple Mac {label} {gb}GB", f"Mac {label} {gb}GB RAM"):
        try:
            d = search(tok, q)
        except Exception as e:
            print(f"    query failed: {str(e)[:60]}", file=sys.stderr)
            continue
        for it in d.get("itemSummaries", []) or []:
            iid = it.get("itemId")
            if iid in seen:
                continue
            seen[iid] = True
            title = it.get("title", "")
            if not wants(title, label, gb):
                continue
            try:
                p = float(it["price"]["value"])
            except Exception:
                continue
            if p <= 0:
                continue
            kept.append((p, title))
    if len(kept) < MIN_SAMPLE:
        return None, len(kept), kept
    med = statistics.median([p for p, _ in kept])
    kept = [(p, t) for p, t in kept if p <= med * OUTLIER_FACTOR and p >= med / OUTLIER_FACTOR]
    if len(kept) < MIN_SAMPLE:
        return None, len(kept), kept
    ps = sorted(p for p, _ in kept)
    return {"usd": int(round(statistics.median(ps))), "n": len(ps),
            "low": int(ps[0]), "high": int(ps[-1])}, len(ps), kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chip")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    # The picker's chip table is the source of truth for what can be selected;
    # validate.py reads it the same way, so a price can never describe a machine
    # nobody can pick.
    import validate
    chips = validate.picker_machines()
    if chips is None:
        raise SystemExit("could not read MACHINES out of render_status.py")
    tok = token()
    todo = [k for k in chips if a.all or k == a.chip]
    if not todo:
        raise SystemExit(f"unknown chip; have: {', '.join(chips)}")
    for cid in todo:
        label, mems = chips[cid]
        print(f"== {cid} ({label})")
        for gb in sorted(mems):
            res, n, kept = price_for(tok, label, gb)
            if res:
                print(f"   {gb:>4} GB  ${res['usd']:>7,}  n={res['n']:<3} "
                      f"range ${res['low']:,}-${res['high']:,}")
            else:
                print(f"   {gb:>4} GB  -- only {n} usable listings, below the "
                      f"{MIN_SAMPLE}-listing floor")
            if a.verbose:
                for p, t in sorted(kept)[:8]:
                    print(f"        ${p:>8,.0f}  {t[:72]}")


if __name__ == "__main__":
    main()
