"""Run study 1: does the shock day metric recover the priors?

Usage: python -m study.run_study
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from study.data import fetch_prices, log_returns
from study.metric import pair_metric, read_metric, stock_residuals
from study.pairs import MARKET, PAIRS, PERIOD

SECTOR = {
    "KO": "XLP", "PEP": "XLP",
    "V": "XLF", "MA": "XLF",
    "HD": "XLI", "LOW": "XLI",
    "NVDA": "XLK", "TSM": "XLK", "AAPL": "XLK",
}

RESULTS = Path(__file__).resolve().parents[1] / "results"


def main():
    tickers = sorted({p["x"] for p in PAIRS} | {p["y"] for p in PAIRS}
                     | {MARKET} | set(SECTOR.values()))
    prices = fetch_prices(tickers, period=PERIOD)
    rets = log_returns(prices)
    print(f"window: {rets.index[0].date()} to {rets.index[-1].date()}, "
          f"{len(rets)} trading days")

    market = rets[MARKET]
    sector_rets = {t: rets[SECTOR[t]] for t in SECTOR}
    resid = stock_residuals(rets[[t for t in SECTOR]], market,
                            pd.Series(sector_rets))

    raw = rets[[t for t in SECTOR]]
    rows = []
    for pair in PAIRS:
        x, y = pair["x"], pair["y"]
        m = pair_metric(resid[x], resid[y])
        reading = read_metric(m["shock_corr_avg"], m["p_xy"], m["p_yx"])
        raw_corr = float(raw[x].corr(raw[y]))
        match = (reading == pair["prior"]
                 or (reading.startswith("neutral") and pair["prior"] == "control"))
        rows.append({
            "pair": f"{x}/{y}", "prior": pair["prior"], "reading": reading,
            "match": match,
            "shock_corr_avg": round(m["shock_corr_avg"], 3),
            "shock_corr_xy": round(m["shock_corr_xy"], 3),
            "shock_corr_yx": round(m["shock_corr_yx"], 3),
            "p_xy": round(m["p_xy"], 3), "p_yx": round(m["p_yx"], 3),
            "resid_corr_full": round(m["resid_corr_full"], 3),
            "raw_corr": round(raw_corr, 3),
            "n_shocks": m["n_shocks_xy"],
        })

    table = pd.DataFrame(rows)
    print(table.to_string(index=False))
    table.to_csv(RESULTS / "study_1.csv", index=False)

    n_match = int(table["match"].sum())
    lines = [
        "# Study 1 results",
        "",
        f"Window: {rets.index[0].date()} to {rets.index[-1].date()} "
        f"({len(rets)} trading days).",
        "",
        "Shock days are the top 5% of absolute residual days for the shocked",
        "stock. Residuals come from regressing each stock on SPY plus its own",
        "sector ETF. P values come from a 5000 draw permutation test.",
        "",
        table.to_markdown(index=False),
        "",
        f"Score: {n_match}/{len(table)} priors recovered.",
        "",
        "Reading the contrasts: raw_corr is what a naive correlation says.",
        "resid_corr_full is the portfolio side definition. shock_corr_avg is",
        "the demand side metric this study is testing.",
    ]
    (RESULTS / "study_1.md").write_text("\n".join(lines) + "\n")
    print(f"\nScore: {n_match}/{len(table)} priors recovered.")


if __name__ == "__main__":
    main()
