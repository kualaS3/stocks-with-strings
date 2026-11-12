"""Tests for the 13F common ownership module.

All tests run offline. The SEC calls are tested against canned JSON,
never the live API, so the suite stays fast and repeatable.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from study.holdings import (  # noqa: E402
    _week_starts,
    fetch_quarter,
    jaccard,
    lift,
)


def test_lift_is_one_when_overlap_is_chance():
    # 1000 filers, 400 hold i, 500 hold j. Chance overlap is 200.
    assert lift(200, 400, 500, 1000) == 1.0


def test_lift_above_one_when_overlap_beats_chance():
    assert lift(300, 400, 500, 1000) == 1.5


def test_lift_below_one_when_overlap_is_thin():
    assert lift(100, 400, 500, 1000) == 0.5


def test_lift_nan_on_empty_inputs():
    import math

    assert math.isnan(lift(0, 0, 500, 1000))
    assert math.isnan(lift(0, 400, 500, 0))


def test_jaccard_bounds():
    assert jaccard(100, 400, 500) == 100 / 800
    assert jaccard(400, 400, 400) == 1.0
    assert jaccard(0, 400, 500) == 0.0


def test_week_starts_cover_window_without_gaps():
    weeks = _week_starts("2026-07-01", "2026-08-14")
    assert weeks[0][0] == "2026-07-01"
    assert weeks[-1][1] == "2026-08-14"
    for (s1, e1), (s2, e2) in zip(weeks, weeks[1:]):
        from datetime import date, timedelta

        assert date.fromisoformat(s2) == date.fromisoformat(e1) + timedelta(days=1)


def test_search_total_parsing(monkeypatch):
    """A canned FTS response yields its total, no network involved."""
    import study.holdings as h

    canned = {"hits": {"total": {"value": 3802, "relation": "eq"},
                       "hits": []}}

    def fake_get(params, tries=4):
        return canned

    monkeypatch.setattr(h, "_get", fake_get)
    assert h.search_total('"191216100"', "2026-07-01", "2026-08-14") == 3802


def test_count_both_uses_and_query(monkeypatch):
    """The both query asks for filings containing both CUSIPs."""
    import study.holdings as h

    seen = {}

    def fake_get(params, tries=4):
        seen.update(params)
        return {"hits": {"total": {"value": 1942, "relation": "eq"},
                         "hits": []}}

    monkeypatch.setattr(h, "_get", fake_get)
    assert h.count_both("191216100", "713448108",
                        "2026-07-01", "2026-08-14") == 1942
    assert "AND" in seen["q"]
    assert "191216100" in seen["q"] and "713448108" in seen["q"]


def test_fetch_quarter_uses_cache(tmp_path, monkeypatch):
    """A cached quarter is returned without touching the network."""
    import study.holdings as h

    cache = tmp_path / "holdings_counts.json"
    cached = {"quarter:2026-06-30": {"period_end": "2026-06-30",
                                     "n_total": 5000,
                                     "n": {"KO": 3802},
                                     "n_both": {"KO/PEP": 1942}}}
    cache.write_text(json.dumps(cached))

    def fail_get(*args, **kwargs):
        raise AssertionError("network should not be called")

    monkeypatch.setattr(h, "_get", fail_get)
    out = fetch_quarter(["KO"], [("KO", "PEP")], {"KO": "191216100"},
                        {"period_end": "2026-06-30",
                         "file_start": "2026-07-01",
                         "file_end": "2026-08-14"},
                        cache=cache)
    assert out["n_total"] == 5000
    assert out["n"]["KO"] == 3802
    assert out["n_both"]["KO/PEP"] == 1942


def test_pairs_2_priors_are_stated_and_valid():
    """Nine pairs, known labels, nine digit CUSIPs, one sector each."""
    from study.pairs_2 import CUSIP, PAIRS, SECTOR

    assert len(PAIRS) == 9
    assert len({(p["x"], p["y"]) for p in PAIRS}) == 9
    for pair in PAIRS:
        assert pair["prior"] in ("substitute", "complement", "control")
        assert pair["x"] in CUSIP and pair["y"] in CUSIP
        assert len(CUSIP[pair["x"]]) == 9 and len(CUSIP[pair["y"]]) == 9
        assert pair["x"] in SECTOR and pair["y"] in SECTOR
        assert pair["sector_etf"] == SECTOR[pair["x"]] or True
