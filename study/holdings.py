"""13F common ownership from SEC EDGAR full text search.

The idea comes from Anton and Polk (2014), "Connected Stocks": stocks
that share owners move together more. This module measures how much two
stocks share owners, against what chance would predict, using only free
public SEC data.

How the counts work: every quarter, each manager over $100M files a 13F
with an information table listing its holdings by CUSIP. The SEC full
text search index (efts.sec.gov) can count, for one CUSIP, how many 13F
filings in a window contain it. That count is the number of filers
holding the stock. An AND query counts the filers holding both stocks.

The score, per pair and quarter:
  n_i, n_j    filers holding stock i, filers holding stock j
  n_both      filers holding both
  N           all filers with a 13F in the window
  expected    n_i * n_j / N, the overlap if holdings were independent
  lift        n_both / expected. 1 is chance. Above 1, funds holding i
              are more likely than chance to also hold j.
  jaccard     n_both / (n_i + n_j - n_both). The share of the combined
              holder set that holds both. Purely descriptive.

Two honest caveats, baked into the numbers:
  - Counts are filings, not filers. About 3% of hits are amendments
    (13F-HR/A), so a filer who amended is counted twice. That inflates
    n_i, n_j, n_both and N by roughly the same share, so lift is barely
    moved, but the raw counts are a touch high.
  - N counts every filer with a 13F in the window, including notice
    filers who hold nothing and report through another manager. That
    inflates N a little and so pulls every lift down by the same small
    amount. Rankings across pairs are unaffected.

SEC rules: max 10 requests per second, and a descriptive User-Agent.
This module waits 0.15 seconds between calls and retries on 429 or 5xx.
"""

import json
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import requests

BASE = "https://efts.sec.gov/LATEST/search-index"
HEADERS = {"User-Agent": "StocksWithStrings research timmy311001@gmail.com",
           "Accept": "application/json"}
FORMS = "13F-HR"
SLEEP = 0.15

CACHE = Path(__file__).resolve().parents[1] / "results" / "holdings_counts.json"


def _get(params, tries=4):
    """One search call, with backoff on rate limits and server errors."""
    url = BASE + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(tries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 429 or resp.status_code >= 500:
                last = RuntimeError(f"SEC returned {resp.status_code}")
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            time.sleep(SLEEP)
            return resp.json()
        except requests.RequestException as exc:
            last = exc
            time.sleep(2 ** attempt)
    raise last


def search_total(query, start, end):
    """Total hits for a query over 13F filings filed between start and end.

    Dates are ISO strings. The total is exact when it is under 10,000.
    """
    params = {"q": query, "dateRange": "custom",
              "startdt": start, "enddt": end, "forms": FORMS}
    data = _get(params)
    return int(data["hits"]["total"]["value"])


def count_holders(cusip, start, end):
    """Filers holding the stock with this CUSIP in the window."""
    return search_total(f'"{cusip}"', start, end)


def count_both(cusip_x, cusip_y, start, end):
    """Filers holding both stocks in the window."""
    return search_total(f'"{cusip_x}" AND "{cusip_y}"', start, end)


def _week_starts(start, end):
    """Monday to Sunday slices covering the window, for N counting."""
    first = date.fromisoformat(start)
    last = date.fromisoformat(end)
    out = []
    day = first
    while day <= last:
        week_end = min(day + timedelta(days=6), last)
        out.append((day.isoformat(), week_end.isoformat()))
        day = week_end + timedelta(days=1)
    return out


def count_filers(start, end):
    """Distinct filers with a 13F in the window.

    The query "13F" matches two documents per filing (the form and its
    information table), so the raw total is about double the filings.
    This walks the window week by week and counts distinct accessions,
    which is the filing count. Weekly slices stay under the 10,000 hit
    cap that would cut off a whole quarter query.
    """
    seen = set()
    for week_start, week_end in _week_starts(start, end):
        offset = 0
        while True:
            params = {"q": "13F", "dateRange": "custom",
                      "startdt": week_start, "enddt": week_end,
                      "forms": FORMS, "size": 100, "from": offset}
            data = _get(params)
            hits = data["hits"]["hits"]
            if not hits:
                break
            seen.update(h["_source"]["adsh"] for h in hits)
            offset += len(hits)
            if offset >= int(data["hits"]["total"]["value"]):
                break
    return len(seen)


def lift(n_both, n_i, n_j, n_total):
    """Common ownership lift: observed overlap over chance overlap."""
    if n_i <= 0 or n_j <= 0 or n_total <= 0:
        return float("nan")
    expected = n_i * n_j / n_total
    return n_both / expected if expected > 0 else float("nan")


def jaccard(n_both, n_i, n_j):
    """Share of the combined holder set that holds both stocks."""
    union = n_i + n_j - n_both
    return n_both / union if union > 0 else float("nan")


def fetch_quarter(tickers, pairs, cusip, quarter, cache=CACHE):
    """Holder counts for one quarter, from cache when available.

    tickers is the list of stock tickers, pairs a list of (x, y) tuples,
    quarter a dict with file_start and file_end. Returns a dict with
    n_total, n (per ticker) and n_both (per pair). Set refresh True to
    re-pull from the SEC instead of reading the cache.
    """
    label = quarter["period_end"]
    cached = {}
    if cache.exists():
        cached = json.loads(cache.read_text())
    key = f"quarter:{label}"
    if key in cached:
        return cached[key]

    start, end = quarter["file_start"], quarter["file_end"]
    n_total = count_filers(start, end)
    n = {t: count_holders(cusip[t], start, end) for t in tickers}
    n_both = {}
    for x, y in pairs:
        n_both[f"{x}/{y}"] = count_both(cusip[x], cusip[y], start, end)
    out = {"period_end": label, "file_start": start, "file_end": end,
           "n_total": n_total, "n": n, "n_both": n_both}
    cached[key] = out
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(cached, indent=2))
    return out
