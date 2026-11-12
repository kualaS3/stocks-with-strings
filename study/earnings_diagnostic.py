"""Diagnostic: same question, but only on earnings days.

Generic shock days mix two things: firm specific news and sub sector news
that the broad sector ETF does not remove. Earnings days are the clean
version: the shock belongs to the reporting firm alone. If the substitute
pairs flip to negative here while staying positive on generic shocks, the
diagnosis is confirmed and the fix is to use earnings days as the shocks.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from study.data import fetch_prices, log_returns
from study.metric import stock_residuals
from study.pairs import MARKET, PAIRS, PERIOD
from study.run_study import SECTOR


def earnings_dates(ticker, index_dates):
    """Earnings dates for ticker that fall on trading days in the window.

    Yahoo throttles repeated calls, so this sleeps between tickers. The
    index is timezone aware, so dates are normalised before matching.
    """
    import time

    time.sleep(1.0)
    try:
        dates = yf.Ticker(ticker).get_earnings_dates(limit=12)
        if dates is None or dates.empty:
            return []
        stamps = pd.to_datetime(dates.index).tz_localize(None).normalize()
        return [d for d in stamps if d in index_dates]
    except Exception:
        return []


def main():
    tickers = sorted({p["x"] for p in PAIRS} | {p["y"] for p in PAIRS}
                     | {MARKET} | set(SECTOR.values()))
    prices = fetch_prices(tickers, period=PERIOD)
    rets = log_returns(prices)
    market = rets[MARKET]
    sector_rets = {t: rets[SECTOR[t]] for t in SECTOR}
    resid = stock_residuals(rets[[t for t in SECTOR]], market,
                            pd.Series(sector_rets))

    rows = []
    index_dates = set(resid.index)
    for pair in PAIRS:
        x, y = pair["x"], pair["y"]
        for ticker, other in ((x, y), (y, x)):
            days = earnings_dates(ticker, index_dates)
            if len(days) < 4:
                rows.append({"pair": f"{ticker} earns -> {other}",
                             "n": len(days), "mean_other_resid": None,
                             "corr": None})
                continue
            xs = resid.loc[days, ticker]
            ys = resid.loc[days, other]
            rows.append({
                "pair": f"{ticker} earns -> {other}",
                "n": len(days),
                "mean_other_resid": round(float(ys.mean()), 3),
                "corr": round(float(np.corrcoef(xs, ys)[0, 1]), 3),
            })
    table = pd.DataFrame(rows)
    print(table.to_string(index=False))
    table.to_csv(Path(__file__).resolve().parents[1] / "results"
                 / "earnings_diagnostic.csv", index=False)


if __name__ == "__main__":
    main()
