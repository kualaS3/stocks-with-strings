"""Price fetching for the study.

One function, one cache file. Prices come from Yahoo Finance and are stored
as adjusted closes, because returns must be split and dividend adjusted.
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE = Path(__file__).resolve().parents[1] / "results" / "prices.csv"


def fetch_prices(tickers, period="2y", cache=CACHE):
    """Download adjusted closes for tickers, or read the cache if it exists."""
    if cache.exists():
        frame = pd.read_csv(cache, index_col=0, parse_dates=True)
        missing = [t for t in tickers if t not in frame.columns]
        if not missing:
            return frame
    frame = yf.download(tickers, period=period, auto_adjust=False,
                        progress=False)["Adj Close"]
    frame = frame.dropna(how="all")
    cache.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(cache)
    return frame


def log_returns(prices):
    """Daily log returns, in percent."""
    import numpy as np

    return 100 * np.log(prices / prices.shift(1)).dropna()
