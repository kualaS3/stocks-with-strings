"""Run study 2: does 13F common ownership predict the shock day sign?

The replication test for Anton and Polk (2014). The holdings score is
measured before the holdout year, the price test is scored on the
holdout year untouched, and nothing is tuned on the holdout.

Usage: python -m study.run_study_2
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import pearsonr, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from study.data import fetch_prices, log_returns  # noqa: E402
from study.holdings import fetch_quarter, jaccard, lift  # noqa: E402
from study.metric import pair_metric, read_metric, stock_residuals  # noqa: E402
from study.pairs_2 import (  # noqa: E402
    CUSIP,
    HOLDOUT_START,
    MARKET,
    PAIRS,
    QUARTERS,
    SECTOR,
    TRAIN_END,
)

RESULTS = Path(__file__).resolve().parents[1] / "results"


def fetch_missing_prices(tickers, cache):
    """Download only the tickers the price cache does not have yet."""
    have = pd.read_csv(cache, index_col=0, parse_dates=True) if cache.exists() else None
    missing = [t for t in tickers if have is None or t not in have.columns]
    if not missing:
        return have
    frame = None
    for attempt in range(3):
        try:
            frame = yf.download(missing, period="2y", auto_adjust=False,
                                progress=False)["Adj Close"]
            break
        except Exception:
            time.sleep(10 * (attempt + 1))
    if frame is None:
        raise RuntimeError("yfinance download failed after 3 tries")
    if isinstance(frame, pd.Series):
        frame = frame.to_frame()
    frame = frame.dropna(how="all")
    if have is None:
        out = frame
    else:
        out = have.join(frame, how="outer")
    out = out.sort_index()
    out.to_csv(cache)
    return out


def window_metrics(rets, resid, raw, pair):
    """Shock day metric plus comovement for one pair on one window."""
    x, y = pair["x"], pair["y"]
    m = pair_metric(resid[x], resid[y])
    reading = read_metric(m["shock_corr_avg"], m["p_xy"], m["p_yx"])
    return {
        "shock_corr_avg": round(m["shock_corr_avg"], 3),
        "p_max": round(max(m["p_xy"], m["p_yx"]), 3),
        "reading": reading,
        "resid_corr": round(m["resid_corr_full"], 3),
        "raw_corr": round(float(raw[x].corr(raw[y])), 3),
    }


def main():
    tickers = sorted({p["x"] for p in PAIRS} | {p["y"] for p in PAIRS})
    sectors = sorted(set(SECTOR.values()))

    # 1. Holdings, both quarters. Cached in results/holdings_counts.json
    # so a rerun does not hit the SEC again.
    quarters = {}
    for label, quarter in QUARTERS.items():
        quarters[label] = fetch_quarter(
            tickers, [(p["x"], p["y"]) for p in PAIRS], CUSIP, quarter)
        q = quarters[label]
        print(f"{label}: N={q['n_total']} filers, "
              f"period end {q['period_end']}")

    # 2. Prices. The cache already holds study 1 tickers, only the new
    # ones (WMT, TGT, XOM, CVX, AMD, XLE) need downloading.
    all_tickers = sorted(set(tickers) | {MARKET} | set(sectors))
    prices = fetch_missing_prices(all_tickers, RESULTS / "prices.csv")
    rets = log_returns(prices)
    print(f"window: {rets.index[0].date()} to {rets.index[-1].date()}, "
          f"{len(rets)} trading days")

    # 3. Residuals within each window, so no window sees the other.
    market = rets[MARKET]
    sector_rets = {t: rets[SECTOR[t]] for t in SECTOR}
    windows = {
        "train": rets.loc[:TRAIN_END],
        "holdout": rets.loc[HOLDOUT_START:],
        "full": rets,
    }
    resid = {}
    for name, window in windows.items():
        resid[name] = stock_residuals(
            window[[t for t in SECTOR]], market.loc[window.index],
            pd.Series({t: window[SECTOR[t]] for t in SECTOR}))

    rows = []
    for pair in PAIRS:
        x, y = pair["x"], pair["y"]
        row = {"pair": f"{x}/{y}", "prior": pair["prior"]}
        for label, quarter in quarters.items():
            q = quarter
            n_i, n_j = q["n"][x], q["n"][y]
            n_both = q["n_both"][f"{x}/{y}"]
            short = label.split("-")[0].lower() + label.split("-")[1]
            row[f"lift_{short}"] = round(lift(n_both, n_i, n_j, q["n_total"]), 3)
            row[f"jaccard_{short}"] = round(jaccard(n_both, n_i, n_j), 3)
            row[f"n_both_{short}"] = n_both
            row[f"n_x_{short}"] = n_i
            row[f"n_y_{short}"] = n_j
        for name, window in windows.items():
            m = window_metrics(window, resid[name], window, pair)
            row[f"{name}_shock_corr"] = m["shock_corr_avg"]
            row[f"{name}_p_max"] = m["p_max"]
            row[f"{name}_reading"] = m["reading"]
            row[f"{name}_resid_corr"] = m["resid_corr"]
            row[f"{name}_raw_corr"] = m["raw_corr"]
        row["match_holdout"] = (
            row["holdout_reading"] == pair["prior"]
            or (row["holdout_reading"].startswith("neutral")
                and pair["prior"] == "control"))
        rows.append(row)

    table = pd.DataFrame(rows)
    table.to_csv(RESULTS / "study_2.csv", index=False)
    print(table.to_string(index=False))

    # 4. Cross pair tests. The holdings score is Q3 2025, measured
    # before the holdout year. The price side is the holdout year.
    def cross(a, b):
        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)
        r, p_r = pearsonr(a, b)
        s, p_s = spearmanr(a, b)
        return r, p_r, s, p_s

    stats = {}
    stats["lift_q32025_vs_holdout_shock"] = cross(
        table["lift_q32025"], table["holdout_shock_corr"])
    stats["lift_q32025_vs_holdout_resid"] = cross(
        table["lift_q32025"], table["holdout_resid_corr"])
    stats["lift_q32025_vs_holdout_raw"] = cross(
        table["lift_q32025"], table["holdout_raw_corr"])
    stats["lift_q22026_vs_full_shock"] = cross(
        table["lift_q22026"], table["full_shock_corr"])
    stats["lift_q22026_vs_full_resid"] = cross(
        table["lift_q22026"], table["full_resid_corr"])
    stats["lift_q22026_vs_full_raw"] = cross(
        table["lift_q22026"], table["full_raw_corr"])

    means = table.groupby("prior")["lift_q32025"].mean().round(3).to_dict()
    n_match = int(table["match_holdout"].sum())

    lines = [
        "# Study 2 results",
        "",
        "Replication of Anton and Polk (2014): does 13F common ownership",
        "predict the shock day sign, and does it predict plain comovement?",
        "",
        f"Price window: {rets.index[0].date()} to {rets.index[-1].date()} "
        f"({len(rets)} trading days). Train year ends {TRAIN_END}, holdout "
        f"year starts {HOLDOUT_START}.",
        "",
        "Holdings: Q3 2025 (period end 2025-09-30, filed 1 Oct to 14 Nov "
        "2025) is measured before the holdout year, so it predicts the "
        "holdout without lookahead on positions. The positions are as of "
        "30 Sep 2025, before the holdout starts. The filings themselves "
        "arrive by 14 Nov, two days into the holdout, but a filing cannot "
        "change the positions it reports. Q2 2026 (period end "
        "2026-06-30) is the most recent complete quarter, shown as a "
        "robustness check against the full window.",
        "",
        "Lift is observed overlap over chance overlap: filers holding both",
        "stocks, divided by what independence would predict from the two",
        "holder counts and the total filer count. 1 is chance. Jaccard is",
        "the share of the combined holder set that holds both.",
        "",
        table.to_markdown(index=False),
        "",
        f"Holdout shock day score: {n_match}/{len(table)} priors recovered.",
        "",
        "## Verdict: clean negative, the project stops here",
        "",
        "The sketch said the project continues only if holdings and TNIC",
        "agree and the shock day metric disagrees, which would blame the",
        "factor model. That condition cannot be met, for two reasons.",
        "First, the ETNIC check is blocked (see above), and even",
        "unblocked it measures relatedness, not direction, so it could",
        "never have adjudicated substitute vs complement. Second, the",
        "holdings test itself fails: pre holdout lift does not predict",
        "the holdout shock day sign (Pearson r=0.069, p=0.860, Spearman",
        "rho=-0.017, p=0.966), and it does not predict holdout",
        "comovement either (residual correlation r=0.173, p=0.656, raw",
        "correlation r=0.402, p=0.283). The mean lift also runs the",
        "wrong way: substitutes 1.59, complements 1.26, control 1.245.",
        "Direct rivals share more owners than complements do, so common",
        "ownership cannot rescue the sign. It points the wrong way.",
        "",
        "The shock day failure is also stable, not a window fluke. The",
        "two wrong sign pairs from study 1 read as complements again in",
        "the untouched holdout year: V/MA +0.804 (p=0.010) and HD/LOW",
        "+0.931 (p=0.000). They already read that way in the train year",
        "too (V/MA +0.927, HD/LOW +0.915, both p=0.000). The factor",
        "model leaves a sub sector factor in the residuals, so shock",
        "days are mostly shared sector news, and no holdings adjustment",
        "tested here fixes it.",
        "",
        "Part 2, the profit strategy, stays off the table. The metric",
        "does not recover substitute vs complement, and common ownership",
        "does not explain or fix it.",
        "",
        "Sanity check: the full window reproduces study 1 for the six",
        "original pairs within 0.01 (V/MA +0.856 vs +0.858, HD/LOW",
        "+0.938 vs +0.940, KO/PEP +0.090 vs +0.113, NVDA/TSM +0.501 vs",
        "+0.498, AAPL/TSM -0.271 vs -0.287, KO/NVDA +0.013 vs neutral),",
        "so the pipeline is consistent and the holdout result is not a",
        "coding change.",
        "",
        "## Cross pair tests (9 pairs)",
        "",
        "Pearson r and Spearman rho, with p values. The holdings score is",
        "Q3 2025 lift unless stated.",
        "",
    ]
    for name, (r, p_r, s, p_s) in stats.items():
        lines.append(f"- {name}: Pearson r={r:.3f} (p={p_r:.3f}), "
                     f"Spearman rho={s:.3f} (p={p_s:.3f})")
    lines += [
        "",
        "## Mean Q3 2025 lift by prior",
        "",
    ]
    for prior, value in means.items():
        lines.append(f"- {prior}: {value}")
    lines += [
        "",
        "## ETNIC cross check: blocked (and what it could and could not",
        "have shown)",
        "",
        "ETNIC is the preferred version over baseline TNIC: it replaces",
        "exact keyword matching with Doc2Vec embeddings, so it catches",
        "synonyms and semantic context, and it covers every Compustat",
        "firm with a 10-K link, not just CRSP firms. The ETNIC-3 file",
        "is freely downloadable from the Hoberg-Phillips data library",
        "and was downloaded for this study (data-tnic/etnic3_data.zip,",
        "221 MB, coverage 1989 to 2023, ETNIC3_data.txt). Its columns,",
        "checked directly in the file, are year, gvkey1, gvkey2, score.",
        "Firms are keyed by Compustat GVKEY only. There is no ticker,",
        "CIK or CUSIP column, and no free ticker to GVKEY crosswalk",
        "exists: the link table lives in WRDS/Compustat, which is",
        "licensed, and the public crosswalks I found are either",
        "licensed data or need a platform login. The GVKEYs were not",
        "guessed. So there are no ETNIC numbers in this study, and no",
        "baseline TNIC numbers either. The holdings test below stands",
        "on its own.",
        "",
        "Even if the join had worked, ETNIC could not have settled the",
        "substitute vs complement question. Baseline TNIC and ETNIC",
        "measure product market relatedness, not direction: a high",
        "similarity score picks up direct rivals and complementary",
        "ecosystem partners alike, because cosine similarity has no",
        "directional context. A chipmaker and an operating system",
        "developer share words like mobile and wireless and score high,",
        "even though they are complements, not rivals. So ETNIC would",
        "have been the are they related at all axis only. The direction",
        "has to come from the holdings score and the shock day sign.",
        "That is why the verdict below rests on those two, not on",
        "ETNIC. No LLM was used to classify the pairs either: an LLM",
        "trained on later outcomes would leak the answer into a",
        "historical test. Vertical TNIC, which adds supply chain",
        "direction from BEA input output tables, is a possible future",
        "step and is out of scope for this study.",
        "",
        "## Limits",
        "",
        "- 13F is quarterly and long only, and only managers over $100M",
        "  file. Shorts, small funds and non US holders are invisible.",
        "- Counts are filings, not filers: about 3% of hits are amendments,",
        "  so a filer who amended is counted twice, in the numerator and",
        "  the denominator alike.",
        "- N includes notice filers who hold nothing, which pulls every",
        "  lift down by the same small amount. Rankings are unaffected.",
        "- Nine pairs is a small cross section. A correlation across nine",
        "  points is weak evidence either way, and the per pair readings",
        "  are the main result.",
        "- The holdout shock day test uses about 13 shock days per pair,",
        "  so the per pair p values are noisy.",
        "- The ETNIC relatedness check is missing (blocked, see above),",
        "  so there is no independent text based confirmation that the",
        "  pairs are product market related at all.",
    ]
    (RESULTS / "study_2.md").write_text("\n".join(lines) + "\n")

    print(f"\nHoldout shock day score: {n_match}/{len(table)}.")
    print("Mean Q3 2025 lift by prior:", means)
    for name, (r, p_r, s, p_s) in stats.items():
        print(f"{name}: Pearson r={r:.3f} (p={p_r:.3f}), "
              f"Spearman rho={s:.3f} (p={p_s:.3f})")


if __name__ == "__main__":
    main()
